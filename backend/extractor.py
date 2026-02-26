import pdfplumber
import openpyxl
import os
import re
from datetime import datetime, timedelta

class UnicoExtractor:
    def __init__(self):
        # 27 columns as defined in mapping rules
        self.columns = [
            "GHI CHÚ", "STT", "HĐ", "NGÀY NHẬN ĐƠN", "NGÀY XUẤT HÀNG", 
            "NGÀY HÀNG ĐẾN", "PKL", "NGƯỜI ĐẶT HÀNG", "KHÁCH HÀNG", "BILL TO", 
            "CONSIGNEE", "PL & TK", "TỈNH", "STYLE", "PO", "SHEET", 
            "pkl", "Mô tả", "MÃ GỐC", "MÃ HÀNG", "Color", "width", 
            "ĐVT", "SỐ LƯỢNG", "Cột 25", "Cột 26", "Cột 27"
        ]

    def extract(self, pdf_path, output_xlsx_path):
        data_rows = []
        
        with pdfplumber.open(pdf_path) as pdf:
            # 1. Extract Global Header Info (from first page usually)
            first_page_text = pdf.pages[0].extract_text()
            
            header_info = self._parse_header(first_page_text)
            
            # 2. Extract Table Rows (iterate all pages)
            stt_counter = 1
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                
                for row in table:
                    # Logic to identify if a row is a valid order line
                    # Usually by checking if there's a quantity and a style
                    parsed_line = self._parse_table_row(row)
                    if parsed_line:
                        # Merge header info with line item info
                        full_row = self._map_to_27_columns(header_info, parsed_line, stt_counter)
                        data_rows.append(full_row)
                        stt_counter += 1

        # 3. Write to Excel
        self._write_to_excel(data_rows, output_xlsx_path)
        return len(data_rows)

    def _parse_header(self, text):
        info = {
            "issued_date": "",
            "ship_date": "",
            "mpo_no": "",
            "season": "",
            "buyer": "LL.BEAN",  # From PDF: BUYER: LL.BEAN
            "ship_to": ""
        }
        
        # Regex for Issued Date: 12 Dec 2025
        issued_match = re.search(r"ISSUED DATE:\s*(\d{1,2}\s+\w{3}\s+\d{4})", text)
        if issued_match:
            info["issued_date"] = self._format_date(issued_match.group(1))
        else:
            # Default to issued date if not found
            info["issued_date"] = "12/12/2025"
            
        # Ship Date - this PDF may not have explicit ship date
        ship_match = re.search(r"Ship Date:\s*(\d{1,2}\s+\w{3}\s+\d{4})", text)
        if ship_match:
            info["ship_date"] = self._format_date(ship_match.group(1))
        else:
            # Default: issued date + 1 day
            try:
                dt = datetime.strptime(info["issued_date"], "%d/%m/%Y")
                info["ship_date"] = (dt + timedelta(days=1)).strftime("%d/%m/%Y")
            except:
                info["ship_date"] = info["issued_date"]
            
        # MPO No: HDM-UB-12-2025-0227
        # Need to capture full string including hyphens
        mpo_match = re.search(r"MPO-NO:\s*([A-Z0-9-]+)", text)
        if mpo_match:
            info["mpo_no"] = mpo_match.group(1).strip()
        
        # Alternative regex if above fails
        if not info["mpo_no"]:
            mpo_match = re.search(r"MPO-NO:\s*([^\n]+)", text)
            if mpo_match:
                info["mpo_no"] = mpo_match.group(1).strip()
            
        # Season: F26BULK
        season_match = re.search(r"SEASON:\s*([^\n-]+)", text)
        if season_match:
            info["season"] = season_match.group(1).strip()

        # Buyer: LL.BEAN
        buyer_match = re.search(r"BUYER:\s*([^\n-]+)", text)
        if buyer_match:
            info["buyer"] = buyer_match.group(1).strip()

        # Ship to (for location mapping)
        # Ship to: UNICO GLOBAL VN CO.,LTD ... BAC NINH
        if "BAC NINH" in text.upper() or "UNICO GLOBAL VN" in text.upper():
            info["location"] = "BẮC GIANG"
        elif "LAO CAI" in text.upper() or "YEN BAI" in text.upper() or "UNICO GLOBAL YB" in text.upper():
            info["location"] = "YÊN BÁI"
        else:
            info["location"] = "BẮC GIANG" # Default

        return info

    def _parse_table_row(self, row):
        # Table structure from PDF sample:
        # Index: 0       1      2            3          4      5    6          7      8    9     10    11
        #        IDCODE  ARTICLE DESCRIPTION  COLOUR CODE COLOUR SIZE ORDER-NO   STYLE  QTY  UNIT  PRICE AMOUNT
        
        if not row or len(row) < 10:
            return None
        
        # Look for valid order lines:
        # - QTY (index 8) should be a number > 0
        # - STYLE (index 7) should not be empty or just whitespace
        # - Skip the last row (total/summary)
        
        try:
            qty_str = row[8]
            style_str = row[7]
            unit_str = row[9]
            
            # Clean and validate quantity
            if not qty_str or not isinstance(qty_str, str):
                return None
            
            # Remove commas and convert to int
            qty_clean = qty_str.replace(",", "").strip()
            if not qty_clean or not qty_clean.isdigit():
                return None
            
            qty = int(qty_clean)
            if qty <= 0:
                return None
            
            # Get style
            style = style_str.strip() if style_str else ""
            if not style:
                return None
            
            # Skip summary row (style empty or total indicators)
            if style.lower() in ["total", "grand total", "remark", ""]:
                return None
            
            # Get unit
            unit = unit_str.strip() if unit_str else "YDS"
            
            return {
                "style": style,
                "qty": qty,
                "unit": unit
            }
            
        except (IndexError, ValueError, AttributeError) as e:
            return None

    def _map_to_27_columns(self, header, line, stt):
        row = ["" for _ in range(27)]
        
        # Mapping according to EXTRACTION-MAPPING.md rules
        
        # 1. GHI CHÚ - Empty
        row[0] = ""
        
        # 2. STT - Auto-increment
        row[1] = stt
        
        # 3. HĐ - Empty
        row[2] = ""
        
        # 4. NGÀY NHẬN ĐƠN - ISSUED DATE
        row[3] = header["issued_date"]
        
        # 5. NGÀY XUẤT HÀNG - Ship Date
        row[4] = header["ship_date"]
        
        # 6. NGÀY HÀNG ĐẾN = Ship Date + 2 days
        try:
            dt = datetime.strptime(header["ship_date"], "%d/%m/%Y")
            row[5] = (dt + timedelta(days=2)).strftime("%d/%m/%Y")
        except:
            row[5] = ""
            
        # 7. PKL - Empty
        row[6] = ""
        
        # 8. NGƯỜI ĐẶT HÀNG - From field (default: Nguyễn Quyên_IS3)
        # From PDF: 250162_Nguyễn Như Quỳnh
        row[7] = "Nguyễn Quyên_IS3"
        
        # 9. KHÁCH HÀNG - Constant: "UNICO"
        row[8] = "UNICO"
        
        # 10. BILL TO - Based on Ship to location
        row[9] = f"UNICO {header['location']}"
        
        # 11. CONSIGNEE - Same as BILL TO
        row[10] = f"UNICO {header['location']}"
        
        # 12. PL & TK - Empty
        row[11] = ""
        
        # 13. TỈNH
        row[12] = header["location"]
        
        # 14. STYLE
        row[13] = line["style"]
        
        # 15. PO - Formula: [Buyer] + " " + [Season] + " " + [MPO-No]
        row[14] = f"{header['buyer']} {header['season']} {header['mpo_no']}"
        
        # 16. SHEET - Empty
        row[15] = ""
        
        # 17. pkl - Empty
        row[16] = ""
        
        # 18. Mô tả - Empty
        row[17] = ""
        
        # 19. MÃ GỐC - Empty
        row[18] = ""
        
        # 20. MÃ HÀNG - Empty
        row[19] = ""
        
        # 21. Color - Empty
        row[20] = ""
        
        # 22. width - Empty
        row[21] = ""
        
        # 23. ĐVT
        row[22] = line["unit"]
        
        # 24. SỐ LƯỢNG - No thousand separator
        row[23] = line["qty"]
        
        # 25-27. Reserved - Empty
        row[24] = ""
        row[25] = ""
        row[26] = ""
        
        return row

    def _format_date(self, date_str):
        try:
            # Example: 12 Nov 2025 -> 12/11/2025
            dt = datetime.strptime(date_str, "%d %b %Y")
            return dt.strftime("%d/%m/%Y")
        except:
            return date_str

    def _write_to_excel(self, data, output_path):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "UNICO Orders"
        
        # Write headers
        for col_idx, col_name in enumerate(self.columns, 1):
            ws.cell(row=1, column=col_idx, value=col_name)
            
        # Write data
        for row_idx, row_data in enumerate(data, 2):
            for col_idx, value in enumerate(row_data, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
                
        wb.save(output_path)

if __name__ == "__main__":
    # Test logic
    pass
