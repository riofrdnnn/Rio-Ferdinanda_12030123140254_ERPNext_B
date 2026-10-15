import frappe
from frappe.utils import flt

def run():
    print("=== MEMULAI TAHAP 2: KASUS 2 - PENYUSUNAN RESEP PRODUKSI (BOM) ===")
    company_name = "PT Terang Maju Manufaktur"
    item_code = "FG-001"

    # Periksa apakah BOM sudah ada
    existing_bom = frappe.db.get_value("BOM", {"item": item_code, "company": company_name, "is_active": 1, "docstatus": 1}, "name")
    if existing_bom:
        print(f"BOM aktif sudah ada: {existing_bom}")
        return

    bom = frappe.new_doc("BOM")
    bom.item = item_code
    bom.company = company_name
    bom.quantity = 1.0
    bom.uom = "Unit"
    bom.with_operations = 0
    bom.is_active = 1
    bom.is_default = 1
    bom.rm_cost_as_per = "Valuation Rate"
    bom.currency = "IDR"

    bom.append("items", {
        "item_code": "RM-001",
        "qty": 2.0,
        "uom": "Lembar",
        "rate": 150000.0
    })
    bom.append("items", {
        "item_code": "RM-002",
        "qty": 1.0,
        "uom": "Kaleng",
        "rate": 50000.0
    })

    bom.insert(ignore_permissions=True)
    bom.submit()
    frappe.db.commit()

    print(f"BOM berhasil dibuat dan disubmit: {bom.name}")
    print(f"Produk Jadi: {bom.item} ({bom.item_name}) | Qty: {bom.quantity} {bom.uom}")
    print(f"Total Biaya Bahan Baku Pokok (HPP Estimasi): Rp {bom.raw_material_cost:,.2f}")
    for it in bom.items:
        print(f"  - {it.item_code} ({it.item_name}): {it.qty} {it.uom} @ Rp {it.rate:,.2f} = Rp {it.amount:,.2f}")

    # Set default BOM di master Item FG-001
    frappe.db.set_value("Item", item_code, "default_bom", bom.name)
    frappe.db.commit()
    print(f"Default BOM pada master item {item_code} berhasil diset ke: {bom.name}")

    print("\n=== TAHAP 2 SELESAI DENGAN SUKSES! KASUS 2 TUNTAS ===")

if __name__ == "__main__":
    run()
