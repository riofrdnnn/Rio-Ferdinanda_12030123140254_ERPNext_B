import frappe

def run():
    company = "PT Terang Maju Manufaktur"
    accs = frappe.db.sql("""
        select name, account_type, root_type 
        from `tabAccount` 
        where company = %s and root_type = 'Asset'
        order by name
    """, (company,), as_dict=True)
    for a in accs:
        if any(w in a.name.lower() for w in ["stock", "persediaan", "wip", "hand"]):
            print(a)
            
    whs = frappe.get_all("Warehouse", filters={"company": company}, fields=["name", "warehouse_name", "account"])
    for w in whs:
        print(w)
