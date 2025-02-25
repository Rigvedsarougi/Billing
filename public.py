import streamlit as st
import pandas as pd
import pdfplumber
import os

# Function to extract data from invoice PDFs
def extract_invoice_data(pdf_file):
    extracted_data = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                invoice_info = {
                    "Customer Name": "",
                    "GST Number": "",
                    "Contact": "",
                    "Address": "",
                    "Total Amount": "",
                    "Invoice Date": "",
                    "Products": []
                }
                
                address_flag = False
                for line in lines:
                    line = line.strip()
                    if "Name:" in line and not invoice_info["Customer Name"]:
                        invoice_info["Customer Name"] = line.split("Name:")[-1].strip()
                    elif "GSTIN/UN:" in line:
                        invoice_info["GST Number"] = line.split("GSTIN/UN:")[-1].strip()
                    elif "Contact:" in line:
                        invoice_info["Contact"] = line.split("Contact:")[-1].strip()
                    elif "Address:" in line:
                        address_flag = True
                        invoice_info["Address"] = line.split("Address:")[-1].strip()
                    elif address_flag and line:
                        invoice_info["Address"] += " " + line.strip()
                    elif "Grand Total" in line:
                        invoice_info["Total Amount"] = line.split("Grand Total")[-1].strip()
                    elif "Date:" in line:
                        invoice_info["Invoice Date"] = line.split("Date:")[-1].strip()
                    elif any(char.isdigit() for char in line) and "INR" not in line and len(line.split()) > 2:
                        invoice_info["Products"].append(line)
                
                extracted_data.append(invoice_info)
    
    return extracted_data

# Streamlit UI
st.title("Invoice Data Extractor")

uploaded_files = st.file_uploader("Upload Invoice PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        data = extract_invoice_data(uploaded_file)
        all_data.extend(data)
    
    df = pd.DataFrame(all_data)
    
    # Ensure 'Products' column is properly formatted
    df["Products"] = df["Products"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    
    st.write("Extracted Data:", df)
    
    csv_file = "extracted_invoice_data.csv"
    df.to_csv(csv_file, index=False)
    with open(csv_file, "rb") as f:
        st.download_button("Download CSV", f, file_name=csv_file)
