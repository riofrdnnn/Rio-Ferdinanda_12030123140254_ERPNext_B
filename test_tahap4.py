import frappe
from frappe.utils import nowdate, nowtime, add_to_date, now_datetime

def run():
    print("=== TEST PRODUCTION WORKFLOW INSPECTION ===")
    company_name = "PT Rio Ferdinanda Manufaktur"
    
    # Check customer
    cust = frappe.db.get_value("Customer", {"customer_name": "Toko Furnitur Sejahtera Abadi"}, "name")
    print("Customer:", cust)
    
    # Check item
    item = frappe.get_doc("Item", "PROD-MEJA-01")
    print("Item:", item.name, "Default BOM:", item.default_bom)
    
    # Check BOM
    bom = frappe.get_doc("BOM", "BOM-PROD-MEJA-01-001")
    print("BOM:", bom.name, "with_operations:", bom.with_operations)
