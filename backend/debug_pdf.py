#!/usr/bin/env python3
"""Debug PDF structure"""

import pdfplumber

PDF_PATH = "../docs/samples/6764805e-6b93-47f3-a790-69d42db9c64c.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"📄 PDF has {len(pdf.pages)} pages\n")
    
    for i, page in enumerate(pdf.pages):
        print(f"=== PAGE {i+1} ===")
        
        # Extract text
        text = page.extract_text()
        print("--- TEXT (first 1500 chars) ---")
        print(text[:1500] if text else "No text found")
        
        # Extract table
        tables = page.extract_tables()
        print(f"\n--- TABLES: {len(tables)} found ---")
        if tables:
            for j, table in enumerate(tables):
                print(f"\nTable {j+1} ({len(table)} rows):")
                for row in table[:10]:  # First 10 rows
                    print(row)
        
        print("\n" + "="*50 + "\n")
