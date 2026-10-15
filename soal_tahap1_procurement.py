import frappe
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
from frappe.utils import nowdate, nowtime, add_to_date, flt

def run():
    print("=== MEMULAI TAHAP 1: KASUS 1 - PENGADAAN BAHAN BAKU (PROCUREMENT & STOCK) ===")
    company_name = "PT Terang Maju Manufaktur"
    company = frappe.get_doc("Company", company_name)
    supplier_name = "CV Kayu Nusantara"
    wh_raw = "Gudang Bahan Baku - TMM"

    # Pastikan Supplier ada
    if not frappe.db.exists("Supplier", supplier_name):
        sg = "Raw Material" if frappe.db.exists("Supplier Group", "Raw Material") else "All Supplier Groups"
        frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": supplier_name,
            "supplier_group": sg,
            "supplier_type": "Company",
            "country": "Indonesia"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Supplier dibuat: {supplier_name}")
    else:
        print(f"Supplier ditemukan: {supplier_name}")

    # 1. BUAT PURCHASE ORDER (PO)
    print("\n--- 1. Membuat Purchase Order (PO) ---")
    po = frappe.new_doc("Purchase Order")
    po.company = company_name
    po.supplier = supplier_name
    po.transaction_date = nowdate()
    po.schedule_date = add_to_date(nowdate(), days=3)
    
    po.append("items", {
        "item_code": "RM-001",
        "qty": 100.0,
        "rate": 150000.0,
        "uom": "Lembar",
        "stock_uom": "Lembar",
        "schedule_date": add_to_date(nowdate(), days=3),
        "warehouse": wh_raw
    })
    po.append("items", {
        "item_code": "RM-002",
        "qty": 20.0,
        "rate": 50000.0,
        "uom": "Kaleng",
        "stock_uom": "Kaleng",
        "schedule_date": add_to_date(nowdate(), days=3),
        "warehouse": wh_raw
    })
    
    po.insert(ignore_permissions=True)
    po.submit()
    frappe.db.commit()
    print(f"Purchase Order berhasil disubmit: {po.name}")
    print(f"Supplier: {po.supplier} | Total Nilai PO: Rp {po.grand_total:,.2f}")
    for it in po.items:
        print(f"  - {it.item_code} ({it.item_name}): {it.qty} {it.uom} @ Rp {it.rate:,.2f} = Rp {it.amount:,.2f}")

    # 2. BUAT PURCHASE RECEIPT (GRN)
    print("\n--- 2. Membuat Purchase Receipt (GRN) Penerimaan Barang ---")
    pr_doc = make_purchase_receipt(po.name)
    pr_doc.posting_date = nowdate()
    pr_doc.posting_time = nowtime()
    for it in pr_doc.items:
        it.warehouse = wh_raw
    pr_doc.insert(ignore_permissions=True)
    pr_doc.submit()
    frappe.db.commit()
    print(f"Purchase Receipt (GRN) berhasil disubmit: {pr_doc.name}")
    print(f"Barang Diterima di: {wh_raw}")

    # Verifikasi Jurnal Akuntansi GRN
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Purchase Receipt ---")
    pr_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (pr_doc.name,), as_dict=True)
    for gl in pr_gl:
        print(f"  Account: {gl.account:<40} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 3. BUAT PURCHASE INVOICE (FAKTUR PEMBELIAN)
    print("\n--- 3. Menerbitkan Purchase Invoice (Faktur Pembelian) ---")
    pi_doc = make_purchase_invoice(pr_doc.name)
    pi_doc.posting_date = nowdate()
    pi_doc.posting_time = nowtime()
    pi_doc.insert(ignore_permissions=True)
    pi_doc.submit()
    frappe.db.commit()
    print(f"Purchase Invoice berhasil disubmit: {pi_doc.name}")
    print(f"Total Nilai Tagihan Utang: Rp {pi_doc.grand_total:,.2f} | Status: {pi_doc.status}")

    # Verifikasi Jurnal Akuntansi PI
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Purchase Invoice ---")
    pi_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (pi_doc.name,), as_dict=True)
    for gl in pi_gl:
        print(f"  Account: {gl.account:<40} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 4. VERIFIKASI SALDO STOK DI GUDANG
    print(f"\n--- Verifikasi Saldo Fisik di {wh_raw} ---")
    for code in ["RM-001", "RM-002"]:
        actual_qty = frappe.db.get_value("Bin", {"item_code": code, "warehouse": wh_raw}, "actual_qty")
        val_rate = frappe.db.get_value("Bin", {"item_code": code, "warehouse": wh_raw}, "valuation_rate")
        stock_val = flt(actual_qty) * flt(val_rate)
        print(f"Item: {code:<8} | Qty: {actual_qty} | Valuation Rate: Rp {flt(val_rate):,.2f} | Total Nilai: Rp {stock_val:,.2f}")

    print("\n=== TAHAP 1 SELESAI DENGAN SUKSES! KASUS 1 TUNTAS ===")

if __name__ == "__main__":
    run()
