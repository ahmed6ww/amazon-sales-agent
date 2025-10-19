import time
import logging
import threading
from typing import Dict, Any, List
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    start_time: float
    end_time: float = 0
    retry_count: int = 0
    error_count: int = 0
    success: bool = False
    error_message: str = ""

@dataclass
class AgentStats:
    """Statistics for an agent"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_retries: int = 0
    total_errors: int = 0
    total_duration: float = 0
    avg_duration: float = 0
    requests_per_minute: float = 0

class OpenAIMonitor:
    """Comprehensive monitoring for OpenAI API requests and performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.agent_stats: Dict[str, AgentStats] = defaultdict(AgentStats)
        self.active_requests: Dict[str, RequestMetrics] = {}
        self.request_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()  # Use thread-safe lock instead of asyncio lock
    
    def log_request_start(self, agent_name: str, request_id: str, item_count: int = 0):
        """Log the start of a request"""
        start_time = time.time()
        self.active_requests[request_id] = RequestMetrics(start_time=start_time)
        
        logger.info(f"🔄 [{agent_name}] Starting request {request_id} with {item_count} items")
        
        # Update agent stats
        self.agent_stats[agent_name].total_requests += 1
    
    def log_retry(self, agent_name: str, request_id: str, attempt: int, delay: float, error: str = ""):
        """Log a retry attempt"""
        if request_id in self.active_requests:
            self.active_requests[request_id].retry_count += 1
        
        self.agent_stats[agent_name].total_retries += 1
        
        logger.warning(f"🔄 [{agent_name}] Retry #{attempt} for {request_id} after {delay:.1f}s delay - {error}")
    
    def log_error(self, agent_name: str, request_id: str, error: str):
        """Log an error"""
        if request_id in self.active_requests:
            self.active_requests[request_id].error_count += 1
            self.active_requests[request_id].error_message = error
        
        self.agent_stats[agent_name].total_errors += 1
        self.agent_stats[agent_name].failed_requests += 1
        
        logger.error(f"❌ [{agent_name}] Error in {request_id}: {error}")
    
    def log_success(self, agent_name: str, request_id: str, item_count: int = 0):
        """Log successful completion"""
        end_time = time.time()
        
        if request_id in self.active_requests:
            request_metrics = self.active_requests[request_id]
            request_metrics.end_time = end_time
            request_metrics.success = True
            
            duration = end_time - request_metrics.start_time
            
            # Update agent stats
            self.agent_stats[agent_name].successful_requests += 1
            self.agent_stats[agent_name].total_duration += duration
            
            # Calculate average duration
            if self.agent_stats[agent_name].successful_requests > 0:
                self.agent_stats[agent_name].avg_duration = (
                    self.agent_stats[agent_name].total_duration / 
                    self.agent_stats[agent_name].successful_requests
                )
            
            # Store in history
            self.request_history.append({
                "agent_name": agent_name,
                "request_id": request_id,
                "duration": duration,
                "retry_count": request_metrics.retry_count,
                "error_count": request_metrics.error_count,
                "item_count": item_count,
                "success": True,
                "timestamp": end_time
            })
            
            # Remove from active requests
            del self.active_requests[request_id]
            
            logger.info(f"✅ [{agent_name}] Completed {request_id} in {duration:.1f}s ({item_count} items)")
        else:
            logger.warning(f"⚠️ [{agent_name}] Success logged for unknown request {request_id}")
    
    def log_timeout(self, agent_name: str, request_id: str, timeout_duration: float):
        """Log a timeout"""
        if request_id in self.active_requests:
            request_metrics = self.active_requests[request_id]
            request_metrics.end_time = time.time()
            request_metrics.success = False
            request_metrics.error_message = f"Timeout after {timeout_duration}s"
            
            duration = request_metrics.end_time - request_metrics.start_time
            
            # Update agent stats
            self.agent_stats[agent_name].failed_requests += 1
            self.agent_stats[agent_name].total_errors += 1
            
            # Store in history
            self.request_history.append({
                "agent_name": agent_name,
                "request_id": request_id,
                "duration": duration,
                "retry_count": request_metrics.retry_count,
                "error_count": request_metrics.error_count,
                "success": False,
                "error": "Timeout",
                "timestamp": request_metrics.end_time
            })
            
            # Remove from active requests
            del self.active_requests[request_id]
            
            logger.error(f"⏰ [{agent_name}] Timeout for {request_id} after {duration:.1f}s")
        else:
            logger.warning(f"⚠️ [{agent_name}] Timeout logged for unknown request {request_id}")
    
    def get_agent_stats(self, agent_name: str) -> AgentStats:
        """Get statistics for a specific agent"""
        return self.agent_stats.get(agent_name, AgentStats())
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall monitoring statistics"""
        elapsed = time.time() - self.start_time
        
        total_requests = sum(stats.total_requests for stats in self.agent_stats.values())
        total_successful = sum(stats.successful_requests for stats in self.agent_stats.values())
        total_failed = sum(stats.failed_requests for stats in self.agent_stats.values())
        total_retries = sum(stats.total_retries for stats in self.agent_stats.values())
        total_errors = sum(stats.total_errors for stats in self.agent_stats.values())
        
        success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        retry_rate = (total_retries / total_requests * 100) if total_requests > 0 else 0
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "elapsed_time": elapsed,
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "failed_requests": total_failed,
            "total_retries": total_retries,
            "total_errors": total_errors,
            "success_rate": success_rate,
            "retry_rate": retry_rate,
            "error_rate": error_rate,
            "requests_per_minute": (total_requests / elapsed * 60) if elapsed > 0 else 0,
            "active_requests": len(self.active_requests),
            "agent_count": len(self.agent_stats)
        }
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed statistics including per-agent breakdown"""
        overall = self.get_overall_stats()
        
        agent_details = {}
        for agent_name, stats in self.agent_stats.items():
            agent_details[agent_name] = {
                "total_requests": stats.total_requests,
                "successful_requests": stats.successful_requests,
                "failed_requests": stats.failed_requests,
                "total_retries": stats.total_retries,
                "total_errors": stats.total_errors,
                "avg_duration": stats.avg_duration,
                "success_rate": (stats.successful_requests / stats.total_requests * 100) if stats.total_requests > 0 else 0,
                "retry_rate": (stats.total_retries / stats.total_requests * 100) if stats.total_requests > 0 else 0,
                "error_rate": (stats.total_errors / stats.total_requests * 100) if stats.total_requests > 0 else 0
            }
        
        return {
            "overall": overall,
            "agents": agent_details,
            "recent_requests": self.request_history[-10:] if self.request_history else []
        }
    
    def print_summary(self):
        """Print a summary of current statistics"""
        stats = self.get_overall_stats()
        
        logger.info("=" * 80)
        logger.info("📊 OPENAI API MONITORING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"⏱️  Elapsed Time: {stats['elapsed_time']:.1f}s")
        logger.info(f"📈 Total Requests: {stats['total_requests']}")
        logger.info(f"✅ Successful: {stats['successful_requests']} ({stats['success_rate']:.1f}%)")
        logger.info(f"❌ Failed: {stats['failed_requests']} ({100-stats['success_rate']:.1f}%)")
        logger.info(f"🔄 Retries: {stats['total_retries']} ({stats['retry_rate']:.1f}%)")
        logger.info(f"⚠️  Errors: {stats['total_errors']} ({stats['error_rate']:.1f}%)")
        logger.info(f"🚀 Requests/min: {stats['requests_per_minute']:.1f}")
        logger.info(f"🔄 Active Requests: {stats['active_requests']}")
        logger.info("=" * 80)
        
        # Per-agent breakdown
        if self.agent_stats:
            logger.info("📋 PER-AGENT BREAKDOWN:")
            for agent_name, agent_stats in self.agent_stats.items():
                success_rate = (agent_stats.successful_requests / agent_stats.total_requests * 100) if agent_stats.total_requests > 0 else 0
                logger.info(f"  {agent_name}: {agent_stats.total_requests} req, {success_rate:.1f}% success, {agent_stats.avg_duration:.1f}s avg")
        
        logger.info("=" * 80)

# Global monitor instance
monitor = OpenAIMonitor()
