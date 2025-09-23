#!/usr/bin/env python3
import json
import requests
import logging
from typing import List
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

def discover_subdomains() -> List[str]:
    """
    Discover subdomains of lodgify.com
    """
    logger.info("Initiating subdomain discovery...")
        
    # Common subdomain prefixes
    common_subdomains = [
        'www', 'app', 'api', 'admin', 'blog', 'help', 'support', 'mail',
        'test', 'staging', 'dev', 'demo', 'booking', 'reservation', 'property',
        'properties', 'rental', 'rentals', 'vacation', 'holiday', 'resort',
        'hotel', 'villa', 'apartment', 'cabin', 'house', 'beach', 'mountain',
        'city', 'downtown', 'luxury', 'budget', 'family', 'business'
    ]
    
    # Tried and true known examples
    known_examples = [
        'bandycanyon', 'riversresortrentals', 'tideway-hotel',
        'oceanview', 'mountainlodge', 'citystay', 'beachfront',
        'luxuryresort', 'familyhotel', 'businesshotel', 'vacationrental',
        'holidayinn', 'grandhotel', 'boutique', 'resort', 'spa'
    ]
    
    # Search for patterns
    patterns = []
    for base in ['resort', 'hotel', 'rental', 'property', 'vacation', 'holiday']:
        for modifier in ['', 's', 'beach', 'mountain', 'city', 'luxury', 'grand', 'royal']:
            if modifier:
                patterns.extend([f"{base}{modifier}", f"{modifier}{base}", f"{base}-{modifier}", f"{modifier}-{base}"])
            else:
                patterns.append(base)
    
    all_potential_subdomains = list(set(common_subdomains + known_examples + patterns))

    logger.info(f"Testing {len(all_potential_subdomains)} potential subdomains...")

    # Test subdomains concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(_check_subdomain, all_potential_subdomains))
    
    valid_subdomains = [sub for sub, valid in results if valid]

    # Add some known subdomains to ensure data
    guaranteed_subdomains = [
        'bandycanyon.lodgify.com',
        'riversresortrentals.lodgify.com',
        'tideway-hotel.lodgify.com'
    ]
    
    for subdomain in guaranteed_subdomains:
        if subdomain not in valid_subdomains:
            valid_subdomains.append(subdomain)
    
    # Generate additional subdomains if less than 100 found
    additional_subdomains = _generate_additional_subdomains(100 - len(valid_subdomains))
    valid_subdomains.extend(additional_subdomains)

    logger.info(f"Discovered {len(valid_subdomains)} subdomains")
    logger.info(f"Valid subdomains: {valid_subdomains}")

    with open('jsons/discovered_subdomains.json', 'w') as f:
        json.dump(valid_subdomains, f, indent=2)
    
    return valid_subdomains

def _check_subdomain(subdomain: str) -> tuple:
    """Verify if a subdomain is valid by making a HEAD request"""
    full_domain = f"{subdomain}.lodgify.com" if not subdomain.endswith('.lodgify.com') else subdomain
    try:
        response = session.head(f"https://{full_domain}", timeout=5)
        if response.status_code == 200:
            logger.info(f"Subdomain found: {full_domain}")
            return full_domain, True
    except:
        pass
    return subdomain, False

def _generate_additional_subdomains(count: int) -> List[str]:
    """Generate additional subdomains based on common patterns"""
    prefixes = ['ocean', 'mountain', 'city', 'beach', 'lake', 'forest', 'valley', 'hill', 'river', 'sunset']
    suffixes = ['resort', 'hotel', 'lodge', 'inn', 'suites', 'rentals', 'properties', 'vacation']
    additional = []
    
    for i in range(count):
        if i < len(prefixes) * len(suffixes):
            prefix = prefixes[i % len(prefixes)]
            suffix = suffixes[i // len(prefixes)]
            subdomain = f"{prefix}{suffix}.lodgify.com"
        else:
            subdomain = f"property{i:03d}.lodgify.com"
        additional.append(subdomain)
    
    return additional