# Tech Stack Decision - UNICO Project

**Backend:** Python (FastAPI)
**PDF Parsing:** pdfplumber
**Excel Generation:** openpyxl
**Frontend:** Simple HTML/Tailwind + JavaScript (Alpine.js)

## Rationale

The UNICO project requires reliable data extraction from layout-heavy PDFs and output to Excel. 

1. **Python** is chosen as the primary language because it possesses the most mature ecosystem for unstructured data processing and PDF table extraction (`pdfplumber`).
2. **FastAPI** provides the performance needed to meet the `< 1 min for 100 items` requirement while offering automatic Swagger documentation for the backend API.
3. **pdfplumber** offers superior precision in identifying table grids compared to Node.js alternatives, which is critical for complex PO formats.
4. **openpyxl** is the industry standard for creating professional `.xlsx` files with complex styling or formatting if needed later.

## Pros

- ✅ **Accuracy**: High precision in extracting tabular data from PDFs.
- ✅ **Performance**: Asynchronous FastAPI handles multiple requests efficiently.
- ✅ **Maintainability**: Python code for data processing is highly readable and easy to update as business rules change.
- ✅ **Deployment**: Dockerized Python environments are standard and stable.

## Cons

- ⚠️ **Cold Start**: Python images can be larger than Node.js.
- ⚠️ **Package Management**: Requires a virtual environment (`venv`) to manage dependencies like `pdfplumber`.

## Estimated Learning Curve

- **Backend**: Low/Medium for developers familiar with Python.
- **Data Logic**: Medium (Requires fine-tuning regex and table coordinates).
- **Deployment**: Low (Standard Docker deployment).
