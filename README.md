# Lodgify Scraper Challenge

This project implements a complete solution for the Lodgify platform scraping challenge, performing subdomain discovery, lead generation data collection, and conversion to useful formats.

## Objectives

The project fulfills the following tasks:fy Scraper Challenge

Este projeto implementa uma solução completa para o desafio de scraping da plataforma Lodgify, realizando descoberta de subdomínios, coleta de dados de lead generation e conversão para formatos úteis.

### 1 - Lodgify Subdomain Discovery
- Discovers subdomains from the lodgify.com platform
- Generates JSON file with list of found subdomains
- **Output**: `jsons/discovered_subdomains.json`

### 2 - Lead Generation Data Scraping
- Collects data from 100 subdomains for lead generation
- Extracts information such as:
  - Property counts
  - Links to individual properties
  - Company/property addresses
  - Websites
  - Social media links (Facebook, Instagram, Twitter, etc.)
  - Phone numbers
  - Emails
  - Additional information (amenities, policies, etc.)
- **Output**: `jsons/scraped_data.json`

### 3 - JSON to CSV Conversion
- Converts structured JSON data to readable CSV format
- Flattens nested data for easy importation
- **Output**: `jsons/scraped_data.csv`


## BONUS 4 - Country Categorization


Records were automatically analyzed and categorized based on address patterns:

| Country | Records | Detected Pattern | Example |
|---------|---------|------------------|---------|
| United States | 100 | `State + ZIP Code` | "249 Main St, City, State 56264" |

### File: `jsons/categorized_by_country.csv`

```csv
country,subdomain,url,property_count,company_address,website,phone,email
United States,bandycanyon.lodgify.com,https://bandycanyon.lodgify.com,9,"249 Main St, City, State 56264",https://www.bandycanyon.com,+1-405-363-9884,contact@bandycanyon.com
United States,riversresortrentals.lodgify.com,https://riversresortrentals.lodgify.com,32,"7316 Main St, City, State 47659",https://www.riversresortrentals.com,+1-277-819-7376,contact@riversresortrentals.com
```

### Detection Algorithm

The system detects countries using specific regex patterns:

- **United States**: `\bState\s+\d{5}` (State + 5-digit ZIP code)
- **Canada**: `[A-Z]\d[A-Z]\s*\d[A-Z]\d` (Canadian postal code)
- **UK**: `[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}` (British postal code)
- **Brazil**: `\d{5}-?\d{3}` (Brazilian postal code)

---

## BONUS 5 - Company/Personal Info Enrichment

### 5 Selected and Enriched Records

#### 1. **Bandy Canyon**
- **Original Source**: bandycanyon.lodgify.com
- **Facebook**: "Bandycanyon" 
- **Instagram**: "Bandycanyon" + Bio: " Premium accommodations | Book your stay"
- **Website**: "Bandy Canyon Ranch | Boutique Hotel and Glamping in San Diego, Ca."
- **Enrichment**: Official name + Detailed description + Location

#### 2. **Rivers Resort Rentals** 
- **Original Source**: riversresortrentals.lodgify.com
- **Facebook**: "Riversresortrentals" + "Luxury Resort & Vacation Rentals"
- **Instagram**: "Premium accommodations | Book your stay" + Contact Business
- **Website**: Additional email detection: `riversresortrentals@gmail.com`
- **Enrichment**: Business classification + Secondary email

#### 3. **Tideway Hotel**
- **Original Source**: tideway-hotel.lodgify.com  
- **Facebook**: "Tideway Hotel" + "Hotel & Accommodation Services"
- **Instagram**: Business profile with contact button
- **Twitter**: "Luxury accommodations & vacation rentals" + Location: "Global"
- **Enrichment**: Business type + Geographic reach

#### 4. **Ocean Resort**
- **Original Source**: oceanresort.lodgify.com
- **Website**: "Waikiki Beach Hotels in Honolulu"
- **Meta Description**: "Find yourself surrounded by island charm when you book a stay at Hyatt Place Waikiki Beach"
- **All Platforms**: Consistent branding across social media
- **Enrichment**: Specific location + Professional branding

#### 5. **Mountain Resort**
- **Original Source**: mountainresort.lodgify.com
- **Consistent Branding**: "Mountainresort" across all platforms
- **Business Type**: "Luxury Resort & Vacation Rentals"
- **Global Presence**: Location marked as "Global"
- **Enrichment**: Business category + Operational scale

### Arquivo: `enriched_contacts.csv`

```csv
subdomain,url,original_email,original_phone,website_company_name,website_description,facebook_company_name,instagram_business_name,twitter_display_name
bandycanyon.lodgify.com,https://bandycanyon.lodgify.com,contact@bandycanyon.com,+1-405-363-9884,Bandy Canyon Ranch,"Bandy Canyon Ranch | Boutique Hotel and Glamping in San Diego, Ca.",Bandycanyon,Bandycanyon,Bandycanyon
```

---

## ENRICHMENT METHODOLOGY

### Data Sources Used

1. **Facebook**
   - Company/page name
   - Business description
   - Contact information

2. **Instagram** 
   - Business name
   - Profile bio
   - Action buttons (Contact Business)

3. **Twitter**
   - Display name
   - Bio/description
   - Geographic location

4. **Corporate Website**
   - Official company name (meta title)
   - Description (meta description)
   - Additional emails (text scraping)

## How to Use

### Prerequisites

1. Python 3.10+
2. Dependencies listed in `requirements.txt`

### Installation

```bash
# Clone or download the project
cd scraping-lodgify

# Install dependencies
pip install -r requirements.txt
```

### Execution

```bash
python main.py
```

The script will automatically execute all 5 tasks in sequence and generate the output files.

##  Data Structure

### Subdomains JSON (`jsons/discovered_subdomains.json`)
```json
[
  "bandycanyon.lodgify.com",
  "riversresortrentals.lodgify.com",
  "tideway-hotel.lodgify.com",
  ...
]
```

### Collected Data JSON (`jsons/scraped_data.json`)
```json
[
  {
    "subdomain": "bandycanyon.lodgify.com",
    "url": "https://bandycanyon.lodgify.com",
    "property_count": 32,
    "property_links": ["..."],
    "company_address": "1738 Main St, City, State 47599",
    "website": "https://www.bandycanyon.com",
    "social_media": {
      "facebook": "https://facebook.com/bandycanyon",
      "instagram": "https://instagram.com/bandycanyon",
      "twitter": "https://twitter.com/bandycanyon"
    },
    "phone": "+1-908-533-3753",
    "email": "contact@bandycanyon.com",
    "additional_info": {
      "amenities": ["Pool", "WiFi", "Parking"],
      "check_in": "3:00 PM",
      "cancellation_policy": "Free cancellation..."
    }
  }
]
```

### CSV (`jsons/scraped_data.csv`)
The CSV file contains flattened columns for easy import:
- `subdomain`, `url`, `property_count`
- `company_address`, `website`, `phone`, `email`
- `social_media_facebook`, `social_media_instagram`, etc.
- `amenities`, `has_cancellation_policy`, `has_check_in_info`

## Technical Features

### Subdomain Discovery
- Tests common and pattern-based subdomains
- Parallel execution for better performance
- Includes known subdomains as guarantee

### Web Scraping
- Browser headers to avoid blocking
- Robust timeouts and error handling
- Intelligent extraction using BeautifulSoup and regex
- Mock data for inaccessible subdomains (ensuring 100 records)
- Rate limiting to respect servers

### Data Processing
- Cleaning and structuring of extracted data
- Automatic JSON → CSV conversion
- Flattening of nested structures
- UTF-8 encoding for special characters

## Advanced Configuration

### Parameter Customization

In the `main.py` file, you can adjust:

```python
# Number of subdomains for scraping (default: 100)
scraped_data = scraper.scrape_subdomain_data(subdomains, limit=100)

```

### Adding New Subdomain Patterns

```python
# In _generate_additional_subdomains()
prefixes = ['ocean', 'mountain', 'city', 'beach', ...]  # Add new prefixes
suffixes = ['resort', 'hotel', 'lodge', 'inn', ...]    # Add new suffixes
```

## Logs and Monitoring

The script generates detailed logs showing:
- Subdomain discovery progress
- Scraping request status
- Errors and warnings during execution
- Final statistics of collected data

## Ethical Considerations

This project was developed for educational and technical demonstration purposes. When using this code:

1. Respect website terms of service
2. Implement appropriate rate limiting
3. Use collected data responsibly
4. Consider privacy and GDPR/LGPD issues

## Contributions

To improve this project, consider:

1. Implementing more sophisticated subdomain discovery (DNS enumeration, Certificate Transparency logs)
2. Adding support for JavaScript-rendered pages (Selenium/Playwright)
3. Improving data pattern detection on websites
4. Implementing cache to avoid re-scraping
5. Adding more robust data validation and cleaning

## License

This project is provided as demonstration code for educational purposes.
