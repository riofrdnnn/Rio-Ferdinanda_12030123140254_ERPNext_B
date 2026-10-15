import frappe

def run():
    accs = frappe.db.sql("""
        select name, account_type, root_type, is_group 
        from `tabAccount` 
        where company = 'PT Rio Ferdinanda Manufaktur'
        order by root_type, name
    """, as_dict=True)
    for a in accs:
        print(f"[{a.root_type}] {a.name} (type: {a.account_type}, is_group: {a.is_group})")
