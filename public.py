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
st.title("Invoice Data Extraction System")

# Upload multiple invoices
uploaded_files = st.file_uploader("Upload Invoice PDFs", type="pdf", accept_multiple_files=True)

# Function to extract data from a single PDF
def extract_invoice_data(pdf_path, file_name):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
    
    # Extract relevant data from text
    lines = text.split("\n")
    data = {"File Name": file_name, "Invoice Date": "", "Shop Name": "", "GST": "", "Contact": "", "Employee Name": "", "Products": []}
    
    for i, line in enumerate(lines):
        if "Invoice Date:" in line:
            data["Invoice Date"] = line.replace("Invoice Date: ", "").strip()
        if "Bill To:" in line:
            data["Shop Name"] = lines[i + 1].replace("Name: ", "").strip()
        if "GSTIN/UN:" in line:
            data["GST"] = line.replace("GSTIN/UN: ", "").strip()
        if "Contact:" in line:
            data["Contact"] = line.replace("Contact: ", "").strip()
        if "Sales Person:" in line:
            data["Employee Name"] = line.replace("Sales Person: ", "").strip()
        if "Product Name" in line:
            product_start_index = i + 1
            break
    
    # Extract product details
    for line in lines[product_start_index:]:
        if "Subtotal" in line:
            break
        parts = line.split()
        if len(parts) >= 6:
            product_name = " ".join(parts[1:-4])
            quantity = int(parts[-3])
            rate = float(parts[-2])
            amount = float(parts[-1])
            data["Products"].append({
                "Product Name": product_name,
                "Quantity": quantity,
                "Rate": rate,
                "Amount": amount
            })
    return data

# Process uploaded files
if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        with open(file_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        invoice_data = extract_invoice_data(file_name, file_name)
        shop_name = invoice_data["Shop Name"]
        gst = invoice_data["GST"]
        contact = invoice_data["Contact"]
        employee_name = invoice_data["Employee Name"]
        invoice_date = invoice_data["Invoice Date"]
        
        # Fetch details from Outlet and Person
        outlet_details = Outlet[Outlet['Shop Name'] == shop_name].iloc[0] if not Outlet[Outlet['Shop Name'] == shop_name].empty else {}
        person_details = Person[Person['Employee Name'] == employee_name].iloc[0] if not Person[Person['Employee Name'] == employee_name].empty else {}
        
        # Process products
        for product in invoice_data["Products"]:
            product_details = Products[Products['Product Name'] == product["Product Name"]].iloc[0] if not Products[Products['Product Name'] == product["Product Name"]].empty else {}
            all_data.append({
                "File Name": file_name,
                "Invoice Date": invoice_date,
                "Shop Name": shop_name,
                "Address": outlet_details.get("Address", ""),
                "Contact": contact,
                "State": outlet_details.get("State", ""),
                "City": outlet_details.get("City", ""),
                "GST": gst,
                "Employee Name": employee_name,
                "Discount Category": person_details.get("Discount Category", ""),
                "Employee Code": person_details.get("Employee Code", ""),
                "Designation": person_details.get("Designation", ""),
                "Product ID": product_details.get("Product ID", ""),
                "Product Name": product["Product Name"],
                "Quantity": product["Quantity"],
                "Rate": product["Rate"],
                "Amount": product["Amount"]
            })
        os.remove(file_name)
    
    df = pd.DataFrame(all_data)
    st.write("Extracted Data:")
    st.dataframe(df)
    
    csv_file = f"product_wise_sales_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    df.to_csv(csv_file, index=False)
    with open(csv_file, "rb") as f:
        st.download_button("Download CSV", f, file_name=csv_file)
else:
    st.info("Please upload invoice PDFs to extract data.")
