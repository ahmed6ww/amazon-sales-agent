#!/usr/bin/env python3
"""
Real-world test: Make 10 requests to Amazon with anti-blocking features

This script tests:
1. Anti-blocking features work with real Amazon URLs
2. Success rate across multiple requests
3. Response quality and data extraction
4. Performance and timing

Note: Uses subprocess to avoid Scrapy ReactorNotRestartable error
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Add backend to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


# Test URLs - mix of different product categories (verified active products)
TEST_URLS = [
    "https://www.amazon.com/dp/B0BSHF7WHW",  # MacBook Pro 16" M2
    "https://www.amazon.com/dp/B073TY2GTF",  # Garlic Press (Cuisinart)
    "https://www.amazon.com/dp/B0D1XD1ZV3",  # AirPods Pro 2 (2024)
    "https://www.amazon.com/dp/B09B93ZDG4",  # Echo Dot 5th Gen (Charcoal)
    "https://www.amazon.com/dp/B09SWW583J",  # Kindle Paperwhite 11th Gen
    "https://www.amazon.com/dp/B0CHX7R6WJ",  # Apple Watch SE (2023)
    "https://www.amazon.com/dp/B09G9FPHY6",  # iPad 9th Gen
    "https://www.amazon.com/dp/B08J5F3G18",  # Graphics Card RTX 3090
    "https://www.amazon.com/dp/B07ZPKN6YR",  # iPhone 11 Renewed
    "https://www.amazon.com/dp/B0BP9SNVH9",  # Fire TV Stick 4K Max
]


def scrape_url_subprocess(url):
    """
    Scrape a URL using subprocess to avoid Scrapy ReactorNotRestartable error
    Each request runs in a fresh Python process
    """
    scraper_path = backend_dir / "app" / "services" / "amazon" / "scraper.py"
    
    try:
        # Run scraper in subprocess
        result = subprocess.run(
            [sys.executable, str(scraper_path), url],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd=str(backend_dir)
        )
        
        # Parse JSON output
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': 'Failed to parse JSON output',
                    'stdout': result.stdout[:500]
                }
        else:
            # Extract error from stderr
            error_msg = result.stderr.split('\n')[-100:] if result.stderr else 'Unknown error'
            return {
                'success': False,
                'error': f'Scraper exited with code {result.returncode}',
                'stderr': '\n'.join(error_msg) if isinstance(error_msg, list) else error_msg
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Request timed out after 60 seconds'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Subprocess error: {str(e)}'
        }


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_result_summary(result, index, url):
    """Print a summary of a single scraping result"""
    success = result.get('success', False)
    status_icon = "✅" if success else "❌"
    
    print(f"\n{status_icon} Request #{index + 1}")
    print(f"   URL: {url}")
    
    if success:
        data = result.get('data', {})
        title = data.get('title', 'N/A')
        response_size = data.get('response_size', 0)
        image_count = data.get('images', {}).get('image_count', 0)
        
        # Truncate title if too long
        if len(title) > 70:
            title = title[:67] + "..."
        
        print(f"   ✓ Title: {title}")
        print(f"   ✓ Response Size: {response_size:,} bytes")
        print(f"   ✓ Images Found: {image_count}")
        
        # Check what elements were found
        elements = data.get('elements', {})
        found_elements = [name for name, elem in elements.items() if elem.get('present')]
        print(f"   ✓ Elements Found: {', '.join(found_elements[:5])}")
        
        # Check price
        price = data.get('price', {})
        if price.get('present'):
            print(f"   ✓ Price: {price.get('raw', 'N/A')}")
    else:
        error = result.get('error', 'Unknown error')
        print(f"   ✗ Error: {error}")
        
        # Check if blocked
        blocked_reason = result.get('blocked_reason', '')
        if blocked_reason:
            print(f"   ✗ Blocked: {blocked_reason}")


def main():
    """Run real-world tests with 10 Amazon URLs"""
    print_section("Amazon Scraper - Real-World Test (10 Requests)")
    
    print(f"🕐 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total URLs to test: {len(TEST_URLS)}")
    print(f"🛡️  Anti-blocking features: ENABLED\n")
    
    results = []
    successful = 0
    failed = 0
    total_time = 0
    
    start_time = time.time()
    
    # Process each URL
    for i, url in enumerate(TEST_URLS):
        print(f"\n⏳ Processing request {i + 1}/{len(TEST_URLS)}...")
        
        request_start = time.time()
        
        try:
            # Use subprocess to avoid Scrapy reactor restart issues
            result = scrape_url_subprocess(url)
            results.append({
                'url': url,
                'result': result,
                'time': time.time() - request_start
            })
            
            if result.get('success'):
                successful += 1
            else:
                failed += 1
                
            # Print summary
            print_result_summary(result, i, url)
            
            # Show timing
            request_time = time.time() - request_start
            total_time += request_time
            print(f"   ⏱️  Request Time: {request_time:.2f}s")
            
        except Exception as e:
            failed += 1
            print(f"\n❌ Request #{i + 1} - Exception occurred")
            print(f"   URL: {url}")
            print(f"   Error: {str(e)}")
            results.append({
                'url': url,
                'result': {'success': False, 'error': str(e)},
                'time': time.time() - request_start
            })
        
        # Add delay between requests to be polite
        if i < len(TEST_URLS) - 1:
            delay = 2
            print(f"   ⏸️  Waiting {delay}s before next request...")
            time.sleep(delay)
    
    end_time = time.time()
    total_elapsed = end_time - start_time
    
    # Print final summary
    print_section("Final Results Summary")
    
    success_rate = (successful / len(TEST_URLS)) * 100
    
    print(f"📈 Success Rate: {successful}/{len(TEST_URLS)} ({success_rate:.1f}%)")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Time: {total_elapsed:.2f}s")
    print(f"⏱️  Average Time per Request: {total_time/len(TEST_URLS):.2f}s")
    
    # Analyze failures if any
    if failed > 0:
        print(f"\n❌ Failed Requests:")
        for i, item in enumerate(results):
            if not item['result'].get('success'):
                print(f"   {i + 1}. {item['url']}")
                print(f"      Error: {item['result'].get('error', 'Unknown')}")
    
    # Extract successful data stats
    if successful > 0:
        print(f"\n✅ Successful Extractions:")
        total_images = 0
        total_elements = 0
        prices_found = 0
        
        for item in results:
            if item['result'].get('success'):
                data = item['result'].get('data', {})
                total_images += data.get('images', {}).get('image_count', 0)
                elements = data.get('elements', {})
                total_elements += sum(1 for elem in elements.values() if elem.get('present'))
                if data.get('price', {}).get('present'):
                    prices_found += 1
        
        avg_images = total_images / successful if successful > 0 else 0
        avg_elements = total_elements / successful if successful > 0 else 0
        
        print(f"   📸 Average Images per Product: {avg_images:.1f}")
        print(f"   📄 Average Elements per Product: {avg_elements:.1f}")
        print(f"   💰 Prices Found: {prices_found}/{successful}")
    
    # Save detailed results to JSON
    output_file = backend_dir / "test_real_requests_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(TEST_URLS),
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'total_time': total_elapsed,
                'avg_time_per_request': total_time / len(TEST_URLS)
            },
            'results': results
        }, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Final verdict
    print_section("Test Verdict")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT! Anti-blocking is working very well.")
        print("   Success rate is above 80% - safe to push to production!")
    elif success_rate >= 60:
        print("✅ GOOD! Anti-blocking is working reasonably well.")
        print("   Success rate is above 60% - acceptable for production.")
    elif success_rate >= 40:
        print("⚠️  MODERATE. Anti-blocking needs improvement.")
        print("   Consider adding proxies or ScraperAPI for better results.")
    else:
        print("❌ POOR. Anti-blocking is not working well enough.")
        print("   Recommend using proxies or ScraperAPI before production.")
    
    print(f"\n🕐 End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n{'='*80}\n")
    
    # Return exit code based on success rate
    sys.exit(0 if success_rate >= 60 else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
