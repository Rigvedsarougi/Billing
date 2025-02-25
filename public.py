from PyPDF2 import PdfReader
import re

def extract_invoice_data(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    data = {}
    
    # Extracting invoice details
    invoice_no_match = re.search(r'Invoice No[:\s]+(\S+)', text)
    date_match = re.search(r'Date[:\s]+(\S+)', text)
    gst_match = re.search(r'GST[:\s]+(\S+)', text)
    employee_match = re.search(r'Sales Person[:\s]+(.+)', text)
    
    data['Invoice No'] = invoice_no_match.group(1) if invoice_no_match else None
    data['Date'] = date_match.group(1) if date_match else None
    data['GST'] = gst_match.group(1) if gst_match else None
    data['Employee Name'] = employee_match.group(1).strip() if employee_match else None
    
    # Extract product details
    product_lines = re.findall(r'(Product Name[:\s]+.*?Quantity[:\s]+(\d+).*?Rate[:\s]+([0-9]+\.?[0-9]*))', text, re.DOTALL)
    
    products = []
    for line in product_lines:
        product_details = line[0].split('\n')
        product_name = product_details[0].replace('Product Name:', '').strip()
        quantity = int(line[1])
        rate = float(line[2])
        
        products.append({
            'Product Name': product_name,
            'Quantity': quantity,
            'Rate': rate
        })
    
    data['Products'] = products
    
    # Extracting tax percentage safely
    tax_match = re.search(r'Tax[:\s]+(\d+)%', text)
    if tax_match:
        data['Tax'] = float(tax_match.group(1))  # Convert to float safely
    else:
        data['Tax'] = None
    
    return data

# Example usage
invoice_data = extract_invoice_data("invoice.pdf")
print(invoice_data)
