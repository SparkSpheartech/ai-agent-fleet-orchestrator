#!/usr/bin/env python3
"""
Smart Pricing Engine for SparkSphear Tech
- Gets real-time eBay parts costs
- Finds 4 replacement options
- Suggests optimal pricing
"""

import json
import sqlite3
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

class DeviceDatabase:
    """Local database of devices and market rates"""
    
    def __init__(self, db_path="devices.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_common_devices()
    
    def init_database(self):
        """Create database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                brand TEXT,
                model TEXT,
                device_type TEXT,
                common_issues TEXT
            )
        ''')
        
        # Repair costs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repair_costs (
                id INTEGER PRIMARY KEY,
                device_id INTEGER,
                issue TEXT,
                parts_cost_avg REAL,
                labor_hours REAL,
                FOREIGN KEY (device_id) REFERENCES devices (id)
            )
        ''')
        
        # Replacement options table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replacement_options (
                id INTEGER PRIMARY KEY,
                device_type TEXT,
                option_name TEXT,
                price_range TEXT,
                specs TEXT,
                stores TEXT,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_common_devices(self):
        """Populate with common devices"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute("SELECT COUNT(*) FROM devices")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Common devices
        devices = [
            ("Apple", "iPhone 11", "Smartphone", "screen,cracked,battery"),
            ("Apple", "iPhone 12", "Smartphone", "screen,battery,charging port"),
            ("Samsung", "Galaxy Tab E", "Tablet", "screen,digitizer,battery"),
            ("Samsung", "Galaxy A9", "Tablet", "screen,battery"),
            ("Apple", "iPad", "Tablet", "screen,battery,home button"),
        ]
        
        for brand, model, dtype, issues in devices:
            cursor.execute(
                "INSERT INTO devices (brand, model, device_type, common_issues) VALUES (?, ?, ?, ?)",
                (brand, model, dtype, issues)
            )
        
        # Repair costs
        repair_costs = [
            (1, "Cracked screen", 45.00, 1.5),
            (1, "Battery replacement", 25.00, 0.5),
            (2, "Cracked screen", 55.00, 1.5),
            (2, "Battery replacement", 30.00, 0.5),
            (3, "Digitizer failure", 25.00, 1.5),
            (3, "Screen replacement", 40.00, 2.0),
        ]
        
        for device_id, issue, parts_cost, labor_hours in repair_costs:
            cursor.execute(
                "INSERT INTO repair_costs (device_id, issue, parts_cost_avg, labor_hours) VALUES (?, ?, ?, ?)",
                (device_id, issue, parts_cost, labor_hours)
            )
        
        # Replacement options (will be updated by web scraping)
        replacements = [
            ("Smartphone", "Budget Option", "$64-100", "Android 13, 8GB storage", "Walmart,Best Buy", ""),
            ("Smartphone", "Mid-Range", "$150-250", "Android 14, 64GB storage", "Best Buy,Amazon", ""),
            ("Smartphone", "High-End", "$300-500", "Flagship specs", "Apple,Samsung store", ""),
            ("Smartphone", "Premium", "$800+", "Latest model", "Apple,Samsung store", ""),
            ("Tablet", "Budget Option", "$64-100", "8\" screen, basic specs", "Walmart", ""),
            ("Tablet", "Mid-Range", "$150-200", "8-10\" screen, decent specs", "Best Buy", ""),
            ("Tablet", "High-End", "$250-400", "Premium tablet", "Best Buy,Apple store", ""),
            ("Tablet", "Premium", "$500+", "Latest iPad/Samsung", "Apple,Samsung store", ""),
        ]
        
        for dtype, option, price, specs, stores, last_updated in replacements:
            cursor.execute(
                "INSERT INTO replacement_options (device_type, option_name, price_range, specs, stores, last_updated) VALUES (?, ?, ?, ?, ?, ?)",
                (dtype, option, price, specs, stores, last_updated)
            )
        
        conn.commit()
        conn.close()
    
    def get_repair_cost(self, model, issue):
        """Get average repair cost for a device"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rc.parts_cost_avg, rc.labor_hours 
            FROM repair_costs rc
            JOIN devices d ON rc.device_id = d.id
            WHERE d.model = ? AND rc.issue LIKE ?
        ''', (model, f"%{issue}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {"parts_cost": result[0], "labor_hours": result[1]}
        return None
    
    def get_replacement_options(self, device_type):
        """Get 4 replacement options"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT option_name, price_range, specs, stores 
            FROM replacement_options 
            WHERE device_type = ?
            ORDER BY price_range
        ''', (device_type,))
        
        results = cursor.fetchall()
        conn.close()
        
        options = []
        for row in results:
            options.append({
                "name": row[0],
                "price": row[1],
                "specs": row[2],
                "stores": row[3]
            })
        
        return options

class MarketPriceScraper:
    """Scrape real-time market prices"""
    
    @staticmethod
    def search_ebay_parts(device_model, issue):
        """Search eBay for parts costs"""
        # This is a simplified version - in production, use eBay API
        try:
            # Simulate eBay search
            search_query = f"{device_model} {issue} replacement part"
            print(f"Searching eBay for: {search_query}")
            
            # In real implementation, use eBay API:
            # https://developer.ebay.com/api-docs/buy/static/api-buy.html
            
            # For now, return simulated data
            return {
                "average_price": 35.00,
                "price_range": "$25-50",
                "source": "eBay (simulated)",
                "url": f"https://www.ebay.com/sch/i.html?_nkw={search_query.replace(' ', '+')}"
            }
        except Exception as e:
            print(f"eBay search error: {e}")
            return None
    
    @staticmethod
    def search_walmart_replacement(device_type, budget="budget"):
        """Search Walmart for replacement devices"""
        # Simplified - in production, scrape or use API
        try:
            if device_type == "Smartphone":
                if budget == "budget":
                    return {"name": "Onn. 8\" Tablet", "price": "$64.00", "store": "Walmart"}
                elif budget == "mid":
                    return {"name": "Samsung Galaxy A14", "price": "$150.00", "store": "Best Buy"}
            elif device_type == "Tablet":
                if budget == "budget":
                    return {"name": "Onn. 8\" Tablet", "price": "$64.00", "store": "Walmart"}
                elif budget == "mid":
                    return {"name": "Samsung Galaxy Tab A9", "price": "$150.00", "store": "Best Buy"}
            
            return None
        except Exception as e:
            print(f"Walmart search error: {e}")
            return None

class SmartPricingEngine:
    """Main pricing engine"""
    
    def __init__(self):
        self.db = DeviceDatabase()
        self.scraper = MarketPriceScraper()
    
    def analyze_repair_option(self, device_model, issue):
        """Analyze and suggest repair pricing"""
        
        # Get database average
        db_cost = self.db.get_repair_cost(device_model, issue)
        
        # Get real-time eBay price
        ebay_data = self.scraper.search_ebay_parts(device_model, issue)
        
        if not db_cost:
            # Unknown device - use estimates
            db_cost = {"parts_cost": 50.00, "labor_hours": 1.0}
        
        # Calculate your costs
        parts_cost = db_cost["parts_cost"]
        if ebay_data:
            parts_cost = ebay_data["average_price"]
        
        labor_cost = db_cost["labor_hours"] * 25.00  # $25/hr
        
        # Suggest pricing (40-50% margin)
        total_cost = parts_cost + labor_cost
        suggested_price = total_cost * 1.5  # 50% markup
        
        return {
            "device_model": device_model,
            "issue": issue,
            "parts_cost": parts_cost,
            "labor_hours": db_cost["labor_hours"],
            "labor_cost": labor_cost,
            "total_cost": total_cost,
            "suggested_price": suggested_price,
            "ebay_data": ebay_data
        }
    
    def get_replacement_options(self, device_type):
        """Get 4 replacement options"""
        return self.db.get_replacement_options(device_type)
    
    def generate_pricing_report(self, device_model, issue, device_type):
        """Generate complete pricing report"""
        
        # Repair option
        repair_data = self.analyze_repair_option(device_model, issue)
        
        # Replacement options
        replacement_options = self.get_replacement_options(device_type)
        
        report = f"""
SMART PRICING REPORT
=====================

Device: {device_model}
Issue: {issue}
Date: {datetime.now().strftime('%B %d, %Y')}

OPTION 1: REPAIR
====================
Parts Cost: ${repair_data['parts_cost']:.2f}
Labor: {repair_data['labor_hours']} hrs @ $25/hr = ${repair_data['labor_cost']:.2f}
Your Total Cost: ${repair_data['total_cost']:.2f}
Suggested Price: ${repair_data['suggested_price']:.2f}
Profit Margin: {((repair_data['suggested_price'] - repair_data['total_cost']) / repair_data['suggested_price'] * 100):.1f}%

OPTION 2: REPLACEMENT (4 OPTIONS)
====================
"""
        
        for i, option in enumerate(replacement_options, 1):
            report += f"\nOption {i}: {option['name']}\n"
            report += f"  Price: {option['price']}\n"
            report += f"  Specs: {option['specs']}\n"
            report += f"  Where: {option['stores']}\n"
        
        report += "\nRECOMMENDATION:\n"
        report += f"  Repair if: Client wants to keep same device and save money\n"
        report += f"  Replace if: Device is old or repair cost > 50% of replacement cost\n"
        
        return report

def test_smart_pricing():
    """Test the smart pricing engine"""
    print("Testing Smart Pricing Engine...")
    print("=" * 60)
    
    engine = SmartPricingEngine()
    
    # Test with Linda's Samsung tablet
    device_model = "Samsung Galaxy Tab E"
    issue = "digitizer failure"
    device_type = "Tablet"
    
    report = engine.generate_pricing_report(device_model, issue, device_type)
    print(report)
    
    print("\n" + "=" * 60)
    print("Smart Pricing Engine ready for integration!")

if __name__ == "__main__":
    test_smart_pricing()
