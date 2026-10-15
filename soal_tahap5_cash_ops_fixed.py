import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils import nowdate, nowtime, flt

def run():
    print("=== MEMULAI PENYELESAIAN TAHAP 5: KASUS 5 ===")
    company_name = "PT Terang Maju Manufaktur"
    abbr = "TMM"
    company = frappe.get_doc("Company", company_name)
    si_name = "ACC-SINV-2026-00002"
    
    bca_acc = f"1112 - Bank BCA - {abbr}"
    util_acc = f"5310 - Beban Listrik & Utilitas Pabrik - {abbr}"

    # 1. CEK / JALANKAN PELUNASAN PIUTANG
    pe_name = frappe.db.get_value("Payment Entry", {"party": "PT Mebel Indah", "docstatus": 1}, "name")
    if not pe_name:
        print("\n--- 1. Pencatatan Pelunasan Piutang (Payment Entry) ---")
        pe = get_payment_entry("Sales Invoice", si_name, bank_account=bca_acc)
        pe.posting_date = nowdate()
        pe.paid_to = bca_acc
        pe.reference_no = f"TRF-BCA-MEBEL-{nowdate()}"
        pe.reference_date = nowdate()
        pe.insert(ignore_permissions=True)
        pe.submit()
        frappe.db.commit()
        pe_name = pe.name
        print(f"Payment Entry berhasil disubmit: {pe_name}")
    else:
        print(f"Payment Entry sudah ada & tersimpan: {pe_name}")

    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Pelunasan Piutang ---")
    pe_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (pe_name,), as_dict=True)
    for gl in pe_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 2. PEMBAYARAN BEBAN LISTRIK & UTILITAS PABRIK
    je_name = frappe.db.get_value("Journal Entry", {"user_remark": "Pembayaran beban listrik & utilitas operasional pabrik akhir bulan", "docstatus": 1}, "name")
    if not je_name:
        print("\n--- 2. Pencatatan Pembayaran Beban Listrik & Utilitas Pabrik ---")
        cost_center = company.cost_center or frappe.db.get_value("Cost Center", {"company": company_name, "is_group": 0}, "name")
        
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Bank Entry"
        je.company = company_name
        je.posting_date = nowdate()
        je.cheque_no = f"TRF-PLN-{nowdate()}"
        je.cheque_date = nowdate()
        je.user_remark = "Pembayaran beban listrik & utilitas operasional pabrik akhir bulan"
        
        je.append("accounts", {
            "account": util_acc,
            "debit_in_account_currency": 500000.0,
            "credit_in_account_currency": 0.0,
            "cost_center": cost_center
        })
        je.append("accounts", {
            "account": bca_acc,
            "debit_in_account_currency": 0.0,
            "credit_in_account_currency": 500000.0,
            "cost_center": cost_center
        })
        
        je.insert(ignore_permissions=True)
        je.submit()
        frappe.db.commit()
        je_name = je.name
        print(f"Journal Entry Beban Utilitas berhasil disubmit: {je_name}")
    else:
        print(f"Journal Entry sudah ada: {je_name}")

    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Beban Utilitas Pabrik ---")
    je_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (je_name,), as_dict=True)
    for gl in je_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 3. VERIFIKASI SALDO AKHIR BANK BCA
    bca_balance = frappe.db.sql("""
        select sum(debit - credit) as balance 
        from `tabGL Entry` 
        where account = %s and is_cancelled = 0
    """, (bca_acc,), as_dict=True)[0].balance or 0.0

    print(f"\n--- Saldo Akhir Rekening {bca_acc} ---")
    print(f"Saldo Akhir Kas/Bank: Rp {flt(bca_balance):,.2f} (Penerimaan Rp 3.750.000 - Pembayaran Beban Rp 500.000)")

    print("\n=== TAHAP 5 SELESAI DENGAN SUKSES! KASUS 5 TUNTAS ===")

if __name__ == "__main__":
    run()
