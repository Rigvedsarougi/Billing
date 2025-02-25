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
def extract_invoice_data(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    # Extract relevant data from the text
    lines = text.split("\n")
    data = {}
    for line in lines:
        if "Bill To:" in line:
            data["Shop Name"] = lines[lines.index(line) + 1].replace("Name: ", "").strip()
        if "GSTIN/UN:" in line:
            data["GST"] = line.replace("GSTIN/UN: ", "").strip()
        if "Contact:" in line:
            data["Contact"] = line.replace("Contact: ", "").strip()
        if "Sales Person:" in line:
            data["Employee Name"] = line.replace("Sales Person: ", "").strip()
        if "Product Name" in line:
            product_start_index = lines.index(line) + 1
            break

    # Extract product details
    products = []
    for line in lines[product_start_index:]:
        if "Subtotal" in line:
            break
        if line.strip():
            parts = line.split()
            if len(parts) >= 6:
                product_name = " ".join(parts[1:-4])
                quantity = int(parts[-3])
                rate = float(parts[-2])
                amount = float(parts[-1])
                products.append({
                    "Product Name": product_name,
                    "Quantity": quantity,
                    "Rate": rate,
                    "Amount": amount
                })

    data["Products"] = products
    return data

# Process uploaded files
if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        # Save the uploaded file temporarily
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract data from the PDF
        invoice_data = extract_invoice_data(uploaded_file.name)
        shop_name = invoice_data.get("Shop Name")
        gst = invoice_data.get("GST")
        contact = invoice_data.get("Contact")
        employee_name = invoice_data.get("Employee Name")

        # Fetch additional details from Outlet and Person
        outlet_details = Outlet[Outlet['Shop Name'] == shop_name].iloc[0]
        person_details = Person[Person['Employee Name'] == employee_name].iloc[0]

        # Process each product in the invoice
        for product in invoice_data["Products"]:
            product_details = Products[Products['Product Name'] == product["Product Name"]].iloc[0]
            all_data.append({
                "Shop Name": shop_name,
                "Address": outlet_details["Address"],
                "Contact": contact,
                "State": outlet_details["State"],
                "City": outlet_details["City"],
                "GST": gst,
                "Employee Name": employee_name,
                "Discount Category": person_details["Discount Category"],
                "Employee Code": person_details["Employee Code"],
                "Designation": person_details["Designation"],
                "Product ID": product_details["Product ID"],
                "Product Name": product["Product Name"],
                "Quantity": product["Quantity"],
                "Rate": product["Rate"],
                "Amount": product["Amount"]
            })

        # Remove the temporary file
        os.remove(uploaded_file.name)

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Display the extracted data
    st.write("Extracted Data:")
    st.dataframe(df)

    # Download as CSV
    csv_file = f"product_wise_sales_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    df.to_csv(csv_file, index=False)
    with open(csv_file, "rb") as f:
        st.download_button("Download CSV", f, file_name=csv_file)
else:
    st.info("Please upload invoice PDFs to extract data.")
