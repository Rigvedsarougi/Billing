import streamlit as st
import pandas as pd
import PyPDF2
import os
from datetime import datetime

# Load data
Products = pd.read_csv('Invoice - Products.csv')
Outlet = pd.read_csv('Invoice - Outlet.csv')
Person = pd.read_csv('Invoice - Person.csv')

# Streamlit UI
st.title("Invoice Data Extractor")

# Upload multiple invoices
uploaded_files = st.file_uploader("Upload Invoices (PDF)", type="pdf", accept_multiple_files=True)

# Function to extract data from a single PDF
def extract_invoice_data(pdf_file):
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    text = ""
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        text += page.extract_text()

    # Extract relevant information from the text
    lines = text.split('\n')
    data = {}
    for line in lines:
        if "Bill To:" in line:
            data['Shop Name'] = lines[lines.index(line) + 1].split("Name: ")[1].strip()
            data['Date'] = lines[lines.index(line) + 1].split("Date: ")[1].strip()
            data['GST'] = lines[lines.index(line) + 2].split("GSTIN/UN: ")[1].strip()
            data['Contact'] = lines[lines.index(line) + 2].split("Contact: ")[1].strip()
            data['Address'] = lines[lines.index(line) + 3].split("Address: ")[1].strip()
        if "Sales Person:" in line:
            data['Employee Name'] = line.split("Sales Person: ")[1].strip()
        if "Product Name" in line:
            start_index = lines.index(line) + 1
            products = []
            quantities = []
            rates = []
            amounts = []
            for i in range(start_index, len(lines)):
                if "Subtotal" in lines[i]:
                    break
                parts = lines[i].split()
                if len(parts) >= 6:
                    products.append(" ".join(parts[1:-4]))
                    quantities.append(int(parts[-4]))
                    rates.append(float(parts[-3]))
                    amounts.append(float(parts[-2]))
            data['Products'] = products
            data['Quantities'] = quantities
            data['Rates'] = rates
            data['Amounts'] = amounts

    return data

# Process uploaded files
if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        data = extract_invoice_data(uploaded_file)
        for i in range(len(data['Products'])):
            row = {
                'Shop Name': data['Shop Name'],
                'Address': data['Address'],
                'Contact': data['Contact'],
                'State': Outlet[Outlet['Shop Name'] == data['Shop Name']]['State'].values[0],
                'City': Outlet[Outlet['Shop Name'] == data['Shop Name']]['City'].values[0],
                'GST': data['GST'],
                'Employee Name': data['Employee Name'],
                'Discount Category': Person[Person['Employee Name'] == data['Employee Name']]['Discount Category'].values[0],
                'Employee Code': Person[Person['Employee Name'] == data['Employee Name']]['Employee Code'].values[0],
                'Designation': Person[Person['Employee Name'] == data['Employee Name']]['Designation'].values[0],
                'Product Name': data['Products'][i],
                'Quantity': data['Quantities'][i],
                'Rate': data['Rates'][i],
                'Amount': data['Amounts'][i]
            }
            all_data.append(row)

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Save to CSV
    csv_file = f"invoice_data_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    df.to_csv(csv_file, index=False)

    # Download link
    st.success("Data extracted successfully!")
    with open(csv_file, "rb") as f:
        st.download_button("Download CSV", f, file_name=csv_file)
else:
    st.info("Please upload PDF invoices to extract data.")
