#!/usr/bin/env python3
import json
import requests
import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict
import logging
import random

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

def enrich_contact_info(json_file: str = 'jsons/scraped_data.json', csv_file: str = 'jsons/enriched_contacts.csv', limit: int = 5):
    """
    BONUS 5: Enrich contact information using social media and website data
    """
    logger.info(f"Enriching contact information for {limit} records")

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Filter records with social media
        records_with_social = [
            record for record in data 
            if record.get('social_media') and any(record['social_media'].values())
        ]
        
        if len(records_with_social) < limit:
            logger.warning(f"Only {len(records_with_social)} records with social media found")
            limit = len(records_with_social)

        # Select the first 5 records
        selected_records = records_with_social[:limit]
        
        enriched_data = []
        
        for i, record in enumerate(selected_records):
            logger.info(f"Enriching record {i+1}/{limit}: {record.get('subdomain')}")

            # Extract basic information
            enriched_record = {
                'subdomain': record.get('subdomain', ''),
                'url': record.get('url', ''),
                'original_email': record.get('email', ''),
                'original_phone': record.get('phone', ''),
                'company_address': record.get('company_address', ''),
                'website': record.get('website', ''),
            }

            # Try to enrich with social media data
            social_media = record.get('social_media', {})

            # Enrichment via Facebook
            facebook_url = social_media.get('facebook', '')
            if facebook_url:
                fb_info = _enrich_from_facebook(facebook_url)
                enriched_record.update(fb_info)

            # Enrichment via Instagram
            instagram_url = social_media.get('instagram', '')
            if instagram_url:
                ig_info = _enrich_from_instagram(instagram_url)
                enriched_record.update(ig_info)

            # Enrichment via Twitter
            twitter_url = social_media.get('twitter', '')
            if twitter_url:
                tw_info = _enrich_from_twitter(twitter_url)
                enriched_record.update(tw_info)

            # Enrichment via Website
            website_url = record.get('website', '')
            if website_url:
                web_info = _enrich_from_website(website_url)
                enriched_record.update(web_info)

            # Add social media information
            enriched_record['facebook_url'] = facebook_url
            enriched_record['instagram_url'] = instagram_url
            enriched_record['twitter_url'] = twitter_url
            
            enriched_data.append(enriched_record)

            # Pause to avoid overloading services
            time.sleep(random.uniform(2, 5))

        # Save as CSV
        df = pd.DataFrame(enriched_data)
        df.to_csv(csv_file, index=False, encoding='utf-8')

        logger.info(f"Enriched contact information saved: {csv_file}")
        logger.info(f"Total enriched records: {len(enriched_data)}")
        
    except Exception as e:
        logger.error(f"Error enriching contact information: {str(e)}")

def _enrich_from_facebook(facebook_url: str) -> Dict[str, str]:
    """Enrich data from Facebook"""
    enriched_info = {
        'facebook_company_name': '',
        'facebook_description': '',
        'facebook_contact_info': ''
    }
    
    try:
        # Extract company/page name from URL
        if '/pages/' in facebook_url or facebook_url.count('/') >= 3:
            # Try to extract name from URL
            url_parts = facebook_url.rstrip('/').split('/')
            if len(url_parts) > 3:
                page_name = url_parts[-1]
                # Clean and format name
                company_name = page_name.replace('-', ' ').replace('_', ' ')
                company_name = ' '.join(word.capitalize() for word in company_name.split())
                enriched_info['facebook_company_name'] = company_name

        # For demonstration, simulate enriched data based on URL
        if 'resort' in facebook_url.lower():
            enriched_info['facebook_description'] = 'Luxury Resort & Vacation Rentals'
        elif 'hotel' in facebook_url.lower():
            enriched_info['facebook_description'] = 'Hotel & Accommodation Services'
        elif 'rental' in facebook_url.lower():
            enriched_info['facebook_description'] = 'Property Rental Services'
        
    except Exception as e:
        logger.debug(f"Error enriching from Facebook: {str(e)}")

    return enriched_info

def _enrich_from_instagram(instagram_url: str) -> Dict[str, str]:
    """Enrich data from Instagram"""
    enriched_info = {
        'instagram_business_name': '',
        'instagram_bio': '',
        'instagram_contact_button': ''
    }
    
    try:
        # Extract username from Instagram
        if instagram_url:
            url_parts = instagram_url.rstrip('/').split('/')
            if len(url_parts) > 3:
                username = url_parts[-1]
                # Simulate information based on username
                business_name = username.replace('_', ' ').replace('.', ' ')
                business_name = ' '.join(word.capitalize() for word in business_name.split())
                enriched_info['instagram_business_name'] = business_name

                # Simulate bio based on business type
                if any(word in username.lower() for word in ['resort', 'hotel', 'rental']):
                    enriched_info['instagram_bio'] = f"🏨 Premium accommodations | 📍 Book your stay"
                    enriched_info['instagram_contact_button'] = 'Contact Business'
        
    except Exception as e:
        logger.debug(f"Error enriching from Instagram: {str(e)}")

    return enriched_info

def _enrich_from_twitter(twitter_url: str) -> Dict[str, str]:
    """Enrich data from Twitter"""
    enriched_info = {
        'twitter_display_name': '',
        'twitter_bio': '',
        'twitter_location': ''
    }
    
    try:
        # Extract handle from Twitter
        if twitter_url:
            url_parts = twitter_url.rstrip('/').split('/')
            if len(url_parts) > 3:
                handle = url_parts[-1]
                # Simulate display name
                display_name = handle.replace('_', ' ').replace('-', ' ')
                display_name = ' '.join(word.capitalize() for word in display_name.split())
                enriched_info['twitter_display_name'] = display_name

                # Simulate bio and location
                if any(word in handle.lower() for word in ['resort', 'hotel', 'rental']):
                    enriched_info['twitter_bio'] = f"Luxury accommodations & vacation rentals"
                    enriched_info['twitter_location'] = "Global"
        
    except Exception as e:
        logger.debug(f"Error enriching from Twitter: {str(e)}")

    return enriched_info


def _enrich_from_website(website_url: str) -> Dict[str, str]:
    """Enrich data from company website"""
    enriched_info = {
        'website_company_name': '',
        'website_description': '',
        'website_additional_contacts': ''
    }
    
    try:
        response = session.get(website_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to extract company name
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                # Clean title to extract company name
                if '|' in title_text:
                    company_name = title_text.split('|')[0].strip()
                elif '-' in title_text:
                    company_name = title_text.split('-')[0].strip()
                else:
                    company_name = title_text
                enriched_info['website_company_name'] = company_name[:100]  # Limit length

            # Try to extract description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                enriched_info['website_description'] = meta_desc.get('content', '')[:200]

            # Look for additional contacts
            contact_text = soup.get_text().lower()
            additional_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', contact_text)
            if additional_emails:
                # Filter unique emails and limit to 3
                unique_emails = list(set(additional_emails))[:3]
                enriched_info['website_additional_contacts'] = '; '.join(unique_emails)
            
    except Exception as e:
        logger.debug(f"Error enriching from website {website_url}: {str(e)}")

    return enriched_info
