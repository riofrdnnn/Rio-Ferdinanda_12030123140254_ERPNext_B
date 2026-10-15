import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils import nowdate, nowtime, flt

def run():
    print("=== MEMULAI TAHAP 5: KASUS 5 - PELUNASAN KAS & BIAYA OPERASIONAL PABRIK ===")
    company_name = "PT Terang Maju Manufaktur"
    abbr = "TMM"
    company = frappe.get_doc("Company", company_name)
    si_name = "ACC-SINV-2026-00002"
    
    # 0. SETUP / RENAME AKUN SESUAI KODE SOAL
    # Akun Bank BCA
    bca_acc = f"1112 - Bank BCA - {abbr}"
    if not frappe.db.exists("Account", bca_acc):
        old_bca = f"Bank BCA - {abbr}"
        if frappe.db.exists("Account", old_bca):
            frappe.rename_doc("Account", old_bca, bca_acc, force=True)
            print(f"Renamed account to: {bca_acc}")
        else:
            bank_parent = f"Bank Accounts - {abbr}"
            frappe.get_doc({
                "doctype": "Account",
                "account_name": "1112 - Bank BCA",
                "company": company_name,
                "parent_account": bank_parent,
                "account_type": "Bank",
                "root_type": "Asset",
                "is_group": 0
            }).insert(ignore_permissions=True)
            print(f"Created account: {bca_acc}")

    # Akun Beban Listrik & Utilitas Pabrik
    util_acc = f"5310 - Beban Listrik & Utilitas Pabrik - {abbr}"
    if not frappe.db.exists("Account", util_acc):
        old_util = f"Beban Listrik & Utilitas Pabrik - {abbr}"
        if frappe.db.exists("Account", old_util):
            frappe.rename_doc("Account", old_util, util_acc, force=True)
            print(f"Renamed account to: {util_acc}")
        else:
            exp_parent = f"Expenses - {abbr}"
            if frappe.db.exists("Account", f"Indirect Expenses - {abbr}"):
                exp_parent = f"Indirect Expenses - {abbr}"
            frappe.get_doc({
                "doctype": "Account",
                "account_name": "5310 - Beban Listrik & Utilitas Pabrik",
                "company": company_name,
                "parent_account": exp_parent,
                "account_type": "Expense Account",
                "root_type": "Expense",
                "is_group": 0
            }).insert(ignore_permissions=True)
            print(f"Created account: {util_acc}")

    frappe.db.commit()

    # 1. PELUNASAN PIUTANG DARI PT MEBEL INDAH (PAYMENT ENTRY)
    print("\n--- 1. Pencatatan Pelunasan Piutang (Payment Entry) ---")
    pe = get_payment_entry("Sales Invoice", si_name, bank_account=bca_acc)
    pe.posting_date = nowdate()
    pe.paid_to = bca_acc
    pe.reference_no = f"TRF-BCA-MEBEL-{nowdate()}"
    pe.reference_date = nowdate()
    pe.insert(ignore_permissions=True)
    pe.submit()
    frappe.db.commit()
    print(f"Payment Entry berhasil disubmit: {pe.name}")
    print(f"Dari Pelanggan: {pe.party_name} | Diterima di: {pe.paid_to} | Jumlah: Rp {pe.paid_amount:,.2f}")

    # Dampak Jurnal Pelunasan Piutang
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Pelunasan Piutang ---")
    pe_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (pe.name,), as_dict=True)
    for gl in pe_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 2. PEMBAYARAN BEBAN LISTRIK & UTILITAS PABRIK (JOURNAL ENTRY)
    print("\n--- 2. Pencatatan Pembayaran Beban Listrik & Utilitas Pabrik ---")
    cost_center = company.cost_center or frappe.db.get_value("Cost Center", {"company": company_name, "is_group": 0}, "name")
    
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Bank Entry"
    je.company = company_name
    je.posting_date = nowdate()
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
    print(f"Journal Entry Beban Utilitas berhasil disubmit: {je.name}")
    print(f"Dibayar dari: {bca_acc} | Beban: {util_acc} | Jumlah: Rp 500,000.00")

    # Dampak Jurnal Beban Utilitas
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Beban Utilitas Pabrik ---")
    je_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (je.name,), as_dict=True)
    for gl in je_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 3. VERIFIKASI SALDO AKHIR BANK BCA
    bca_balance = frappe.db.sql("""
        select sum(debit - credit) as balance 
        from `tabGL Entry` 
        where account = %s and is_cancelled = 0
    """, (bca_acc,), as_dict=True)[0].balance or 0.0

    print(f"\n--- Saldo Akhir Rekening {bca_acc} ---")
    print(f"Saldo Akhir: Rp {flt(bca_balance):,.2f} (Penerimaan Rp 3.750.000 - Pengeluaran Beban Rp 500.000)")

    print("\n=== TAHAP 5 SELESAI DENGAN SUKSES! KASUS 5 TUNTAS ===")

if __name__ == "__main__":
    run()
