import sys
from app.services.amazon.scrapper import scrape_url, display_results


def main():
    """Main function to handle user input and scraping."""

    while True:
        try:
            url = input("\nEnter a URL to scrape (or 'quit' to exit): ").strip()

            if url.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            result = scrape_url(url)

            if "error" in result:
                print(f"Scraping failed: {result['error']}")
            else:

                display_results(result)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An unexpected error occurred in main loop: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_url = "https://www.amazon.com/dp/B08KT2Z93D"
        print(f"🧪 Running test on: {test_url}")
        test_result = scrape_url(test_url)
        display_results(test_result)
    else:
        main()
