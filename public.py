import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

def extract_invoice_data(pdf_bytes):
    extracted_data = []
    
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Extract Shop Name
                shop_name = re.search(r"Shop Name: (.+)", text)
                shop_name = shop_name.group(1) if shop_name else "Unknown"
                
                # Extract Address
                address = re.search(r"Address: (.+)", text)
                address = address.group(1) if address else "Unknown"
                
                # Extract Contact
                contact = re.search(r"Contact: (.+)", text)
                contact = contact.group(1) if contact else "Unknown"
                
                # Extract State and City
                state = re.search(r"State: (.+)", text)
                state = state.group(1) if state else "Unknown"
                
                city = re.search(r"City: (.+)", text)
                city = city.group(1) if city else "Unknown"
                
                # Extract GST
                gst = re.search(r"GST: (.+)", text)
                gst = gst.group(1) if gst else "Unknown"
                
                # Extract Employee Details
                emp_name = re.search(r"Employee Name: (.+)", text)
                emp_name = emp_name.group(1) if emp_name else "Unknown"
                
                discount_category = re.search(r"Discount Category: (.+)", text)
                discount_category = discount_category.group(1) if discount_category else "Unknown"
                
                emp_code = re.search(r"Employee Code: (.+)", text)
                emp_code = emp_code.group(1) if emp_code else "Unknown"
                
                designation = re.search(r"Designation: (.+)", text)
                designation = designation.group(1) if designation else "Unknown"
                
                # Extract Product Information
                product_lines = re.findall(r"(\d+)\s+([\w\s]+)\s+([\w\s]+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)", text)
                for prod in product_lines:
                    product_id, product_name, category, quantity, price, total_amount = prod
                    extracted_data.append([
                        shop_name, address, contact, state, city, gst,
                        emp_name, discount_category, emp_code, designation,
                        product_id, product_name, category, price, quantity, total_amount
                    ])
    
    return extracted_data

st.title("Invoice Extraction System")

uploaded_files = st.file_uploader("Upload Invoice PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    
    for uploaded_file in uploaded_files:
        pdf_bytes = uploaded_file.read()
        data = extract_invoice_data(pdf_bytes)
        all_data.extend(data)
    
    if all_data:
        df = pd.DataFrame(all_data, columns=[
            "Shop Name", "Address", "Contact", "State", "City", "GST",
            "Employee Name", "Discount Category", "Employee Code", "Designation",
            "Product ID", "Product Name", "Product Category", "Price", "Quantity Sold", "Total Amount"
        ])
        
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "invoice_data.csv", "text/csv")
