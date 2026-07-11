#!/usr/bin/env python3
"""
SparkSphear Tech - Client Workflow App with Auto Distance Calculation
Base Location: 1427 Park Ave, Fort Wayne, IN 46807
Uses OpenStreetMap APIs (free, no key needed)
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
import math
from datetime import datetime

# Try to import requests, otherwise use urllib
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Note: requests not installed. Using urllib (slower).")

class GeoCoder:
    """Free geocoding using OpenStreetMap Nominatim"""
    
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    HEADERS = {'User-Agent': 'SparkSphearTech/1.0 (sparksphear4me@gmail.com)'}
    
    @staticmethod
    def geocode(address):
        """
        Geocode an address to (lat, lon)
        Returns: (latitude, longitude) or None
        """
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
        """
        Get driving distance between two points in miles
        Returns: distance in miles or None
        """
        try:
            # OSRM expects lon,lat format
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
                    # Distance is in meters, convert to miles
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

class SparkSphearApp:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SparkSphear Tech - Client Workflow")
        self.root.geometry("1100x850")
        self.root.configure(bg='#f0f0f0')
        
        # Base location (your home/office)
        self.base_address = "1427 Park Ave, Fort Wayne, IN 46807"
        self.base_coords = None  # Will be set after geocoding
        
        # Data storage
        self.devices = []
        self.current_client = {}
        self.client_folder = ""
        
        # Google Drive path
        self.base_path = r"G:\My Drive\SparkSphear_Core\04_Clients\Clients\SPARKSPHEAR TECH SUPPORT"
        
        # Create widgets
        self.create_widgets()
        
        # Geocode base address on startup
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
            text="⚡ SparkSphear Tech - Client Workflow (Auto Distance)",
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
        stage_frame = tk.LabelFrame(left_panel, text="📍 Workflow Stage", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
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
        
        # Client Info with Auto-Distance
        client_frame = tk.LabelFrame(left_panel, text="👤 Client Information & Auto-Distance", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        client_frame.pack(fill='x', padx=10, pady=10)
        
        # Base address (read-only)
        tk.Label(client_frame, text="Your Base:", bg='white', font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.base_display = tk.Entry(client_frame, width=40, state='readonly')
        self.base_display.insert(0, self.base_address)
        self.base_display.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Client address
        tk.Label(client_frame, text="Client Address:*", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.client_address = tk.Entry(client_frame, width=40)
        self.client_address.grid(row=1, column=1, pady=5, padx=(10, 0))
        self.client_address.bind('<FocusOut>', self.auto_calculate_distance)
        
        # Calculate distance button
        calc_btn = tk.Button(client_frame, text="📍 Calculate Distance", command=self.calculate_distance, bg='#3498db', fg='white', font=('Arial', 9, 'bold'), padx=10, pady=5)
        calc_btn.grid(row=2, column=1, pady=5, padx=(10, 0), sticky='e')
        
        # Distance display
        self.distance_label = tk.Label(client_frame, text="Distance: Not calculated", font=('Arial', 10, 'bold'), fg='blue', bg='white')
        self.distance_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Auto-filled fields
        tk.Label(client_frame, text="Client Name:*", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.client_name = tk.Entry(client_frame, width=40)
        self.client_name.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Phone:*", bg='white').grid(row=5, column=0, sticky='w', pady=5)
        self.client_phone = tk.Entry(client_frame, width=40)
        self.client_phone.grid(row=5, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Email:", bg='white').grid(row=6, column=0, sticky='w', pady=5)
        self.client_email = tk.Entry(client_frame, width=40)
        self.client_email.grid(row=6, column=1, pady=5, padx=(10, 0))
        
        # Miles (auto-filled, but editable)
        tk.Label(client_frame, text="Round-Trip Miles:", bg='white').grid(row=7, column=0, sticky='w', pady=5)
        self.miles_var = tk.StringVar(value="")
        self.miles_entry = tk.Entry(client_frame, textvariable=self.miles_var, width=15, state='readonly')
        self.miles_entry.grid(row=7, column=1, pady=5, padx=(10, 0), sticky='w')
        
        self.travel_cost_label = tk.Label(client_frame, text="Trip Fee: $0.00", font=('Arial', 10, 'bold'), fg='green', bg='white')
        self.travel_cost_label.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Device Entry
        device_frame = tk.LabelFrame(left_panel, text="📱 Add Device", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
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
        
        tk.Label(device_frame, text="Parts Cost ($):", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.parts_cost = tk.Entry(device_frame, width=15)
        self.parts_cost.grid(row=3, column=1, pady=5, padx=(10, 0), sticky='w')
        
        tk.Label(device_frame, text="Option:", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.device_option = tk.StringVar(value="repair")
        tk.Radiobutton(device_frame, text="Repair", variable=self.device_option, value="repair", bg='white').grid(row=4, column=1, sticky='w', padx=(10, 0))
        tk.Radiobutton(device_frame, text="Replace", variable=self.device_option, value="replace", bg='white').grid(row=4, column=1, sticky='e')
        
        add_device_btn = tk.Button(device_frame, text="➕ Add Device", command=self.add_device, bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=5)
        add_device_btn.grid(row=5, column=0, columnspan=2, pady=15)
        
        tk.Label(device_frame, text="Devices Added:", font=('Arial', 10, 'bold'), bg='white').grid(row=6, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.devices_listbox = tk.Listbox(device_frame, height=4, width=60)
        self.devices_listbox.grid(row=7, column=0, columnspan=2, pady=5)
        
        # ===== RIGHT PANEL =====
        
        # Action Buttons
        action_frame = tk.Frame(right_panel, bg='white')
        action_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(action_frame, text="⚡ Actions", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        create_folder_btn = tk.Button(action_frame, text="📁 Create Client Folder", command=self.create_client_folder, bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        create_folder_btn.pack(fill='x', pady=3)
        
        gen_initial_btn = tk.Button(action_frame, text="📄 Generate INITIAL Quote", command=lambda: self.generate_quote("initial"), bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        gen_initial_btn.pack(fill='x', pady=3)
        
        gen_work_btn = tk.Button(action_frame, text="📄 Generate WORK ORDER", command=lambda: self.generate_quote("work_order"), bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        gen_work_btn.pack(fill='x', pady=3)
        
        view_quote_btn = tk.Button(action_frame, text="👁️ View Latest Quote", command=self.view_latest_quote, bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        view_quote_btn.pack(fill='x', pady=3)
        
        open_folder_btn = tk.Button(action_frame, text="📂 Open Client Folder", command=self.open_client_folder, bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        open_folder_btn.pack(fill='x', pady=3)
        
        # Quote Preview
        preview_frame = tk.LabelFrame(right_panel, text="📄 Quote Preview", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.quote_preview = ScrolledText(preview_frame, height=35, width=70, font=('Courier', 9), wrap='word', state='disabled')
        self.quote_preview.pack(fill='both', expand=True)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready - Geocoding base address...", bd=1, relief='sunken', anchor='w', bg='#ecf0f1')
        self.status_bar.pack(side='bottom', fill='x')
    
    def auto_calculate_distance(self, event=None):
        """Auto-calculate distance when address field loses focus"""
        address = self.client_address.get().strip()
        if address and len(address) > 10:  # Minimum address length
            self.calculate_distance()
    
    def calculate_distance(self):
        """Calculate driving distance from base to client"""
        client_address = self.client_address.get().strip()
        
        if not client_address:
            messagebox.showwarning("Missing Address", "Please enter client address")
            return
        
        if not self.base_coords:
            messagebox.showerror("Base Location Error", "Base address not geocoded yet.\nPlease wait or restart app.")
            return
        
        self.status_bar.config(text="Calculating distance...")
        self.root.update()
        
        # Geocode client address
        client_coords = GeoCoder.geocode(client_address)
        
        if not client_coords:
            messagebox.showerror("Geocoding Failed", f"Could not find address:\n{client_address}\n\nTry adding city/state.")
            self.status_bar.config(text="Geocoding failed")
            return
        
        # Calculate driving distance
        distance_miles = RouteCalculator.get_driving_distance(
            self.base_coords[0], self.base_coords[1],
            client_coords[0], client_coords[1]
        )
        
        if distance_miles is None:
            messagebox.showerror("Routing Failed", "Could not calculate driving route.")
            self.status_bar.config(text="Routing failed")
            return
        
        # Round trip
        round_trip = distance_miles * 2
        
        # Update UI
        self.miles_var.set(f"{round_trip:.1f}")
        self.distance_label.config(text=f"Distance: {distance_miles:.1f} mi one-way → {round_trip:.1f} mi round-trip")
        
        # Auto-calculate trip fee
        trip_fee = PricingCalculator.calculate_trip_fee(round_trip)
        self.travel_cost_label.config(text=f"Trip Fee: ${trip_fee:.2f}")
        
        self.status_bar.config(text=f"Distance calculated: {round_trip:.1f} miles round-trip")
    
    def update_stage(self):
        """Update workflow stage"""
        stage = self.workflow_stage.get()
        stage_text = dict([
            ("initial_contact", "Initial Contact"),
            ("home_visit", "Home Visit - Diagnosis"),
            ("quote_presented", "Quote Presented"),
            ("approved", "Approved - Creating Work Order"),
            ("in_progress", "Work In Progress"),
            ("completed", "Work Completed"),
            ("closed", "Paid & Closed")
        ]).get(stage, "Unknown")
        
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
            parts = float(self.parts_cost.get()) if self.parts_cost.get() else 0.0
        except ValueError:
            messagebox.showwarning("Invalid Input", "Labor hours and parts cost must be numbers")
            return
        
        device = {
            'type': device_type,
            'issue': issue,
            'labor_hours': labor,
            'parts_cost': parts,
            'option': self.device_option.get()
        }
        
        self.devices.append(device)
        
        display_text = f"{device_type} - {issue} ({device['option']}) - Labor: {labor}hrs"
        if parts > 0:
            display_text += f", Parts: ${parts:.2f}"
        self.devices_listbox.insert('end', display_text)
        
        # Clear inputs
        self.device_issue.delete(0, 'end')
        self.parts_cost.delete(0, 'end')
        self.labor_hours.delete(0, 'end')
        self.labor_hours.insert(0, '1.0')
        
        self.status_bar.config(text=f"Added {device_type} to list ({len(self.devices)} total)")
    
    def create_client_folder(self):
        """Create client folder in Google Drive path"""
        client_name = self.client_name.get().strip()
        
        if not client_name:
            messagebox.showwarning("Missing Name", "Please enter client name first")
            return
        
        # Sanitize folder name
        safe_name = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        
        # Build path
        self.client_folder = os.path.join(self.base_path, safe_name)
        
        try:
            # Create main folder
            os.makedirs(self.client_folder, exist_ok=True)
            
            # Create subfolders
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
            
            # Create client info file
            info_file = os.path.join(self.client_folder, "client_info.txt")
            with open(info_file, 'w') as f:
                f.write(f"Client Name: {client_name}\n")
                f.write(f"Phone: {self.client_phone.get()}\n")
                f.write(f"Address: {self.client_address.get()}\n")
                f.write(f"Email: {self.client_email.get()}\n")
                f.write(f"Distance from Base: {self.miles_var.get()} miles\n")
                f.write(f"Base Address: {self.base_address}\n")
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Workflow Stage: {self.workflow_stage.get()}\n")
            
            messagebox.showinfo("Success", f"Client folder created:\n{self.client_folder}\n\nSubfolders: {len(subfolders)}")
            self.status_bar.config(text=f"Folder created: {safe_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder:\n{str(e)}")
    
    def generate_quote(self, quote_type):
        """Generate quote (text-based for now)"""
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
        try:
            miles = float(self.miles_var.get())
        except ValueError:
            miles = 20.0
        
        trip_fee = PricingCalculator.calculate_trip_fee(miles)
        diagnosis_fee = PricingCalculator.DIAGNOSIS_FEE if quote_type == "initial" else 0
        
        # Build quote data
        quote_data = {
            'client_name': client_name,
            'client_phone': self.client_phone.get(),
            'client_address': self.client_address.get(),
            'client_email': self.client_email.get(),
            'trip_fee': trip_fee,
            'diagnosis_fee': diagnosis_fee,
            'devices': self.devices,
            'quote_type': quote_type,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'distance_miles': miles,
            'base_address': self.base_address
        }
        
        # Calculate total
        total = trip_fee + diagnosis_fee
        for device in self.devices:
            if device['option'] == 'repair':
                total += PricingCalculator.calculate_repair_cost(device['labor_hours'], device['parts_cost'])
        
        quote_data['total'] = total
        
        # Determine output folder
        if quote_type == "initial":
            output_folder = os.path.join(self.client_folder, "01_Initial_Contact")
        else:
            output_folder = os.path.join(self.client_folder, "03_Work_Orders")
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{quote_type}_{client_name.replace(' ', '_')}_{timestamp}.txt"
        output_path = os.path.join(output_folder, filename)
        
        # Generate text quote
        quote_text = self.format_quote_text(quote_data)
        
        with open(output_path, 'w') as f:
            f.write(quote_text)
        
        # Update preview
        self.quote_preview.config(state='normal')
        self.quote_preview.delete('1.0', 'end')
        self.quote_preview.insert('1.0', quote_text)
        self.quote_preview.config(state='disabled')
        
        self.status_bar.config(text=f"Quote generated: {filename}")
        messagebox.showinfo("Success", f"Quote saved to:\n{output_path}")
        
        # Save quote data as JSON
        json_path = output_path.replace('.txt', '.json')
        with open(json_path, 'w') as f:
            json.dump(quote_data, f, indent=2)
    
    def format_quote_text(self, quote_data):
        """Format quote as text"""
        lines = []
        lines.append("=" * 70)
        lines.append("  SPARKSPHEAR TECH - REPAIR QUOTE")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Date: {quote_data['date']}")
        lines.append(f"Client: {quote_data['client_name']}")
        lines.append(f"Address: {quote_data['client_address']}")
        lines.append(f"Phone: {quote_data['client_phone']}")
        lines.append(f"Base: {quote_data['base_address']}")
        lines.append(f"Distance: {quote_data['distance_miles']:.1f} miles round-trip")
        lines.append("")
        lines.append("-" * 70)
        lines.append("MANDATORY FEES")
        lines.append("-" * 70)
        lines.append(f"  Service Call Fee:    ${quote_data['trip_fee']:.2f}")
        lines.append(f"  (based on {quote_data['distance_miles']:.1f} miles round-trip)")
        lines.append(f"  Diagnosis Fee:        ${quote_data['diagnosis_fee']:.2f}")
        if quote_data['quote_type'] == 'work_order':
            lines.append("  (Diagnosis fee waived - approved repair)")
        lines.append("")
        lines.append("-" * 70)
        lines.append("DEVICES")
        lines.append("-" * 70)
        
        for i, device in enumerate(quote_data['devices'], 1):
            lines.append(f"  Device {i}: {device['type']}")
            lines.append(f"    Issue: {device['issue']}")
            lines.append(f"    Option: {device['option']}")
            if device['option'] == 'repair':
                repair_cost = PricingCalculator.calculate_repair_cost(device['labor_hours'], device['parts_cost'])
                lines.append(f"    Repair Cost: ${repair_cost:.2f}")
            lines.append("")
        
        lines.append("-" * 70)
        lines.append(f"TOTAL: ${quote_data['total']:.2f}")
        lines.append("-" * 70)
        lines.append("")
        lines.append("Payment: Cash, Card, Venmo, CashApp")
        lines.append("Warranty: 30 days labor, 90 days parts")
        lines.append("Quote valid for 7 days")
        lines.append("")
        lines.append("=" * 70)
        lines.append("  Thank you for choosing SparkSphear Tech!")
        lines.append("=" * 70)
        
        return '\n'.join(lines)
    
    def view_latest_quote(self):
        """Open latest quote"""
        if not self.client_folder:
            messagebox.showwarning("No Folder", "Please create client folder first")
            return
        
        # Find latest txt/pdf in subfolders
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
            else:
                subprocess.call(['open', latest_file])
            
            self.status_bar.config(text=f"Opened: {os.path.basename(latest_file)}")
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
            else:
                subprocess.call(['open', self.client_folder])
            
            self.status_bar.config(text=f"Opened folder: {os.path.basename(self.client_folder)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder:\n{str(e)}")

def main():
    """Main entry point"""
    root = tk.Tk()
    app = SparkSphearApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
