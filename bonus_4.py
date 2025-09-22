#!/usr/bin/env python3
import json
import re
import pandas as pd
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
        

def categorize_by_country(json_file: str = 'jsons/scraped_data.json', csv_file: str = 'jsons/categorized_by_country.csv'):
    """
    BONUS 4: Categorize records by country based on address patterns
    """
    logger.info(f"Starting to categorize records by country from {json_file}")

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if not data:
            logger.warning("No data found in JSON file")
            return

        # Map common countries based on address patterns
        country_patterns = {
            'United States': [r'USA', r'US\b', r'United States', r'\bState\s+\d{5}', r'[A-Z]{2}\s+\d{5}'],
            'Canada': [r'Canada', r'CA\b', r'[A-Z]\d[A-Z]\s*\d[A-Z]\d'],
            'United Kingdom': [r'UK\b', r'United Kingdom', r'England', r'Scotland', r'Wales', r'[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}'],
            'Australia': [r'Australia', r'AU\b', r'NSW', r'VIC', r'QLD', r'SA', r'WA', r'TAS', r'NT', r'ACT'],
            'Germany': [r'Germany', r'DE\b', r'Deutschland', r'\d{5}\s+[A-Za-z]'],
            'France': [r'France', r'FR\b', r'\d{5}\s+[A-Za-z]'],
            'Spain': [r'Spain', r'ES\b', r'España', r'\d{5}\s+[A-Za-z]'],
            'Italy': [r'Italy', r'IT\b', r'Italia', r'\d{5}\s+[A-Za-z]'],
            'Netherlands': [r'Netherlands', r'NL\b', r'Holland', r'\d{4}\s*[A-Z]{2}'],
            'Brazil': [r'Brazil', r'BR\b', r'Brasil', r'\d{5}-?\d{3}'],
            'Mexico': [r'Mexico', r'MX\b', r'México', r'C\.P\.\s*\d{5}']
        }
        
        categorized_data = []
        
        for record in data:
            address = record.get('company_address', '').strip()
            country = _detect_country(address, country_patterns)

            # Create categorized record
            categorized_record = {
                'country': country,
                'subdomain': record.get('subdomain', ''),
                'url': record.get('url', ''),
                'property_count': record.get('property_count', 0),
                'company_address': address,
                'website': record.get('website', ''),
                'phone': record.get('phone', ''),
                'email': record.get('email', ''),
                'property_links_count': len(record.get('property_links', [])),
            }

            # Add social media
            social_media = record.get('social_media', {})
            categorized_record['social_media_facebook'] = social_media.get('facebook', '')
            categorized_record['social_media_instagram'] = social_media.get('instagram', '')
            categorized_record['social_media_twitter'] = social_media.get('twitter', '')
            
            categorized_data.append(categorized_record)

        # Order by country
        categorized_data.sort(key=lambda x: x['country'])

        # Save as CSV
        df = pd.DataFrame(categorized_data)
        df.to_csv(csv_file, index=False, encoding='utf-8')

        # Statistics by country
        country_counts = df['country'].value_counts()
        logger.info(f"Categorization by country completed:")
        for country, count in country_counts.items():
            logger.info(f"  {country}: {count} records")

        logger.info(f"CSV categorized saved: {csv_file}")

    except Exception as e:
        logger.error(f"Error categorizing by country: {str(e)}")

def _detect_country(address: str, country_patterns: Dict[str, List[str]]) -> str:
    """Detect country based on address"""
    if not address:
        return 'Unknown'
    
    address_upper = address.upper()
    
    for country, patterns in country_patterns.items():
        for pattern in patterns:
            if re.search(pattern.upper(), address_upper):
                return country
    
    return 'Unknown'
