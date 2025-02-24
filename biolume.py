import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime

# Load data
Products = pd.read_csv('Invoice - Products.csv')
Outlet = pd.read_csv('Invoice - Outlet.csv')
Person = pd.read_csv('Invoice - Person.csv')

# Company Details
company_name = "ALLGEN TRADING INTERNATIONAL (OPC) PVT LTD"
company_address = """23B, Mastermind IV, Royal Palms, Aarey Milk colony,
Goregaon (EAST) Mumbai 400065.
GSTIN/UIN: 27AASCA7650C1ZJ
State Name : Mumbai, Code : 400065
"""
company_logo = 'ALLGEN TRADING logo.png'
photo_logo = 'ALLGEN_TRADING_gpay-removebg-preview.png'

bank_details = """
"""

# Custom PDF class
class PDF(FPDF):
    def header(self):
        if company_logo:
            self.image(company_logo, 10, 8, 33)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, company_name, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, company_address, align='C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Invoice', ln=True, align='C')
        self.line(10, 50, 200, 50)
        self.ln(5)

    def footer(self):
        if photo_logo:
            self.image(photo_logo, 10, 265, 33)
        self.set_y(-40)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 5, bank_details, align='R')
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# Generate Invoice
def generate_invoice(customer_name, gst_number, contact_number, address, selected_products, quantities, discount_category):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    current_date = datetime.now().strftime("%d-%m-%Y")

    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, f"Party: {customer_name}")
    pdf.cell(90, 10, f"Date: {current_date}", ln=True, align='R')
    pdf.cell(100, 10, f"GSTIN/UN: {gst_number}")
    pdf.cell(90, 10, f"Contact: {contact_number}", ln=True, align='R')

    pdf.cell(100, 10, "Address: ", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 10, address)
    pdf.ln(10)

    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(10, 8, "S.No", border=1, align='C', fill=True)
    pdf.cell(60, 8, "Description of Goods", border=1, align='C', fill=True)
    pdf.cell(20, 8, "HSN/SAC", border=1, align='C', fill=True)
    pdf.cell(20, 8, "GST Rate", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Qty", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Rate", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Amount", border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_font("Arial", '', 9)
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = Products[Products['Product Name'] == product].iloc[0]
        quantity = quantities[idx]

        if discount_category in product_data:
            unit_price = float(product_data[discount_category])  # Use discount category price
        else:
            unit_price = float(product_data['Price'])

        item_total_price = unit_price * quantity

        pdf.cell(10, 8, str(idx + 1), border=1)
        pdf.cell(60, 8, product, border=1)
        pdf.cell(20, 8, "3304", border=1, align='C')
        pdf.cell(20, 8, "18%", border=1, align='C')
        pdf.cell(20, 8, str(quantity), border=1, align='C')
        pdf.cell(20, 8, f"{unit_price:.2f}", border=1, align='R')
        pdf.cell(20, 8, f"{item_total_price:.2f}", border=1, align='R')
        total_price += item_total_price
        pdf.ln()

    pdf.ln(5)
    tax_rate = 0.18
    tax_amount = total_price * tax_rate
    grand_total = math.ceil(total_price + tax_amount)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(160, 10, "CGST (9%)", border=0, align='R')
    pdf.cell(30, 10, f"{tax_amount / 2:.2f}", border=1, align='R')
    pdf.ln()
    pdf.cell(160, 10, "SGST (9%)", border=0, align='R')
    pdf.cell(30, 10, f"{tax_amount / 2:.2f}", border=1, align='R')
    pdf.ln()
    pdf.cell(160, 10, "Grand Total", border=0, align='R')
    pdf.cell(30, 10, f"{grand_total} INR", border=1, align='R')
    pdf.ln(20)

    return pdf

# Streamlit UI
st.title("Biolume + ALLGEN TRADING: Billing System")

# Employee Selection
st.subheader("Employee Details")
employee_names = Person['Employee Name'].tolist()
selected_employee = st.selectbox("Select Employee", employee_names)

# Fetch Discount Category
discount_category = Person[Person['Employee Name'] == selected_employee]['Discount Category'].values[0]

# Product Selection
st.subheader("Product Details")
product_names = Products['Product Name'].tolist()
selected_products = st.multiselect("Select Products", product_names)


discounted_prices = []
if selected_products:
    for product in selected_products:
        product_data = Products[Products['Product Name'] == product].iloc[0]
        if discount_category in product_data:  # Ensure column exists
            discounted_price = product_data[discount_category]
        else:
            discounted_price = product_data['Price']  # Default to normal price
        discounted_prices.append(discounted_price)

# Outlet Selection
st.subheader("Outlet Details")
outlet_names = Outlet['Shop Name'].tolist()
selected_outlet = st.selectbox("Select Outlet", outlet_names)

# Fetch Outlet Details
outlet_details = Outlet[Outlet['Shop Name'] == selected_outlet].iloc[0]

# Display Details
st.subheader("Selected Details")
st.write(f"Employee Name: {selected_employee}")
st.write(f"Discount Category: {discount_category}")
st.write("Selected Products:")
for product, price in zip(selected_products, discounted_prices):
    st.write(f"- {product}: {price}")
st.write(f"Selected Outlet: {selected_outlet}")
st.write(f"Outlet Address: {outlet_details['Address']}")
st.write(f"Outlet GST: {outlet_details['GST']}")

# Generate Invoice button
if st.button("Generate Invoice"):
    if selected_employee and selected_products and selected_outlet:
        customer_name = selected_outlet
        gst_number = outlet_details['GST']
        contact_number = outlet_details['Contact']
        address = outlet_details['Address']
        quantities = [1] * len(selected_products)  # Assuming quantity 1 for each product

        pdf = generate_invoice(customer_name, gst_number, contact_number, address, selected_products, quantities, discount_category)
        pdf_file = f"invoice_{customer_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("Download Invoice", f, file_name=pdf_file)
    else:
        st.error("Please fill all fields and select products.")
