import frappe

def run():
    print("=== MEMULAI TAHAP 0: SETUP MASTER DATA (SOAL PRAKTIKUM PT TMM) ===")
    company_name = "PT Terang Maju Manufaktur"
    abbr = "TMM"
    
    company = frappe.get_doc("Company", company_name)
    print(f"Company: {company.name} ({abbr})")

    # Set default operating & stock accounts
    exp_val = f"Expenses Included In Valuation - {abbr}"
    if frappe.db.exists("Account", exp_val):
        company.default_operating_cost_account = exp_val
        company.expenses_added_to_stock_account = exp_val
        company.save(ignore_permissions=True)
    frappe.db.commit()

    # Customer Group non-group
    cg_name = "Commercial"
    if not frappe.db.exists("Customer Group", cg_name):
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": cg_name,
            "parent_customer_group": "All Customer Groups",
            "is_group": 0
        }).insert(ignore_permissions=True)

    customer_name = "PT Mebel Indah"
    default_territory = "Indonesia" if frappe.db.exists("Territory", "Indonesia") else "All Territories"
    if not frappe.db.exists("Customer", customer_name):
        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_group": cg_name,
            "customer_type": "Company",
            "territory": default_territory
        }).insert(ignore_permissions=True)
        print(f"Customer created: {customer_name}")
    else:
        print(f"Customer exists: {customer_name}")
    frappe.db.commit()

    # SETUP ACCOUNTS (BANK BCA & BEBAN LISTRIK)
    bank_parent = f"Bank Accounts - {abbr}"
    bca_acc = f"Bank BCA - {abbr}"
    if not frappe.db.exists("Account", bca_acc):
        if frappe.db.exists("Account", bank_parent):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": "Bank BCA",
                "company": company_name,
                "parent_account": bank_parent,
                "account_type": "Bank",
                "root_type": "Asset",
                "is_group": 0
            }).insert(ignore_permissions=True)
            print(f"Account created: {bca_acc}")
    else:
        print(f"Account exists: {bca_acc}")

    # Beban Listrik & Utilitas Pabrik
    exp_parent = f"Indirect Expenses - {abbr}"
    if not frappe.db.exists("Account", exp_parent):
        exp_parent = f"Expenses - {abbr}"
    
    util_acc = f"Beban Listrik & Utilitas Pabrik - {abbr}"
    if not frappe.db.exists("Account", util_acc):
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "Beban Listrik & Utilitas Pabrik",
            "company": company_name,
            "parent_account": exp_parent,
            "account_type": "Expense Account",
            "root_type": "Expense",
            "is_group": 0
        }).insert(ignore_permissions=True)
        print(f"Account created: {util_acc}")
    else:
        print(f"Account exists: {util_acc}")
    frappe.db.commit()

    print("\n=== TAHAP 0 SELESAI DENGAN SUKSES! DATA MASTER PT TMM SIAP ===")

if __name__ == "__main__":
    run()
