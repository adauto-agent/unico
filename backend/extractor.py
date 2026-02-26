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
            "buyer": "UNICO",
            "ship_to": ""
        }
        
        # Regex for Issued Date
        issued_match = re.search(r"ISSUED DATE:\s*(\d{1,2}\s+\w{3}\s+\d{4})", text)
        if issued_match:
            info["issued_date"] = self._format_date(issued_match.group(1))
            
        # Regex for Ship Date
        ship_match = re.search(r"Ship Date:\s*(\d{1,2}\s+\w{3}\s+\d{4})", text)
        if ship_match:
            info["ship_date"] = self._format_date(ship_match.group(1))
            
        # MPO No
        mpo_match = re.search(r"MPO-NO:\s*([^\n]+)", text)
        if mpo_match:
            info["mpo_no"] = mpo_match.group(1).strip()
            
        # Season
        season_match = re.search(r"SEASON:\s*([^\n]+)", text)
        if season_match:
            info["season"] = season_match.group(1).strip()

        # Ship to (for location mapping)
        if "BAC NINH" in text or "UNICO GLOBAL VN" in text:
            info["location"] = "BẮC GIANG"
        elif "LAO CAI" in text or "YEN BAI" in text or "UNICO GLOBAL YB" in text:
            info["location"] = "YÊN BÁI"
        else:
            info["location"] = "BẮC GIANG" # Default

        return info

    def _parse_table_row(self, row):
        # Example logic: Order No, Colour, Article, Style, Description, Unit, Qty
        # Needs to be flexible based on column headers
        if not row or len(row) < 5:
            return None
            
        # Try to find quantity (usually a string with numbers and commas)
        qty_str = ""
        style = ""
        unit = "YDS"
        
        # Basic heuristic for VYMEX format
        # Row example: ['150CM', '0.6300', '37.170', '59', 'F26B-1110B...', 'WHITE', 'NP80G-1', ...]
        # This part requires specific mapping based on Nunes' analysis
        # For now, we look for numeric values in expected columns
        
        # Placeholder for real parsing logic based on PDF samples
        # Let's assume style is in index 4 and qty is in index 3 for this sample
        try:
            qty = row[3].replace(",", "") if row[3] else "0"
            if qty.isdigit() and int(qty) > 0:
                return {
                    "style": row[4] if row[4] else "UNKNOWN",
                    "qty": int(qty),
                    "unit": "YDS" # Default
                }
        except:
            pass
            
        return None

    def _map_to_27_columns(self, header, line, stt):
        row = ["" for _ in range(27)]
        
        # Mapping according to rules
        row[1] = stt # STT
        row[3] = header["issued_date"] # NGÀY NHẬN ĐƠN
        row[4] = header["ship_date"] # NGÀY XUẤT HÀNG
        
        # NGÀY HÀNG ĐẾN = Ship Date + 2 days
        try:
            dt = datetime.strptime(header["ship_date"], "%d/%m/%Y")
            row[5] = (dt + timedelta(days=2)).strftime("%d/%m/%Y")
        except:
            row[5] = ""
            
        row[7] = "Nguyễn Quyên_IS3" # NGƯỜI ĐẶT HÀNG (Default)
        row[8] = "UNICO" # KHÁCH HÀNG
        row[9] = f"UNICO {header['location']}" # BILL TO
        row[10] = f"UNICO {header['location']}" # CONSIGNEE
        row[12] = header["location"] # TỈNH
        row[13] = line["style"] # STYLE
        row[14] = f"LL.BEAN {header['season']} {header['mpo_no']}" # PO Formula
        row[22] = line["unit"] # ĐVT
        row[23] = line["qty"] # SỐ LƯỢNG
        
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
