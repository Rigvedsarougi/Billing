import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime

# Load data
Products = pd.read_csv('/content/Invoice - Products.csv')
Outlet = pd.read_csv('/content/Invoice - Outlet.csv')
Person = pd.read_csv('/content/Invoice - Person.csv')

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
HDFC Bank, Jogeshwari East Mumbai, Maharashtra: Ac No 50200045580571, IFSC code HDFC0001019 
Mobile - 9819067929 / GPay / PhonePe 
Delivery/Payment Support: +918657927412 Customer Support: +919311662808
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
def generate_invoice(customer_name, gst_number, contact_number, address, selected_products, quantities, discounts):
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
    pdf.cell(20, 8, "Disc. %", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Amount", border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", '', 9)
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = Products[Products['Product Name'] == product].iloc[0]
        quantity = quantities[idx]
        unit_price = float(product_data['Price'])
        discount = discounts[idx]  # Use the provided discount
        after_disc = unit_price * (1 - discount / 100)  # Calculate discounted price
        item_total_price = after_disc * quantity

        pdf.cell(10, 8, str(idx + 1), border=1)
        pdf.cell(60, 8, product, border=1)
        pdf.cell(20, 8, "3304", border=1, align='C')
        pdf.cell(20, 8, "18%", border=1, align='C')
        pdf.cell(20, 8, str(quantity), border=1, align='C')
        pdf.cell(20, 8, f"{unit_price:.2f}", border=1, align='R')
        pdf.cell(20, 8, f"{discount:.1f}%", border=1, align='R')
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
employee_name = st.selectbox("Select Employee", Person['Employee Name'].tolist())

# Fetch Discount Category
discount_category = Person[Person['Employee Name'] == employee_name]['Discount Category'].values[0]

# Product Selection
st.subheader("Product Details")
selected_products = st.multiselect("Select Products", Products['Product Name'].tolist())

# Fetch Discounted Price
discounted_prices = []
if selected_products:
    for product in selected_products:
        product_data = Products[Products['Product Name'] == product].iloc[0]
        discounted_price = product_data[discount_category]
        discounted_prices.append(discounted_price)

# Outlet Selection
st.subheader("Outlet Details")
outlet_name = st.selectbox("Select Outlet", Outlet['Shop Name'].tolist())

# Fetch Outlet Details
outlet_details = Outlet[Outlet['Shop Name'] == outlet_name].iloc[0]

# Display Details
st.subheader("Selected Details")
st.write(f"Employee Name: {employee_name}")
st.write(f"Discount Category: {discount_category}")
st.write("Selected Products and Discounted Prices:")
for product, price in zip(selected_products, discounted_prices):
    st.write(f"{product}: {price}")
st.write(f"Outlet Name: {outlet_details['Shop Name']}")
st.write(f"Outlet Address: {outlet_details['Address']}")
st.write(f"Outlet GST: {outlet_details['GST']}")

# Generate Invoice button
if st.button("Generate Invoice"):
    if employee_name and selected_products and outlet_name:
        # Generate invoice logic here
        st.success("Invoice generated successfully!")
    else:
        st.error("Please fill all fields and select products.")
