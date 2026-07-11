#!/usr/bin/env python3
"""
SparkSphear Tech - Complete Client Workflow App
With PDF generation and Google Drive integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import subprocess

# PDF generation
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: fpdf not installed. PDF features disabled.")

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
    
    @staticmethod
    def calculate_replace_cost(device_cost, include_setup=True, include_data_transfer=False):
        sourcing = PricingCalculator.SOURCING_FEE
        device = device_cost * PricingCalculator.DEVICE_MARKUP_MIN
        setup = PricingCalculator.SETUP_FEE if include_setup else 0
        data_transfer = PricingCalculator.DATA_TRANSFER_FEE if include_data_transfer else 0
        return sourcing + device + setup + data_transfer

class PDFGenerator:
    """Generate PDF quotes and invoices"""
    
    @staticmethod
    def generate_quote_pdf(quote_data, output_path, quote_type="initial"):
        """Generate PDF for quote"""
        if not PDF_AVAILABLE:
            messagebox.showerror("PDF Error", "fpdf library not installed.\nRun: pip install fpdf2")
            return False
        
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "SPARKSPHEAR TECH", ln=True, align="C")
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 5, "Fort Wayne, IN | (260) 267-0641 | sparksphear4me@gmail.com", ln=True, align="C")
            pdf.ln(5)
            
            # Quote type
            pdf.set_font("Arial", "B", 14)
            if quote_type == "initial":
                pdf.cell(0, 10, "INITIAL CONTACT QUOTE", ln=True, align="C")
            else:
                pdf.cell(0, 10, "WORK ORDER / FINAL QUOTE", ln=True, align="C")
            pdf.ln(5)
            
            # Client info
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 7, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True)
            pdf.cell(0, 7, f"Client: {quote_data.get('client_name', 'N/A')}", ln=True)
            pdf.cell(0, 7, f"Address: {quote_data.get('client_address', 'N/A')}", ln=True)
            pdf.cell(0, 7, f"Phone: {quote_data.get('client_phone', 'N/A')}", ln=True)
            pdf.ln(5)
            
            # Quote details
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "SERVICES & PRICING", ln=True)
            pdf.ln(2)
            
            # Table header
            pdf.set_font("Arial", "B", 10)
            pdf.cell(80, 7, "Description", border=1, align="C")
            pdf.cell(30, 7, "Qty/Hrs", border=1, align="C")
            pdf.cell(40, 7, "Rate", border=1, align="C")
            pdf.cell(40, 7, "Amount", border=1, align="C")
            pdf.ln()
            
            # Trip fee
            pdf.set_font("Arial", "", 10)
            pdf.cell(80, 7, "Service Call (Trip Fee)", border=1)
            pdf.cell(30, 7, "1", border=1, align="C")
            pdf.cell(40, 7, f"${quote_data.get('trip_fee', 0):.2f}", border=1, align="R")
            pdf.cell(40, 7, f"${quote_data.get('trip_fee', 0):.2f}", border=1, align="R")
            pdf.ln()
            
            # Diagnosis
            if quote_data.get('diagnosis_fee', 0) > 0:
                pdf.cell(80, 7, "Diagnosis Fee", border=1)
                pdf.cell(30, 7, "1", border=1, align="C")
                pdf.cell(40, 7, f"${quote_data.get('diagnosis_fee', 0):.2f}", border=1, align="R")
                pdf.cell(40, 7, f"${quote_data.get('diagnosis_fee', 0):.2f}", border=1, align="R")
                pdf.ln()
            
            # Devices
            for i, device in enumerate(quote_data.get('devices', []), 1):
                desc = f"Device {i}: {device.get('type', '')} - {device.get('issue', '')}"
                labor_cost = device.get('labor_hours', 1) * 25  # Assuming $25/hr
                parts_cost = device.get('parts_cost', 0) * 1.25
                
                pdf.cell(80, 7, desc[:50], border=1)
                pdf.cell(30, 7, f"{device.get('labor_hours', 1)} hrs", border=1, align="C")
                pdf.cell(40, 7, "$25/hr", border=1, align="R")
                pdf.cell(40, 7, f"${labor_cost:.2f}", border=1, align="R")
                pdf.ln()
                
                if parts_cost > 0:
                    pdf.cell(80, 7, f"  + Parts (25% markup)", border=1)
                    pdf.cell(30, 7, "1", border=1, align="C")
                    pdf.cell(40, 7, f"${device.get('parts_cost', 0):.2f} -> ${parts_cost:.2f}", border=1, align="R")
                    pdf.cell(40, 7, f"${parts_cost:.2f}", border=1, align="R")
                    pdf.ln()
            
            # Total
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"TOTAL: ${quote_data.get('total', 0):.2f}", ln=True, align="R")
            
            # Footer
            pdf.ln(10)
            pdf.set_font("Arial", "I", 9)
            pdf.cell(0, 5, "Payment: Cash, Card, Venmo, CashApp", ln=True)
            pdf.cell(0, 5, "Warranty: 30 days labor, 90 days parts", ln=True)
            pdf.cell(0, 5, "Quote valid for 7 days", ln=True)
            
            # Save
            pdf.output(output_path)
            return True
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            return False

class SparkSphearApp:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SparkSphear Tech - Client Workflow")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.devices = []
        self.current_client = {}
        self.client_folder = ""
        
        # Google Drive path
        self.base_path = r"G:\My Drive\SparkSphear_Core\04_Clients\Clients\SPARKSPHEAR TECH SUPPORT"
        
        # Create widgets
        self.create_widgets()
        
        # Check PDF support
        if not PDF_AVAILABLE:
            messagebox.showwarning("PDF Support", "Install fpdf2 for PDF features:\npip install fpdf2")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="⚡ SparkSphear Tech - Client Workflow Manager",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Client & Device Input
        left_panel = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Workflow & Output
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
        
        # Client Info
        client_frame = tk.LabelFrame(left_panel, text="👤 Client Information", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        client_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(client_frame, text="Name:*", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.client_name = tk.Entry(client_frame, width=30)
        self.client_name.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Phone:*", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.client_phone = tk.Entry(client_frame, width=30)
        self.client_phone.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Address:*", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.client_address = tk.Entry(client_frame, width=30)
        self.client_address.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Email:", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.client_email = tk.Entry(client_frame, width=30)
        self.client_email.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Miles (round-trip):*", bg='white').grid(row=4, column=0, sticky='w', pady=5)
        self.miles_var = tk.StringVar(value="20")
        self.miles_spinbox = tk.Spinbox(client_frame, from_=1, to=200, textvariable=self.miles_var, width=10)
        self.miles_spinbox.grid(row=4, column=1, pady=5, padx=(10, 0), sticky='w')
        
        self.travel_cost_label = tk.Label(client_frame, text="Trip Fee: $35.00", font=('Arial', 10, 'bold'), fg='blue', bg='white')
        self.travel_cost_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.miles_spinbox.config(command=self.update_travel_cost)
        self.miles_var.trace('w', self.update_travel_cost)
        
        # Device Entry
        device_frame = tk.LabelFrame(left_panel, text="📱 Add Device", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        device_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(device_frame, text="Type:", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.device_type = ttk.Combobox(device_frame, values=['Smartphone', 'Tablet', 'Laptop', 'Desktop', 'Game Console', 'Other'], width=27, state='readonly')
        self.device_type.set('Smartphone')
        self.device_type.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        tk.Label(device_frame, text="Issue:*", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.device_issue = tk.Entry(device_frame, width=30)
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
        
        self.devices_listbox = tk.Listbox(device_frame, height=4, width=50)
        self.devices_listbox.grid(row=7, column=0, columnspan=2, pady=5)
        
        # ===== RIGHT PANEL =====
        
        # Action Buttons
        action_frame = tk.Frame(right_panel, bg='white')
        action_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(action_frame, text="⚡ Actions", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        create_folder_btn = tk.Button(action_frame, text="📁 Create Client Folder", command=self.create_client_folder, bg='#3498db', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        create_folder_btn.pack(fill='x', pady=3)
        
        gen_initial_btn = tk.Button(action_frame, text="📄 Generate INITIAL Quote (PDF)", command=lambda: self.generate_quote("initial"), bg='#2ecc71', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        gen_initial_btn.pack(fill='x', pady=3)
        
        gen_work_btn = tk.Button(action_frame, text="📄 Generate WORK ORDER (PDF)", command=lambda: self.generate_quote("work_order"), bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        gen_work_btn.pack(fill='x', pady=3)
        
        view_quote_btn = tk.Button(action_frame, text="👁️ View Latest Quote", command=self.view_latest_quote, bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        view_quote_btn.pack(fill='x', pady=3)
        
        open_folder_btn = tk.Button(action_frame, text="📂 Open Client Folder", command=self.open_client_folder, bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=8)
        open_folder_btn.pack(fill='x', pady=3)
        
        # Quote Preview
        preview_frame = tk.LabelFrame(right_panel, text="📄 Quote Preview", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.quote_preview = ScrolledText(preview_frame, height=30, width=60, font=('Courier', 9), wrap='word', state='disabled')
        self.quote_preview.pack(fill='both', expand=True)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready - Enter client info and add devices", bd=1, relief='sunken', anchor='w', bg='#ecf0f1')
        self.status_bar.pack(side='bottom', fill='x')
    
    def update_travel_cost(self, *args):
        """Update travel cost display"""
        try:
            miles = float(self.miles_var.get())
            cost = PricingCalculator.calculate_trip_fee(miles)
            self.travel_cost_label.config(text=f"Trip Fee: ${cost:.2f}")
        except ValueError:
            self.travel_cost_label.config(text="Trip Fee: $0.00")
    
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
                f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Workflow Stage: {self.workflow_stage.get()}\n")
            
            messagebox.showinfo("Success", f"Client folder created:\n{self.client_folder}\n\nSubfolders: {len(subfolders)}")
            self.status_bar.config(text=f"Folder created: {safe_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create folder:\n{str(e)}")
    
    def generate_quote(self, quote_type):
        """Generate quote PDF"""
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
            'date': datetime.now().strftime('%Y-%m-%d')
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
        filename = f"{quote_type}_{client_name.replace(' ', '_')}_{timestamp}.pdf"
        output_path = os.path.join(output_folder, filename)
        
        # Generate PDF
        if PDF_AVAILABLE:
            success = PDFGenerator.generate_quote_pdf(quote_data, output_path, quote_type)
            if success:
                self.status_bar.config(text=f"PDF generated: {filename}")
                messagebox.showinfo("Success", f"PDF quote generated:\n{output_path}")
                
                # Update preview
                self.update_quote_preview(quote_data)
            else:
                messagebox.showerror("Error", "Failed to generate PDF")
        else:
            # Fallback to text file
            text_path = output_path.replace('.pdf', '.txt')
            with open(text_path, 'w') as f:
                f.write(self.format_quote_text(quote_data))
            messagebox.showinfo("PDF Not Available", f"Text quote generated:\n{text_path}")
        
        # Save quote data as JSON
        json_path = output_path.replace('.pdf', '.json')
        with open(json_path, 'w') as f:
            json.dump(quote_data, f, indent=2)
    
    def format_quote_text(self, quote_data):
        """Format quote as text (fallback)"""
        lines = []
        lines.append("=" * 60)
        lines.append("  SPARKSPHEAR TECH - REPAIR QUOTE")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Date: {quote_data['date']}")
        lines.append(f"Client: {quote_data['client_name']}")
        lines.append(f"Address: {quote_data['client_address']}")
        lines.append(f"Phone: {quote_data['client_phone']}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("MANDATORY FEES")
        lines.append("-" * 60)
        lines.append(f"  Service Call Fee:    ${quote_data['trip_fee']:.2f}")
        lines.append(f"  Diagnosis Fee:        ${quote_data['diagnosis_fee']:.2f}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("DEVICES")
        lines.append("-" * 60)
        
        for i, device in enumerate(quote_data['devices'], 1):
            lines.append(f"  Device {i}: {device['type']}")
            lines.append(f"    Issue: {device['issue']}")
            lines.append(f"    Option: {device['option']}")
            lines.append("")
        
        lines.append("-" * 60)
        lines.append(f"TOTAL: ${quote_data['total']:.2f}")
        lines.append("-" * 60)
        
        return '\n'.join(lines)
    
    def update_quote_preview(self, quote_data):
        """Update quote preview text"""
        text = self.format_quote_text(quote_data)
        
        self.quote_preview.config(state='normal')
        self.quote_preview.delete('1.0', 'end')
        self.quote_preview.insert('1.0', text)
        self.quote_preview.config(state='disabled')
    
    def view_latest_quote(self):
        """Open latest quote PDF"""
        if not self.client_folder:
            messagebox.showwarning("No Folder", "Please create client folder first")
            return
        
        # Find latest PDF in subfolders
        found_files = []
        for root, dirs, files in os.walk(self.client_folder):
            for file in files:
                if file.endswith('.pdf'):
                    found_files.append(os.path.join(root, file))
        
        if not found_files:
            messagebox.showinfo("No Quotes", "No PDF quotes found for this client")
            return
        
        # Open most recent
        latest_file = max(found_files, key=os.path.getmtime)
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(latest_file)
            else:
                subprocess.call(['open', latest_file])
            
            self.status_bar.config(text=f"Opened: {os.path.basename(latest_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
    
    def open_client_folder(self):
        """Open client folder in file explorer"""
        if not self.client_folder:
            messagebox.showwarning("No Folder", "Please create client folder first")
            return
        
        try:
            if os.name == 'nt':  # Windows
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
