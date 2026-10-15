import frappe
from frappe.utils import nowdate

def run():
    company = "PT Terang Maju Manufaktur"
    abbr = "TMM"
    
    # Check balance of Stock In Hand - TMM
    sih = f"Stock In Hand - {abbr}"
    raw_acc = f"1141 - Persediaan Bahan Baku - {abbr}"
    
    sih_bal = frappe.db.sql("""
        select sum(debit - credit) as bal 
        from `tabGL Entry` 
        where account = %s and is_cancelled = 0
    """, (sih,), as_dict=True)[0].bal or 0.0
    print(f"Current balance of {sih}: Rp {sih_bal:,.2f}")
    
    if sih_bal > 0:
        cost_center = frappe.db.get_value("Company", company, "cost_center") or frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.company = company
        je.posting_date = nowdate()
        je.user_remark = "Reklasifikasi saldo awal penerimaan barang ke akun 1141 Persediaan Bahan Baku"
        
        je.append("accounts", {
            "account": raw_acc,
            "debit_in_account_currency": sih_bal,
            "credit_in_account_currency": 0.0,
            "cost_center": cost_center
        })
        je.append("accounts", {
            "account": sih,
            "debit_in_account_currency": 0.0,
            "credit_in_account_currency": sih_bal,
            "cost_center": cost_center
        })
        
        je.insert(ignore_permissions=True)
        je.submit()
        frappe.db.commit()
        print(f"Reclassification Journal Entry submitted: {je.name}")
        
    # Check new balance of 1141
    raw_bal = frappe.db.sql("""
        select sum(debit - credit) as bal 
        from `tabGL Entry` 
        where account = %s and is_cancelled = 0
    """, (raw_acc,), as_dict=True)[0].bal or 0.0
    print(f"New balance of {raw_acc}: Rp {raw_bal:,.2f}")
