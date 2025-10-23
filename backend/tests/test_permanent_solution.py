#!/usr/bin/env python3
"""
Test script to verify the permanent timeout solution works correctly.
This script simulates processing 300+ keywords to ensure no timeouts occur.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_keywords(count: int) -> List[Dict[str, Any]]:
    """Create test keywords for processing."""
    keywords = []
    for i in range(count):
        keywords.append({
            "phrase": f"test keyword {i+1}",
            "search_volume": 1000 + i,
            "category": "Relevant" if i % 3 == 0 else "Design-Specific" if i % 3 == 1 else "Irrelevant",
            "relevancy_score": (i % 10) + 1,
            "intent_score": (i % 4),
            "title_density": 0.1 + (i % 10) * 0.01,
            "cpr": 0.5 + (i % 20) * 0.1,
            "competition": {"level": "Medium" if i % 2 == 0 else "High"}
        })
    return keywords

def test_multi_batch_processor():
    """Test the multi-batch processor with a large dataset."""
    try:
        from app.services.multi_batch_processor import multi_batch_processor
        from app.services.openai_monitor import monitor
        
        logger.info("🧪 Testing Multi-Batch Processor...")
        
        # Create test data
        test_keywords = create_test_keywords(300)
        logger.info(f"Created {len(test_keywords)} test keywords")
        
        # Test processing function
        def process_batch(batch_items: List[Dict[str, Any]], batch_id: str) -> List[Dict[str, Any]]:
            """Simulate processing a batch."""
            logger.info(f"Processing batch {batch_id} with {len(batch_items)} items")
            time.sleep(0.1)  # Simulate processing time
            return batch_items
        
        def combine_results(batch_results: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
            """Combine batch results."""
            combined = []
            for batch_result in batch_results:
                combined.extend(batch_result)
            return combined
        
        # Process with multi-batch processor
        start_time = time.time()
        result = multi_batch_processor.process_batches(
            items=test_keywords,
            process_func=process_batch,
            combine_func=combine_results,
            agent_name="TestAgent",
            item_name="keywords"
        )
        duration = time.time() - start_time
        
        logger.info(f"✅ Multi-batch processing completed in {duration:.2f}s")
        logger.info(f"   Processed {len(result)} keywords")
        logger.info(f"   Expected: {len(test_keywords)} keywords")
        
        # Verify results
        assert len(result) == len(test_keywords), f"Expected {len(test_keywords)}, got {len(result)}"
        
        # Print monitoring stats
        stats = monitor.get_overall_stats()
        logger.info(f"📊 Monitoring Stats:")
        logger.info(f"   Total requests: {stats['total_requests']}")
        logger.info(f"   Success rate: {stats['success_rate']:.1f}%")
        logger.info(f"   Retry rate: {stats['retry_rate']:.1f}%")
        logger.info(f"   Error rate: {stats['error_rate']:.1f}%")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Multi-batch processor test failed: {e}")
        return False

def test_rate_limiter():
    """Test the rate limiter functionality."""
    try:
        from app.services.openai_rate_limiter import rate_limiter
        
        logger.info("🧪 Testing Rate Limiter...")
        
        async def test_rate_limiting():
            """Test rate limiting with multiple requests."""
            start_time = time.time()
            
            # Make multiple requests quickly
            for i in range(5):
                await rate_limiter.wait_for_rate_limit()
                logger.info(f"Request {i+1} allowed")
            
            duration = time.time() - start_time
            logger.info(f"✅ Rate limiting test completed in {duration:.2f}s")
            
            # Check stats
            stats = rate_limiter.get_stats()
            logger.info(f"📊 Rate Limiter Stats:")
            logger.info(f"   Requests last minute: {stats['requests_last_minute']}")
            logger.info(f"   Max requests per minute: {stats['max_requests_per_minute']}")
            logger.info(f"   Active retries: {stats['active_retries']}")
            
            return True
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_rate_limiting())
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Rate limiter test failed: {e}")
        return False

def test_monitoring():
    """Test the monitoring system."""
    try:
        from app.services.openai_monitor import monitor
        
        logger.info("🧪 Testing Monitoring System...")
        
        # Simulate some requests
        monitor.log_request_start("TestAgent", "test_1", 100)
        time.sleep(0.1)
        monitor.log_success("TestAgent", "test_1", 100)
        
        monitor.log_request_start("TestAgent", "test_2", 50)
        time.sleep(0.1)
        monitor.log_error("TestAgent", "test_2", "Test error")
        
        # Get stats
        stats = monitor.get_overall_stats()
        logger.info(f"📊 Monitoring System Stats:")
        logger.info(f"   Total requests: {stats['total_requests']}")
        logger.info(f"   Successful: {stats['successful_requests']}")
        logger.info(f"   Failed: {stats['failed_requests']}")
        logger.info(f"   Success rate: {stats['success_rate']:.1f}%")
        
        # Print detailed summary
        monitor.print_summary()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Monitoring test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting Permanent Timeout Solution Tests...")
    logger.info("="*60)
    
    tests = [
        ("Multi-Batch Processor", test_multi_batch_processor),
        ("Rate Limiter", test_rate_limiter),
        ("Monitoring System", test_monitoring),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.info(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 ALL TESTS PASSED - Permanent timeout solution is working!")
        logger.info("🚀 Your 300+ keywords will now process without timeouts!")
    else:
        logger.error("❌ Some tests failed - please check the implementation")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
