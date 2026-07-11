#!/usr/bin/env python3
"""
SPARKSPHEAR TECH - Main App with LOGGING
- All actions are logged
- Logs shown in UI
- Logs saved to file
- Debug, fix, and enhance based on logs
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading
import urllib.parse
import urllib.request
import json
import os
import re
import logging
import traceback

try:
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# ===== LOGGING SETUP =====
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"sparkphear_{datetime.now().strftime('%Y%m%d')}.log")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SPARKSPHEAR')

logger.info("=" * 60)
logger.info("SPARKSPHEAR TECH APP STARTED")
logger.info("=" * 60)

# ===== CONSTANTS =====
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

PARTS_MARKUP = 0.25
SOURCING_FEE = 15.00
HOURLY_LABOR = 25.00
BASE_TRIP_FEE = 35.00
BASE_MILES = 15
PER_MILE_RATE = 0.67
DIAGNOSIS_FEE = 25.00
MIN_LABOR_HOURS = 1.0
BASE_PATH = r"G:\My Drive\SPARKSPHEAR_Core\04_Clients\Clients\SPARKSPHEAR TECH SUPPORT"
BASE_ADDRESS = "1427 Park Ave, Fort Wayne, IN 46807"

class CostMatrix:
    """Reads and parses the cost_matrix.txt file for pricing data"""
    
    def __init__(self, matrix_path=None):
        if matrix_path is None:
            matrix_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cost_matrix.txt")
        self.matrix_path = matrix_path
        self.data = {}
        self.load()
    
    def load(self):
        """Load and parse the cost matrix file"""
        if not os.path.exists(self.matrix_path):
            logger.warning(f"Cost matrix not found: {self.matrix_path}")
            return
        
        current_section = None
        try:
            with open(self.matrix_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # New section
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        self.data[current_section] = {}
                        continue
                    # Key = Value
                    if '=' in line and current_section:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        self.data[current_section][key] = value
            
            logger.info(f"Cost matrix loaded: {len(self.data)} sections from {self.matrix_path}")
        except Exception as e:
            logger.error(f"Failed to load cost matrix: {e}")
    
    def get(self, section, key, default=None):
        """Get a value from the cost matrix"""
        try:
            value = self.data.get(section, {}).get(key, default)
            if value is None:
                return default
            # Try to convert to float
            try:
                return float(value)
            except (ValueError, TypeError):
                return value
        except Exception:
            return default
    
    def get_part_price(self, device_type, part_name):
        """Get base price for a specific device part"""
        key = f"{device_type}:{part_name}"
        price = self.get('DEVICE_PARTS', key)
        return price if price else None
    
    def get_replacement_options(self, device_type):
        """Get replacement options for a device type"""
        options = []
        for tier in ['Budget', 'Mid-Range', 'High-End', 'Premium']:
            key = f"{device_type}:{tier}"
            price_range = self.get('REPLACEMENT_DEVICES', key)
            if price_range:
                options.append({
                    'name': f"{tier} Option",
                    'price': price_range,
                    'specs': f"{device_type} replacement"
                })
        return options

# Load cost matrix
cost_matrix = CostMatrix()
HOURLY_LABOR = cost_matrix.get('SERVICES', 'HOURLY_LABOR', 25.00)
BASE_TRIP_FEE = cost_matrix.get('SERVICES', 'TRIP_FEE_BASE', 35.00)
BASE_MILES = int(cost_matrix.get('SERVICES', 'TRIP_FEE_INCLUDED_MILES', 15))
PER_MILE_RATE = cost_matrix.get('SERVICES', 'TRIP_FEE_PER_MILE', 0.67)
DIAGNOSIS_FEE = cost_matrix.get('SERVICES', 'DIAGNOSIS_FEE', 25.00)
MIN_LABOR_HOURS = cost_matrix.get('SERVICES', 'MIN_LABOR_HOURS', 1.0)
PARTS_MARKUP = cost_matrix.get('PARTS', 'PARTS_MARKUP', 0.25)
SOURCING_FEE = cost_matrix.get('PARTS', 'SOURCING_FEE', 15.00)
MIN_PARTS_PRICE = cost_matrix.get('PARTS', 'MIN_PARTS_PRICE', 10.00)

logger.info(f"Loaded pricing: Labor=${HOURLY_LABOR}/hr, Trip=${BASE_TRIP_FEE}, Markup={PARTS_MARKUP*100:.0f}%, Fee=${SOURCING_FEE}")

class GeoCoder:
    """Free geocoding using OpenStreetMap Nominatim"""
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    HEADERS = {'User-Agent': 'SPARKSPHEARTech/1.0 (sparksphear4me@gmail.com)'}
    
    @staticmethod
    def geocode(address):
        try:
            params = {'q': address, 'format': 'json', 'limit': 1}
            url = f"{GeoCoder.BASE_URL}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=GeoCoder.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            if data and len(data) > 0:
                return (float(data[0]['lat']), float(data[0]['lon']))
            return None
        except Exception as e:
            logger.debug(f"Geocoding error: {e}")
            return None

class RouteCalculator:
    """Free route calculation using OSRM"""
    BASE_URL = "https://router.project-osrm.org/route/v1/driving"
    
    @staticmethod
    def get_driving_distance(lat1, lon1, lat2, lon2):
        try:
            coords = f"{lon1},{lat1};{lon2},{lat2}"
            url = f"{RouteCalculator.BASE_URL}/{coords}?overview=false&alternatives=false"
            req = urllib.request.Request(url, headers={'User-Agent': 'SPARKSPHEARTech/1.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
            if data and data.get('code') == 'Ok':
                routes = data.get('routes', [])
                if routes:
                    distance_meters = routes[0]['distance']
                    return distance_meters * 0.000621371
            return None
        except Exception as e:
            logger.debug(f"Routing error: {e}")
            return None

def calculate_trip_fee(round_trip_miles):
    """Calculate trip fee based on distance"""
    if round_trip_miles <= BASE_MILES:
        return BASE_TRIP_FEE
    else:
        extra_miles = round_trip_miles - BASE_MILES
        return BASE_TRIP_FEE + (extra_miles * PER_MILE_RATE)

class PartsScraper:
    def __init__(self, client_folder):
        self.client_folder = client_folder
        self.parts_folder = os.path.join(client_folder, "03_Parts_Research")
        os.makedirs(self.parts_folder, exist_ok=True)
        logger.debug(f"PartsScraper initialized: {self.parts_folder}")
    
    def search_and_download(self, issue_text, device_model, issue_id):
        logger.info(f"[Issue #{issue_id}] Starting search: model='{device_model}' text='{issue_text[:50]}...'")
        
        query = f"{device_model} {issue_text}".strip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        all_parts = []
        
        sources = [
            ('Google Shopping', f"https://www.google.com/search?tbm=shop&q={urllib.parse.quote_plus(query)}"),
            ('eBay', f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote_plus(query)}"),
            ('Amazon', f"https://www.amazon.com/s?k={urllib.parse.quote_plus(query)}"),
            ('BestBuy', f"https://www.bestbuy.com/site/searchpage.jsp?st={urllib.parse.quote_plus(query)}"),
            ('Walmart', f"https://www.walmart.com/search?q={urllib.parse.quote_plus(query)}")
        ]
        
        for source_name, url in sources:
            filename = f"issue_{issue_id:02d}_{source_name}_{timestamp}.html"
            filepath = os.path.join(self.parts_folder, filename)
            
            logger.debug(f"[Issue #{issue_id}] Downloading from {source_name}: {url[:80]}...")
            
            # Retry logic: try 3 times with different delays
            html = None
            last_error = None
            for attempt in range(3):
                try:
                    if attempt > 0:
                        import time
                        delay = attempt * 2  # 2s, 4s delays
                        logger.debug(f"[Issue #{issue_id}] {source_name}: Retry {attempt + 1}/3 after {delay}s")
                        time.sleep(delay)
                    
                    req = urllib.request.Request(url, headers=HEADERS)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        html = response.read().decode('utf-8', errors='ignore')
                    break  # Success, exit retry loop
                except Exception as e:
                    last_error = e
                    logger.debug(f"[Issue #{issue_id}] {source_name}: Attempt {attempt + 1} failed: {e}")
            
            if html:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(html)
                    
                    file_size = os.path.getsize(filepath)
                    logger.info(f"[Issue #{issue_id}] ✅ {source_name}: Downloaded {file_size} bytes")
                    
                    parts = self._extract_parts(html, source_name, filepath)
                    all_parts.extend(parts)
                    logger.debug(f"[Issue #{issue_id}] {source_name}: Extracted {len(parts)} parts")
                except Exception as e:
                    logger.error(f"[Issue #{issue_id}] ❌ {source_name}: Error saving: {e}")
            else:
                logger.error(f"[Issue #{issue_id}] ❌ {source_name}: Failed after 3 attempts: {last_error}")
                error_file = filepath.replace('.html', '_error.txt')
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"Error after 3 attempts: {last_error}\n{traceback.format_exc()}")
                logger.warning(f"[Issue #{issue_id}] {source_name}: No parts found (scraping failed)")
                # NO SIMULATED DATA - just log and continue
        
        all_parts.sort(key=lambda x: x['base_price'])
        logger.info(f"[Issue #{issue_id}] Total parts found: {len(all_parts)}")
        
        json_file = os.path.join(self.parts_folder, f"issue_{issue_id:02d}_summary_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'issue_id': issue_id,
                'device_model': device_model,
                'issue_text': issue_text,
                'query': query,
                'sources_searched': 5,
                'files_downloaded': 5,
                'parts_found': len(all_parts),
                'parts': all_parts
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[Issue #{issue_id}] JSON summary saved: {os.path.basename(json_file)}")
        return all_parts
    
    def search_replacements(self, device_model, repair_cost):
        """
        Search for replacement devices online
        Returns 4 options based on min/median/max from real scraped prices
        Only returns options that are cheaper than repair_cost
        """
        import statistics
        logger.info(f"Searching replacement options for: {device_model} (repair cost: ${repair_cost:.2f})")
        
        all_prices = []
        query = f"{device_model} tablet phone new buy"  # Add keywords for new devices
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Search all 4 sources
        sources = [
            ('Walmart', f"https://www.walmart.com/search?q={urllib.parse.quote_plus(query)}"),
            ('BestBuy', f"https://www.bestbuy.com/site/searchpage.jsp?st={urllib.parse.quote_plus(query)}"),
            ('Amazon', f"https://www.amazon.com/s?k={urllib.parse.quote_plus(query)}"),
            ('eBay', f"https://www.ebay.com/sch/i.html?_nkw={urllib.parse.quote_plus(query)}&LH_BIN=1&_sacat=0")
        ]
        
        for source_name, url in sources:
            filename = f"replacement_{device_model.replace(' ', '_')}_{source_name}_{timestamp}.html"
            filepath = os.path.join(self.parts_folder, filename)
            
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                # Extract prices
                prices = self._extract_replacement_prices(html, source_name, device_model)
                all_prices.extend(prices)
                logger.debug(f"{source_name}: Found {len(prices)} replacement prices")
                
            except Exception as e:
                logger.debug(f"{source_name}: {e}")
        
        if not all_prices:
            logger.warning(f"No replacement prices found for {device_model}")
            return None
        
        # Sort prices
        all_prices.sort()
        
        # Calculate statistics
        min_price = all_prices[0]
        max_price = all_prices[-1]
        median_price = statistics.median(all_prices)
        avg_price = statistics.mean(all_prices)
        
        logger.info(f"Replacement stats: Min=${min_price:.2f}, Median=${median_price:.2f}, Max=${max_price:.2f}, Avg=${avg_price:.2f}")
        
        # Build 4 options based on min/median/max
        # Only show if cheaper than repair
        options = []
        
        if min_price < repair_cost:
            options.append({
                'name': 'Budget Option (Min)',
                'price': f"${min_price:.2f}",
                'tier': 'budget',
                'note': 'Cheapest option found'
            })
        
        if min_price < median_price < max_price and median_price < repair_cost:
            options.append({
                'name': 'Mid-Range Option (Median)',
                'price': f"${median_price:.2f}",
                'tier': 'mid',
                'note': 'Middle price point'
            })
        
        if avg_price < repair_cost and avg_price != min_price and avg_price != max_price:
            options.append({
                'name': 'Average Price',
                'price': f"${avg_price:.2f}",
                'tier': 'average',
                'note': 'Typical market price'
            })
        
        if max_price < repair_cost:
            options.append({
                'name': 'Premium Option (Max)',
                'price': f"${max_price:.2f}",
                'tier': 'premium',
                'note': 'Highest quality found'
            })
        
        # If we don't have 4 options, add more based on available prices
        if len(options) < 4 and len(all_prices) >= 4:
            # Add more options from the price range
            quartile_1 = all_prices[len(all_prices)//4]
            quartile_3 = all_prices[3*len(all_prices)//4]
            
            if quartile_1 < repair_cost and not any(o['tier'] == 'budget' for o in options):
                options.insert(0, {
                    'name': 'Budget Option (25th percentile)',
                    'price': f"${quartile_1:.2f}",
                    'tier': 'budget',
                    'note': 'Low-cost option'
                })
            
            if quartile_3 < repair_cost and not any(o['tier'] == 'premium' for o in options):
                options.append({
                    'name': 'Premium Option (75th percentile)',
                    'price': f"${quartile_3:.2f}",
                    'tier': 'premium',
                    'note': 'Higher quality'
                })
        
        # Sort by price
        options.sort(key=lambda x: float(x['price'].replace('$', '').replace(',', '')))
        
        logger.info(f"Generated {len(options)} replacement options (all under ${repair_cost:.2f})")
        return options[:4]  # Return max 4 options
    
    def _extract_replacement_prices(self, html, source, device_model):
        """Extract prices from replacement device search results"""
        prices = []
        
        if not SCRAPING_AVAILABLE:
            return prices
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            if source == 'Walmart':
                items = soup.find_all('div', {'data-item-id': True}, limit=20)
                for item in items:
                    price_elem = item.find('span', class_='price-main') or item.find('span', class_='price')
                    if price_elem:
                        price_text = price_elem.get_text()
                        m = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if m:
                            try:
                                p = float(m.group())
                                if p > 20:  # Filter out unrealistic prices
                                    prices.append(p)
                            except: pass
            
            elif source == 'BestBuy':
                items = soup.find_all('li', class_='sku-item', limit=20)
                for item in items:
                    price_elem = item.find('div', class_='priceView-customer-price')
                    if price_elem:
                        price_text = price_elem.get_text()
                        m = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if m:
                            try:
                                p = float(m.group())
                                if p > 20:
                                    prices.append(p)
                            except: pass
            
            elif source == 'Amazon':
                items = soup.find_all('div', {'data-component-type': 's-search-result'}, limit=20)
                for item in items:
                    price_whole = item.find('span', class_='a-price-whole')
                    if price_whole:
                        try:
                            p = float(price_whole.get_text().replace(',', '').replace('$', ''))
                            if p > 20:
                                prices.append(p)
                        except: pass
            
            elif source == 'eBay':
                items = soup.find_all('div', class_='s-item__info', limit=20)
                for item in items:
                    price = item.find('span', class_='s-item__price')
                    if price:
                        m = re.search(r'[\d,]+\.?\d*', price.get_text().replace(',', ''))
                        if m:
                            try:
                                p = float(m.group())
                                if p > 20:
                                    prices.append(p)
                            except: pass
        
        except Exception as e:
            logger.debug(f"Price extraction error for {source}: {e}")
        
        return prices

    def _extract_parts(self, html, source, html_file):
        parts = []
        if not SCRAPING_AVAILABLE:
            logger.debug(f"Scraping not available for {source}")
            return parts  # Return empty list - NO SIMULATED DATA
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            if source == 'eBay':
                items = soup.find_all('div', class_='s-item__info', limit=5)
                for item in items:
                    title = item.find('div', class_='s-item__title')
                    price = item.find('span', class_='s-item__price')
                    if title and price:
                        t = title.get_text(strip=True)
                        m = re.search(r'[\d,]+\.?\d*', price.get_text().replace(',', ''))
                        if m:
                            parts.append(self._make_part(t, float(m.group()), source, html_file, 'New/Used'))
            elif source == 'Amazon':
                # Improved Amazon parsing - try multiple selectors
                items = soup.find_all('div', {'data-component-type': 's-search-result'}, limit=10)
                if not items:
                    # Try alternative selector
                    items = soup.find_all('div', class_='s-result-item', limit=10)
                
                for item in items:
                    # Try multiple title selectors
                    title = (item.find('span', class_='a-text-normal') or 
                            item.find('h2') or
                            item.find('span', class_='a-size-medium'))
                    
                    # Try multiple price selectors
                    price_whole = item.find('span', class_='a-price-whole')
                    price_fraction = item.find('span', class_='a-price-fraction')
                    price_off = item.find('span', class_='a-price')
                    
                    if title:
                        t = title.get_text(strip=True)
                        p = 0
                        
                        if price_whole:
                            try:
                                whole_text = price_whole.get_text().replace(',', '').replace('$', '').strip()
                                p = float(whole_text)
                                if price_fraction:
                                    p += float(price_fraction.get_text()) / 100
                            except: pass
                        elif price_off:
                            try:
                                price_text = price_off.get_text()
                                m = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                                if m:
                                    p = float(m.group())
                            except: pass
                        
                        if p > 0:
                            parts.append(self._make_part(t, p, source, html_file, 'New'))
            elif source == 'Google Shopping':
                # Google Shopping uses various class names, try multiple selectors
                # Shopping results are in divs with data-doc-idx or specific classes
                items = soup.find_all('div', class_='sh-dgr__grid-result', limit=5)
                if not items:
                    items = soup.find_all('div', {'data-doc-idx': True}, limit=5)
                if not items:
                    # Try to find any product-like divs
                    items = soup.find_all('div', class_='g', limit=5)
                
                for item in items:
                    # Try multiple title selectors
                    title = (item.find('h3') or item.find('h4') or 
                            item.find('div', class_='sh-np__product-title') or
                            item.find('span', class_='sh-np__product-title'))
                    
                    # Try multiple price selectors
                    price = (item.find('span', class_='sh-np__product-price') or
                            item.find('span', attrs={'aria-label': lambda x: x and 'price' in x.lower() if x else False}) or
                            item.find('div', class_='a8Pemb') or
                            item.find('span', class_='o39Cmb'))
                    
                    if title and price:
                        t = title.get_text(strip=True)
                        price_text = price.get_text(strip=True)
                        m = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if m:
                            try:
                                p = float(m.group())
                                if p > 0:
                                    parts.append(self._make_part(t, p, source, html_file, 'New'))
                            except: pass
        except Exception as e:
            logger.error(f"Parse error for {source}: {e}")
        
        return parts if parts else []  # Return empty if no parts found - NO SIMULATED DATA
    
    def _make_part(self, name, base_price, source, html_file, condition):
        marked_up = base_price * (1 + PARTS_MARKUP)
        final = marked_up + SOURCING_FEE
        return {
            'name': name[:80],
            'base_price': round(base_price, 2),
            'marked_up_price': round(marked_up, 2),
            'sourcing_fee': SOURCING_FEE,
            'final_price': round(final, 2),
            'source': source,
            'condition': condition,
            'html_file': os.path.basename(html_file)
        }
    
    def _simulate_parts(self, source, query, html_file):
        prices = {
            'Google Shopping': [16, 20, 24, 28, 32],
            'eBay': [15, 18, 22, 25, 28],
            'Amazon': [20, 25, 30, 35, 40],
            'BestBuy': [25, 30, 35, 40, 45],
            'Walmart': [18, 22, 26, 30, 34]
        }
        parts = []
        for p in prices.get(source, [20, 25, 30]):
            parts.append(self._make_part(
                f"{query} Part from {source}", p, source, html_file,
                'New' if source != 'eBay' else 'New/Used'
            ))
        return parts

# ===== MAIN APP =====
class SPARKSPHEARApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SPARKSPHEAR TECH - Main App (with Logging)")
        self.root.geometry("1500x900")
        self.root.configure(bg='#f0f0f0')
        
        self.issues_list = []
        self.client_folder = ""
        self.base_coords = None
        self.distance_miles = 0
        self.trip_fee = 0
        
        logger.info("Initializing main application UI")
        self.create_widgets()
        logger.info("Application UI created successfully")
        
        # Geocode base address on startup
        logger.info(f"Geocoding base address: {BASE_ADDRESS}")
        self.base_coords = GeoCoder.geocode(BASE_ADDRESS)
        if self.base_coords:
            logger.info(f"Base geocoded: {self.base_coords[0]:.4f}, {self.base_coords[1]:.4f}")
        else:
            logger.warning("Could not geocode base address - will retry when calculating distance")
    
    def create_widgets(self):
        """Create main widgets - auto-fits to screen size"""
        
        # Auto-fit window to screen (works on any resolution)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        # Use 90% of screen, with minimum sizes
        win_w = min(1500, int(screen_w * 0.9))
        win_h = min(950, int(screen_h * 0.9))
        # Center the window
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.minsize(1200, 700)  # Minimum size
        self.root.configure(bg='#f0f0f0')
        
        # Title bar
        title_f = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_f.pack(fill='x')
        title_f.pack_propagate(False)
        
        tk.Label(title_f, text="SPARKSPHEAR TECH - Client Workflow",
                 font=('Arial', 16, 'bold'), bg='#2c3e50', fg='white').pack(pady=8)
        tk.Label(title_f, text=f"5 Sources • {PARTS_MARKUP*100:.0f}% Markup + ${SOURCING_FEE} Fee • Linda Samsung PDF Template",
                 font=('Arial', 9), bg='#2c3e50', fg='#ecf0f1').pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab 1: Main App
        self.main_tab = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.main_tab, text="📋 Main App")
        
        # Tab 2: Activity Log
        self.log_tab = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(self.log_tab, text="📊 Activity Log")
        
        self.create_main_tab()
        self.create_log_tab()
        
        # Status bar
        self.status = tk.Label(self.root, text="Ready",
                               bd=1, relief='sunken', anchor='w', bg='#ecf0f1',
                               font=('Arial', 9))
        self.status.pack(side='bottom', fill='x')
    
    def log_to_ui(self, message, level="INFO"):
        """Add log message to the activity log tab"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[{timestamp}] [{level:5s}] {message}\n"
        self.log_display.insert('end', log_line)
        self.log_display.see('end')
    
    def update_make_dropdown(self):
        """Step 1->2: Update Make dropdown based on selected Device Type"""
        device_type = self.device_type_var.get()
        # Reset downstream dropdowns
        self.maker_dropdown.config(values=['Select...'], state='disabled')
        self.maker_var.set('Select...')
        self.model_dropdown.config(values=['Select...'], state='disabled')
        self.model_var.set('Select...')

        if device_type in ('Select...', '') or device_type not in self.device_hierarchy:
            return

        makers = ['Select...'] + sorted(self.device_hierarchy[device_type].keys())
        self.maker_dropdown.config(values=makers, state='readonly')
        self.maker_var.set('Select...')
        self.status.config(text=f"Step 2: {device_type} selected - choose a make")

    def update_model_dropdown(self):
        """Step 2->3: Update Model dropdown based on Device Type + Make"""
        device_type = self.device_type_var.get()
        maker = self.maker_var.get()
        # Reset model dropdown
        self.model_dropdown.config(values=['Select...'], state='disabled')
        self.model_var.set('Select...')

        if device_type not in self.device_hierarchy:
            return
        if maker in ('Select...', '') or maker not in self.device_hierarchy[device_type]:
            return

        models = ['Select...'] + self.device_hierarchy[device_type][maker]
        # state='normal' allows typing a custom model too
        self.model_dropdown.config(values=models, state='normal')
        self.model_var.set('Select...')
        self.status.config(text=f"Step 3: {maker} {device_type} - choose a model (or type custom)")

    def get_selected_device(self):
        """Return the full device string from the 3 dropdowns, e.g. 'Samsung Galaxy Tab E'."""
        maker = self.maker_var.get().strip()
        model = self.model_var.get().strip()
        if model in ('Select...', ''):
            return ''
        # Avoid duplicating maker if model already contains it (e.g. 'Galaxy S23' under Samsung)
        if maker and maker not in ('Select...', '') and maker.lower() not in model.lower():
            return f"{maker} {model}"
        return model

    def update_device_totals(self):
        """Calculate and display per-device totals and grand total"""
        if not hasattr(self, 'device_totals_display'):
            return
        
        # Group issues by device
        device_groups = {}
        for iss in self.issues_list:
            model = iss['model']
            if model not in device_groups:
                device_groups[model] = {
                    'issues': [],
                    'total_cost': 0,
                    'issue_count': 0
                }
            device_groups[model]['issues'].append(iss)
            device_groups[model]['issue_count'] += 1
            
            # Calculate cost for this issue (if parts have been scraped)
            if iss.get('parts') and len(iss['parts']) > 0:
                top_parts = iss['parts'][:5]
                if top_parts:
                    avg_base = sum(p['base_price'] for p in top_parts) / len(top_parts)
                    avg_marked_up = avg_base * (1 + PARTS_MARKUP)
                    issue_cost = avg_marked_up + SOURCING_FEE
                    device_groups[model]['total_cost'] += issue_cost
        
        # Build display text
        display_text = ""
        grand_total = 0
        
        if not device_groups:
            display_text = "No devices added yet.\n"
            display_text += "Select a device from the dropdown above,\n"
            display_text += "enter an issue, and click 'Add Issue'."
        else:
            display_text = "=" * 50 + "\n"
            display_text += "DEVICES & TOTALS\n"
            display_text += "=" * 50 + "\n\n"
            
            for idx, (model, data) in enumerate(device_groups.items(), 1):
                display_text += f"Device {idx}: {model}\n"
                display_text += f"  Issues: {data['issue_count']}\n"
                
                # Show each issue
                for iss in data['issues']:
                    display_text += f"    - {iss['text'][:40]}\n"
                
                if data['total_cost'] > 0:
                    display_text += f"  Subtotal: ${data['total_cost']:.2f}\n\n"
                    grand_total += data['total_cost']
                else:
                    display_text += f"  Subtotal: Pending (find parts first)\n\n"
            
            display_text += "=" * 50 + "\n"
            if grand_total > 0:
                display_text += f"GRAND TOTAL: ${grand_total:.2f}\n"
            else:
                display_text += "GRAND TOTAL: Pending parts search\n"
            display_text += "=" * 50 + "\n"
            
            if grand_total > 0:
                display_text += f"\n✅ {len(device_groups)} device(s) ready for quote\n"
            else:
                display_text += f"\n⚠️ Click 'FIND PARTS' to calculate costs\n"
        
        # Update display
        self.device_totals_display.config(state='normal')
        self.device_totals_display.delete('1.0', 'end')
        self.device_totals_display.insert('1.0', display_text)
        self.device_totals_display.config(state='disabled')
        
        # Update grand total in status
        if grand_total > 0:
            self.status.config(text=f"💰 Grand Total: ${grand_total:.2f} across {len(device_groups)} device(s)")
        elif device_groups:
            self.status.config(text=f"📱 {len(device_groups)} device(s) added - find parts to calculate total")

    def auto_calculate_distance(self, event=None):
        """Auto-calculate distance when address field loses focus"""
        address = self.client_address.get().strip()
        if address and len(address) > 5:
            self.calculate_distance()
    
    def calculate_distance(self):
        """Calculate driving distance from base to client and trip fee"""
        if not self.base_coords:
            logger.debug("Base address not geocoded yet, geocoding now")
            self.base_coords = GeoCoder.geocode(BASE_ADDRESS)
        
        client_address = self.client_address.get().strip()
        if not client_address:
            messagebox.showwarning("Missing Address", "Please enter client address")
            return
        
        self.status.config(text="Calculating distance...")
        self.root.update()
        
        client_coords = GeoCoder.geocode(client_address)
        if not client_coords:
            self.distance_label.config(text="Distance: Could not find address")
            self.status.config(text="Geocoding failed")
            logger.warning(f"Geocoding failed for: {client_address}")
            return
        
        distance_miles = RouteCalculator.get_driving_distance(
            self.base_coords[0], self.base_coords[1],
            client_coords[0], client_coords[1]
        )
        
        if distance_miles is None:
            self.distance_label.config(text="Distance: Routing failed")
            self.status.config(text="Routing failed")
            return
        
        round_trip = distance_miles * 2
        trip_fee = calculate_trip_fee(round_trip)
        
        self.distance_label.config(
            text=f"Distance: {distance_miles:.1f} mi one-way, {round_trip:.1f} mi round-trip | Trip Fee: ${trip_fee:.2f}"
        )
        self.status.config(text=f"Distance: {round_trip:.1f} mi | Trip Fee: ${trip_fee:.2f}")
        logger.info(f"Distance calculated: {round_trip:.1f} mi round-trip, Trip Fee: ${trip_fee:.2f}")
        self.log_to_ui(f"Distance: {round_trip:.1f} mi | Trip Fee: ${trip_fee:.2f}")
    
    def create_main_tab(self):
        """Create main tab with intuitive 3-column layout"""
        main = tk.Frame(self.main_tab, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Use PanedWindow for resizable columns
        paned = tk.PanedWindow(main, orient='horizontal', sashrelief='raised', bg='#f0f0f0', bd=0)
        paned.pack(fill='both', expand=True)
        
        # ===== LEFT: Client + Workflow + Issues (scrollable) =====
        left_container = tk.Frame(paned, bg='#f0f0f0')
        paned.add(left_container, minsize=350)
        
        # Canvas for scrolling
        left_canvas = tk.Canvas(left_container, bg='white', highlightthickness=0)
        left_scrollbar = tk.Scrollbar(left_container, orient='vertical', command=left_canvas.yview)
        left_scrollable = tk.Frame(left_canvas, bg='white')
        
        left_scrollable.bind(
            '<Configure>',
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox('all'))
        )
        
        left_canvas.create_window((0, 0), window=left_scrollable, anchor='nw')
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        left_canvas.pack(side='left', fill='both', expand=True)
        left_scrollbar.pack(side='right', fill='y')
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        left_canvas.bind_all('<MouseWheel>', _on_mousewheel)
        
        left = left_scrollable  # Use scrollable frame as 'left'
        
        # Client Info section
        cf = tk.LabelFrame(left, text="👤 Client Info", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        cf.pack(fill='x', padx=5, pady=5)
        
        tk.Label(cf, text="Name:*", bg='white', font=('Arial', 9)).grid(row=0, column=0, sticky='w', pady=3)
        self.client_name = tk.Entry(cf, width=25, font=('Arial', 10))
        self.client_name.grid(row=0, column=1, pady=3, padx=(10, 0))
        
        tk.Label(cf, text="Phone:", bg='white', font=('Arial', 9)).grid(row=1, column=0, sticky='w', pady=3)
        self.client_phone = tk.Entry(cf, width=25, font=('Arial', 10))
        self.client_phone.grid(row=1, column=1, pady=3, padx=(10, 0))
        
        tk.Label(cf, text="Address:*", bg='white', font=('Arial', 9)).grid(row=2, column=0, sticky='w', pady=3)
        self.client_address = tk.Entry(cf, width=25, font=('Arial', 10))
        self.client_address.grid(row=2, column=1, pady=3, padx=(10, 0))
        self.client_address.insert(0, "2523 Caroline St, Fort Wayne, IN")
        self.client_address.bind('<FocusOut>', lambda e: self.auto_calculate_distance())
        
        # Distance display label
        self.distance_label = tk.Label(cf, text="Distance: Not calculated", font=('Arial', 9, 'bold'), fg='blue', bg='white')
        self.distance_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Calculate distance button
        tk.Button(cf, text="📏 Calculate Distance & Trip Fee", command=self.calculate_distance,
                  bg='#3498db', fg='white', font=('Arial', 9, 'bold'),
                  padx=10, pady=5).grid(row=4, column=0, columnspan=2, pady=5)
        
        def setup_folder():
            name = self.client_name.get().strip()
            if not name:
                logger.warning("Setup folder attempted with no client name")
                messagebox.showwarning("Missing", "Enter client name")
                return
            
            logger.info(f"Setting up client folder for: {name}")
            safe = name.replace(' ', '_')
            self.client_folder = os.path.join(BASE_PATH, safe)
            
            try:
                for sub in ["01_Initial_Contact", "02_Quotes", "03_Parts_Research", "04_Invoices", "05_Completed"]:
                    os.makedirs(os.path.join(self.client_folder, sub), exist_ok=True)
                
                self.folder_label.config(text=f"📁 {self.client_folder}")
                self.status.config(text=f"✅ Folder ready for {safe}")
                logger.info(f"Client folder created: {self.client_folder}")
                self.log_to_ui(f"Client folder created: {safe}")
            except Exception as e:
                logger.error(f"Failed to create client folder: {e}")
                messagebox.showerror("Error", f"Failed: {e}")
        
        tk.Button(cf, text="📁 Setup Client Folder", command=setup_folder,
                  bg='#9b59b6', fg='white', font=('Arial', 9, 'bold'),
                  padx=10, pady=5).grid(row=5, column=0, columnspan=2, pady=5)
        
        self.folder_label = tk.Label(cf, text="📁 (Setup to create)", bg='white', font=('Arial', 8), fg='gray')
        self.folder_label.grid(row=6, column=0, columnspan=2, pady=3)
        
        # Workflow Stages (radio buttons)
        wf_f = tk.LabelFrame(left, text="📊 Workflow Stage", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        wf_f.pack(fill='x', padx=10, pady=10)
        
        self.workflow_stage = tk.StringVar(value="initial_contact")
        stages = [
            ("1. Initial Contact", "initial_contact"),
            ("2. Home Visit - Diagnosis", "home_visit"),
            ("3. Quote Presented", "quote_presented"),
            ("4. Approved - Work Order", "approved"),
            ("5. In Progress", "in_progress"),
            ("6. Completed", "completed"),
            ("7. Paid & Closed", "closed")
        ]
        
        for text, value in stages:
            tk.Radiobutton(wf_f, text=text, variable=self.workflow_stage,
                          value=value, bg='white').pack(anchor='w', pady=1)
        
        # Issue List
        issue_f = tk.LabelFrame(left, text="📋 Device & Issue List (Add Multiple)", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        issue_f.pack(fill='both', expand=True, padx=10, pady=10)
        
        # ===== CASCADING DROPDOWN SYSTEM =====
        # Define the complete device hierarchy: Device Type -> Make -> Models
        device_hierarchy = {
            'Phone': {
                'Apple': ['iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15', 'iPhone SE (2022)', 'iPhone SE (2020)'],
                'Samsung': ['Galaxy S23', 'Galaxy S22', 'Galaxy S21', 'Galaxy A54', 'Galaxy A34', 'Galaxy A14', 'Galaxy A04', 'Galaxy Note 20'],
                'Google': ['Pixel 8 Pro', 'Pixel 8', 'Pixel 7 Pro', 'Pixel 7', 'Pixel 6 Pro', 'Pixel 6', 'Pixel 6a', 'Pixel 5'],
                'Motorola': ['Moto G Power', 'Moto G Stylus', 'Moto Edge', 'Moto Razr'],
                'OnePlus': ['OnePlus 11', 'OnePlus 10', 'OnePlus Nord', 'OnePlus 9']
            },
            'Tablet': {
                'Apple': ['iPad', 'iPad Pro 12.9"', 'iPad Pro 11"', 'iPad Air', 'iPad Mini', 'iPad (9th gen)', 'iPad (10th gen)'],
                'Samsung': ['Galaxy Tab S9', 'Galaxy Tab S8', 'Galaxy Tab A9', 'Galaxy Tab A8', 'Galaxy Tab E', 'Galaxy Tab A', 'Galaxy Tab S6 Lite'],
                'Google': ['Pixel Tablet', 'Nexus 9', 'Nexus 7'],
                'Microsoft': ['Surface Pro 9', 'Surface Pro 8', 'Surface Go 3'],
                'Amazon': ['Fire HD 10', 'Fire HD 8', 'Fire 7']
            },
            'Laptop': {
                'Apple': ['MacBook Air M2', 'MacBook Air M1', 'MacBook Pro 13"', 'MacBook Pro 14"', 'MacBook Pro 16"', 'MacBook Pro M2'],
                'Dell': ['XPS 13', 'XPS 15', 'XPS 17', 'Inspiron 15', 'Latitude 7420', 'Gaming G15', 'Gaming G16'],
                'HP': ['Spectre x360', 'Envy 15', 'Pavilion 15', 'Omen 16', 'EliteBook 840', 'ProBook 450'],
                'Lenovo': ['ThinkPad X1 Carbon', 'ThinkPad T14', 'ThinkPad E15', 'IdeaPad 5', 'Legion 5', 'Yoga 9i', 'Yoga Slim 7'],
                'Asus': ['ZenBook 13', 'ZenBook 14', 'VivoBook 15', 'ROG Strix', 'TUF Gaming', 'ExpertBook'],
                'Razer': ['Blade 15', 'Blade 14', 'Blade Stealth 13', 'Blade 17'],
                'Microsoft': ['Surface Laptop 5', 'Surface Laptop 4', 'Surface Laptop Studio'],
                'Google': ['Pixelbook Go', 'Chromebook Plus', 'Chromebook Pro']
            },
            'Desktop': {
                'Apple': ['iMac 24"', 'iMac 27"', 'Mac Mini M2', 'Mac Studio', 'Mac Pro'],
                'Dell': ['XPS Desktop', 'Inspiron Desktop', 'Alienware Aurora', 'OptiPlex'],
                'HP': ['Pavilion Desktop', 'Envy Desktop', 'Omen Desktop', 'EliteDesk'],
                'Custom': ['Custom Built PC - Gaming', 'Custom Built PC - Workstation', 'Custom Built PC - Home Office']
            },
            'Game Console': {
                'Sony': ['PS5', 'PS5 Digital Edition', 'PS4 Pro', 'PS4 Slim', 'PS Vita'],
                'Microsoft': ['Xbox Series X', 'Xbox Series S', 'Xbox One X', 'Xbox One S', 'Xbox 360'],
                'Nintendo': ['Switch OLED', 'Switch', 'Switch Lite', '3DS XL', 'New 3DS'],
                'Steam': ['Steam Deck OLED', 'Steam Deck LCD']
            },
            'Wearable': {
                'Apple': ['Apple Watch Series 9', 'Apple Watch Series 8', 'Apple Watch SE', 'Apple Watch Ultra'],
                'Samsung': ['Galaxy Watch 6', 'Galaxy Watch 5', 'Galaxy Watch 4', 'Galaxy Watch Active'],
                'Google': ['Pixel Watch 2', 'Pixel Watch', 'Fitbit Charge', 'Fitbit Versa'],
                'Garmin': ['Garmin Venu', 'Garmin Forerunner', 'Garmin Fenix']
            },
            'Headphones': {
                'Apple': ['AirPods Pro 2', 'AirPods Pro', 'AirPods 3', 'AirPods 2', 'AirPods Max', 'Beats Solo', 'Beats Studio'],
                'Samsung': ['Galaxy Buds Pro', 'Galaxy Buds 2', 'Galaxy Buds Live', 'Galaxy Buds FE'],
                'Sony': ['WH-1000XM5', 'WH-1000XM4', 'WF-1000XM4', 'WF-1000XM5', 'LinkBuds'],
                'Bose': ['QuietComfort 45', 'QuietComfort Ultra', 'SoundLink']
            }
        }
        
        # Level 1: Device Type dropdown
        tk.Label(issue_f, text="1. Device Type:", bg='white', font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w', pady=2)
        self.device_type_var = tk.StringVar()
        device_types = ['Select...'] + sorted(device_hierarchy.keys())
        self.device_type_dropdown = ttk.Combobox(issue_f, textvariable=self.device_type_var, values=device_types, width=20, state='readonly', font=('Arial', 10))
        self.device_type_dropdown.set('Select...')
        self.device_type_dropdown.grid(row=0, column=1, columnspan=2, pady=2, padx=(5, 0), sticky='ew')
        self.device_type_dropdown.bind('<<ComboboxSelected>>', lambda e: self.update_make_dropdown())

        # Level 2: Make dropdown
        tk.Label(issue_f, text="2. Make:", bg='white', font=('Arial', 9, 'bold')).grid(row=1, column=0, sticky='w', pady=2)
        self.maker_var = tk.StringVar()
        self.maker_dropdown = ttk.Combobox(issue_f, textvariable=self.maker_var, values=['Select...'], width=20, state='disabled', font=('Arial', 10))
        self.maker_dropdown.set('Select...')
        self.maker_dropdown.grid(row=1, column=1, columnspan=2, pady=2, padx=(5, 0), sticky='ew')
        self.maker_dropdown.bind('<<ComboboxSelected>>', lambda e: self.update_model_dropdown())

        # Level 3: Model dropdown
        tk.Label(issue_f, text="3. Model:*", bg='white', font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky='w', pady=2)
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(issue_f, textvariable=self.model_var, values=['Select...'], width=20, state='disabled', font=('Arial', 10))
        self.model_dropdown.set('Select...')
        self.model_dropdown.grid(row=2, column=1, columnspan=2, pady=2, padx=(5, 0), sticky='ew')

        # Helper text
        tk.Label(issue_f, text="Tip: pick Type -> Make -> Model. You can also type a custom model.",
                 bg='white', font=('Arial', 8), fg='gray').grid(row=3, column=0, columnspan=3, sticky='w', pady=(0, 4))

        # Store hierarchy as instance variable
        self.device_hierarchy = device_hierarchy

        # Issue text input
        tk.Label(issue_f, text="Issue:*", bg='white', font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='nw', pady=3)
        self.issue_text = scrolledtext.ScrolledText(issue_f, height=4, width=35, font=('Arial', 10), wrap='word')
        self.issue_text.grid(row=4, column=1, columnspan=2, pady=3, padx=(5, 0), sticky='ew')

        def add_issue():
            model = self.get_selected_device()
            text = self.issue_text.get('1.0', 'end').strip()

            if not model:
                messagebox.showwarning("Missing Device", "Select Device Type -> Make -> Model (or type a custom model).")
                return
            if not text:
                logger.warning("Add issue attempted with empty text")
                messagebox.showwarning("Missing Issue", "Enter an issue description for this device.")
                return

            issue_id = len(self.issues_list) + 1
            self.issues_list.append({'id': issue_id, 'model': model, 'text': text, 'parts': []})
            self.issues_listbox.insert('end', f"#{issue_id} - {model}: {text[:45]}")
            self.issue_count.config(text=f"Issues: {len(self.issues_list)}")
            self.issue_text.delete('1.0', 'end')

            # Update device totals display
            self.update_device_totals()

            logger.info(f"Added issue #{issue_id}: {model} - {text[:50]}")
            self.log_to_ui(f"Added issue #{issue_id}: {model}")
            self.status.config(text=f"Added issue #{issue_id} for {model}")

        # Action buttons row
        btn_frame = tk.Frame(issue_f, bg='white')
        btn_frame.grid(row=5, column=0, columnspan=3, pady=6, sticky='ew')

        tk.Button(btn_frame, text="+ Add This Device & Issue", command=add_issue,
                  bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                  padx=12, pady=6).pack(side='left', expand=True, fill='x', padx=2)

        def remove_issue():
            sel = self.issues_listbox.curselection()
            if not sel:
                messagebox.showinfo("Select Item", "Click an issue in the list to remove it.")
                return
            removed = self.issues_list.pop(sel[0])
            for i, iss in enumerate(self.issues_list):
                iss['id'] = i + 1
            self.issues_listbox.delete(0, 'end')
            for iss in self.issues_list:
                self.issues_listbox.insert('end', f"#{iss['id']} - {iss['model']}: {iss['text'][:45]}")
            self.issue_count.config(text=f"Issues: {len(self.issues_list)}")
            self.update_device_totals()
            logger.info(f"Removed issue #{removed['id']}: {removed['model']}")
            self.log_to_ui(f"Removed issue #{removed['id']}")

        tk.Button(btn_frame, text="Remove Selected", command=remove_issue,
                  bg='#e74c3c', fg='white', font=('Arial', 9, 'bold'),
                  padx=10, pady=6).pack(side='left', padx=2)

        # Issues list
        self.issue_count = tk.Label(issue_f, text="Issues: 0", font=('Arial', 10, 'bold'), bg='white')
        self.issue_count.grid(row=6, column=0, columnspan=3, pady=(4, 2))

        self.issues_listbox = tk.Listbox(issue_f, height=4, width=55, font=('Arial', 9))
        self.issues_listbox.grid(row=7, column=0, columnspan=3, pady=2, sticky='ew')

        # Per-device & grand total display
        totals_label = tk.Label(issue_f, text="Per-Device & Grand Total:", font=('Arial', 9, 'bold'), bg='white')
        totals_label.grid(row=8, column=0, columnspan=3, sticky='w', pady=(6, 2))

        self.device_totals_display = tk.Text(issue_f, height=8, width=50, font=('Courier', 9),
                                              wrap='word', state='disabled', bg='#f8f9fa', relief='solid', bd=1)
        self.device_totals_display.grid(row=9, column=0, columnspan=3, pady=2, sticky='ew')

        def find_parts():
            if not self.issues_list:
                messagebox.showwarning("No Issues", "Add at least one device & issue first.")
                return
            if not self.client_folder:
                messagebox.showwarning("No Folder", "Click 'Setup Client Folder' first.")
                return

            # Disable button to prevent double-clicks
            self.find_parts_btn.config(state='disabled', text="Searching... please wait")
            logger.info(f"Starting parts search for {len(self.issues_list)} issues")
            self.log_to_ui(f"Starting parts search for {len(self.issues_list)} issues")
            self.status.config(text="Scraping 5 sources & downloading files...")
            self.scrape_display.config(state='normal')
            self.scrape_display.delete('1.0', 'end')
            self.scrape_display.insert('1.0', "Scraping 5 sources (Google Shopping, eBay, Amazon, Best Buy, Walmart)...\n\n")
            self.root.update()

            def do_work():
                try:
                    scraper = PartsScraper(self.client_folder)
                    total = 0
                    for iss in self.issues_list:
                        self.scrape_display.insert('end', f"\nIssue #{iss['id']}: {iss['model']}\n")
                        self.scrape_display.insert('end', f"   {iss['text'][:60]}\n")
                        self.scrape_display.see('end')
                        self.root.update()
                        self.log_to_ui(f"Scraping Issue #{iss['id']}: {iss['model']}")
                        try:
                            parts = scraper.search_and_download(iss['text'], iss['model'], iss['id'])
                            iss['parts'] = parts
                            total += len(parts)
                            if parts:
                                self.scrape_display.insert('end', f"   OK - {len(parts)} parts found across sources\n")
                            else:
                                self.scrape_display.insert('end', f"   No parts found from any source\n")
                            self.log_to_ui(f"Issue #{iss['id']}: {len(parts)} parts found")
                        except Exception as e:
                            logger.error(f"Issue #{iss['id']} failed: {e}\n{traceback.format_exc()}")
                            self.scrape_display.insert('end', f"   ERROR: {e}\n")
                        self.scrape_display.see('end')
                        self.root.update()

                    self.scrape_display.insert('end', f"\nDone! {total} parts total. Files saved to 03_Parts_Research/\n")
                    self.status.config(text=f"{total} parts found & downloaded")
                    logger.info(f"Parts search complete: {total} total parts across {len(self.issues_list)} issues")
                    self.log_to_ui(f"Complete: {total} parts found")
                    # Refresh totals now that costs are known
                    self.update_device_totals()
                except Exception as e:
                    logger.critical(f"Parts search critical error: {e}\n{traceback.format_exc()}")
                    messagebox.showerror("Critical Error", f"Failed: {e}")
                finally:
                    self.find_parts_btn.config(state='normal', text="STEP 2: FIND PARTS (All Devices)")

            threading.Thread(target=do_work, daemon=True).start()

        self.find_parts_btn = tk.Button(issue_f, text="STEP 2: FIND PARTS (All Devices)", command=find_parts,
                  bg='#27ae60', fg='white', font=('Arial', 11, 'bold'),
                  padx=15, pady=10)
        self.find_parts_btn.grid(row=10, column=0, columnspan=3, pady=12, sticky='ew')

        # Make column 1 expandable
        issue_f.columnconfigure(1, weight=1)
        
        # MIDDLE: Scraping Status
        mid = tk.Frame(paned, bg='white', relief='raised', bd=2)
        paned.add(mid, minsize=300)
        
        sf = tk.LabelFrame(mid, text="🔄 Scraping Status", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        sf.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.scrape_display = scrolledtext.ScrolledText(sf, height=25, width=40, font=('Courier', 9), wrap='word')
        self.scrape_display.pack(fill='both', expand=True, pady=5)
        
        # RIGHT: Report
        right = tk.Frame(paned, bg='white', relief='raised', bd=2)
        paned.add(right, minsize=350)
        
        def generate_report():
            if not self.issues_list:
                logger.warning("Generate report attempted with no issues")
                messagebox.showwarning("No Issues", "Add issues first")
                return
            
            logger.info("Generating final report")
            self.log_to_ui("Generating final report")
            
            report = []
            grand_total = 0
            
            report.append("=" * 80)
            report.append(" " * 25 + "SPARKSPHEAR TECH")
            report.append(" " * 18 + "DIAGNOSTIC & PRICING REPORT")
            report.append("=" * 80)
            report.append("")
            report.append(f"Client: {self.client_name.get()}")
            report.append(f"Address: {self.client_address.get()}")
            report.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
            report.append("")
            
            for iss in self.issues_list:
                report.append("=" * 80)
                report.append(f"ISSUE #{iss['id']}: {iss['model']}")
                report.append("=" * 80)
                report.append("")
                report.append("PROBLEM:")
                report.append("-" * 80)
                report.append(iss['text'])
                report.append("")
                
                if iss.get('parts') and len(iss['parts']) > 0:
                    # Take top 5 parts for averaging
                    top_parts = iss['parts'][:5]
                    report.append(f"PARTS NEEDED:")
                    report.append("-" * 80)
                    for i, p in enumerate(top_parts, 1):
                        n = p['name'][:60] + '..' if len(p['name']) > 60 else p['name']
                        report.append(f"  {i}. {n}")
                    report.append("-" * 80)
                    
                    # Calculate average of 5 parts
                    if len(top_parts) >= 5:
                        avg_base = sum(p['base_price'] for p in top_parts) / len(top_parts)
                    else:
                        avg_base = sum(p['base_price'] for p in top_parts) / len(top_parts) if top_parts else 0
                    
                    # Apply markup (CLIENT DOESN'T SEE THIS)
                    avg_marked_up = avg_base * (1 + PARTS_MARKUP)
                    avg_final = avg_marked_up + SOURCING_FEE
                    
                    # ONLY show final price to client - NO markup talk
                    report.append(f"  Cost for this repair: ${avg_final:.2f}")
                    report.append("")
                    
                    grand_total += avg_final
                else:
                    report.append("PARTS: Unable to find parts at this time")
                    report.append("We will source parts and provide pricing separately")
                    report.append("")
                report.append("")
            
            # PROMINENT FINAL PRICE - CLIENT FACING ONLY
            report.append("=" * 80)
            report.append(f"  TOTAL DUE: ${grand_total:.2f}")
            report.append("=" * 80)
            report.append("")
            report.append("This quote includes parts and labor for all repairs listed above.")
            report.append("Payment is due upon completion of work.")
            report.append("=" * 80)
            
            self.report_display.config(state='normal')
            self.report_display.delete('1.0', 'end')
            self.report_display.insert('1.0', '\n'.join(report))
            self.report_display.config(state='disabled')
            
            self.status.config(text=f"✅ Report generated! ${grand_total:.2f}")
            logger.info(f"Report generated: {len(self.issues_list)} issues, ${grand_total:.2f} total")
            self.log_to_ui(f"Report generated: ${grand_total:.2f} total")
        
        af = tk.Frame(right, bg='white')
        af.pack(fill='x', padx=10, pady=10)
        
        tk.Button(af, text="📄 Generate Final Report", command=generate_report,
                  bg='#e67e22', fg='white', font=('Arial', 11, 'bold'),
                  padx=15, pady=10).pack(fill='x', pady=3)
        
        def save_report():
            content = self.report_display.get('1.0', 'end').strip()
            if not content:
                logger.warning("Save report attempted with empty report")
                messagebox.showwarning("Empty", "Generate report first")
                return
            if not self.client_folder:
                messagebox.showwarning("No Folder", "Setup folder first")
                return
            
            save_dir = os.path.join(self.client_folder, "02_Quotes")
            os.makedirs(save_dir, exist_ok=True)
            fn = f"Quote_{self.client_name.get().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            fp = os.path.join(save_dir, fn)
            
            try:
                with open(fp, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Report saved: {fp}")
                self.log_to_ui(f"Report saved: {fn}")
                messagebox.showinfo("Saved", f"Saved to:\n{fp}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
                messagebox.showerror("Error", f"Failed: {e}")
        
        def generate_pdf():
            """Generate client-facing PDF matching Linda Samsung template exactly
            Supports multiple devices - generates full 8-section template for each"""
            if not self.issues_list:
                messagebox.showwarning("No Issues", "Add issues first")
                return
            if not self.client_folder:
                messagebox.showwarning("No Folder", "Setup folder first")
                return
            
            try:
                from fpdf import FPDF, XPos, YPos
            except ImportError:
                messagebox.showerror("Missing", "Install fpdf2: pip install fpdf2")
                return
            
            logger.info(f"Generating client PDF (Linda template) for {len(self.issues_list)} device(s)")
            self.log_to_ui(f"Generating PDF for {len(self.issues_list)} device(s)")
            
            # ===== BACKGROUND CALCULATIONS (CLIENT DOESN'T SEE) =====
            pdf_data = []
            grand_total = 0
            
            for iss in self.issues_list:
                issue_cost = 0
                issue_parts = []
                
                if iss.get('parts') and len(iss['parts']) > 0:
                    top_parts = iss['parts'][:5]
                    for p in top_parts:
                        issue_parts.append(p['name'][:60])
                    
                    if top_parts:
                        avg_base = sum(p['base_price'] for p in top_parts) / len(top_parts)
                        avg_marked_up = avg_base * (1 + PARTS_MARKUP)
                        issue_cost = avg_marked_up + SOURCING_FEE
                        grand_total += issue_cost
                
                pdf_data.append({
                    'model': iss['model'],
                    'problem': iss['text'],
                    'parts': issue_parts,
                    'cost': issue_cost
                })
            
            # ===== BUILD PDF (LINDA SAMSUNG TEMPLATE) =====
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # ===== COVER PAGE =====
            pdf.add_page()
            
            # Add LOGO at top
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            if os.path.exists(logo_path):
                try:
                    # Center the logo
                    pdf.image(logo_path, x=55, y=20, w=100)
                    pdf.ln(35)  # Space after logo
                except Exception as e:
                    logger.warning(f"Could not add logo: {e}")
                    pdf.ln(10)
            else:
                pdf.ln(10)
            
            # Company header
            pdf.set_font("helvetica", "B", 18)
            pdf.cell(0, 10, "SPARKSPHEAR TECH", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.set_font("helvetica", "", 9)
            pdf.cell(0, 5, "260-267-0641  |  sparksphear4me@gmail.com", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.cell(0, 5, "Mon-Fri, 8:00 AM - 5:00 PM", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.ln(10)
            
            # Main title
            pdf.set_font("helvetica", "B", 20)
            pdf.cell(0, 12, "DEVICE ASSESSMENT & REPAIR QUOTE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.ln(5)
            
            # Prepared for
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 8, f"Prepared for: {self.client_name.get()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, f"Date: {datetime.now().strftime('%B %d, %Y')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            if hasattr(self, 'client_address') and self.client_address.get():
                pdf.cell(0, 6, f"Address: {self.client_address.get()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            if hasattr(self, 'client_phone') and self.client_phone.get():
                pdf.cell(0, 6, f"Phone: {self.client_phone.get()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.ln(8)
            
            # Summary box
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "QUOTE SUMMARY", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True, align="C")
            pdf.ln(2)
            
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 6, f"Number of Devices: {len(pdf_data)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            for idx, dev in enumerate(pdf_data, 1):
                pdf.cell(0, 6, f"  {idx}. {dev['model']} - Cost: ${dev['cost']:.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, f"GRAND TOTAL: ${grand_total:.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            pdf.ln(10)
            
            pdf.set_font("helvetica", "I", 9)
            pdf.multi_cell(0, 5, "This quote includes a complete assessment and cost breakdown for each device. Detailed information for each device follows on the next pages.")
            
            # ===== DEVICE SECTIONS (Full Linda Samsung template for each) =====
            for device_idx, dev in enumerate(pdf_data, 1):
                
                # ===== PAGE 1 FOR THIS DEVICE =====
                pdf.add_page()
                
                # Top header
                pdf.set_font("helvetica", "", 8)
                pdf.cell(0, 4, f"SPARKSPHEAR TECH  |  260-267-0641  |  sparksphear4me@gmail.com  |  Page {pdf.page_no()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(5)
                
                # Small logo
                if os.path.exists(logo_path):
                    try:
                        pdf.image(logo_path, x=80, y=15, w=50)
                        pdf.ln(15)
                    except: pass
                
                # Title
                pdf.set_font("helvetica", "B", 16)
                pdf.cell(0, 10, f"Device {device_idx} of {len(pdf_data)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.set_font("helvetica", "B", 20)
                pdf.cell(0, 12, "DEVICE ASSESSMENT & REPAIR QUOTE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(3)
                
                # Contact
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, "260-267-0641", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.cell(0, 5, "sparksphear4me@gmail.com", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.cell(0, 5, "Mon-Fri, 8:00 AM - 5:00 PM", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(8)
                
                # Device title
                pdf.set_font("helvetica", "B", 14)
                pdf.cell(0, 8, f"{dev['model']} - Device Assessment & Repair Options", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(2)
                
                pdf.set_font("helvetica", "I", 9)
                pdf.cell(0, 5, "A clear breakdown of what's wrong, what it costs to fix, and how it compares to buying new.", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(8)
                
                # Prepared for/by table
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(45, 6, "PREPARED FOR", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 6, f" {self.client_name.get()}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(45, 6, "DATE", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 6, f" {datetime.now().strftime('%B %d, %Y')}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(45, 6, "PREPARED BY", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 6, " Shazaly M - SPARKSPHEAR TECH", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(45, 6, "DEVICE", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 6, f" {dev['model']}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(8)
                
                # 01 EXECUTIVE SUMMARY
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "01  EXECUTIVE SUMMARY", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                pdf.set_font("helvetica", "", 10)
                summary = f"After thorough diagnostics of your {dev['model']}, I've identified the issue: {dev['problem'][:100]}. "
                summary += "Good news - this is repairable. I've researched every option, from repair to full replacement, "
                summary += "and built a complete cost comparison below so you can make the call that's right for you."
                pdf.multi_cell(0, 5, summary)
                pdf.ln(5)
                
                # 02 DIAGNOSTIC FINDINGS
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "02  DIAGNOSTIC FINDINGS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Device: {dev['model']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 5, f"Issue: {dev['problem'][:80]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(3)
                
                pdf.set_font("helvetica", "", 10)
                findings = [
                    "Device diagnosed and issue identified",
                    "Problem is repairable",
                    "Parts researched from multiple sources",
                    "Cost comparison completed"
                ]
                for f in findings:
                    pdf.cell(0, 5, f"[X] {f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)
                
                # 03 REPAIR OPTION
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "03  REPAIR OPTION - COST BREAKDOWN", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                if dev['parts']:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, f"What needs to be done: {dev['problem'][:60]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.ln(3)
                    
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(90, 6, "ITEM", border=1, align="C")
                    pdf.cell(60, 6, "NOTES", border=1, align="C")
                    pdf.cell(40, 6, "COST", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    pdf.set_font("helvetica", "", 10)
                    for part in dev['parts'][:3]:
                        pdf.cell(90, 5, part[:35], border=1)
                        pdf.cell(60, 5, "Market price average", border=1)
                        pdf.cell(40, 5, f"${dev['cost']/len(dev['parts']):.2f}", border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(150, 7, "TOTAL REPAIR COST", border=1, align="R")
                    pdf.cell(40, 7, f"${dev['cost']:.2f}", border=1, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.ln(5)
                    
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, "What's included:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 10)
                    for item in ["Complete diagnosis and repair", "Quality parts from verified sources", "Professional installation", "30-day warranty on repair work"]:
                        pdf.cell(0, 5, f"[X] {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, "Parts: To be sourced - pricing will be provided", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # ===== PAGE 2 FOR THIS DEVICE =====
                pdf.add_page()
                pdf.set_font("helvetica", "", 8)
                pdf.cell(0, 4, f"SPARKSPHEAR TECH  |  260-267-0641  |  sparksphear4me@gmail.com  |  Page {pdf.page_no()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(5)
                
                # 04 REPLACEMENT OPTIONS
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "04  REPLACEMENT OPTIONS - IF YOU'D RATHER GO NEW", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                pdf.set_font("helvetica", "", 10)
                
                # Search for real replacement options
                try:
                    scraper = PartsScraper(self.client_folder)
                    dynamic_options = scraper.search_replacements(dev['model'], dev['cost'])
                    
                    if dynamic_options and len(dynamic_options) > 0:
                        pdf.cell(0, 5, f"Based on real prices from Walmart, Best Buy, Amazon, and eBay:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.cell(0, 5, f"Options below are cheaper than the ${dev['cost']:.2f} repair cost:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.ln(3)
                        
                        for idx, opt in enumerate(dynamic_options[:4], 1):
                            opt_label = f"OPTION {chr(64+idx)}"
                            pdf.set_font("helvetica", "B", 10)
                            pdf.cell(0, 5, f"{opt_label}  {opt['name']}  {opt['price']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("helvetica", "", 10)
                            pdf.cell(0, 5, f"  Note: {opt.get('note', 'Online pricing')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.cell(0, 5, f"  Source: Scraped from online retailers", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("helvetica", "B", 10)
                            pdf.cell(0, 5, f"  + Cheaper than repair by ${dev['cost'] - float(opt['price'].replace('$', '').replace(',', '')):.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.set_font("helvetica", "", 10)
                            pdf.cell(0, 5, f"  - May require data transfer from old device", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                            pdf.ln(3)
                    else:
                        pdf.cell(0, 5, f"Based on our research, replacement devices in this category cost more than the ${dev['cost']:.2f} repair.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.cell(0, 5, f"REPAIR IS THE BETTER VALUE - You save money by fixing your current device.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                        pdf.ln(3)
                except Exception as e:
                    logger.error(f"Replacement search failed: {e}")
                    pdf.cell(0, 5, "Contact us for current replacement options in your area.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.ln(3)
                
                # 05 COST COMPARISON MATRIX
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "05  COST COMPARISON MATRIX", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(70, 6, "OPTION", border=1, align="C")
                pdf.cell(40, 6, "TOTAL COST", border=1, align="C")
                pdf.cell(30, 6, "TIME", border=1, align="C")
                pdf.cell(50, 6, "WHY IT MIGHT WIN", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                pdf.set_font("helvetica", "", 10)
                repair_cost_str = f"${dev['cost']:.2f}" if dev['cost'] > 0 else "TBD"
                options = [
                    ("Repair (my service)", repair_cost_str, "2 hrs", "Keep your device"),
                    ("New budget tablet", "$64.00", "0 hrs", "New device, warranty"),
                    ("New quality tablet", "$150.00", "0 hrs", "Modern, lasts longer"),
                    ("Used same model", "$50.00", "3-5 days", "Cheapest option")
                ]
                
                for opt, cost, time, why in options:
                    pdf.cell(70, 5, opt, border=1)
                    pdf.cell(40, 5, cost, border=1, align="C")
                    pdf.cell(30, 5, time, border=1, align="C")
                    pdf.cell(50, 5, why, border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)
                
                # 06 MY RECOMMENDATION
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "06  MY RECOMMENDATION", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                pdf.set_font("helvetica", "", 10)
                pdf.multi_cell(0, 5, f"I can fix your {dev['model']} for you. Here's how to think about which path fits you best:")
                pdf.ln(5)
                
                # ===== PAGE 3 FOR THIS DEVICE =====
                pdf.add_page()
                pdf.set_font("helvetica", "", 8)
                pdf.cell(0, 4, f"SPARKSPHEAR TECH  |  260-267-0641  |  sparksphear4me@gmail.com  |  Page {pdf.page_no()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(5)
                
                # Repair vs Replace
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(95, 6, "REPAIR IS A GOOD OPTION IF...", border=1, align="C")
                pdf.cell(95, 6, "CONSIDER REPLACEMENT IF...", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                repair_ifs = ["You like this device and want to keep using it", "Apps and data are already set up", "You want the most economical solution", "The device has sentimental value"]
                replace_ifs = ["You want a faster, more modern device", "You're concerned about security updates", "You want a warranty and brand-new device", "Budget allows for $64-$150 investment"]
                
                for r, rep in zip(repair_ifs, replace_ifs):
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(95, 8, f"[X] {r}", border=1)
                    pdf.cell(95, 8, f"[!] {rep}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(8)
                
                # 07 NEXT STEPS
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "07  NEXT STEPS - YOUR CHOICE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                next_steps = [
                    ("OPTION 1  Proceed with repair", [f"I order the necessary parts", f"You approve the ${dev['cost']:.2f} total cost", "I complete the repair (1.5-2 hours)", "You get your device back, fully working"], 'Reply: "Yes, proceed with repair"'),
                    ("OPTION 2  Buy a new device", ["I provide store locations and exact models", "You purchase the new device", "I can help transfer your data (+$25)"], 'Reply: "Send me new tablet options"'),
                    ("OPTION 3  Take more time to decide", ["Take your time reviewing this quote", "I'm available to answer any questions", "No pressure - it's your decision"], 'Reply: "I need more time"')
                ]
                
                for opt_title, steps, reply in next_steps:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 6, opt_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "", 10)
                    for s in steps:
                        pdf.cell(0, 5, f"[X] {s}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("helvetica", "I", 9)
                    pdf.cell(0, 5, f"To confirm, {reply}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.ln(3)
                
                # ===== PAGE 4 FOR THIS DEVICE =====
                pdf.add_page()
                pdf.set_font("helvetica", "", 8)
                pdf.cell(0, 4, f"SPARKSPHEAR TECH  |  260-267-0641  |  sparksphear4me@gmail.com  |  Page {pdf.page_no()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.ln(5)
                
                # 08 IMPORTANT NOTES
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "08  IMPORTANT NOTES", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
                pdf.ln(2)
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, "Transparent pricing", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("helvetica", "", 10)
                for t in ["No hidden fees", "Parts sourced from verified retailers", "30-day warranty on repair work", "If the repair fails, there's no charge"]:
                    pdf.cell(0, 5, f"[X] {t}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, "Local availability", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, "All replacement devices listed above are confirmed available in Fort Wayne:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 5, "Walmart: 10420 Maysville Rd | 702 Coliseum Blvd W | 6151 Stellhorn Rd", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 5, "Best Buy: 4110 Jefferson Blvd, Fort Wayne, IN 46804", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)
                
                pdf.set_font("helvetica", "", 10)
                pdf.multi_cell(0, 5, "I've given you all the information to make the best decision for your situation. Whether you choose repair or replacement, I'm here to help - either way, you'll have a working device.")
                pdf.ln(3)
                pdf.multi_cell(0, 5, "Looking forward to hearing from you!")
                pdf.ln(5)
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "Shazaly M", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, "SPARKSPHEAR TECH", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 5, "260-267-0641", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 5, "sparksphear4me@gmail.com", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)
                
                pdf.set_font("helvetica", "I", 9)
                pdf.multi_cell(0, 5, "Available Mon-Fri, 8:00 AM-5:00 PM - text or call anytime, email for detailed questions, or I can meet in person to walk through the diagnostic results.")
                pdf.ln(8)
                
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(0, 6, "Want round-the-clock peace of mind?", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, "Add 24/7 priority support for just $15/month", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
                pdf.set_font("helvetica", "I", 9)
                pdf.cell(0, 5, "Ask Shazaly for details", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            
            # Save PDF
            save_dir = os.path.join(self.client_folder, "02_Quotes")
            os.makedirs(save_dir, exist_ok=True)
            fn = f"Quote_{self.client_name.get().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            fp = os.path.join(save_dir, fn)
            
            try:
                pdf.output(fp)
                logger.info(f"PDF generated (Linda template): {fp}")
                self.log_to_ui(f"PDF generated: {fn}")
                messagebox.showinfo("PDF Generated", f"Client PDF saved:\n{fp}")
                if os.name == 'nt':
                    os.startfile(fp)
            except Exception as e:
                logger.error(f"PDF generation failed: {e}")
                messagebox.showerror("Error", f"Failed: {e}")
        
        tk.Button(af, text="💾 Save Report (Text)", command=save_report,
                  bg='#16a085', fg='white', font=('Arial', 10, 'bold'),
                  padx=15, pady=8).pack(fill='x', pady=3)
        
        tk.Button(af, text="📄 Generate Client PDF", command=generate_pdf,
                  bg='#c0392b', fg='white', font=('Arial', 11, 'bold'),
                  padx=15, pady=10).pack(fill='x', pady=3)
        
        # Cost Matrix controls
        cost_frame = tk.LabelFrame(right, text="💰 Cost Matrix", font=('Arial', 10, 'bold'), bg='white', padx=5, pady=5)
        cost_frame.pack(fill='x', padx=10, pady=5)
        
        # Show current pricing
        pricing_text = f"Labor: ${HOURLY_LABOR}/hr | Trip: ${BASE_TRIP_FEE} | Markup: {PARTS_MARKUP*100:.0f}% | Fee: ${SOURCING_FEE}"
        tk.Label(cost_frame, text=pricing_text, bg='white', font=('Arial', 8), fg='gray').pack(pady=2)
        
        def open_cost_matrix():
            """Open cost matrix file in default text editor"""
            matrix_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cost_matrix.txt")
            if os.path.exists(matrix_path):
                os.startfile(matrix_path) if os.name == 'nt' else None
                logger.info(f"Opened cost matrix: {matrix_path}")
                self.log_to_ui(f"Opened cost matrix for editing")
            else:
                messagebox.showerror("Missing", "Cost matrix file not found")
        
        def reload_cost_matrix():
            """Reload cost matrix from file"""
            global HOURLY_LABOR, BASE_TRIP_FEE, BASE_MILES, PER_MILE_RATE, DIAGNOSIS_FEE
            global MIN_LABOR_HOURS, PARTS_MARKUP, SOURCING_FEE, MIN_PARTS_PRICE
            
            cost_matrix.load()
            HOURLY_LABOR = cost_matrix.get('SERVICES', 'HOURLY_LABOR', 25.00)
            BASE_TRIP_FEE = cost_matrix.get('SERVICES', 'TRIP_FEE_BASE', 35.00)
            BASE_MILES = int(cost_matrix.get('SERVICES', 'TRIP_FEE_INCLUDED_MILES', 15))
            PER_MILE_RATE = cost_matrix.get('SERVICES', 'TRIP_FEE_PER_MILE', 0.67)
            DIAGNOSIS_FEE = cost_matrix.get('SERVICES', 'DIAGNOSIS_FEE', 25.00)
            MIN_LABOR_HOURS = cost_matrix.get('SERVICES', 'MIN_LABOR_HOURS', 1.0)
            PARTS_MARKUP = cost_matrix.get('PARTS', 'PARTS_MARKUP', 0.25)
            SOURCING_FEE = cost_matrix.get('PARTS', 'SOURCING_FEE', 15.00)
            MIN_PARTS_PRICE = cost_matrix.get('PARTS', 'MIN_PARTS_PRICE', 10.00)
            
            new_pricing = f"Labor: ${HOURLY_LABOR}/hr | Trip: ${BASE_TRIP_FEE} | Markup: {PARTS_MARKUP*100:.0f}% | Fee: ${SOURCING_FEE}"
            pricing_label.config(text=new_pricing)
            logger.info(f"Cost matrix reloaded: {new_pricing}")
            self.log_to_ui(f"Cost matrix reloaded")
            messagebox.showinfo("Reloaded", f"Pricing updated:\n{new_pricing}")
        
        btn_frame = tk.Frame(cost_frame, bg='white')
        btn_frame.pack(fill='x', pady=2)
        
        tk.Button(btn_frame, text="📝 Edit", command=open_cost_matrix,
                  bg='#3498db', fg='white', font=('Arial', 9, 'bold'),
                  padx=10, pady=5).pack(side='left', expand=True, fill='x', padx=2)
        
        tk.Button(btn_frame, text="🔄 Reload", command=reload_cost_matrix,
                  bg='#27ae60', fg='white', font=('Arial', 9, 'bold'),
                  padx=10, pady=5).pack(side='left', expand=True, fill='x', padx=2)
        
        pricing_label = tk.Label(cost_frame, text="", bg='white', font=('Arial', 8, 'bold'), fg='blue')
        pricing_label.pack(pady=2)
        
        pf = tk.LabelFrame(right, text="📄 Final Report", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        pf.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.report_display = scrolledtext.ScrolledText(pf, height=25, width=75, font=('Courier', 9), wrap='word', state='disabled')
        self.report_display.pack(fill='both', expand=True)
    
    def create_log_tab(self):
        """Create the activity log tab"""
        log_f = tk.Frame(self.log_tab, bg='white')
        log_f.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Frame(log_f, bg='#34495e', height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Activity Log - All actions tracked here",
                 font=('Arial', 12, 'bold'), bg='#34495e', fg='white').pack(pady=10)
        
        # Log controls
        ctrl = tk.Frame(log_f, bg='white')
        ctrl.pack(fill='x', pady=5)
        
        def clear_log():
            self.log_display.delete('1.0', 'end')
            logger.info("Log display cleared")
        
        def open_log_file():
            if os.path.exists(LOG_FILE):
                logger.info(f"Opening log file: {LOG_FILE}")
                os.startfile(LOG_FILE) if os.name == 'nt' else None
            else:
                messagebox.showinfo("No Log", "Log file not found")
        
        def copy_log():
            content = self.log_display.get('1.0', 'end')
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            logger.info("Log copied to clipboard")
            self.status.config(text="✅ Log copied to clipboard")
        
        tk.Button(ctrl, text="🗑️ Clear Display", command=clear_log,
                  bg='#e74c3c', fg='white', font=('Arial', 9),
                  padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Button(ctrl, text="📂 Open Log File", command=open_log_file,
                  bg='#3498db', fg='white', font=('Arial', 9),
                  padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Button(ctrl, text="📋 Copy Log", command=copy_log,
                  bg='#9b59b6', fg='white', font=('Arial', 9),
                  padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Label(ctrl, text=f"Log file: {LOG_FILE}", bg='white', font=('Arial', 8), fg='gray').pack(side='right', padx=10)
        
        # Log display
        self.log_display = scrolledtext.ScrolledText(log_f, height=30, width=100, font=('Courier', 9), wrap='word', bg='#1e1e1e', fg='#00ff00')
        self.log_display.pack(fill='both', expand=True, pady=5)
        
        # Initial log message
        self.log_to_ui("Application started - ready to track actions")
        self.log_to_ui(f"Log file: {LOG_FILE}")
        self.log_to_ui("All your actions will be logged here for debugging")

# ===== RUN =====
if __name__ == "__main__":
    try:
        logger.info("Creating main window")
        root = tk.Tk()
        app = SPARKSPHEARApp(root)
        logger.info("Starting main event loop")
        root.mainloop()
    except Exception as e:
        logger.critical(f"Fatal error: {e}\n{traceback.format_exc()}")
        raise
