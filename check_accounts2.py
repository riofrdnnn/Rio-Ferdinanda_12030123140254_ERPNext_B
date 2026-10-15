import frappe

def run():
    print("=== CHECK GL ENTRY FIELDS & STOCK ENTRY ACCOUNTS ===")
    company = "PT Rio Ferdinanda Manufaktur"
    
    # Check default accounts in Company
    comp_doc = frappe.get_doc("Company", company)
    for f in comp_doc.meta.fields:
        if "account" in f.fieldname:
            print(f"{f.fieldname}: {comp_doc.get(f.fieldname)}")
            
    # Check warehouses account
    whs = frappe.get_all("Warehouse", filters={"company": company}, fields=["name", "warehouse_name", "account"])
    for w in whs:
        print(f"Warehouse {w.name} -> account: {w.account}")
