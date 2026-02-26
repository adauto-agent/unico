#!/usr/bin/env python3
"""Test script for UNICO extractor"""

import os
import sys
from extractor import UnicoExtractor

# Paths
SAMPLE_PDF = "../docs/samples/6764805e-6b93-47f3-a790-69d42db9c64c.pdf"
OUTPUT_XLSX = "../outputs/test_output.xlsx"

# Create output dir
os.makedirs("../outputs", exist_ok=True)

# Run extraction
print(f"📄 Processing: {SAMPLE_PDF}")
extractor = UnicoExtractor()
try:
    count = extractor.extract(SAMPLE_PDF, OUTPUT_XLSX)
    print(f"✅ Success! Extracted {count} items")
    print(f"📊 Output: {OUTPUT_XLSX}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
