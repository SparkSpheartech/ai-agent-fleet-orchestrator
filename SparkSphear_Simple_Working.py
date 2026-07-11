#!/usr/bin/env python3
"""
SparkSphear Tech - Simple Working App
ONE file that works - ready for 1:30 PM visit
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime

# Simple pricing database (no external imports needed)
PRICING_DB = {
    "iPhone 11": {
        "screen": {"parts": 45, "labor": 1.5},
        "battery": {"parts": 25, "labor": 0.5}
    },
    "Samsung Galaxy Tab E": {
        "digitizer": {"parts": 25, "labor": 1.5},
        "screen": {"parts": 40, "labor": 2.0}
    }
}

REPLACEMENTS = {
    "Smartphone": [
        {"name": "Budget Option", "price": "$64-100", "specs": "Android 13"},
        {"name": "Mid-Range", "price": "$150-250", "specs": "Android 14"},
        {"name": "High-End", "price": "$300-500", "specs": "Flagship"},
        {"name": "Premium", "price": "$800+", "specs": "Latest model"}
    ],
    "Tablet": [
        {"name": "Budget Option", "price": "$64-100", "specs": "8\\\" screen"},
        {"name": "Mid-Range", "price": "$150-200", "specs": "8-10\\\" screen"},
        {"name": "High-End", "price": "$250-400", "specs": "Premium"},
        {"name": "Premium", "price": "$500+", "specs": "Latest iPad"}
    ]
}

def get_pricing(model, issue):
    """Get repair pricing"""
    if model in PRICING_DB and issue in PRICING_DB[model]:
        data = PRICING_DB[model][issue]
        parts = data["parts"]
        labor_cost = data["labor"] * 25
        total_cost = parts + labor_cost
        suggested_price = total_cost * 1.5  # 50% markup
        
        return {
            "parts": parts,
            "labor_hours": data["labor"],
            "labor_cost": labor_cost,
            "total_cost": total_cost,
            "suggested_price": suggested_price
        }
    return None

def get_replacements(device_type):
    """Get 4 replacement options"""
    if device_type in REPLACEMENTS:
        return REPLACEMENTS[device_type]
    return []

# ===== CREATE THE APP =====
root = tk.Tk()
root.title("SparkSphear Tech - Smart Pricing")
root.geometry("1000x800")
root.configure(bg='#f0f0f0')

# Title
title_frame = tk.Frame(root, bg='#2c3e50', height=70)
title_frame.pack(fill='x')
title_frame.pack_propagate(False)

tk.Label(title_frame, text="SparkSphear Tech", 
         font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white').pack(pady=15)

# Main container
main = tk.Frame(root, bg='#f0f0f0')
main.pack(fill='both', expand=True, padx=20, pady=20)

# Left panel
left = tk.Frame(main, bg='white', relief='raised', bd=2)
left.pack(side='left', fill='both', expand=True, padx=(0, 10))

# Right panel
right = tk.Frame(main, bg='white', relief='raised', bd=2)
right.pack(side='right', fill='both', expand=True, padx=(10, 0))

# ===== LEFT: Client & Device Info =====
client_f = tk.LabelFrame(left, text="👤 Client & Device Info", 
                         font=('Arial', 12, 'bold'), bg='white', 
                         padx=10, pady=10)
client_f.pack(fill='x', padx=10, pady=10)

tk.Label(client_f, text="Client Name:*", bg='white').grid(row=0, column=0, sticky='w', pady=5)
client_name = tk.Entry(client_f, width=35)
client_name.grid(row=0, column=1, pady=5, padx=(10, 0))

tk.Label(client_f, text="Address:", bg='white').grid(row=1, column=0, sticky='w', pady=5)
client_address = tk.Entry(client_f, width=35)
client_address.grid(row=1, column=1, pady=5, padx=(10, 0))
client_address.insert(0, "2523 Caroline St, Fort Wayne, IN")

# Device input
tk.Label(client_f, text="\nDevice Model:*", bg='white', font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=(15, 5))
device_model = tk.Entry(client_f, width=35)
device_model.grid(row=2, column=1, pady=(15, 5), padx=(10, 0))
device_model.insert(0, "Samsung Galaxy Tab E")

tk.Label(client_f, text="Issue:*", bg='white').grid(row=3, column=0, sticky='w', pady=5)
device_issue = tk.Entry(client_f, width=35)
device_issue.grid(row=3, column=1, pady=5, padx=(10, 0))
device_issue.insert(0, "digitizer failure")

# FETCH PRICING BUTTON
def fetch_pricing():
    """Fetch smart pricing - auto-runs when you click"""
    model = device_model.get().strip()
    issue = device_issue.get().strip()
    
    if not model or not issue:
        messagebox.showwarning("Missing", "Enter model and issue")
        return
    
    # Get repair pricing
    pricing = get_pricing(model, issue)
    
    # Get replacements
    device_type = "Tablet" if "tablet" in model.lower() else "Smartphone"
    replacements = get_replacements(device_type)
    
    # Display repair pricing
    if pricing:
        repair_text = f"""OPTION 1: REPAIR
Parts: ${pricing['parts']:.2f}
Labor: {pricing['labor_hours']} hrs @ $25 = ${pricing['labor_cost']:.2f}
YOUR Cost: ${pricing['total_cost']:.2f}
Price to Client: ${pricing['suggested_price']:.2f}
Profit: ${pricing['suggested_price'] - pricing['total_cost']:.2f}
"""
    else:
        repair_text = "Device/issue not in database. Use manual entry.\n"
    
    # Display replacements
    replace_text = "\nOPTION 2: 4 REPLACEMENTS\n"
    for i, opt in enumerate(replacements, 1):
        replace_text += f"\nOption {i}: {opt['name']}\n"
        replace_text += f"  Price: {opt['price']}\n"
        replace_text += f"  Specs: {opt['specs']}\n"
    
    # Show in pricing display
    pricing_display.delete('1.0', 'end')
    pricing_display.insert('1.0', repair_text + replace_text)
    
    # Also show in replacement display
    replacement_display.delete('1.0', 'end')
    replacement_display.insert('1.0', replace_text)
    
    status.config(text="✅ Smart pricing fetched! Ready to generate quote.")

fetch_btn = tk.Button(client_f, text="🧠 FETCH SMART PRICING",
                       command=fetch_pricing,
                       bg='#27ae60', fg='white',
                       font=('Arial', 11, 'bold'),
                       padx=30, pady=15)
fetch_btn.grid(row=4, column=0, columnspan=2, pady=20)

# Pricing display (left panel)
pricing_display = scrolledtext.ScrolledText(left, height=25, width=65, font=('Courier', 9))
pricing_display.pack(fill='both', expand=True, padx=10, pady=10)

# ===== RIGHT: Actions & Preview =====
# Action buttons
action_f = tk.Frame(right, bg='white')
action_f.pack(fill='x', padx=10, pady=10)

tk.Label(action_f, text="⚡ Actions", font=('Arial', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))

def generate_quote():
    """Generate quote with smart pricing"""
    model = device_model.get().strip()
    issue = device_issue.get().strip()
    
    if not model or not issue:
        messagebox.showwarning("Missing", "Enter model and issue first")
        return
    
    # Get pricing
    pricing = get_pricing(model, issue)
    device_type = "Tablet" if "tablet" in model.lower() else "Smartphone"
    replacements = get_replacements(device_type)
    
    # Build quote
    quote = f"""SPARKSPHEAR TECH - SMART PRICING QUOTE
==================================================

Client: {client_name.get()}
Address: {client_address.get()}
Date: {datetime.now().strftime('%B %d, %Y')}

OPTION 1: REPAIR
==================================================
"""
    
    if pricing:
        quote += f"Parts Cost: ${pricing['parts']:.2f}\n"
        quote += f"Labor: {pricing['labor_hours']} hrs @ $25 = ${pricing['labor_cost']:.2f}\n"
        quote += f"\nYOUR Total Cost: ${pricing['total_cost']:.2f}\n"
        quote += f"Suggested Client Price: ${pricing['suggested_price']:.2f}\n"
        quote += f"Profit Margin: {((pricing['suggested_price'] - pricing['total_cost']) / pricing['suggested_price'] * 100):.1f}%\n"
    
    quote += f"\nOPTION 2: 4 REPLACEMENT OPTIONS\n"
    quote += "=" * 50 + "\n\n"
    
    for i, opt in enumerate(replacements, 1):
        quote += f"Option {i}: {opt['name']}\n"
        quote += f"  Price Range: {opt['price']}\n"
        quote += f"  Specifications: {opt['specs']}\n\n"
    
    quote += "RECOMMENDATION:\n"
    quote += "  - Repair if client wants to keep same device\n"
    quote += "  - Replace if device is old or repair cost > 50% of replacement\n"
    
    # Show in preview
    quote_preview.config(state='normal')
    quote_preview.delete('1.0', 'end')
    quote_preview.insert('1.0', quote)
    quote_preview.config(state='disabled')
    
    status.config(text="✅ Quote generated with smart pricing!")

gen_btn = tk.Button(action_f, text="📄 Generate Quote (with Smart Pricing)",
                     command=generate_quote,
                     bg='#e67e22', fg='white',
                     font=('Arial', 11, 'bold'),
                     padx=20, pady=10)
gen_btn.pack(fill='x', pady=3)

# Replacement display (right panel)
replace_f = tk.LabelFrame(right, text="🔄 4 Replacement Options",
                           font=('Arial', 11, 'bold'), bg='white',
                           padx=10, pady=10)
replace_f.pack(fill='x', padx=10, pady=10)

replacement_display = scrolledtext.ScrolledText(replace_f, height=15, width=70, font=('Courier', 9))
replacement_display.pack(fill='both', expand=True, pady=5)

# Quote preview
preview_f = tk.LabelFrame(right, text="📄 Quote Preview",
                           font=('Arial', 11, 'bold'), bg='white',
                           padx=10, pady=10)
preview_f.pack(fill='both', expand=True, padx=10, pady=10)

quote_preview = scrolledtext.ScrolledText(preview_f, height=20, width=70, font=('Courier', 9), state='disabled')
quote_preview.pack(fill='both', expand=True)

# Status bar
status = tk.Label(root, text="Ready - Enter device info and click 'FETCH SMART PRICING'",
                     bd=1, relief='sunken', anchor='w', bg='#ecf0f1')
status.pack(side='bottom', fill='x')

print("✅ App created! Ready to run.")
print("\nTo use:")
print("1. Double-click this file (or run: python SparkSphear_Simple_Working.py)")
print("2. Enter device model + issue")
print("3. Click 'FETCH SMART PRICING'")
print("4. Click 'Generate Quote'")
print("\nOpens at: 1:30 PM today!")

root.mainloop()
