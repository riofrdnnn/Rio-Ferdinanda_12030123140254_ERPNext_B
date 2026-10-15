import frappe
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
from frappe.utils import nowdate, nowtime, flt

def run():
    print("=== TEST MANUFACTURE SUBMISSION ===")
    wo_name = "MFG-WO-2026-00001"
    wo = frappe.get_doc("Work Order", wo_name)
    print("Work Order:", wo.name, "Status:", wo.status)
    
    # Try creating manufacture stock entry
    se_dict = make_stock_entry(wo.name, "Manufacture", qty=10.0)
    se = frappe.get_doc(se_dict)
    se.posting_date = nowdate()
    se.posting_time = nowtime()
    
    print("SE Type:", se.stock_entry_type, "Purpose:", se.purpose)
    print("Total incoming items:", len(se.items))
    for it in se.items:
        print(f"  - Item: {it.item_code}, s_wh: {it.s_warehouse}, t_wh: {it.t_warehouse}, qty: {it.qty}, basic_rate: {it.basic_rate}")
        
    se.insert(ignore_permissions=True)
    se.submit()
    frappe.db.commit()
    print(f"Stock Entry Manufacture BERHASIL DISUBMIT: {se.name}")
    
    wo.reload()
    print(f"Status Work Order {wo.name}: {wo.status} | Produced Qty: {wo.produced_qty}")
    
    fg_wh = "Gudang Barang Jadi - RF - RFM"
    item_code = "PROD-MEJA-01"
    fg_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": fg_wh}, "actual_qty")
    fg_val = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": fg_wh}, "valuation_rate")
    print(f"\n--- Verifikasi Stok Barang Jadi di {fg_wh} ---")
    print(f"Item: {item_code} | Stok Tersedia: {fg_qty} Nos | Valuation Rate: Rp {flt(fg_val):,.2f}")
