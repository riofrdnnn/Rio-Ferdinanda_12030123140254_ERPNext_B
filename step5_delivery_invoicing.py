import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_invoice
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils import nowdate, nowtime, flt

def run():
    print("=== MEMULAI TAHAP 5: PENGIRIMAN & PENJUALAN (DELIVERY, INVOICING & PAYMENT) ===")
    company_name = "PT Rio Ferdinanda Manufaktur"
    company = frappe.get_doc("Company", company_name)
    so_name = "SAL-ORD-2026-00001"
    fg_wh = "Gudang Barang Jadi - RF - RFM"

    # Setup Bank BCA account if not exists
    bank_parent = f"Bank Accounts - {company.abbr}"
    bca_acc_name = f"Bank BCA - {company.abbr}"
    if not frappe.db.exists("Account", bca_acc_name):
        frappe.get_doc({
            "doctype": "Account",
            "account_name": "Bank BCA",
            "company": company_name,
            "parent_account": bank_parent,
            "account_type": "Bank",
            "root_type": "Asset",
            "is_group": 0
        }).insert(ignore_permissions=True)
        print(f"Akun Bank BCA dibuat: {bca_acc_name}")
    frappe.db.commit()

    # 1. BUAT DELIVERY NOTE (SURAT JALAN)
    print("\n--- 1. Menerbitkan Delivery Note (Surat Jalan) ---")
    dn_doc = make_delivery_note(so_name)
    dn_doc.posting_date = nowdate()
    dn_doc.posting_time = nowtime()
    for it in dn_doc.items:
        it.warehouse = fg_wh
    dn_doc.insert(ignore_permissions=True)
    dn_doc.submit()
    frappe.db.commit()
    print(f"Delivery Note berhasil disubmit: {dn_doc.name}")
    print(f"Customer: {dn_doc.customer} | Item: {dn_doc.items[0].item_code} | Qty Dikirim: {dn_doc.items[0].qty} Nos")

    # Verifikasi Stok setelah Delivery Note
    item_code = "PROD-MEJA-01"
    sisa_fg = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": fg_wh}, "actual_qty")
    print(f"Sisa Stok di {fg_wh}: {sisa_fg} Nos (Stok berkurang sesuai barang terkirim)")

    # 2. BUAT SALES INVOICE (FAKTUR PENJUALAN)
    print("\n--- 2. Menerbitkan Sales Invoice (Faktur Penjualan) ---")
    si_doc = make_sales_invoice(dn_doc.name)
    si_doc.posting_date = nowdate()
    si_doc.posting_time = nowtime()
    si_doc.insert(ignore_permissions=True)
    si_doc.submit()
    frappe.db.commit()
    print(f"Sales Invoice berhasil disubmit: {si_doc.name}")
    print(f"Total Nilai Tagihan Piutang: Rp {si_doc.grand_total:,.2f} | Status: {si_doc.status}")

    # 3. BUAT PAYMENT ENTRY (PENERIMAAN PEMBAYARAN KAS/BANK)
    print("\n--- 3. Menerbitkan Payment Entry (Penerimaan Pelunasan) ---")
    pe = get_payment_entry("Sales Invoice", si_doc.name, bank_account=bca_acc_name)
    pe.posting_date = nowdate()
    pe.paid_to = bca_acc_name
    pe.reference_no = f"TRF-BCA-{nowdate()}"
    pe.reference_date = nowdate()
    pe.insert(ignore_permissions=True)
    pe.submit()
    frappe.db.commit()
    print(f"Payment Entry berhasil disubmit: {pe.name}")
    print(f"Diterima di Akun: {pe.paid_to} | Jumlah Diterima: Rp {pe.paid_amount:,.2f}")

    # Reload Sales Invoice to verify status
    si_doc.reload()
    print(f"Status Akhir Sales Invoice {si_doc.name}: {si_doc.status} (Outstanding: Rp {flt(si_doc.outstanding_amount):,.2f})")

    print("\n=== TAHAP 5 SELESAI DENGAN SUKSES! ===")

if __name__ == "__main__":
    run()
