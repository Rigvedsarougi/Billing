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
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    # Extract relevant data from the text
    lines = text.split("\n")
    data = {"File Name": file_name}  # Add file name to data
    invoice_date = None

    for i, line in enumerate(lines):
        if "Bill To:" in line:
            data["Shop Name"] = lines[i + 1].replace("Name: ", "").strip()
        if "Date:" in line:
            invoice_date = line.replace("Date:", "").strip()  # Extract date separately
        if "GSTIN/UN:" in line:
            data["GST"] = line.replace("GSTIN/UN:", "").strip()
        if "Contact:" in line:
            data["Contact"] = line.replace("Contact:", "").strip()
        if "Sales Person:" in line:
            data["Employee Name"] = line.replace("Sales Person:", "").strip()
        if "Product Name" in line:
            product_start_index = i + 1
            break

    # Ensure only the invoice date is stored correctly
    data["Invoice Date"] = invoice_date  

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
        file_name = uploaded_file.name  # Extract filename
        with open(file_name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        invoice_data = extract_invoice_data(file_name, file_name)
        shop_name = invoice_data.get("Shop Name", "Unknown")
        gst = invoice_data.get("GST", "N/A")
        contact = invoice_data.get("Contact", "N/A")
        employee_name = invoice_data.get("Employee Name", "N/A")
        invoice_date = invoice_data.get("Invoice Date", "N/A")

        # Fetch additional details from Outlet and Person
        outlet_match = Outlet[Outlet['Shop Name'].str.strip().str.lower() == shop_name.strip().lower()]
        if not outlet_match.empty:
            address = outlet_match.iloc[0]["Address"]
            state = outlet_match.iloc[0]["State"]
            city = outlet_match.iloc[0]["City"]
        else:
            address, state, city = "N/A", "N/A", "N/A"

        person_match = Person[Person['Employee Name'].str.strip().str.lower() == employee_name.strip().lower()]
        if not person_match.empty:
            discount_category = person_match.iloc[0]["Discount Category"]
            employee_code = person_match.iloc[0]["Employee Code"]
            designation = person_match.iloc[0]["Designation"]
        else:
            discount_category, employee_code, designation = "N/A", "N/A", "N/A"

        # Process each product in the invoice
        for product in invoice_data["Products"]:
            product_match = Products[Products['Product Name'].str.strip().str.lower() == product["Product Name"].strip().lower()]
            product_id = product_match.iloc[0]["Product ID"] if not product_match.empty else "N/A"

            all_data.append({
                "File Name": file_name,
                "Invoice Date": invoice_date,
                "Shop Name": shop_name,
                "Address": address,
                "Contact": contact,
                "State": state,
                "City": city,
                "GST": gst,
                "Employee Name": employee_name,
                "Discount Category": discount_category,
                "Employee Code": employee_code,
                "Designation": designation,
                "Product ID": product_id,
                "Product Name": product["Product Name"],
                "Quantity": product["Quantity"],
                "Rate": product["Rate"],
                "Amount": product["Amount"]
            })

        # Remove the temporary file
        os.remove(file_name)

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
