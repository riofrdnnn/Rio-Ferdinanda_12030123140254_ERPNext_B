import frappe
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry
from frappe.utils import nowdate, nowtime, now_datetime, flt

def run():
    print("=== MEMULAI TAHAP 3: KASUS 3 - PROSES PRODUKSI & PERGERAKAN STOK ===")
    company_name = "PT Terang Maju Manufaktur"
    item_code = "FG-001"
    bom_no = "BOM-FG-001-001"
    order_qty = 10.0

    raw_wh = "Gudang Bahan Baku - TMM"
    wip_wh = "Gudang WIP - TMM"
    fg_wh = "Gudang Barang Jadi - TMM"

    # 1. BUAT WORK ORDER (SPK PRODUKSI)
    print("\n--- 1. Menerbitkan Work Order (SPK Produksi) ---")
    wo = frappe.new_doc("Work Order")
    wo.company = company_name
    wo.production_item = item_code
    wo.bom_no = bom_no
    wo.qty = order_qty
    wo.source_warehouse = raw_wh
    wo.wip_warehouse = wip_wh
    wo.fg_warehouse = fg_wh
    wo.planned_start_date = now_datetime()
    wo.insert(ignore_permissions=True)
    wo.submit()
    frappe.db.commit()
    print(f"Work Order berhasil disubmit: {wo.name}")
    print(f"Produk: {wo.production_item} | Qty: {wo.qty} Unit | BOM: {wo.bom_no}")

    # 2. TRANSFER MATERIAL TO WIP (STOCK ENTRY)
    print("\n--- 2. Transfer Bahan Baku ke WIP (Material Transfer to WIP) ---")
    se_trf_dict = make_stock_entry(wo.name, "Material Transfer for Manufacture", qty=order_qty)
    se_trf = frappe.get_doc(se_trf_dict)
    se_trf.posting_date = nowdate()
    se_trf.posting_time = nowtime()
    se_trf.insert(ignore_permissions=True)
    se_trf.submit()
    frappe.db.commit()
    print(f"Stock Entry Transfer ke WIP berhasil disubmit: {se_trf.name}")
    print(f"Total Nilai Transfer Bahan: Rp {se_trf.total_amount:,.2f}")
    for it in se_trf.items:
        print(f"  - {it.item_code} ({it.item_name}): {it.qty} {it.uom} @ Rp {it.basic_rate:,.2f} = Rp {it.amount:,.2f}")

    # Dampak Jurnal Transfer ke WIP
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Transfer to WIP ---")
    trf_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (se_trf.name,), as_dict=True)
    for gl in trf_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 3. MANUFACTURE (FINISH PRODUKSI)
    print("\n--- 3. Penyelesaian Produksi & Penerimaan Barang Jadi (Manufacture) ---")
    se_mfg_dict = make_stock_entry(wo.name, "Manufacture", qty=order_qty)
    se_mfg = frappe.get_doc(se_mfg_dict)
    se_mfg.posting_date = nowdate()
    se_mfg.posting_time = nowtime()
    se_mfg.insert(ignore_permissions=True)
    se_mfg.submit()
    frappe.db.commit()
    print(f"Stock Entry Manufacture berhasil disubmit: {se_mfg.name}")
    print(f"Hasil Produksi Selesai: 10 Unit {item_code} diterima di {fg_wh}")

    # Dampak Jurnal Manufacture
    print("\n--- Dampak Jurnal Akuntansi (GL Entry) Manufacture ---")
    mfg_gl = frappe.db.sql("""
        select account, debit, credit 
        from `tabGL Entry` 
        where voucher_no = %s and is_cancelled = 0
    """, (se_mfg.name,), as_dict=True)
    for gl in mfg_gl:
        print(f"  Account: {gl.account:<50} | Debet: Rp {gl.debit:>12,.2f} | Kredit: Rp {gl.credit:>12,.2f}")

    # 4. STATUS WORK ORDER & STOK AKHIR
    wo.reload()
    print(f"\nStatus Akhir Work Order {wo.name}: {wo.status} (Produced Qty: {wo.produced_qty})")

    print("\n--- Verifikasi Saldo Persediaan ---")
    for wh_name, codes in [(raw_wh, ["RM-001", "RM-002"]), (wip_wh, ["RM-001", "RM-002"]), (fg_wh, ["FG-001"])]:
        print(f"[GUDANG]: {wh_name}")
        for code in codes:
            qty = frappe.db.get_value("Bin", {"item_code": code, "warehouse": wh_name}, "actual_qty") or 0.0
            rate = frappe.db.get_value("Bin", {"item_code": code, "warehouse": wh_name}, "valuation_rate") or 0.0
            print(f"  Item: {code:<8} | Qty: {qty:<6} | Hrg Satuan: Rp {flt(rate):>10,.2f} | Nilai: Rp {flt(qty)*flt(rate):>12,.2f}")

    print("\n=== TAHAP 3 SELESAI DENGAN SUKSES! KASUS 3 TUNTAS ===")

if __name__ == "__main__":
    run()
