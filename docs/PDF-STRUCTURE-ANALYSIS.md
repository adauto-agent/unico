# PDF-STRUCTURE-ANALYSIS.md - UNICO Order PDF Analysis

This document provides an architectural analysis of the PDF samples to guide implementation.

## 🏗️ PDF Structure Overview

Based on the filenames and business requirements, the PDFs follow a standard Purchase Order (PO) layout:

### 1. Header Section (Top)
- **Metadata**: Found near the top (Buyer name, MPO Number, Season).
- **Dates**: `ISSUED DATE` and `Ship Date` are usually aligned to the right or left near the top.
- **Ship To**: Critical block of text determining the destination mapping.

### 2. Table Section (Body)
- **Dynamic Content**: Orders with up to 100 items will span multiple pages.
- **Columns**: Typical columns include `Style No`, `Description`, `Quantity`, `UOM`.
- **Layout**: Likely contain horizontal/vertical lines separating rows and columns.

### 3. Footer Section (Bottom)
- **Totals**: Contains "Grand Total" or "Total Quantity" for cross-validation.
- **Signatures**: Non-critical for extraction.

## 📊 Pattern Recognition

- **Regex Patterns for Headers**:
  - `NGÀY NHẬN ĐƠN`: `(?i)Issued Date\s*:\s*(\d{2}/\d{2}/\d{4})`
  - `NGÀY XUẤT HÀNG`: `(?i)Ship Date\s*:\s*(\d{2}/\d{2}/\d{4})`
  - `MPO Number`: `(?i)MPO-No\s*:\s*([A-Z0-9-]+)`

- **Table Extraction Strategy**:
  - **pdfplumber** is highly recommended over standard PyPDF2 because it handles table grid detection (lines) better.
  - Strategy: Find rows starting with a non-empty `Style` column.

## 🛠️ Recommended Parsing Library

| Library | Rating | Reason |
|---------|--------|--------|
| **pdfplumber** | ⭐⭐⭐⭐⭐ | Excellent table extraction and text positioning. Best for layout-dependent POs. |
| **Tabula-py** | ⭐⭐⭐ | Good for pure tables, but requires Java. |
| **PyPDF2 / pypdf** | ⭐⭐ | Only extracts raw text strings; loses tabular structure easily. |

## 🚀 Architectural Recommendation

- Implement a **Template Pattern**: Create a base parser and specialized sub-parsers if different buyers have drastically different layouts.
- Use a **Validation Layer**: Always compare the sum of extracted lines against the footer "Grand Total".
