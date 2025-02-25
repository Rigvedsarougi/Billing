import streamlit as st
import pandas as pd
import pdfplumber
import os
from datetime import datetime

# Function to extract invoice data
def extract_invoice_data(pdf_file):
    extracted_data = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")
            invoice_details = {}
            
            # Extract key details
            for line in lines:
                if "Bill To:" in line:
                    invoice_details['Shop Name'] = lines[lines.index(line) + 1]
                elif "GSTIN/UN:" in line:
                    invoice_details['GST'] = line.split(": ")[-1]
                elif "Contact:" in line:
                    invoice_details['Contact'] = line.split(": ")[-1]
                elif "Address:" in line:
                    invoice_details['Address'] = lines[lines.index(line) + 1]
                elif "Sales Person:" in line:
                    invoice_details['Employee Name'] = line.split(": ")[-1]
            
            # Extract product details
            table_start = False
            for line in lines:
                if "S.No" in line and "Product Name" in line:
                    table_start = True
                    continue
                if table_start and line.strip():
                    parts = line.split()
                    if len(parts) >= 7:
                        product_name = " ".join(parts[1:-6])  # Extract product name
                        quantity = int(parts[-4])
                        price = float(parts[-2])
                        amount = float(parts[-1])
                        
                        extracted_data.append({
                            **invoice_details,
                            "Product Name": product_name,
                            "Quantity": quantity,
                            "Price": price,
                            "Amount": amount
                        })
    return extracted_data

# Streamlit UI
st.title("Invoice Sales Extractor")

uploaded_files = st.file_uploader("Upload Invoice PDFs", accept_multiple_files=True, type=["pdf"])

if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        all_data.extend(extract_invoice_data(uploaded_file))
    
    if all_data:
        df = pd.DataFrame(all_data)
        st.dataframe(df)
        
        csv_file = "extracted_sales_data.csv"
        df.to_csv(csv_file, index=False)
        
        with open(csv_file, "rb") as f:
            st.download_button("Download CSV", f, file_name=csv_file)
    else:
        st.error("No data extracted from invoices. Ensure correct formatting.")
