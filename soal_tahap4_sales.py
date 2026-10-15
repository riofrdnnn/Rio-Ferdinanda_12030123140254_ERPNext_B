import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
from frappe.utils import nowdate, nowtime, add_to_date, flt

def run():
    print("=== MEMULAI TAHAP 4: KASUS 4 - PENJUALAN PRODUK JADI (SALES & FULFILLMENT) ===")
    company_name = "PT Terang Maju Manufaktur"
    abbr = "TMM"
    customer_name = "PT Mebel Indah"
    item_code = "FG-001"
    fg_wh = "Gudang Barang Jadi - TMM"

    company = frappe.get_doc("Company", company_name)

    # 0. SETUP AKUN SPESIFIK SESUAI KODE KASUS
    # 5110 - Harga Pokok Penjualan (HPP)
    cogs_acc = f"5110 - Harga Pokok Penjualan (HPP) - {abbr}"
    if not frappe.db.exists("Account", cogs_acc):
        exp_parent = f"Expenses - {abbr}"
        if frappe.db.exists("Account", f"Direct Expenses - {abbr}"):
            exp_parent = f"Direct Expenses - {abbr}"
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "5110 - Harga Pokok Penjualan (HPP)",
            "company": company_name,
            "parent_account": exp_parent,
            "account_type": "Cost of Goods Sold",
            "root_type": "Expense",
            "is_group": 0
        }).insert(ignore_permissions=True)
        print(f"Created account: {cogs_acc}")
    company.default_expense_account = cogs_acc

    # 1131 - Piutang Usaha (Debitur)
    ar_acc = f"1131 - Piutang Usaha (Debitur) - {abbr}"
    if not frappe.db.exists("Account", ar_acc):
        ar_parent = f"Current Assets - {abbr}"
        if frappe.db.exists("Account", f"Accounts Receivable - {abbr}"):
            ar_parent = f"Accounts Receivable - {abbr}"
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "1131 - Piutang Usaha (Debitur)",
            "company": company_name,
            "parent_account": ar_parent,
            "account_type": "Receivable",
            "root_type": "Asset",
            "is_group": 0
        }).insert(ignore_permissions=True)
        print(f"Created account: {ar_acc}")
    company.default_receivable_account = ar_acc

    # 4110 - Pendapatan Penjualan Produk Jadi
    income_acc = f"4110 - Pendapatan Penjualan Produk Jadi - {abbr}"
    if not frappe.db.exists("Account", income_acc):
        inc_parent = f"Income - {abbr}"
        if frappe.db.exists("Account", f"Direct Income - {abbr}"):
            inc_parent = f"Direct Income - {abbr}"
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "4110 - Pendapatan Penjualan Produk Jadi",
            "company": company_name,
            "parent_account": inc_parent,
            "account_type": "Income Account",
            "root_type": "Income",
            "is_group": 0
        }).insert(ignore_permissions=True)
        print(f"Created account: {income_acc}")
    company.default_income_account = income_acc

    company.save(ignore_permissions=True)
    frappe.db.commit()

    # 1. BUAT SALES ORDER (SO)
    print("\n--- 1. Membuat Sales Order (SO) ---")
    so = frappe.new_doc("Sales Order")
    so.company = company_name
    so.customer = customer_name
    so.transaction_date = nowdate()
    so.delivery_date = add_to_date(nowdate(), days=3)
    so.append("items", {
        "item_code": item_code,
        "qty": 5.0,
        "rate": 750000.0,
        "uom": "Unit",
        "stock_uom": "Unit",
        "warehouse": fg_wh,
        "delivery_date": add_to_date(nowdate(), days=3)
    })
    so.insert(ignore_permissions=True)
    so.submit()
    frappe.db.commit()
    print(f"Sales Order berhasil disubmit: {so.name}")
    print(f"Customer: {so.customer} | Total Nilai SO: Rp {so.grand_total:,.2f}")
    for it in so.items:
        print(f"  - {it.item_code} ({it.item_name}): {it.qty} {it.uom} @ Rp {it.rate:,.2f} = Rp {it.amount:,.2f}")

    # 2. BUAT DELIVERY NOTE (DN) PENGIRIMAN BARANG
    print("\n--- 2. Membuat Delivery Note (DN) Pengiriman Barang Jadi ---")
    dn_doc = make_delivery_note(so.name)
    dn_doc.posting_date = nowdate()
    dn_doc.posting_time = nowtime()
    for it in dn_doc.items:
        it.warehouse = fg_wh
        it.expense_account = cogs_acc
    dn_doc.insert(ignore_permissions=True)
    dn_doc.submit()
    frappe.db.commit()
    print(f"Delivery Note berhasil disubmit: {dn_doc.name}")
    print(f"Barang Keluar dari: {fg_wh} | Qty Dikirim: {dn_doc.items[0].qty} Unit")

    # Dampak Jurnal Delivery Note
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Delivery Note ---")
    dn_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (dn_doc.name,), as_dict=True)
    for gl in dn_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 3. BUAT SALES INVOICE (FAKTUR PENJUALAN)
    print("\n--- 3. Menerbitkan Sales Invoice (Faktur Penjualan) ---")
    si_doc = make_sales_invoice(dn_doc.name)
    si_doc.posting_date = nowdate()
    si_doc.posting_time = nowtime()
    si_doc.debit_to = ar_acc
    for it in si_doc.items:
        it.income_account = income_acc
        it.expense_account = cogs_acc
    si_doc.insert(ignore_permissions=True)
    si_doc.submit()
    frappe.db.commit()
    print(f"Sales Invoice berhasil disubmit: {si_doc.name}")
    print(f"Total Tagihan Piutang: Rp {si_doc.grand_total:,.2f} | Status: {si_doc.status}")

    # Dampak Jurnal Sales Invoice
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Sales Invoice ---")
    si_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (si_doc.name,), as_dict=True)
    for gl in si_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 4. VERIFIKASI SALDO BARANG JADI AKHIR
    sisa_fg = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": fg_wh}, "actual_qty")
    val_rate = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": fg_wh}, "valuation_rate")
    total_val = flt(sisa_fg) * flt(val_rate)
    print(f"\n--- Verifikasi Saldo di {fg_wh} ---")
    print(f"Item: {item_code} | Sisa Stok: {sisa_fg} Unit | Hrg Pokok: Rp {flt(val_rate):,.2f} | Total Nilai: Rp {total_val:,.2f}")

    print("\n=== TAHAP 4 SELESAI DENGAN SUKSES! KASUS 4 TUNTAS ===")

if __name__ == "__main__":
    run()
