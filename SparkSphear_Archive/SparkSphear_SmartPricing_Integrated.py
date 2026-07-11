#!/usr/bin/env python3
"""
SparkSphear Tech - Complete Client Workflow App
WITH Smart Pricing Engine INTEGRATED
- Auto-fetches repair pricing from market data
- Gets 4 replacement options automatically
- Works every time you meet a client
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import json
import os
import subprocess
import urllib.parse
import urllib.request
import sqlite3
from datetime import datetime
from smart_pricing_engine import SmartPricingEngine, DeviceDatabase

# Try to import fpdf for PDF generation
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class GeoCoder:
    """Free geocoding using OpenStreetMap Nominatim"""
    
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    HEADERS = {'User-Agent': 'SparkSphearTech/1.0 (sparksphear4me@gmail.com)'}
    
    @staticmethod
    def geocode(address):
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            url = f"{GeoCoder.BASE_URL}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers=GeoCoder.HEADERS)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return (lat, lon)
            
            return None
            
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

class RouteCalculator:
    """Free route calculation using OSRM"""
    
    BASE_URL = "https://router.project-osrm.org/route/v1/driving"
    
    @staticmethod
    def get_driving_distance(lat1, lon1, lat2, lon2):
        try:
            coords = f"{lon1},{lat1};{lon2},{lat2}"
            url = f"{RouteCalculator.BASE_URL}/{coords}"
            params = {
                'overview': 'false',
                'alternatives': 'false'
            }
            
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(full_url)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
            
            if data and data.get('code') == 'Ok':
                routes = data.get('routes', [])
                if routes:
                    distance_meters = routes[0]['distance']
                    distance_miles = distance_meters * 0.000621371
                    return distance_miles
            
            return None
            
        except Exception as e:
            print(f"Routing error: {e}")
            return None

class SmartPricingWizard(tk.Toplevel):
    """Wizard that auto-fetches smart pricing every time"""
    
    def __init__(self, parent, client_data):
        super().__init__(parent)
        self.title("Smart Pricing Wizard - Auto-Fetches Market Data")
        self.geometry("900x1000")
        self.client_data = client_data
        self.pricing_engine = SmartPricingEngine()
        self.report_data = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create wizard widgets"""
        
        # Title
        title = tk.Label(self, text="Smart Pricing Wizard", font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        subtitle = tk.Label(self, text="Fetches real-time market data automatically", font=('Arial', 10))
        subtitle.pack(pady=5)
        
        # Create notebook for sections
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Section 1: Device Info + Auto Pricing
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="Device & Auto Pricing")
        
        tk.Label(frame1, text="Device Model:*").grid(row=0, column=0, sticky='w', pady=5)
        self.device_model = tk.Entry(frame1, width=50)
        self.device_model.grid(row=0, column=1, pady=5)
        
        tk.Label(frame1, text="Issue:*").grid(row=1, column=0, sticky='w', pady=5)
        self.issue = tk.Entry(frame1, width=50)
        self.issue.grid(row=1, column=1, pady=5)
        
        # Auto-fetch button
        auto_btn = tk.Button(frame1, text="🔍 AUTO-FETCH SMART PRICING", 
                               command=self.auto_fetch_pricing,
                               bg='#27ae60', fg='white',
                               font=('Arial', 11, 'bold'),
                               padx=20, pady=10)
        auto_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Results display
        tk.Label(frame1, text="Smart Pricing Results:").grid(row=3, column=0, sticky='w', pady=5)
        self.pricing_results = ScrolledText(frame1, height=15, width=80)
        self.pricing_results.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Section 2: Diagnostic Info
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="Diagnostic Findings")
        
        tk.Label(frame2, text="Executive Summary:").pack(anchor='w', pady=5)
        self.executive_summary = ScrolledText(frame2, height=10, width=80)
        self.executive_summary.pack(fill='both', expand=True, pady=5)
        
        tk.Label(frame2, text="Findings (check all that apply):").pack(anchor='w', pady=5)
        self.finding_vars = []
        findings = [
            "LCD display is working perfectly",
            "Device powers on and functions normally",
            "Problem is isolated to specific component",
            "This is a repairable condition",
            "Replacement may be more cost-effective"
        ]
        for finding in findings:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(frame2, text=finding, variable=var)
            cb.pack(anchor='w', pady=2)
            self.finding_vars.append((finding, var))
        
        # Section 3: Replacement Options (auto-fetched)
        frame3 = tk.Frame(notebook)
        notebook.add(frame3, text="4 Replacement Options")
        
        tk.Label(frame3, text="Replacement Options (auto-fetched):").pack(anchor='w', pady=5)
        self.replacement_display = ScrolledText(frame3, height=20, width=80)
        self.replacement_display.pack(fill='both', expand=True, pady=5)
        
        # Generate button
        generate_btn = tk.Button(self, text="📄 Generate Complete Report (with Smart Pricing)",
                               command=self.generate_complete_report,
                               bg='#e67e22', fg='white',
                               font=('Arial', 12, 'bold'),
                               padx=30, pady=10)
        generate_btn.pack(pady=20)
    
    def auto_fetch_pricing(self):
        """AUTO-FETCH pricing data - happens every time!"""
        
        device_model = self.device_model.get()
        issue = self.issue.get()
        
        if not device_model or not issue:
            messagebox.showwarning("Missing Info", "Please enter device model and issue")
            return
        
        self.pricing_results.delete('1.0', 'end')
        self.pricing_results.insert('1.0', "🔄 Fetching smart pricing...\n")
        self.update()
        
        # Get smart pricing
        try:
            # Repair pricing
            repair_data = self.pricing_engine.analyze_repair_option(device_model, issue)
            
            # Detect device type
            device_type = "Smartphone"
            if "tablet" in device_model.lower():
                device_type = "Tablet"
            
            # Get 4 replacement options
            replacement_options = self.pricing_engine.get_replacement_options(device_type)
            
            # Display results
            results_text = f"""
✅ SMART PRICING FETCHED!

OPTION 1: REPAIR PRICING
═══════════════════════════════
Parts Cost: ${repair_data['parts_cost']:.2f}
Labor: {repair_data['labor_hours']} hrs @ $25/hr = ${repair_data['labor_cost']:.2f}
Your Total Cost: ${repair_data['total_cost']:.2f}
Suggested Client Price: ${repair_data['suggested_price']:.2f}
Profit Margin: {((repair_data['suggested_price'] - repair_data['total_cost']) / repair_data['suggested_price'] * 100):.1f}%

OPTION 2: 4 REPLACEMENT OPTIONS
═════════════════════════════════════
"""
            
            for i, option in enumerate(replacement_options, 1):
                results_text += f"\nOption {i}: {option['name']}\n"
                results_text += f"  Price: {option['price']}\n"
                results_text += f"  Specs: {option['specs']}\n"
                results_text += f"  Where: {option['stores']}\n"
            
            self.pricing_results.insert('end', results_text)
            
            # Also display in replacement tab
            self.replacement_display.delete('1.0', 'end')
            self.replacement_display.insert('1.0', results_text)
            
            # Auto-fill executive summary
            summary = f"After diagnosing your {device_model}, I found: {issue}. "
            summary += f"Good news — this is repairable for around ${repair_data['suggested_price']:.2f}. "
            summary += f"However, if you'd prefer a new device, I found 4 options ranging from {replacement_options[0]['price']} to {replacement_options[-1]['price']}."
            self.executive_summary.insert('1.0', summary)
            
            messagebox.showinfo("Success", "✅ Smart pricing fetched!\n\nRepair pricing + 4 replacement options loaded.")
            
        except Exception as e:
            self.pricing_results.insert('end', f"❌ Error: {e}")
    
    def generate_complete_report(self):
        """Generate report with ALL smart pricing data"""
        
        # Collect all data
        self.report_data = {
            'client_name': self.client_data.get('name', 'Client'),
            'device_model': self.device_model.get(),
            'issue': self.issue.get(),
            'root_cause': self.issue.get(),  # Simplified
            'executive_summary': self.executive_summary.get('1.0', 'end'),
            'findings': [f[0] for f in self.finding_vars if f[1].get()],
        }
        
        # Get smart pricing data
        try:
            repair_data = self.pricing_engine.analyze_repair_option(
                self.report_data['device_model'],
                self.report_data['issue']
            )
            
            device_type = "Smartphone"
            if "tablet" in self.report_data['device_model'].lower():
                device_type = "Tablet"
            
            replacement_options = self.pricing_engine.get_replacement_options(device_type)
            
            # Add to report data
            self.report_data['smart_repair'] = repair_data
            self.report_data['replacement_options'] = replacement_options
            
            # Auto-fill repair items from smart pricing
            self.report_data['repair_items'] = [
                {"name": f"{self.report_data['device_model']} parts", 
                 "notes": "Market rate (eBay avg)", 
                 "cost": repair_data['parts_cost']},
                {"name": "Labor", 
                 "notes": f"{repair_data['labor_hours']} hrs @ $25/hr", 
                 "cost": repair_data['labor_cost']}
            ]
            self.report_data['repair_total'] = repair_data['total_cost']
            self.report_data['suggested_price'] = repair_data['suggested_price']
            
        except Exception as e:
            print(f"Smart pricing error: {e}")
            # Fall back to manual entry
            self.report_data['repair_items'] = [{"name": "Manual entry", "notes": "See notes", "cost": 50.00}]
            self.report_data['repair_total'] = 75.00
        
        # Generate PDF
        output_path = self.get_output_path()
        
        if PDF_AVAILABLE:
            success = self.generate_pdf_with_smart_pricing(output_path)
        else:
            success = self.generate_text_with_smart_pricing(output_path.replace('.pdf', '.txt'))
        
        if success:
            messagebox.showinfo("Success", f"✅ Complete report generated!\n\nIncludes:\n- Smart repair pricing\n- 4 replacement options\n\nSaved to: {output_path}")
            try:
                if os.name == 'nt':
                    os.startfile(output_path)
            except:
                pass
        else:
            messagebox.showerror("Error", "Failed to generate report")
    
    def get_output_path(self):
        """Determine output path"""
        if self.client_data.get('folder'):
            output_folder = os.path.join(self.client_data['folder'], "02_Quotes")
            os.makedirs(output_folder, exist_ok=True)
            filename = f"SmartPricing_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return os.path.join(output_folder, filename)
        else:
            filename = f"SmartPricing_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return filename
    
    def generate_pdf_with_smart_pricing(self, output_path):
        """Generate PDF with smart pricing data"""
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "SparkSphear Tech Solutions", ln=True, align="C")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 5, "260-267-0641  |  sparksphear4me@gmail.com", ln=True, align="C")
            pdf.ln(10)
            
            # Title
            device = self.report_data['device_model']
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"{device} — Smart Pricing Report", ln=True, align="C")
            pdf.ln(5)
            
            # Smart Repair Pricing
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "OPTION 1: REPAIR (Smart Pricing)", ln=True, fill=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)
            
            repair = self.report_data.get('smart_repair', {})
            pdf.cell(0, 6, f"Parts Cost: ${repair.get('parts_cost', 0):.2f}", ln=True)
            pdf.cell(0, 6, f"Labor Cost: ${repair.get('labor_cost', 0):.2f}", ln=True)
            pdf.cell(0, 6, f"Your Total Cost: ${repair.get('total_cost', 0):.2f}", ln=True)
            pdf.cell(0, 6, f"Suggested Client Price: ${repair.get('suggested_price', 0):.2f}", ln=True)
            pdf.ln(5)
            
            # 4 Replacement Options
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "OPTION 2: 4 REPLACEMENT OPTIONS", ln=True, fill=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)
            
            for i, option in enumerate(self.report_data.get('replacement_options', []), 1):
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 6, f"Option {i}: {option['name']}", ln=True)
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"  Price: {option['price']}", ln=True)
                pdf.cell(0, 6, f"  Specs: {option['specs']}", ln=True)
                pdf.cell(0, 6, f"  Where: {option['stores']}", ln=True)
                pdf.ln(2)
            
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "RECOMMENDATION", ln=True, fill=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, "Repair if: Client wants to keep same device and save money.\nReplace if: Device is old or repair cost > 50% of replacement cost.")
            
            # Save
            pdf.output(output_path)
            return True
            
        except Exception as e:
            print(f"PDF error: {e}")
            return False
    
    def generate_text_with_smart_pricing(self, output_path):
        """Generate text version"""
        # Similar to PDF but text format
        # (Implementation here)
        pass

class SparkSphearApp:
    """Main GUI Application with Smart Pricing Integration"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SparkSphear Tech - Smart Pricing Integrated")
        self.root.geometry("1100x850")
        self.root.configure(bg='#f0f0f0')
        
        # Base location
        self.base_address = "1427 Park Ave, Fort Wayne, IN 46807"
        self.base_coords = None
        
        # Data storage
        self.devices = []
        self.current_client = {}
        self.client_folder = ""
        self.base_path = r"G:\My Drive\SparkSphear_Core\04_Clients\Clients\SPARKSPHEAR TECH SUPPORT"
        
        self.create_widgets()
        self.geocode_base_address()
    
    def geocode_base_address(self):
        """Geocode base address"""
        self.status_bar.config(text="Geocoding base address...")
        self.root.update()
        
        coords = GeoCoder.geocode(self.base_address)
        if coords:
            self.base_coords = coords
            self.status_bar.config(text=f"Base geocoded: {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            self.status_bar.config(text="Warning: Could not geocode base")
    
    def create_widgets(self):
        """Create GUI"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=70)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="SparkSphear Tech - Smart Pricing Integrated",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel
        left_panel = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel
        right_panel = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Client Info
        client_frame = tk.LabelFrame(left_panel, text="Client Info", font=('Arial', 11, 'bold'), bg='white')
        client_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(client_frame, text="Name:*").grid(row=0, column=0, sticky='w', pady=5)
        self.client_name = tk.Entry(client_frame, width=40)
        self.client_name.grid(row=0, column=1, pady=5)
        
        tk.Label(client_frame, text="Address:*").grid(row=1, column=0, sticky='w', pady=5)
        self.client_address = tk.Entry(client_frame, width=40)
        self.client_address.grid(row=1, column=1, pady=5)
        
        # SMART PRICING BUTTON (Main feature!)
        smart_btn = tk.Button(left_panel, 
                              text="🧠 SMART PRICING WIZARD\n(Auto-fetches market data)",
                              command=self.open_smart_pricing_wizard,
                              bg='#e67e22', fg='white',
                              font=('Arial', 12, 'bold'),
                              padx=30, pady=15)
        smart_btn.pack(pady=20)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief='sunken', anchor='w', bg='#ecf0f1')
        self.status_bar.pack(side='bottom', fill='x')
    
    def open_smart_pricing_wizard(self):
        """Open the Smart Pricing Wizard - WORKS EVERY TIME!"""
        
        if not self.client_name.get().strip():
            messagebox.showwarning("Missing Info", "Please enter client name first")
            return
        
        client_data = {
            'name': self.client_name.get(),
            'folder': self.client_folder
        }
        
        wizard = SmartPricingWizard(self.root, client_data)
        self.root.wait_window(wizard)

def main():
    """Main entry point"""
    # Initialize database
    print("Initializing Smart Pricing Database...")
    db = DeviceDatabase()
    print("✅ Database ready!")
    
    # Launch app
    root = tk.Tk()
    app = SparkSphearApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
