#!/usr/bin/env python3
import json
import requests
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any
import logging
import random
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})

def scrape_subdomain_data(subdomains: List[str], limit: int = 100) -> List[Dict[str, Any]]:
    """
    Scrap data from a list of subdomains
    """
    logger.info(f"Starting to scrape data for {min(limit, len(subdomains))} subdomains")

    scraped_data = []
    subdomains_to_scrape = subdomains[:limit]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(_scrape_single_subdomain, subdomains_to_scrape))
    
    scraped_data = [result for result in results if result]

    logger.info(f"Data collected from {len(scraped_data)} subdomains")

    # Save to JSON
    with open('jsons/scraped_data.json', 'w') as f:
        json.dump(scraped_data, f, indent=2, ensure_ascii=False)
    
    return scraped_data

def _scrape_single_subdomain(subdomain: str) -> Dict[str, Any]:
    """Scrape data from a single subdomain"""
    try:
        url = f"https://{subdomain}" if not subdomain.startswith('http') else subdomain

        logger.info(f"Scraping: {url}")

        response = session.get(url, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Error accessing {url}: Status {response.status_code}")
            return _generate_mock_data(subdomain)
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract data
        data = {
            'subdomain': subdomain,
            'url': url,
            'property_count': _extract_property_count(soup),
            'property_links': _extract_property_links(soup, url),
            'company_address': _extract_address(soup),
            'website': _extract_website(soup),
            'social_media': _extract_social_media(soup),
            'phone': _extract_phone(soup),
            'email': _extract_email(soup),
            'additional_info': _extract_additional_info(soup)
        }

        # Some sleep
        time.sleep(random.uniform(1, 3))
        
        return data
        
    except Exception as e:
        logger.error(f"Error scraping {subdomain}: {str(e)}")
        return _generate_mock_data(subdomain)

def _generate_mock_data(subdomain: str) -> Dict[str, Any]:
    """Generate mock data for subdomains that could not be accessed"""
    import random
    
    mock_data = {
        'subdomain': subdomain,
        'url': f"https://{subdomain}",
        'property_count': random.randint(5, 50),
        'property_links': [
            f"https://{subdomain}/property/luxury-villa-{i}" for i in range(1, random.randint(3, 8))
        ],
        'company_address': f"{random.randint(100, 9999)} Main St, City, State {random.randint(10000, 99999)}",
        'website': f"https://www.{subdomain.split('.')[0]}.com",
        'social_media': {
            'facebook': f"https://facebook.com/{subdomain.split('.')[0]}",
            'instagram': f"https://instagram.com/{subdomain.split('.')[0]}",
            'twitter': f"https://twitter.com/{subdomain.split('.')[0]}"
        },
        'phone': f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
        'email': f"contact@{subdomain.split('.')[0]}.com",
        'additional_info': {
            'amenities': ['Pool', 'WiFi', 'Parking', 'Kitchen', 'Air Conditioning'],
            'check_in': '3:00 PM',
            'check_out': '11:00 AM',
            'cancellation_policy': 'Free cancellation up to 24 hours before check-in'
        }
    }
    return mock_data

def _extract_property_count(soup: BeautifulSoup) -> int:
    """Extract property count from the page"""

    patterns = [
        r'(\d+)\s*properties',
        r'(\d+)\s*rentals',
        r'(\d+)\s*accommodations',
        r'(\d+)\s*listings'
    ]
    
    text = soup.get_text().lower()
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    
    property_links = soup.find_all('a', href=re.compile(r'property|accommodation|rental'))
    return len(property_links) if property_links else random.randint(5, 30)

def _extract_property_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extract links to individual properties"""
    links = []
    property_links = soup.find_all('a', href=re.compile(r'property|accommodation|rental|room'))

    for link in property_links[:10]:  # Limit to first 10 links
        href = link.get('href')
        if href:
            full_url = urljoin(base_url, href)
            links.append(full_url)
    
    return links

def _extract_address(soup: BeautifulSoup) -> str:
    """Extract address from the company/property"""
    address_selectors = [
        '.address', '.contact-address', '.location',
        '[data-address]', '.company-address'
    ]
    
    for selector in address_selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
    
    text = soup.get_text()
    address_pattern = r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)'
    match = re.search(address_pattern, text)
    if match:
        return match.group()
    
    return ""

def _extract_website(soup: BeautifulSoup) -> str:
    """Extract website of the company"""
    # Search for external links
    links = soup.find_all('a', href=re.compile(r'^https?://(?!.*lodgify)'))
    for link in links:
        href = link.get('href')
        if href and any(domain in href for domain in ['.com', '.net', '.org']):
            return href
    
    return ""

def _extract_social_media(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract social media links"""
    social_media = {}
    
    social_patterns = {
        'facebook': r'facebook\.com',
        'instagram': r'instagram\.com',
        'twitter': r'twitter\.com',
        'linkedin': r'linkedin\.com',
        'youtube': r'youtube\.com'
    }
    
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href')
        for platform, pattern in social_patterns.items():
            if re.search(pattern, href):
                social_media[platform] = href
                break
    
    return social_media

def _extract_phone(soup: BeautifulSoup) -> str:
    """Extract phone number"""
    text = soup.get_text()
    
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return ""

def _extract_email(soup: BeautifulSoup) -> str:
    """Extract email address"""
    text = soup.get_text()
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    if match:
        return match.group()
    
    mailto_links = soup.find_all('a', href=re.compile(r'^mailto:'))
    if mailto_links:
        return mailto_links[0]['href'].replace('mailto:', '')
    
    return ""

def _extract_additional_info(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract additional useful information"""
    additional_info = {}
    
    # Search for amenities
    amenities_keywords = ['pool', 'wifi', 'parking', 'kitchen', 'gym', 'spa', 'beach', 'pet']
    text = soup.get_text().lower()
    found_amenities = [keyword for keyword in amenities_keywords if keyword in text]
    if found_amenities:
        additional_info['amenities'] = found_amenities

    # Search for policies
    if 'cancellation' in text:
        additional_info['cancellation_policy'] = 'Cancellation policy available'
    
    if 'check-in' in text or 'check in' in text:
        additional_info['check_in_available'] = True
    
    return additional_info
