import frappe
from frappe.utils import nowdate, nowtime, now_datetime, add_to_date, flt
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry

def run():
    print("=== MEMULAI TAHAP 4: SIKLUS PRODUKSI (WORK ORDER & JOB CARDS) ===")
    company_name = "PT Rio Ferdinanda Manufaktur"
    company = frappe.get_doc("Company", company_name)
    
    customer_name = "Toko Furnitur Sejahtera Abadi"
    item_code = "PROD-MEJA-01"
    bom_no = "BOM-PROD-MEJA-01-001"
    order_qty = 10.0
    selling_price = 475000.0

    raw_wh = "Gudang Bahan Baku - RF - RFM"
    wip_wh = "Gudang WIP Produksi - RF - RFM"
    fg_wh = "Gudang Barang Jadi - RF - RFM"

    # 1. BUAT SALES ORDER
    print("\n--- 1. Membuat Sales Order ---")
    so = frappe.new_doc("Sales Order")
    so.company = company_name
    so.customer = customer_name
    so.transaction_date = nowdate()
    so.delivery_date = add_to_date(nowdate(), days=7)
    so.append("items", {
        "item_code": item_code,
        "qty": order_qty,
        "rate": selling_price,
        "delivery_date": add_to_date(nowdate(), days=7),
        "warehouse": fg_wh
    })
    so.insert(ignore_permissions=True)
    so.submit()
    frappe.db.commit()
    print(f"Sales Order berhasil dibuat & disubmit: {so.name}")
    print(f"Customer: {so.customer} | Total Nilai SO: Rp {so.grand_total:,.2f}")

    # 2. BUAT WORK ORDER
    print("\n--- 2. Membuat Work Order (SPK Produksi) ---")
    wo = frappe.new_doc("Work Order")
    wo.company = company_name
    wo.production_item = item_code
    wo.bom_no = bom_no
    wo.qty = order_qty
    wo.sales_order = so.name
    wo.source_warehouse = raw_wh
    wo.wip_warehouse = wip_wh
    wo.fg_warehouse = fg_wh
    wo.planned_start_date = now_datetime()
    wo.insert(ignore_permissions=True)
    wo.submit()
    frappe.db.commit()
    print(f"Work Order berhasil dibuat & disubmit: {wo.name}")
    print(f"Item: {wo.production_item} | Qty to Produce: {wo.qty} Nos")

    # 3. TRANSFER MATERIAL FOR MANUFACTURE (RAW -> WIP)
    print("\n--- 3. Transfer Bahan Baku ke Gudang WIP ---")
    se_transfer_dict = make_stock_entry(wo.name, "Material Transfer for Manufacture", qty=order_qty)
    se_transfer = frappe.get_doc(se_transfer_dict)
    se_transfer.posting_date = nowdate()
    se_transfer.posting_time = nowtime()
    se_transfer.insert(ignore_permissions=True)
    se_transfer.submit()
    frappe.db.commit()
    print(f"Stock Entry Transfer Bahan ke WIP berhasil: {se_transfer.name}")
    print(f"Dari: {raw_wh} -> Ke: {wip_wh}")
    for it in se_transfer.items:
        print(f"  - {it.item_code} ({it.item_name}): {it.qty} {it.uom}")

    # 4. EKSEKUSI JOB CARDS
    print("\n--- 4. Eksekusi & Penyelesaian Job Cards ---")
    job_cards = frappe.get_all(
        "Job Card", 
        filters={"work_order": wo.name}, 
        fields=["name", "operation", "workstation", "for_quantity"]
    )
    print(f"Ditemukan {len(job_cards)} Job Card untuk Work Order ini:")

    base_time = now_datetime()
    for idx, jc_info in enumerate(job_cards):
        jc = frappe.get_doc("Job Card", jc_info.name)
        start_time = add_to_date(base_time, minutes=idx * 30)
        end_time = add_to_date(start_time, minutes=20)
        
        jc.append("time_logs", {
            "from_time": start_time,
            "to_time": end_time,
            "time_in_mins": 20,
            "completed_qty": jc.for_quantity
        })
        jc.for_quantity = jc.for_quantity
        jc.docstatus = 0
        jc.save(ignore_permissions=True)
        jc.submit()
        frappe.db.commit()
        print(f"  [Job Card Selesai] {jc.name} | Operasi: {jc.operation} | WS: {jc.workstation} | Qty: {jc.for_quantity}")

    # 5. MANUFACTURE STOCK ENTRY (WIP -> FG)
    print("\n--- 5. Penyelesaian Produksi & Penerimaan Barang Jadi (Manufacture) ---")
    se_mfg_dict = make_stock_entry(wo.name, "Manufacture", qty=order_qty)
    se_mfg = frappe.get_doc(se_mfg_dict)
    se_mfg.posting_date = nowdate()
    se_mfg.posting_time = nowtime()
    se_mfg.insert(ignore_permissions=True)
    se_mfg.submit()
    frappe.db.commit()
    print(f"Stock Entry Manufacture berhasil: {se_mfg.name}")
    print(f"Hasil Produksi Diterima di: {fg_wh}")

    # Reload Work Order to check status
    wo.reload()
    print(f"Status Akhir Work Order {wo.name}: {wo.status} (Produced Qty: {wo.produced_qty})")

    # Verifikasi Saldo Barang Jadi
    fg_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": fg_wh}, "actual_qty")
    fg_val = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": fg_wh}, "valuation_rate")
    print(f"\n--- Verifikasi Stok Barang Jadi di {fg_wh} ---")
    print(f"Item: {item_code} | Stok Tersedia: {fg_qty} Nos | Valuation Rate (HPP Satuan): Rp {flt(fg_val):,.2f}")

    print("=== TAHAP 4 SELESAI DENGAN SUKSES! ===")

if __name__ == "__main__":
    run()
