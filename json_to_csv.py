#!/usr/bin/env python3
import json
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
        
    
def convert_json_to_csv(json_file: str = 'jsons/scraped_data.json', csv_file: str = 'jsons/scraped_data.csv'):
    """
    Task 3: Convert JSON data to CSV
    """
    logger.info(f"Converting {json_file} to {csv_file}")

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if not data:
            logger.warning("No data found in JSON file.")
            return
        
        flattened_data = []
        
        for record in data:
            flattened_record = {
                'subdomain': record.get('subdomain', ''),
                'url': record.get('url', ''),
                'property_count': record.get('property_count', 0),
                'property_links_count': len(record.get('property_links', [])),
                'property_links': '; '.join(record.get('property_links', [])),
                'company_address': record.get('company_address', ''),
                'website': record.get('website', ''),
                'phone': record.get('phone', ''),
                'email': record.get('email', ''),
            }
            
            # Flatten social media links
            social_media = record.get('social_media', {})
            for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube']:
                flattened_record[f'social_media_{platform}'] = social_media.get(platform, '')

            # Flatten additional information
            additional_info = record.get('additional_info', {})
            flattened_record['amenities'] = '; '.join(additional_info.get('amenities', []))
            flattened_record['has_cancellation_policy'] = 'cancellation_policy' in additional_info
            flattened_record['has_check_in_info'] = additional_info.get('check_in_available', False)
            
            flattened_data.append(flattened_record)

        # Save as CSV
        df = pd.DataFrame(flattened_data)
        df.to_csv(csv_file, index=False, encoding='utf-8')

        logger.info(f"CSV created successfully: {csv_file}")
        logger.info(f"Total records: {len(flattened_data)}")
        
    except Exception as e:
        logger.error(f"Error converting JSON to CSV: {str(e)}")
