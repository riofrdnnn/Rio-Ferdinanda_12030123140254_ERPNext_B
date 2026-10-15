import frappe

def run():
    company_name = "PT Rio Ferdinanda Manufaktur"
    company = frappe.get_doc("Company", company_name)
    print("Company:", company.name)
    print("Default Stock Adjustment Account:", company.stock_adjustment_account)
    print("Default Inventory Account:", company.default_inventory_account)
    
    whs = frappe.get_all("Warehouse", filters={"company": company_name}, fields=["name", "warehouse_name", "account"])
    for w in whs:
        print("Warehouse:", w)
