import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import uuid

from app.services.openai_rate_limiter import rate_limiter
from app.services.openai_monitor import monitor

logger = logging.getLogger(__name__)

T = TypeVar('T')

@dataclass
class BatchConfig:
    """Configuration for batch processing"""
    batch_size: int = 25  # Small batches to prevent timeouts
    max_concurrent_batches: int = 3  # Limit concurrent processing
    timeout_per_batch: int = 120  # 2 minutes per batch
    retry_failed_batches: bool = True
    max_batch_retries: int = 2

class MultiBatchProcessor(Generic[T]):
    """Advanced multi-batch processor for handling large datasets with AI agents"""
    
    def __init__(self, config: BatchConfig = None):
        self.config = config or BatchConfig()
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_batches)
    
    def process_batches(
        self,
        items: List[T],
        process_func: Callable[[List[T], str], T],
        combine_func: Callable[[List[T]], T],
        agent_name: str,
        item_name: str = "items"
    ) -> T:
        """
        Process items in batches with parallel execution and robust error handling
        
        Args:
            items: List of items to process
            process_func: Function to process a single batch (batch_items, batch_id) -> result
            combine_func: Function to combine all batch results -> final_result
            agent_name: Name of the agent for logging
            item_name: Name of items for logging (e.g., "keywords", "products")
        
        Returns:
            Combined result from all batches
        """
        if not items:
            logger.warning(f"[{agent_name}] No {item_name} to process")
            return combine_func([])
        
        total_items = len(items)
        logger.info(f"[{agent_name}] Processing {total_items} {item_name} in batches of {self.config.batch_size}")
        
        # Split items into batches
        batches = self._create_batches(items)
        logger.info(f"[{agent_name}] Created {len(batches)} batches")
        
        # Process batches with monitoring
        batch_results = []
        failed_batches = []
        
        try:
            # Submit all batches to executor
            future_to_batch = {}
            for i, batch in enumerate(batches):
                batch_id = f"{agent_name}_batch_{i+1}"
                future = self.executor.submit(
                    self._process_single_batch,
                    batch, batch_id, process_func, agent_name, item_name
                )
                future_to_batch[future] = (i, batch_id)
            
            # Collect results as they complete
            for future in as_completed(future_to_batch, timeout=self.config.timeout_per_batch * len(batches)):
                batch_index, batch_id = future_to_batch[future]
                
                try:
                    result = future.result(timeout=self.config.timeout_per_batch)
                    batch_results.append((batch_index, result))
                    logger.info(f"[{agent_name}] ✅ Batch {batch_index + 1} completed successfully")
                    
                except Exception as e:
                    logger.error(f"[{agent_name}] ❌ Batch {batch_index + 1} failed: {str(e)}")
                    failed_batches.append((batch_index, batch_id, str(e)))
            
            # Sort results by batch index to maintain order
            batch_results.sort(key=lambda x: x[0])
            results = [result for _, result in batch_results]
            
            # Handle failed batches
            if failed_batches and self.config.retry_failed_batches:
                logger.warning(f"[{agent_name}] Retrying {len(failed_batches)} failed batches")
                retry_results = self._retry_failed_batches(
                    failed_batches, batches, process_func, agent_name, item_name
                )
                results.extend(retry_results)
            
            # Combine all results
            final_result = combine_func(results)
            
            success_count = len(batch_results)
            total_batches = len(batches)
            logger.info(f"[{agent_name}] ✅ Processing complete: {success_count}/{total_batches} batches successful")
            
            return final_result
            
        except Exception as e:
            logger.error(f"[{agent_name}] ❌ Batch processing failed: {str(e)}")
            raise e
    
    def _create_batches(self, items: List[T]) -> List[List[T]]:
        """Split items into batches"""
        batches = []
        for i in range(0, len(items), self.config.batch_size):
            batch = items[i:i + self.config.batch_size]
            batches.append(batch)
        return batches
    
    def _process_single_batch(
        self,
        batch_items: List[T],
        batch_id: str,
        process_func: Callable[[List[T], str], T],
        agent_name: str,
        item_name: str
    ) -> T:
        """Process a single batch with rate limiting and monitoring"""
        request_id = f"{batch_id}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Start monitoring
            monitor.log_request_start(agent_name, request_id, len(batch_items))
            
            # Apply rate limiting
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(rate_limiter.wait_for_rate_limit())
            loop.close()
            
            # Process the batch
            start_time = time.time()
            result = process_func(batch_items, batch_id)
            duration = time.time() - start_time
            
            # Log success
            monitor.log_success(agent_name, request_id, len(batch_items))
            rate_limiter.reset_retry_count(request_id)
            
            logger.info(f"[{agent_name}] Batch {batch_id} processed {len(batch_items)} {item_name} in {duration:.1f}s")
            return result
            
        except Exception as e:
            # Log error
            monitor.log_error(agent_name, request_id, str(e))
            logger.error(f"[{agent_name}] Batch {batch_id} failed: {str(e)}")
            raise e
    
    def _retry_failed_batches(
        self,
        failed_batches: List[tuple],
        original_batches: List[List[T]],
        process_func: Callable[[List[T], str], T],
        agent_name: str,
        item_name: str
    ) -> List[T]:
        """Retry failed batches with exponential backoff"""
        retry_results = []
        
        for batch_index, batch_id, error in failed_batches:
            if not rate_limiter.should_retry(batch_id):
                logger.warning(f"[{agent_name}] Skipping retry for {batch_id} (max retries exceeded)")
                continue
            
            try:
                # Wait with exponential backoff
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(rate_limiter.wait_with_exponential_backoff(batch_id, 1))
                loop.close()
                
                # Retry the batch
                batch_items = original_batches[batch_index]
                result = self._process_single_batch(batch_items, batch_id, process_func, agent_name, item_name)
                retry_results.append(result)
                
                logger.info(f"[{agent_name}] ✅ Retry successful for batch {batch_index + 1}")
                
            except Exception as retry_error:
                logger.error(f"[{agent_name}] ❌ Retry failed for batch {batch_index + 1}: {str(retry_error)}")
                # Don't raise here, continue with other batches
        
        return retry_results
    
    def process_with_fallback(
        self,
        items: List[T],
        primary_func: Callable[[List[T], str], T],
        fallback_func: Callable[[List[T], str], T],
        combine_func: Callable[[List[T]], T],
        agent_name: str,
        item_name: str = "items"
    ) -> T:
        """
        Process items with a fallback strategy
        
        Args:
            items: List of items to process
            primary_func: Primary processing function
            fallback_func: Fallback processing function (e.g., smaller batches)
            combine_func: Function to combine results
            agent_name: Name of the agent
            item_name: Name of items
        
        Returns:
            Combined result
        """
        try:
            # Try primary processing
            logger.info(f"[{agent_name}] Attempting primary processing for {len(items)} {item_name}")
            return self.process_batches(items, primary_func, combine_func, agent_name, item_name)
            
        except Exception as primary_error:
            logger.warning(f"[{agent_name}] Primary processing failed: {str(primary_error)}")
            logger.info(f"[{agent_name}] Falling back to alternative processing")
            
            try:
                # Fallback to smaller batches
                fallback_config = BatchConfig(
                    batch_size=max(10, self.config.batch_size // 2),
                    max_concurrent_batches=max(1, self.config.max_concurrent_batches // 2),
                    timeout_per_batch=self.config.timeout_per_batch * 2
                )
                
                fallback_processor = MultiBatchProcessor(fallback_config)
                return fallback_processor.process_batches(
                    items, fallback_func, combine_func, f"{agent_name}_fallback", item_name
                )
                
            except Exception as fallback_error:
                logger.error(f"[{agent_name}] Both primary and fallback processing failed")
                logger.error(f"Primary error: {str(primary_error)}")
                logger.error(f"Fallback error: {str(fallback_error)}")
                raise fallback_error
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "batch_size": self.config.batch_size,
            "max_concurrent_batches": self.config.max_concurrent_batches,
            "timeout_per_batch": self.config.timeout_per_batch,
            "rate_limiter_stats": rate_limiter.get_stats(),
            "monitor_stats": monitor.get_overall_stats()
        }
    
    def __del__(self):
        """Cleanup executor on deletion"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# Global processor instance
multi_batch_processor = MultiBatchProcessor()
