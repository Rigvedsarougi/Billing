import streamlit as st
import pandas as pd
import pdfplumber
import os

def extract_invoice_data(pdf_file):
    extracted_data = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) > 2 and parts[0].isdigit():  # Assuming product lines start with a serial number
                        product_name = ' '.join(parts[1:-3])  # Extract product name
                        quantity = int(parts[-3])
                        rate = float(parts[-2])
                        amount = float(parts[-1])
                        extracted_data.append([product_name, quantity, rate, amount])
    
    return extracted_data

st.title("Invoice Data Extractor - Product Wise Sales")

uploaded_files = st.file_uploader("Upload Invoice PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    
    for uploaded_file in uploaded_files:
        extracted_data = extract_invoice_data(uploaded_file)
        all_data.extend(extracted_data)
    
    df = pd.DataFrame(all_data, columns=["Product Name", "Quantity", "Rate", "Total Amount"])
    product_sales = df.groupby("Product Name").sum().reset_index()
    
    st.write("### Product-wise Sales Collection")
    st.dataframe(product_sales)
    
    csv_file = "product_sales_summary.csv"
    product_sales.to_csv(csv_file, index=False)
    
    with open(csv_file, "rb") as f:
        st.download_button("Download CSV", f, file_name=csv_file)
