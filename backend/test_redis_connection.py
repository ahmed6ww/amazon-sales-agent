"""
Quick test script to verify Redis (Upstash) connection
Run: python test_redis_connection.py
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_redis_connection():
    """Test Redis connection and basic operations."""
    print("="*60)
    print("🔴 REDIS CONNECTION TEST")
    print("="*60)
    
    # Check environment variables
    redis_url = os.getenv("UPSTASH_REDIS_URL")
    redis_token = os.getenv("UPSTASH_REDIS_TOKEN")
    
    print(f"\n📋 Configuration:")
    print(f"   UPSTASH_REDIS_URL: {redis_url[:30]}..." if redis_url else "   ❌ UPSTASH_REDIS_URL not set")
    print(f"   UPSTASH_REDIS_TOKEN: {'✅ Set' if redis_token else '❌ Not set'}")
    
    if not redis_url or not redis_token:
        print("\n❌ ERROR: Redis credentials not configured")
        print("\n📝 To fix:")
        print("   1. Create .env file in backend/ directory")
        print("   2. Add these lines:")
        print("      UPSTASH_REDIS_URL=https://your-redis-url.upstash.io")
        print("      UPSTASH_REDIS_TOKEN=your_token_here")
        print("\n   Get credentials from: https://console.upstash.com/")
        print("   See REDIS_SETUP.md for detailed instructions")
        return False
    
    # Test connection
    try:
        from upstash_redis import Redis
        
        print(f"\n🔌 Connecting to Redis...")
        redis_client = Redis(url=redis_url, token=redis_token)
        
        # Test ping
        print(f"   Testing connection (ping)...")
        result = redis_client.ping()
        print(f"   ✅ Ping successful: {result}")
        
        # Test write
        print(f"\n💾 Testing write operation...")
        test_key = "test:connection"
        test_value = {"status": "success", "timestamp": "2025-10-23"}
        redis_client.set(test_key, str(test_value))
        print(f"   ✅ Write successful")
        
        # Test read
        print(f"\n📖 Testing read operation...")
        read_value = redis_client.get(test_key)
        print(f"   ✅ Read successful: {read_value}")
        
        # Test TTL
        print(f"\n⏱️  Testing TTL (expire)...")
        redis_client.expire(test_key, 60)  # Expire in 60 seconds
        ttl = redis_client.ttl(test_key)
        print(f"   ✅ TTL set: {ttl} seconds")
        
        # Cleanup
        print(f"\n🗑️  Cleaning up test data...")
        redis_client.delete(test_key)
        print(f"   ✅ Cleanup successful")
        
        print(f"\n" + "="*60)
        print(f"✅ ALL TESTS PASSED - Redis is working correctly!")
        print(f"="*60)
        print(f"\n📌 Next steps:")
        print(f"   1. Start your backend server: uv run dev")
        print(f"   2. Look for this log message:")
        print(f"      🔴 [JOB MANAGER] Redis (Upstash) initialized successfully")
        print(f"   3. Submit an analysis and check it completes with results")
        
        return True
        
    except ImportError:
        print(f"\n❌ ERROR: upstash-redis package not installed")
        print(f"\n📝 To fix:")
        print(f"   cd backend")
        print(f"   uv sync")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print(f"\n📝 Common issues:")
        print(f"   1. Wrong URL/Token - check Upstash console")
        print(f"   2. Database paused - check Upstash dashboard")
        print(f"   3. Network issues - check firewall/proxy")
        return False

if __name__ == "__main__":
    test_redis_connection()

