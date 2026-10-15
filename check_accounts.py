import frappe

def run():
    company = frappe.get_doc("Company", "PT Rio Ferdinanda Manufaktur")
    print("expenses_included_in_valuation:", company.expenses_included_in_valuation)
    print("stock_adjustment_account:", company.stock_adjustment_account)
    print("default_inventory_account:", company.default_inventory_account)
    
    accs = frappe.get_all("Account", filters={"company": company.name}, fields=["name", "account_type", "root_type"])
    for a in accs:
        if any(term in a.name.lower() for term in ["valuation", "operating", "expense", "stock", "direct"]):
            print(a)
