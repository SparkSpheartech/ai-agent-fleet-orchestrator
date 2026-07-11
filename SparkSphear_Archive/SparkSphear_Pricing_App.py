#!/usr/bin/env python3
"""
SparkSphear Tech - Mobile Repair Pricing Calculator
Desktop GUI Application for Home Visits
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import json
import os
from datetime import datetime
import math

class PricingCalculator:
    """Core pricing logic"""
    
    # Constants
    BASE_TRIP_FEE = 35.00
    BASE_MILES = 15
    PER_MILE_RATE = 0.67
    DIAGNOSIS_FEE = 25.00
    HOURLY_LABOR = 25.00
    PARTS_MARKUP = 1.25  # 25% markup
    MIN_LABOR_HOURS = 1.0
    
    # Replacement fees
    SOURCING_FEE = 15.00
    DEVICE_MARKUP_MIN = 1.15  # 15%
    DEVICE_MARKUP_MAX = 1.20  # 20%
    SETUP_FEE = 20.00
    DATA_TRANSFER_FEE = 30.00
    
    @staticmethod
    def calculate_trip_fee(round_trip_miles):
        """Calculate trip fee based on distance"""
        if round_trip_miles <= PricingCalculator.BASE_MILES:
            return PricingCalculator.BASE_TRIP_FEE
        else:
            extra_miles = round_trip_miles - PricingCalculator.BASE_MILES
            return PricingCalculator.BASE_TRIP_FEE + (extra_miles * PricingCalculator.PER_MILE_RATE)
    
    @staticmethod
    def calculate_repair_cost(labor_hours, parts_cost):
        """Calculate total repair cost"""
        labor = max(labor_hours, PricingCalculator.MIN_LABOR_HOURS) * PricingCalculator.HOURLY_LABOR
        parts = parts_cost * PricingCalculator.PARTS_MARKUP
        return labor + parts
    
    @staticmethod
    def calculate_replace_cost(device_cost, include_setup=True, include_data_transfer=False):
        """Calculate replacement cost"""
        sourcing = PricingCalculator.SOURCING_FEE
        device = device_cost * PricingCalculator.DEVICE_MARKUP_MIN  # Use 15% by default
        setup = PricingCalculator.SETUP_FEE if include_setup else 0
        data_transfer = PricingCalculator.DATA_TRANSFER_FEE if include_data_transfer else 0
        return sourcing + device + setup + data_transfer

class SparkSphearApp:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SparkSphear Tech - Pricing Calculator")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.devices = []
        self.current_quote = {}
        
        # Load saved data
        self.data_file = os.path.join(os.path.dirname(__file__), "pricing_data.json")
        self.load_data()
        
        # Create GUI
        self.create_widgets()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="⚡ SparkSphear Tech - Pricing Calculator",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Input
        left_panel = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right panel - Quote/Output
        right_panel = tk.Frame(main_container, bg='white', relief='raised', bd=2)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # ===== LEFT PANEL - INPUT =====
        
        # Client Info Section
        client_frame = tk.LabelFrame(left_panel, text="📋 Client Information", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        client_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(client_frame, text="Client Name:", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.client_name = tk.Entry(client_frame, width=30)
        self.client_name.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Address:", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.client_address = tk.Entry(client_frame, width=30)
        self.client_address.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        tk.Label(client_frame, text="Round-Trip Miles:", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.miles_var = tk.StringVar(value="20")
        self.miles_spinbox = tk.Spinbox(client_frame, from_=1, to=200, textvariable=self.miles_var, width=10)
        self.miles_spinbox.grid(row=2, column=1, pady=5, padx=(10, 0), sticky='w')
        
        # Travel cost display
        self.travel_cost_label = tk.Label(client_frame, text="Travel Cost: $0.00", font=('Arial', 10, 'bold'), fg='blue', bg='white')
        self.travel_cost_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Bind miles change
        self.miles_spinbox.config(command=self.update_travel_cost)
        self.miles_var.trace('w', self.update_travel_cost)
        
        # Devices Section
        devices_frame = tk.LabelFrame(left_panel, text="📱 Devices to Repair/Replace", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        devices_frame.pack(fill='x', padx=10, pady=10)
        
        # Device entry
        tk.Label(devices_frame, text="Device Type:", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.device_type = ttk.Combobox(devices_frame, values=['Smartphone', 'Tablet', 'Laptop', 'Desktop', 'Other'], width=27, state='readonly')
        self.device_type.set('Smartphone')
        self.device_type.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        tk.Label(devices_frame, text="Issue:", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.device_issue = tk.Entry(devices_frame, width=30)
        self.device_issue.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        tk.Label(devices_frame, text="Est. Labor (hrs):", bg='white').grid(row=2, column=0, sticky='w', pady=5)
        self.labor_hours = tk.Spinbox(devices_frame, from_=0.5, to=10, increment=0.5, width=10)
        self.labor_hours.delete(0, 'end')
        self.labor_hours.insert(0, '1.0')
        self.labor_hours.grid(row=2, column=1, pady=5, padx=(10, 0), sticky='w')
        
        tk.Label(devices_frame, text="Parts Cost ($):", bg='white').grid(row=3, column=0, sticky='w', pady=5)
        self.parts_cost = tk.Entry(devices_frame, width=15)
        self.parts_cost.grid(row=3, column=1, pady=5, padx=(10, 0), sticky='w')
        
        # Add device button
        add_device_btn = tk.Button(devices_frame, text="➕ Add Device", command=self.add_device, bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=5)
        add_device_btn.grid(row=4, column=0, columnspan=2, pady=15)
        
        # Device list
        tk.Label(devices_frame, text="Added Devices:", font=('Arial', 10, 'bold'), bg='white').grid(row=5, column=0, columnspan=2, sticky='w', pady=(10, 5))
        
        self.devices_listbox = tk.Listbox(devices_frame, height=4, width=50)
        self.devices_listbox.grid(row=6, column=0, columnspan=2, pady=5)
        
        # ===== RIGHT PANEL - OUTPUT =====
        
        # Quote Section
        quote_frame = tk.LabelFrame(right_panel, text="📄 Generated Quote", font=('Arial', 11, 'bold'), bg='white', padx=10, pady=10)
        quote_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Options radio buttons
        self.quote_option = tk.StringVar(value="both")
        options_frame = tk.Frame(quote_frame, bg='white')
        options_frame.pack(fill='x', pady=5)
        
        tk.Radiobutton(options_frame, text="Show Both Options", variable=self.quote_option, value="both", bg='white', command=self.generate_quote).pack(side='left', padx=5)
        tk.Radiobutton(options_frame, text="Repair Only", variable=self.quote_option, value="repair", bg='white', command=self.generate_quote).pack(side='left', padx=5)
        tk.Radiobutton(options_frame, text="Replace Only", variable=self.quote_option, value="replace", bg='white', command=self.generate_quote).pack(side='left', padx=5)
        
        # Quote text area
        self.quote_text = ScrolledText(quote_frame, height=25, width=50, font=('Courier', 9), wrap='word')
        self.quote_text.pack(fill='both', expand=True, pady=(10, 0))
        
        # Buttons at bottom
        button_frame = tk.Frame(right_panel, bg='white')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        generate_btn = tk.Button(button_frame, text="🔄 Generate Quote", command=self.generate_quote, bg='#3498db', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=10)
        generate_btn.pack(side='left', padx=5)
        
        save_btn = tk.Button(button_frame, text="💾 Save Quote", command=self.save_quote, bg='#2ecc71', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=10)
        save_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(button_frame, text="🗑️ Clear All", command=self.clear_all, bg='#e74c3c', fg='white', font=('Arial', 11, 'bold'), padx=20, pady=10)
        clear_btn.pack(side='right', padx=5)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief='sunken', anchor='w', bg='#ecf0f1')
        self.status_bar.pack(side='bottom', fill='x')
        
        # Initial calculations
        self.update_travel_cost()
    
    def update_travel_cost(self, *args):
        """Update travel cost display"""
        try:
            miles = float(self.miles_var.get())
            cost = PricingCalculator.calculate_trip_fee(miles)
            self.travel_cost_label.config(text=f"Travel Cost: ${cost:.2f}")
        except ValueError:
            self.travel_cost_label.config(text="Travel Cost: $0.00")
    
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
            'parts_cost': parts
        }
        
        self.devices.append(device)
        
        # Update listbox
        display_text = f"{device_type} - {issue} (Labor: {labor}hrs, Parts: ${parts:.2f})"
        self.devices_listbox.insert('end', display_text)
        
        # Clear inputs
        self.device_issue.delete(0, 'end')
        self.parts_cost.delete(0, 'end')
        self.labor_hours.delete(0, 'end')
        self.labor_hours.insert(0, '1.0')
        
        self.status_bar.config(text=f"Added {device_type} to list")
    
    def generate_quote(self):
        """Generate the pricing quote"""
        if not self.devices:
            messagebox.showwarning("No Devices", "Please add at least one device")
            return
        
        client_name = self.client_name.get() or "Valued Customer"
        client_address = self.client_address.get() or "Address not provided"
        
        try:
            miles = float(self.miles_var.get())
        except ValueError:
            miles = 20.0
        
        trip_fee = PricingCalculator.calculate_trip_fee(miles)
        diagnosis_fee = PricingCalculator.DIAGNOSIS_FEE
        
        # Build quote text
        quote = []
        quote.append("=" * 60)
        quote.append("  SPARKSPHEAR TECH - REPAIR QUOTE")
        quote.append("=" * 60)
        quote.append("")
        quote.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        quote.append(f"Client: {client_name}")
        quote.append(f"Address: {client_address}")
        quote.append(f"Distance: {miles:.0f} miles round-trip")
        quote.append("")
        quote.append("-" * 60)
        quote.append("MANDATORY FEES (Apply to all visits)")
        quote.append("-" * 60)
        quote.append(f"  Service Call Fee:    ${trip_fee:.2f}")
        quote.append(f"    (includes first {PricingCalculator.BASE_MILES} miles, ${PricingCalculator.PER_MILE_RATE}/mile after)")
        quote.append(f"  Diagnosis Fee:        ${diagnosis_fee:.2f}")
        quote.append(f"    (waived if you choose to repair with us)")
        quote.append("")
        
        option = self.quote_option.get()
        
        if option in ['both', 'repair']:
            quote.append("-" * 60)
            quote.append("OPTION 1: REPAIR YOUR DEVICES")
            quote.append("-" * 60)
            quote.append("")
            
            total_repair = 0
            for i, device in enumerate(self.devices, 1):
                quote.append(f"  Device {i}: {device['type']}")
                quote.append(f"    Issue: {device['issue']}")
                
                repair_cost = PricingCalculator.calculate_repair_cost(device['labor_hours'], device['parts_cost'])
                labor_cost = max(device['labor_hours'], PricingCalculator.MIN_LABOR_HOURS) * PricingCalculator.HOURLY_LABOR
                parts_cost = device['parts_cost'] * PricingCalculator.PARTS_MARKUP
                
                quote.append(f"    Labor: {device['labor_hours']} hrs × ${PricingCalculator.HOURLY_LABOR}/hr = ${labor_cost:.2f}")
                quote.append(f"    Parts: ${device['parts_cost']:.2f} + 25% markup = ${parts_cost:.2f}")
                quote.append(f"    Subtotal: ${repair_cost:.2f}")
                quote.append("")
                
                total_repair += repair_cost
            
            # Add trip/diagnosis to repair total
            total_with_fees = total_repair + trip_fee  # Diagnosis waived
            quote.append(f"  TOTAL REPAIR COST: ${total_with_fees:.2f}")
            quote.append(f"    (Includes trip fee, diagnosis waived)")
            quote.append("")
            quote.append("  Warranty: 30 days labor, 90 days on parts")
            quote.append("")
        
        if option in ['both', 'replace']:
            quote.append("-" * 60)
            quote.append("OPTION 2: REPLACE YOUR DEVICES")
            quote.append("-" * 60)
            quote.append("")
            quote.append("  I can source new or refurbished devices for you.")
            quote.append("")
            
            total_replace = 0
            for i, device in enumerate(self.devices, 1):
                quote.append(f"  Device {i}: {device['type']}")
                quote.append(f"    Issue: {device['issue']}")
                quote.append("")
                quote.append("    To provide a replacement quote, I need:")
                quote.append("    - Your desired specs (storage, RAM, etc.)")
                quote.append("    - New vs Refurbished preference")
                quote.append("")
                quote.append("    Fees if you choose this option:")
                quote.append(f"    - Sourcing Fee: ${PricingCalculator.SOURCING_FEE:.2f}")
                quote.append(f"    - Device Cost + 15-20% markup")
                quote.append(f"    - Setup/Delivery: ${PricingCalculator.SETUP_FEE:.2f}")
                quote.append(f"    - Data Transfer (optional): ${PricingCalculator.DATA_TRANSFER_FEE:.2f}")
                quote.append("")
            
            quote.append(f"  TOTAL REPLACE: Varies by device choice")
            quote.append(f"  (Includes trip fee + sourcing + setup)")
            quote.append("")
        
        quote.append("-" * 60)
        quote.append("RECOMMENDATION")
        quote.append("-" * 60)
        quote.append("")
        quote.append("  Based on the diagnosis:")
        
        # Simple recommendation logic
        for device in self.devices:
            if device['parts_cost'] > 150:
                quote.append(f"  - {device['type']}: Consider replacement (parts cost >$150)")
            else:
                quote.append(f"  - {device['type']}: Repair recommended (cost-effective)")
        
        quote.append("")
        quote.append("  Next Steps:")
        quote.append("  1. Approve this quote by signing below")
        quote.append("  2. I'll order parts (if repairing) or source device (if replacing)")
        quote.append("  3. Service completed within 2-5 business days")
        quote.append("")
        quote.append("-" * 60)
        quote.append("PAYMENT & CONTACT")
        quote.append("-" * 60)
        quote.append("")
        quote.append("  Payment Methods: Cash, Card, Venmo, CashApp")
        quote.append("  Contact: (260) 267-0641 | sparksphear4me@gmail.com")
        quote.append("")
        quote.append("  Client Approval:")
        quote.append("  Signature: _______________________  Date: ____________")
        quote.append("")
        quote.append("=" * 60)
        quote.append("  Thank you for choosing SparkSphear Tech!")
        quote.append("=" * 60)
        
        # Display quote
        self.quote_text.delete('1.0', 'end')
        self.quote_text.insert('1.0', '\n'.join(quote))
        
        # Save current quote
        self.current_quote = {
            'client': client_name,
            'address': client_address,
            'miles': miles,
            'devices': self.devices,
            'quote_text': '\n'.join(quote)
        }
        
        self.status_bar.config(text="Quote generated successfully")
    
    def save_quote(self):
        """Save quote to file"""
        if not hasattr(self, 'current_quote') or not self.current_quote:
            messagebox.showwarning("No Quote", "Please generate a quote first")
            return
        
        # Ask for save location
        filename = f"Quote_{self.current_quote['client'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.current_quote['quote_text'])
                
                # Also save to JSON for tracking
                json_filepath = os.path.join(os.path.dirname(__file__), "quotes.json")
                quotes = []
                if os.path.exists(json_filepath):
                    with open(json_filepath, 'r') as f:
                        quotes = json.load(f)
                
                quotes.append({
                    'date': datetime.now().isoformat(),
                    'client': self.current_quote['client'],
                    'address': self.current_quote['address'],
                    'total': self.current_quote['quote_text']
                })
                
                with open(json_filepath, 'w') as f:
                    json.dump(quotes, f, indent=2)
                
                messagebox.showinfo("Success", f"Quote saved to:\n{filepath}\n\nAlso logged to quotes.json")
                self.status_bar.config(text=f"Quote saved: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save quote: {str(e)}")
    
    def clear_all(self):
        """Clear all inputs"""
        self.client_name.delete(0, 'end')
        self.client_address.delete(0, 'end')
        self.miles_var.set("20")
        self.device_issue.delete(0, 'end')
        self.parts_cost.delete(0, 'end')
        self.labor_hours.delete(0, 'end')
        self.labor_hours.insert(0, '1.0')
        self.devices_listbox.delete(0, 'end')
        self.quote_text.delete('1.0', 'end')
        self.devices = []
        self.current_quote = {}
        self.status_bar.config(text="All fields cleared")
    
    def load_data(self):
        """Load saved data from JSON"""
        # Create data file if not exists
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({'quotes': [], 'clients': []}, f)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = SparkSphearApp(root)
    app.run()

if __name__ == "__main__":
    main()
