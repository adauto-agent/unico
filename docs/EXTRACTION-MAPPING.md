# EXTRACTION-MAPPING.md - UNICO Order Data Extraction

This document defines the mapping rules from PDF Order files to the mandatory 27-column spreadsheet format.

## 📋 27-Column Mapping Rules

| # | Column Name (Vietnamese) | Source Field in PDF / Calculation Rule | Type |
|---|-------------------------|-----------------------------------------|------|
| 1 | GHI CHÚ | Empty (ĐỂ TRỐNG) | String |
| 2 | STT | Auto-incrementing counter per order line | Integer |
| 3 | HĐ | Empty (ĐỂ TRỐNG) | String |
| 4 | NGÀY NHẬN ĐƠN | Field "ISSUED DATE" in PDF header | Date (DD/MM/YYYY) |
| 5 | NGÀY XUẤT HÀNG | Field "Ship Date" in PDF header | Date (DD/MM/YYYY) |
| 6 | NGÀY HÀNG ĐẾN | [NGÀY XUẤT HÀNG] + 2 days | Date (DD/MM/YYYY) |
| 7 | PKL | Empty (ĐỂ TRỐNG) | String |
| 8 | NGƯỜI ĐẶT HÀNG | PDF "From" field (Default: Nguyễn Quyên_IS3 if provided via email) | String |
| 9 | KHÁCH HÀNG | Constant: "UNICO" | String |
| 10| BILL TO | Mapping based on "Ship to" address (Rule 3) | String |
| 11| CONSIGNEE | Mapping based on "Ship to" address (Rule 3) | String |
| 12| PL & TK | Empty (ĐỂ TRỐNG) | String |
| 13| TỈNH | Mapping based on "Ship to" address (Rule 3) | String |
| 14| STYLE | Field "Style No." or "Article" in table rows | String |
| 15| PO | Formula: [Buyer] + " " + [Season] + " " + [MPO-No] | String |
| 16| SHEET | Empty (ĐỂ TRỐNG) | String |
| 17| pkl | Empty (ĐỂ TRỐNG) | String |
| 18| Mô tả | Empty (ĐỂ TRỐNG) | String |
| 19| MÃ GỐC | Empty (ĐỂ TRỐNG) | String |
| 20| MÃ HÀNG | Empty (ĐỂ TRỐNG) | String |
| 21| Color | Empty (ĐỂ TRỐNG) | String |
| 22| width | Empty (ĐỂ TRỐNG) | String |
| 23| ĐVT | Unit (e.g., YDS/PCS) from table rows | String |
| 24| SỐ LƯỢNG | Quantity from table rows (Integer, no thousand separator) | Integer |
| 25| (Reserved) | Empty | - |
| 26| (Reserved) | Empty | - |
| 27| (Reserved) | Empty | - |

## ⚙️ Logic Rules

### 1. Place Mapping (Rule 3)
| "Ship to" Keyword | BILL TO / CONSIGNEE Value | TỈNH Value |
|-------------------|---------------------------|------------|
| "BAC NINH" / "UNICO GLOBAL VN" | UNICO BẮC GIANG | BẮC GIANG |
| "LAO CAI" / "YEN BAI" / "UNICO GLOBAL YB" | UNICO YÊN BÁI | YÊN BÁI |

### 2. Numerical Formatting
- **Thousands Separator**: Remove all commas (e.g., `1,500` -> `1500`).
- **Decimals**: Cast to integer (no decimal part).
- **Validation**: Sum of extracted line quantities must equal the "Grand Total" in the PDF.

## 🔍 Recommended Extraction Strategy

1. **Header Extraction**: Use Keyword-based Regex for `Issued Date`, `Ship Date`, `Buyer`, `Season`, and `MPO-No`.
2. **Line Item Extraction**: 
   - Use **pdfplumber** to identify the table area.
   - Use table-recognition logic to extract `Style`, `Quantity`, and `Unit`.
   - Each row in the PDF table (with a valid Style/Quantity) should become a separate line in the Excel output.
3. **Global Multi-page Check**: Iterate through all pages to capture multi-page tables.

## ⚠️ Identified Edge Cases
- **Duplicate Styles**: Ensure they are treated as separate lines if listed separately in the PDF.
- **Varying units**: Detect if multiple units (YDS/PCS) exist in the same order.
- **Address variations**: Handle case-insensitivity and minor typos in "Ship to" mapping.
