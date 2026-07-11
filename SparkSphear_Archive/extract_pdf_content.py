#!/usr/bin/env python3
"""
Extract content from Linda Samsung PDF to understand the format
"""
import sys
import os

# Try to import PDF reading libraries
try:
    import PyPDF2
    PDF_LIB = "PyPDF2"
except ImportError:
    try:
        import pypdf
        PDF_LIB = "pypdf"
    except ImportError:
        try:
            import fitz  # PyMuPDF
            PDF_LIB = "PyMuPDF"
        except ImportError:
            print("No PDF reading library found.")
            print("Install one of these:")
            print("  pip install PyPDF2")
            print("  pip install pypdf")
            print("  pip install PyMuPDF")
            sys.exit(1)

def extract_pdf_content(pdf_path):
    """Extract text content from PDF"""
    
    if PDF_LIB == "PyPDF2":
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text
            
    elif PDF_LIB == "pypdf":
        import pypdf
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text
            
    elif PDF_LIB == "PyMuPDF":
        import fitz
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n\n"
        doc.close()
        return text

if __name__ == "__main__":
    pdf_path = r"G:\My Drive\SparkSphear_Core\04_Clients\Clients\SPARKSPHEAR TECH SUPPORT\Linda Samsung\SparkSphear_Quote_Linda.pdf"
    
    print(f"Extracting content from: {pdf_path}")
    print(f"Using: {PDF_LIB}")
    print("=" * 70)
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        print("\nChecking if Google Drive is accessible...")
        print("Make sure G: drive is mounted and accessible.")
        sys.exit(1)
    
    try:
        content = extract_pdf_content(pdf_path)
        
        # Save to text file
        output_path = r"C:\Users\shaza\Desktop\Linda_Samsung_Quote_Extracted.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nExtracted {len(content)} characters")
        print(f"Saved to: {output_path}")
        print("\n" + "=" * 70)
        print("FIRST 2000 CHARACTERS:")
        print("=" * 70)
        print(content[:2000])
        print("\n" + "=" * 70)
        print("To see full content, open:")
        print(output_path)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
