from subdomain_fetch import discover_subdomains
from scraper import scrape_subdomain_data
from json_to_csv import convert_json_to_csv
from bonus_4 import categorize_by_country
from bonus_5 import enrich_contact_info

if __name__ == "__main__":
    
    # Task 1: Discover subdomains
    print("\n Task 1: Discovering Lodgify subdomains...")
    subdomains = discover_subdomains()

    # Task 2: Scrape data
    print("\n Task 2: Scraping lead generation data...")
    scraped_data = scrape_subdomain_data(subdomains, limit=100)

    # Task 3: Convert to CSV
    print("\n Task 3: Converting JSON to CSV...")
    convert_json_to_csv()
    
    # BONUS 4: Categorize by country
    print("\n BONUS 4: Categorizing records by country...")
    categorize_by_country()

    # BONUS 5: Enrich contact data
    print("\n BONUS 5: Enriching contact information (5 records)...")
    enrich_contact_info(limit=5)

    # Show some examples of the collected data
    if scraped_data:
        print(f"\n Example:")
        example = scraped_data[0]
        for key, value in example.items():
            if isinstance(value, (list, dict)):
                print(f"  {key}: {str(value)[:100]}...")
            else:
                print(f"  {key}: {value}")
