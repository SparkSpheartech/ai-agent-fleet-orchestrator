#!/usr/bin/env python3
"""
Generate a PDF Reference Sheet for Client Visit
2523 Caroline St - 1:30 PM Today
"""

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from datetime import datetime

def create_reference_sheet():
    """Create a one-page PDF reference sheet for the client visit"""
    
    if not PDF_AVAILABLE:
        print("FPDF not available. Creating text version instead.")
        create_text_version()
        return
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set margins
    pdf.set_margins(10, 10, 10)
    
    # === HEADER ===
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(44, 62, 80)  # Dark blue
    pdf.cell(0, 12, "SPARKSPHEAR TECH", ln=True, align="C")
    
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Fort Wayne, IN | (260) 267-0641 | sparksphear4me@gmail.com", ln=True, align="C")
    pdf.ln(8)
    
    # === TODAY'S VISIT INFO ===
    pdf.set_fill_color(52, 152, 219)  # Blue
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "TODAY'S VISIT - 1:30 PM", ln=True, align="C", fill=True)
    pdf.ln(5)
    
    # Visit details
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 11)
    
    # Two columns
    col_width = 90
    
    # Left column - Client info
    pdf.set_font("Arial", "B", 11)
    pdf.cell(col_width, 7, "CLIENT & LOCATION:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(col_width, 6, "Address: 2523 Caroline St", ln=True)
    pdf.cell(col_width, 6, "Fort Wayne, IN 46807", ln=True)
    pdf.cell(col_width, 6, "Distance: 1.6 mi one-way", ln=True)
    pdf.cell(col_width, 6, "Round-Trip: 3.2 miles", ln=True)
    pdf.ln(5)
    
    # Right column - Pricing
    pdf.set_xy(110, 45)  # Move to right column
    pdf.set_font("Arial", "B", 11)
    pdf.cell(col_width, 7, "PRICING BREAKDOWN:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_xy(110, 52)
    pdf.cell(col_width, 6, f"Trip Fee: $35.00 (base rate)", ln=True)
    pdf.set_xy(110, 58)
    pdf.cell(col_width, 6, f"Diagnosis: $25.00 (waived if repair)", ln=True)
    pdf.set_xy(110, 64)
    pdf.cell(col_width, 6, f"Labor: $25.00/hour (1 hr min)", ln=True)
    pdf.set_xy(110, 70)
    pdf.cell(col_width, 6, f"Parts: Cost + 25% markup", ln=True)
    pdf.set_xy(110, 76)
    pdf.cell(col_width, 6, f"Minimum Visit: $60.00", ln=True)
    
    # Reset position
    pdf.set_y(85)
    pdf.set_x(10)
    pdf.ln(5)
    
    # === YOUR TALKING POINTS ===
    pdf.set_fill_color(46, 204, 113)  # Green
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "YOUR TALKING POINTS (USE THESE!)", ln=True, fill=True)
    pdf.ln(4)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    
    # Opening script
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "1. OPENING (at the door):", ln=True)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, '"Hi, I\'m Shazaly from SparkSphear Tech. I\'m here to look at your devices. My trip fee is $35 - that\'s based on distance from my base. Since you\'re only 3.2 miles away, it\'s the base rate of $35. I\'ll diagnose your devices for $25, but that\'s waived if you choose to repair with me."')
    pdf.ln(3)
    
    # After diagnosis
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "2. AFTER DIAGNOSIS (present options):", ln=True)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, '"Here\'s what I found: [explain issues]. You have two options:\n\nOPTION 1 - REPAIR: $[X] total. I can fix it today/this week. 30-day warranty.\n\nOPTION 2 - REPLACE: I can source a new/refurbished device for $[X]. I\'ll deliver it and transfer your data. Takes [X] days.\n\nWhich makes more sense for you?"')
    pdf.ln(3)
    
    # Objection handling
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, "3. IF THEY ASK \"WHY SO MUCH?\":", ln=True)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, '"My trip fee covers me driving from my base to you and back - that\'s gas and an hour of my time. The diagnosis fee is for my expertise in figuring out if it\'s worth repairing or replacing. Most repair shops charge $50-75 just to look at your device - I\'m charging $25, and I\'ll waive it if you repair with me."')
    pdf.ln(5)
    
    # === REPAIR VS REPLACE COMPARISON ===
    pdf.set_fill_color(241, 196, 15)  # Yellow
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "REPAIR vs REPLACE - QUICK COMPARISON", ln=True, fill=True)
    pdf.ln(4)
    
    # Table header
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 7, "FACTOR", border=1, align="C")
    pdf.cell(70, 7, "REPAIR", border=1, align="C")
    pdf.cell(70, 7, "REPLACE", border=1, align="C")
    pdf.ln()
    
    # Table rows
    pdf.set_font("Arial", "", 9)
    rows = [
        ("Cost", "$60-$200", "$200-$600"),
        ("Time", "Same day-2 days", "2-5 days"),
        ("Data", "Stays on device", "Transfer included"),
        ("Warranty", "30 days labor", "Varies by device"),
        ("Best for", "Newer devices", "Old/broken beyond repair")
    ]
    
    for factor, repair, replace in rows:
        pdf.cell(50, 6, factor, border=1)
        pdf.cell(70, 6, repair, border=1)
        pdf.cell(70, 6, replace, border=1)
        pdf.ln()
    
    pdf.ln(5)
    
    # === DEVICES COMMON PRICING ===
    pdf.set_fill_color(155, 89, 182)  # Purple
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "COMMON REPAIR PRICES (REFERENCE)", ln=True, fill=True)
    pdf.ln(4)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    
    # Two columns of prices
    prices_col1 = [
        "Smartphone Screen: $75-100",
        "Tablet Screen: $100-125",
        "Laptop Screen: $100-150",
        "Battery Replace: $50-75",
        "Charging Port: $40-60"
    ]
    
    prices_col2 = [
        "Water Damage: $80-120",
        "Software Fix: $25-50",
        "Data Recovery: $100-200",
        "Virus Removal: $50-75",
        "RAM Upgrade: $40-80"
    ]
    
    for i, (left, right) in enumerate(zip(prices_col1, prices_col2)):
        pdf.cell(95, 5, f"• {left}", ln=False)
        pdf.cell(95, 5, f"• {right}", ln=True)
    
    pdf.ln(5)
    
    # === NEXT STEPS ===
    pdf.set_fill_color(231, 76, 60)  # Red
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "NEXT STEPS AFTER CLIENT DECIDES", ln=True, fill=True)
    pdf.ln(4)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    
    steps = [
        "1. IF THEY SAY YES TO REPAIR: Get approval signature, collect 50% deposit, schedule repair time",
        "2. IF THEY SAY YES TO REPLACE: Get approval, collect sourcing fee ($15), source device within 24 hrs",
        "3. IF THEY SAY NO: Thank them, offer 24/7 support ($15/mo), follow up in 1 week",
        "4. ALWAYS: Save quote to client folder, update Google Drive, send thank-you text"
    ]
    
    for step in steps:
        pdf.multi_cell(0, 6, step)
        pdf.ln(1)
    
    pdf.ln(5)
    
    # === CONTACT & NOTES ===
    pdf.set_fill_color(149, 165, 166)  # Gray
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 9, "NOTES & CONTACT INFO", ln=True, fill=True)
    pdf.ln(4)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Your Contact: (260) 267-0641 | sparksphear4me@gmail.com", ln=True)
    pdf.cell(0, 6, "Payment Methods: Cash, Card, Venmo, CashApp", ln=True)
    pdf.cell(0, 6, "Base Location: 1427 Park Ave, Fort Wayne, IN 46807", ln=True)
    pdf.ln(3)
    
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 6, "Notes from today's visit:", ln=True)
    pdf.ln(10)  # Space for writing
    
    # Signature line
    pdf.line(10, pdf.get_y(), 100, pdf.get_y())
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "Client Signature", ln=True)
    
    # Save PDF
    output_path = r"C:\Users\shaza\Desktop\Client_Visit_Reference_2523CarolineSt.pdf"
    pdf.output(output_path)
    print(f"PDF created: {output_path}")
    return output_path

def create_text_version():
    """Create text version if PDF not available"""
    text = []
    text.append("=" * 70)
    text.append("  SPARKSPHEAR TECH - CLIENT VISIT REFERENCE SHEET")
    text.append("=" * 70)
    text.append("")
    text.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    text.append("Time: 1:30 PM")
    text.append("Client Address: 2523 Caroline St, Fort Wayne, IN 46807")
    text.append("")
    text.append("-" * 70)
    text.append("TODAY'S PRICING (Auto-Calculated)")
    text.append("-" * 70)
    text.append("")
    text.append("Distance from base (1427 Park Ave):")
    text.append("  One-way: 1.6 miles")
    text.append("  Round-trip: 3.2 miles")
    text.append("")
    text.append("Trip Fee: $35.00 (base rate, under 15 miles)")
    text.append("Diagnosis Fee: $25.00 (waived if repair)")
    text.append("Labor: $25.00/hour (1-hour minimum)")
    text.append("Parts: Your cost + 25% markup")
    text.append("")
    text.append("Minimum charge for visit: $60.00")
    text.append("")
    text.append("-" * 70)
    text.append("YOUR TALKING POINTS")
    text.append("-" * 70)
    text.append("")
    text.append("OPENING (at the door):")
    text.append('"Hi, I\'m Shazaly from SparkSphear Tech. I\'m here to look at')
    text.append('your devices. My trip fee is $35 - that\'s based on distance')
    text.append('from my base. Since you\'re only 3.2 miles away, it\'s the')
    text.append('base rate of $35. I\'ll diagnose your devices for $25, but')
    text.append('that\'s waived if you choose to repair with me."')
    text.append("")
    text.append("AFTER DIAGNOSIS:")
    text.append('"Here\'s what I found: [explain issues]. You have two options:')
    text.append("")
    text.append("OPTION 1 - REPAIR: $[X] total. I can fix it today/this week.")
    text.append("  30-day warranty.")
    text.append("")
    text.append("OPTION 2 - REPLACE: I can source a new/refurbished device")
    text.append("  for $[X]. I\'ll deliver it and transfer your data.")
    text.append("  Takes [X] days.")
    text.append("")
    text.append("Which makes more sense for you?\"")
    text.append("")
    text.append("IF THEY ASK \"WHY SO MUCH?\":")
    text.append('"My trip fee covers me driving from my base to you and back')
    text.append('- that\'s gas and an hour of my time. The diagnosis fee is')
    text.append('for my expertise in figuring out if it\'s worth repairing or')
    text.append('replacing. Most repair shops charge $50-75 just to look at')
    text.append('your device - I\'m charging $25, and I\'ll waive it if you')
    text.append('repair with me."')
    text.append("")
    text.append("-" * 70)
    text.append("REPAIR vs REPLACE COMPARISON")
    text.append("-" * 70)
    text.append("")
    text.append("REPAIR:")
    text.append("  • Cost: $60-$200")
    text.append("  • Time: Same day-2 days")
    text.append("  • Data: Stays on device")
    text.append("  • Warranty: 30 days labor")
    text.append("  • Best for: Newer devices")
    text.append("")
    text.append("REPLACE:")
    text.append("  • Cost: $200-$600")
    text.append("  • Time: 2-5 days")
    text.append("  • Data: Transfer included")
    text.append("  • Warranty: Varies by device")
    text.append("  • Best for: Old/broken beyond repair")
    text.append("")
    text.append("-" * 70)
    text.append("COMMON REPAIR PRICES (Reference)")
    text.append("-" * 70)
    text.append("")
    text.append("• Smartphone Screen: $75-100")
    text.append("• Tablet Screen: $100-125")
    text.append("• Laptop Screen: $100-150")
    text.append("• Battery Replace: $50-75")
    text.append("• Charging Port: $40-60")
    text.append("• Water Damage: $80-120")
    text.append("• Software Fix: $25-50")
    text.append("")
    text.append("-" * 70)
    text.append("NEXT STEPS")
    text.append("-" * 70)
    text.append("")
    text.append("1. IF THEY SAY YES TO REPAIR:")
    text.append("   - Get approval signature")
    text.append("   - Collect 50% deposit")
    text.append("   - Schedule repair time")
    text.append("")
    text.append("2. IF THEY SAY YES TO REPLACE:")
    text.append("   - Get approval")
    text.append("   - Collect sourcing fee ($15)")
    text.append("   - Source device within 24 hrs")
    text.append("")
    text.append("3. ALWAYS:")
    text.append("   - Save quote to client folder")
    text.append("   - Update Google Drive")
    text.append("   - Send thank-you text")
    text.append("")
    text.append("-" * 70)
    text.append("CONTACT & NOTES")
    text.append("-" * 70)
    text.append("")
    text.append("Your Contact: (260) 267-0641")
    text.append("Payment: Cash, Card, Venmo, CashApp")
    text.append("")
    text.append("Notes from today's visit:")
    text.append("")
    text.append("_" * 50)
    text.append("")
    text.append("Client Signature: " + "_" * 30)
    text.append("")
    text.append("=" * 70)
    
    output_path = r"C:\Users\shaza\Desktop\Client_Visit_Reference_2523CarolineSt.txt"
    with open(output_path, 'w') as f:
        f.write('\n'.join(text))
    
    print(f"Text version created: {output_path}")
    return output_path

if __name__ == "__main__":
    print("Creating reference sheet for today's 1:30 PM client visit...")
    print("Address: 2523 Caroline St, Fort Wayne, IN 46807")
    print("Distance: 3.2 miles round-trip")
    print("Trip Fee: $35.00")
    print("")
    
    if PDF_AVAILABLE:
        output = create_reference_sheet()
    else:
        output = create_text_version()
        print("\nTo create PDF, install: pip install fpdf2")
    
    print(f"\nFile saved to: {output}")
    print("\nYou can now:")
    print("1. Print this file")
    print("2. Save to your phone")
    print("3. Reference during your 1:30 PM visit")
