#!/usr/bin/env python3
"""
SparkSphear Tech - Complete Client Workflow App
WITH Integrated Diagnostic Report Generator
Base Location: 1427 Park Ave, Fort Wayne, IN 46807
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import json
import os
import subprocess
import urllib.parse
import urllib.request
import json
from datetime import datetime

# Smart Pricing Engine
from smart_pricing_engine import SmartPricingEngine, DeviceDatabase

# Try to import fpdf for PDF generation
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Note: fpdf not installed. Install with: pip install fpdf2")

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

class PricingCalculator:
    """Core pricing logic"""
    
    BASE_TRIP_FEE = 35.00
    BASE_MILES = 15
    PER_MILE_RATE = 0.67
    DIAGNOSIS_FEE = 25.00
    HOURLY_LABOR = 25.00
    PARTS_MARKUP = 1.25
    MIN_LABOR_HOURS = 1.0
    
    SOURCING_FEE = 15.00
    DEVICE_MARKUP_MIN = 1.15
    DEVICE_MARKUP_MAX = 1.20
    SETUP_FEE = 20.00
    DATA_TRANSFER_FEE = 30.00
    
    @staticmethod
    def calculate_trip_fee(round_trip_miles):
        if round_trip_miles <= PricingCalculator.BASE_MILES:
            return PricingCalculator.BASE_TRIP_FEE
        else:
            extra_miles = round_trip_miles - PricingCalculator.BASE_MILES
            return PricingCalculator.BASE_TRIP_FEE + (extra_miles * PricingCalculator.PER_MILE_RATE)
    
    @staticmethod
    def calculate_repair_cost(labor_hours, parts_cost):
        labor = max(labor_hours, PricingCalculator.MIN_LABOR_HOURS) * PricingCalculator.HOURLY_LABOR
        parts = parts_cost * PricingCalculator.PARTS_MARKUP
        return labor + parts

class DiagnosticReportGenerator:
    """Generate professional diagnostic reports like Linda Samsung quote"""
    
    @staticmethod
    def generate_pdf(report_data, output_path):
        """Generate PDF diagnostic report"""
        if not PDF_AVAILABLE:
            return DiagnosticReportGenerator.generate_text(report_data, output_path.replace('.pdf', '.txt'))
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "SparkSphear Tech Solutions", ln=True, align="C")
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 5, "260-267-0641  |  sparksphear4me@gmail.com", ln=True, align="C")
            pdf.cell(0, 5, "Mon-Fri, 8:00 AM - 5:00 PM", ln=True, align="C")
            pdf.ln(10)
            
            # Title
            pdf.set_font("Arial", "B", 14)
            title = f"{report_data['device_model']} — Device Assessment & Repair Options"
            pdf.cell(0, 10, title, ln=True, align="C")
            pdf.ln(5)
            
            # Prepared for/by
            pdf.set_font("Arial", "", 11)
            pdf.cell(40, 7, "PREPARED FOR:", ln=False)
            pdf.cell(0, 7, report_data['client_name'], ln=True)
            pdf.cell(40, 7, "DATE:", ln=False)
            pdf.cell(0, 7, datetime.now().strftime('%B %d, %Y'), ln=True)
            pdf.cell(40, 7, "PREPARED BY:", ln=False)
            pdf.cell(0, 7, "Shazaly M - SparkSphear Tech Solutions", ln=True)
            pdf.ln(5)
            
            # Executive Summary
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "01  EXECUTIVE SUMMARY", ln=True, fill=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, report_data['executive_summary'])
            pdf.ln(5)
            
            # Diagnostic Findings
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "02  DIAGNOSTIC FINDINGS", ln=True, fill=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, f"Device: {report_data['device_model']}", ln=True)
            pdf.cell(0, 6, f"Issue: {report_data['issue']}", ln=True)
            pdf.cell(0, 6, f"Root cause: {report_data['root_cause']}", ln=True)
            pdf.ln(3)
            
            # Checkmarks for findings
            for finding in report_data.get('findings', []):
                pdf.cell(10, 6, "[]", ln=False)
                pdf.cell(0, 6, finding, ln=True)
            pdf.ln(5)
            
            # Repair Option
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "03  REPAIR OPTION - COST BREAKDOWN", ln=True, fill=True)
            pdf.ln(3)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, f"What needs to be done: {report_data['repair_description']}")
            pdf.ln(3)
            
            # Cost table
            pdf.set_font("Arial", "B", 10)
            pdf.cell(80, 7, "ITEM", border=1, align="C")
            pdf.cell(60, 7, "NOTES", border=1, align="C")
            pdf.cell(50, 7, "COST", border=1, align="C")
            pdf.ln()
            
            pdf.set_font("Arial", "", 10)
            for item in report_data.get('repair_items', []):
                pdf.cell(80, 6, item['name'], border=1)
                pdf.cell(60, 6, item['notes'], border=1)
                pdf.cell(50, 6, f"${item['cost']:.2f}", border=1, align="R")
                pdf.ln()
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(140, 7, "TOTAL REPAIR COST", border=1, align="R")
            pdf.cell(50, 7, f"${report_data['repair_total']:.2f}", border=1, align="R")
            pdf.ln(10)
            
            # Save PDF
            pdf.output(output_path)
            return True
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            return False
    
    @staticmethod
    def generate_text(report_data, output_path):
        """Generate text version as fallback"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"  {report_data['device_model']} - DEVICE ASSESSMENT & REPAIR OPTIONS")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Prepared for: {report_data['client_name']}")
        lines.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        lines.append(f"Prepared by: Shazaly M - SparkSphear Tech Solutions")
        lines.append("")
        lines.append("-" * 70)
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 70)
        lines.append(report_data['executive_summary'])
        lines.append("")
        lines.append("-" * 70)
        lines.append("DIAGNOSTIC FINDINGS")
        lines.append("-" * 70)
        lines.append(f"Device: {report_data['device_model']}")
        lines.append(f"Issue: {report_data['issue']}")
        lines.append(f"Root cause: {report_data['root_cause']}")
        lines.append("")
        for finding in report_data.get('findings', []):
            lines.append(f"  [] {finding}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("REPAIR OPTION - COST BREAKDOWN")
        lines.append("-" * 70)
        lines.append(f"What needs to be done: {report_data['repair_description']}")
        lines.append("")
        lines.append("ITEM                    NOTES                    COST")
        lines.append("-" * 70)
        for item in report_data.get('repair_items', []):
            lines.append(f"{item['name']:<25} {item['notes']:<25} ${item['cost']:.2f}")
        lines.append("-" * 70)
        lines.append(f"TOTAL REPAIR COST: ${report_data['repair_total']:.2f}")
        lines.append("=" * 70)
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return True

class DiagnosticWizard(tk.Toplevel):
    """Wizard window for creating diagnostic reports"""
    
    def __init__(self, parent, client_data):
        super().__init__(parent)
        self.title("Diagnostic Report Wizard")
        self.geometry("800x900")
        self.client_data = client_data
        self.report_data = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create wizard widgets"""
        
        # Title
        title = tk.Label(self, text="Diagnostic Report Wizard", font=('Arial', 16, 'bold'))
        title.pack(pady=10)
        
        # Create notebook for sections
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Section 1: Device Info
        frame1 = tk.Frame(notebook)
        notebook.add(frame1, text="Device Info")
        
        tk.Label(frame1, text="Device Model:*").grid(row=0, column=0, sticky='w', pady=5)
        self.device_model = tk.Entry(frame1, width=50)
        self.device_model.grid(row=0, column=1, pady=5)
        
        tk.Label(frame1, text="Issue:*").grid(row=1, column=0, sticky='w', pady=5)
        self.issue = tk.Entry(frame1, width=50)
        self.issue.grid(row=1, column=1, pady=5)
        
        tk.Label(frame1, text="Root Cause:*").grid(row=2, column=0, sticky='w', pady=5)
        self.root_cause = tk.Entry(frame1, width=50)
        self.root_cause.grid(row=2, column=1, pady=5)
        
        # Section 2: Executive Summary
        frame2 = tk.Frame(notebook)
        notebook.add(frame2, text="Executive Summary")
        
        tk.Label(frame2, text="Explain the issue in plain language:").pack(anchor='w', pady=5)
        self.executive_summary = ScrolledText(frame2, height=15, width=80)
        self.executive_summary.pack(fill='both', expand=True, pady=5)
        
        # Section 3: Findings
        frame3 = tk.Frame(notebook)
        notebook.add(frame3, text="Diagnostic Findings")
        
        tk.Label(frame3, text="Check all that apply:").pack(anchor='w', pady=5)
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
            cb = tk.Checkbutton(frame3, text=finding, variable=var)
            cb.pack(anchor='w', pady=2)
            self.finding_vars.append((finding, var))
        
        # Section 4: Repair Cost
        frame4 = tk.Frame(notebook)
        notebook.add(frame4, text="Repair Cost Breakdown")
        
        tk.Label(frame4, text="Repair Description:").grid(row=0, column=0, sticky='w', pady=5)
        self.repair_description = tk.Entry(frame4, width=50)
        self.repair_description.grid(row=0, column=1, pady=5)
        
        tk.Label(frame4, text="Repair Items (JSON format):").grid(row=1, column=0, sticky='nw', pady=5)
        self.repair_items_text = ScrolledText(frame4, height=10, width=60)
        self.repair_items_text.grid(row=1, column=1, pady=5)
        self.repair_items_text.insert('1.0', '[\n  {"name": "Part name", "notes": "Source/notes", "cost": 25.00}\n]')
        
        # Generate button
        generate_btn = tk.Button(self, text="Generate Diagnostic Report", 
                               command=self.generate_report, 
                               bg='#27ae60', fg='white', 
                               font=('Arial', 12, 'bold'),
                               padx=30, pady=10)
        generate_btn.pack(pady=20)
    
    def generate_report(self):
        """Generate the diagnostic report"""
        
        # Collect data
        self.report_data = {
            'client_name': self.client_data.get('name', 'Client'),
            'device_model': self.device_model.get(),
            'issue': self.issue.get(),
            'root_cause': self.root_cause.get(),
            'executive_summary': self.executive_summary.get('1.0', 'end'),
            'findings': [f[0] for f in self.finding_vars if f[1].get()],
            'repair_description': self.repair_description.get(),
            'repair_items': json.loads(self.repair_items_text.get('1.0', 'end')),
            'repair_total': sum(item['cost'] for item in json.loads(self.repair_items_text.get('1.0', 'end')))
        }
        
        # Determine output path
        if self.client_data.get('folder'):
            output_folder = os.path.join(self.client_data['folder'], "02_Quotes")
            os.makedirs(output_folder, exist_ok=True)
            output_path = os.path.join(output_folder, f"Diagnostic_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        else:
            output_path = f"Diagnostic_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Generate PDF
        success = DiagnosticReportGenerator.generate_pdf(self.report_data, output_path)
        
        if success:
            messagebox.showinfo("Success", f"Diagnostic report generated:\n{output_path}")
            try:
                if os.name == 'nt':
                    os.startfile(output_path)
            except:
                pass
        else:
            messagebox.showerror("Error", "Failed to generate report")

class SparkSphearApp:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SparkSphear Tech - Client Workflow")
        self.root.geometry("1100x850")
        self.root.configure(bg='#f0f0f0')
        
        # Base location
        self.base_address = "1427 Park Ave, Fort Wayne, IN 46807"
        self.base_coords = None
        
        # Data storage
        self.devices = []
        self.current_client = {}
        self.client_folder = ""
        
        # Google Drive path
        self.base_path = r"G:\My Drive\SparkSphear_Core\04_Clients\Clients\SPARKSPHEAR TECH SUPPORT"
        
        # Create widgets
        self.create_widgets()
        
        # Geocode base address
        self.geocode_base_address()
    
    def geocode_base_address(self):
        """Geocode the base address on startup"""
        self.status_bar.config(text="Geocoding base address: 1427 Park Ave...")
        self.root.update()
        
        coords = GeoCoder.geocode(self.base_address)
        if coords:
            self.base_coords = coords
            self.base_lat_label.config(text=f"Base: {coords[0]:.4f}, {coords[1]:.4f}")
            self.status_bar.config(text="Base address geocoded successfully")
        else:
            self.base_lat_label.config(text="Base: Geocoding failed - using default")
            self.status_bar.config(text="Warning: Could not geocode base address")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=70)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="SparkSphear Tech - Client Workflow + Diagnostics",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Base location display
        self.base_lat_label = tk.Label(
            title_frame,
            text="Base: Geocoding...",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        self.base_lat_label.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel
        left_panel = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel
        right_panel = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # ===== LEFT PANEL =====
        
        # Workflow Stage
        stage_frame = tk.LabelFrame(left_panel, text="Workflow Stage", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        stage_frame.pack(fill='x', padx=10, pady=10)
        
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
            tk.Radiobutton(stage_frame, text=text, variable=self.workflow_stage, 
                          value=value, bg='white', command=self.update_stage).pack(anchor='w', pady=2)
        
        # Client Info
        client_frame = tk.LabelFrame(left_panel, text="Client Information", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        client_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(client_frame, text="Your Base:", bg='white', font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.base_display = tk.Entry(client_frame, width=40, state='readonly')
        self.base_display.insert(0, self.base_address)
        self.base_display.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Client Address:*", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.client_address = tk.Entry(client_frame, width=40)
        self.client_address.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.client_address.bind('<FocusOut>', self.auto_calculate_distance)
        
        tk.Label(client_frame, text="Client Name:*", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.client_name = tk.Entry(client_frame, width=40)
        self.client_name.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Phone:*", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.client_phone = tk.Entry(client_frame, width=40)
        self.client_phone.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Calculate distance button
        calc_btn = tk.Button(client_frame, text="Calculate Distance", command=self.calculate_distance, bg='#3498db', fg='white', font=('Arial', 9, 'bold'), padx=10, pady=5)
        calc_btn.grid(row=4, column=1, pady=5, padx=(10, 0), sticky='e')
        
        self.distance_label = tk.Label(client_frame, text="Distance: Not calculated", font=('Arial', 10, 'bold'), fg='blue', bg='white')
        self.distance_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Device Entry
        device_frame = tk.LabelFrame(left_panel, text="Add Device", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        device_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(device_frame, text="Type:", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.device_type = ttk.Combobox(device_frame, values=['Smartphone', 'Tablet', 'Laptop', 'Desktop', 'Game Console', 'Other'], width=37, state='readonly')
        self.device_type.set('Smartphone')
        self.device_type.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        tk.Label(device_frame, text="Issue:*", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.device_issue = tk.Entry(device_frame, width=40)
        self.device_issue.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        tk.Label(device_frame, text="Labor (hrs):", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.labor_hours = tk.Spinbox(device_frame, from_=0.5, to=10, increment=0.5, width=10)
        self.labor_hours.delete(0, 'end')
        self.labor_hours.insert(0, '1.0')
        self.labor_hours.grid(row=2, column=1, pady=5, padx=(10, 0), sticky='w')
        
        add_device_btn = tk.Button(device_frame, text="Add Device", command=self.add_device, bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=5)
        add_device_btn.grid(row=3, column=0, columnspan=2, pady=15)
        
        self.devices_listbox = tk.Listbox(device_frame, height=4, width=60)
        self.devices_listbox.grid(row=4, column=0, columnspan=2, pady=5)
        
        # ===== RIGHT PANEL =====
        
        # Action Buttons
        action_frame = tk.Frame(right_panel, bg='white')
        action_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(action_frame, text="Actions", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        # Main actions
        create_folder_btn = tk.Button(action_frame, text="Create Client Folder", command=self.create_client_folder, bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        create_folder_btn.pack(fill='x', pady=3)
        
        gen_quote_btn = tk.Button(action_frame, text="Generate Basic Quote", command=lambda: self.generate_quote("basic"), bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        gen_quote_btn.pack(fill='x', pady=3)
        
        # NEW: Diagnostic Report button
        diag_btn = tk.Button(action_frame, text="Generate Diagnostic Report", command=self.open_diagnostic_wizard, bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        diag_btn.pack(fill='x', pady=3)
        
        view_btn = tk.Button(action_frame, text="View Latest Quote", command=self.view_latest_quote, bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        view_btn.pack(fill='x', pady=3)
        
        open_folder_btn = tk.Button(action_frame, text="Open Client Folder", command=self.open_client_folder, bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        open_folder_btn.pack(fill='x', pady=3)
        
        # Quote Preview
        preview_frame = tk.LabelFrame(right_panel, text="Quote Preview", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.quote_preview = ScrolledText(preview_frame, height=35, width=70, font=('Courier', 9), wrap='word', state='disabled')
        self.quote_preview.pack(fill='both', expand=True)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready - Geocoding base address...", bd=1, relief='sunken', anchor='w', bg='#ecf0f1')
        self.status_bar.pack(side='bottom', fill='x')
    
    def open_diagnostic_wizard(self):
        """Open the diagnostic report wizard"""
        if not self.client_name.get().strip():
            messagebox.showwarning("Missing Info", "Please enter client name first")
            return
        
        client_data = {
            'name': self.client_name.get(),
            'folder': self.client_folder
        }
        
        wizard = DiagnosticWizard(self.root, client_data)
        self.root.wait_window(wizard)
    
    def auto_calculate_distance(self, event=None):
        """Auto-calculate distance when address field loses focus"""
        address = self.client_address.get().strip()
        if address and len(address) > 10:
            self.calculate_distance()
    
    def calculate_distance(self):
        """Calculate driving distance from base to client"""
        client_address = self.client_address.get().strip()
        
        if not client_address:
            messagebox.showwarning("Missing Address", "Please enter client address")
            return
        
        if not self.base_coords:
            messagebox.showerror("Base Location Error", "Base address not geocoded yet.")
            return
        
        self.status_bar.config(text="Calculating distance...")
        self.root.update()
        
        client_coords = GeoCoder.geocode(client_address)
        
        if not client_coords:
            messagebox.showerror("Geocoding Failed", f"Could not find address:\n{client_address}")
            self.status_bar.config(text="Geocoding failed")
            return
        
        distance_miles = RouteCalculator.get_driving_distance(
            self.base_coords[0], self.base_coords[1],
            client_coords[0], client_coords[1]
        )
        
        if distance_miles is None:
            messagebox.showerror("Routing Failed", "Could not calculate driving route.")
            self.status_bar.config(text="Routing failed")
            return
        
        round_trip = distance_miles * 2
        self.distance_label.config(text=f"Distance: {distance_miles:.1f} mi one-way → {round_trip:.1f} mi round-trip")
        
        trip_fee = PricingCalculator.calculate_trip_fee(round_trip)
        self.status_bar.config(text=f"Distance calculated: {round_trip:.1f} miles round-trip, Trip Fee: ${trip_fee:.2f}")
    
    def update_stage(self):
        """Update workflow stage"""
        stage = self.workflow_stage.get()
        stage_text = {
            "initial_contact": "Initial Contact",
            "home_visit": "Home Visit - Diagnosis",
            "quote_presented": "Quote Presented",
            "approved": "Approved - Creating Work Order",
            "in_progress": "Work In Progress",
            "completed": "Work Completed",
            "closed": "Paid & Closed"
        }.get(stage, "Unknown")
        
        self.status_bar.config(text=f"Workflow Stage: {stage_text}")
    
    def add_device(self):
        """Add device to list"""
        device_type = self.device_type.get()
        issue = self.device_issue.get()
        
        if not issue:
            messagebox.showwarning("Missing Info", "Please enter the device issue")
            return
        
        try:
            labor = float(self.labor_hours.get())
        except ValueError:
            labor = 1.0
        
        device = {
            'type': device_type,
            'issue': issue,
            'labor_hours': labor
        }
        
        self.devices.append(device)
        
        display_text = f"{device_type} - {issue} - Labor: {labor}hrs"
        self.devices_listbox.insert('end', display_text)
        
        self.device_issue.delete(0, 'end')
        self.labor_hours.delete(0, 'end')
        self.labor_hours.insert(0, '1.0')
        
        self.status_bar.config(text=f"Added {device_type} to list ({len(self.devices)} total)")
    
    def create_client_folder(self):
        """Create client folder in Google Drive path"""
        client_name = self.client_name.get().strip()
        
        if not client_name:
            messagebox.showwarning("Missing Name", "Please enter client name first")
            return
        
        safe_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        self.client_folder = os.path.join(self.base_path, safe_name)
        
        try:
            os.makedirs(self.client_folder, exist_ok=True)
            
            subfolders = [
                "01_Initial_Contact",
                "02_Quotes",
                "03_Work_Orders",
                "04_Invoices",
                "05_Completed",
                "06_Communication"
            ]
            
            for subfolder in subfolders:
                os.makedirs(os.path.join(self.client_folder, subfolder), exist_ok=True)
            
            messagebox.showinfo("Success", f"Client folder created:\n{self.client_folder}")
            self.status_bar.config(text=f"Folder created: {safe_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder:\n{str(e)}")
    
    def generate_quote(self, quote_type):
        """Generate basic quote"""
        if not self.devices:
            messagebox.showwarning("No Devices", "Please add at least one device")
            return
        
        client_name = self.client_name.get().strip()
        if not client_name:
            messagebox.showwarning("Missing Name", "Please enter client name")
            return
        
        if not self.client_folder:
            messagebox.showwarning("No Folder", "Please create client folder first")
            return
        
        # Calculate costs
        trip_fee = 35.00  # Default
        diagnosis_fee = PricingCalculator.DIAGNOSIS_FEE if quote_type == "initial" else 0
        
        # Build quote text
        quote_text = f"""
SPARKSPHEAR TECH - {quote_type.upper()} QUOTE
=================================================

Client: {client_name}
Phone: {self.client_phone.get()}
Address: {self.client_address.get()}
Date: {datetime.now().strftime('%B %d, %Y')}

MANDATORY FEES:
  Service Call Fee: ${trip_fee:.2f}
  Diagnosis Fee: ${diagnosis_fee:.2f}

DEVICES:
"""
        
        total = trip_fee + diagnosis_fee
        
        for i, device in enumerate(self.devices, 1):
            quote_text += f"\n  Device {i}: {device['type']}\n"
            quote_text += f"    Issue: {device['issue']}\n"
            quote_text += f"    Labor: {device['labor_hours']} hrs @ $25/hr = ${device['labor_hours'] * 25:.2f}\n"
            total += device['labor_hours'] * 25
        
        quote_text += f"\nTOTAL: ${total:.2f}\n"
        quote_text += "="*50 + "\n"
        
        # Save quote
        output_folder = os.path.join(self.client_folder, "02_Quotes")
        os.makedirs(output_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{quote_type}_quote_{client_name.replace(' ', '_')}_{timestamp}.txt"
        output_path = os.path.join(output_folder, filename)
        
        with open(output_path, 'w') as f:
            f.write(quote_text)
        
        # Update preview
        self.quote_preview.config(state='normal')
        self.quote_preview.delete('1.0', 'end')
        self.quote_preview.insert('1.0', quote_text)
        self.quote_preview.config(state='disabled')
        
        self.status_bar.config(text=f"Quote generated: {filename}")
        messagebox.showinfo("Success", f"Quote saved to:\n{output_path}")
    
    def view_latest_quote(self):
        """Open latest quote"""
        if not self.client_folder:
            messagebox.showwarning("No Folder", "Please create client folder first")
            return
        
        found_files = []
        for root, dirs, files in os.walk(self.client_folder):
            for file in files:
                if file.endswith('.txt') or file.endswith('.pdf'):
                    found_files.append(os.path.join(root, file))
        
        if not found_files:
            messagebox.showinfo("No Quotes", "No quotes found for this client")
            return
        
        latest_file = max(found_files, key=os.path.getmtime)
        
        try:
            if os.name == 'nt':
                os.startfile(latest_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
    
    def open_client_folder(self):
        """Open client folder in file explorer"""
        if not self.client_folder:
            messagebox.showwarning("No Folder", "Please create client folder first")
            return
        
        try:
            if os.name == 'nt':
                subprocess.run(['explorer', self.client_folder])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = SparkSphearApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
