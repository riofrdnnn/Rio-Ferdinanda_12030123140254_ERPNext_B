import frappe
from frappe.utils import flt, nowdate, nowtime

def run():
    print("=== MEMULAI TAHAP 3: INPUT SALDO AWAL PERSEDIAAN (OPENING STOCK) ===")
    company_name = "PT Rio Ferdinanda Manufaktur"
    company = frappe.get_doc("Company", company_name)
    
    target_warehouse = "Gudang Bahan Baku - RF - RFM"
    if not frappe.db.exists("Warehouse", target_warehouse):
        # Fallback check
        wh = frappe.db.get_value("Warehouse", {"warehouse_name": "Gudang Bahan Baku - RF", "company": company_name}, "name")
        if wh:
            target_warehouse = wh
        else:
            raise Exception(f"Gudang {target_warehouse} tidak ditemukan!")

    cost_center = company.cost_center or frappe.db.get_value("Cost Center", {"company": company_name, "is_group": 0}, "name")
    expense_account = company.stock_adjustment_account or frappe.db.get_value("Account", {"account_type": "Stock Adjustment", "company": company_name}, "name")

    items_data = [
        {"item_code": "RAW-KAYU-01", "qty": 50.0, "rate": 85000.0},
        {"item_code": "RAW-PIPA-01", "qty": 30.0, "rate": 110000.0},
        {"item_code": "RAW-BAUT-01", "qty": 500.0, "rate": 1000.0},
        {"item_code": "RAW-CAT-01", "qty": 20.0, "rate": 45000.0},
        {"item_code": "RAW-KAKI-01", "qty": 200.0, "rate": 2500.0},
        {"item_code": "RAW-AMPLAS-01", "qty": 50.0, "rate": 4000.0}
    ]

    # Check if a submitted opening Stock Entry for this company and warehouse already exists
    existing = frappe.db.sql("""
        select se.name from `tabStock Entry` se
        join `tabStock Entry Detail` sed on sed.parent = se.name
        where se.company = %s and se.purpose = 'Material Receipt' and sed.t_warehouse = %s and se.docstatus = 1
    """, (company_name, target_warehouse), as_dict=True)

    if existing:
        print(f"Opening stock entry already exists: {existing[0].name}")
        return

    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Receipt"
    se.purpose = "Material Receipt"
    se.company = company_name
    se.to_warehouse = target_warehouse
    se.posting_date = nowdate()
    se.posting_time = nowtime()

    for item in items_data:
        uom = frappe.db.get_value("Item", item["item_code"], "stock_uom")
        se.append("items", {
            "item_code": item["item_code"],
            "qty": item["qty"],
            "uom": uom,
            "stock_uom": uom,
            "conversion_factor": 1.0,
            "t_warehouse": target_warehouse,
            "basic_rate": item["rate"],
            "cost_center": cost_center,
            "expense_account": expense_account
        })

    se.insert(ignore_permissions=True)
    se.submit()
    frappe.db.commit()
    print(f"Stock Entry Saldo Awal berhasil disubmit: {se.name}")
    print(f"Total Nilai Persediaan Ditambahkan: Rp {se.total_amount:,.2f}")

    # Check stock balances
    print("\n--- Verifikasi Saldo Stok Bahan Baku ---")
    for item in items_data:
        actual_qty = frappe.db.get_value(
            "Bin", 
            {"item_code": item["item_code"], "warehouse": target_warehouse}, 
            "actual_qty"
        )
        val_rate = frappe.db.get_value(
            "Bin", 
            {"item_code": item["item_code"], "warehouse": target_warehouse}, 
            "valuation_rate"
        )
        print(f"Item: {item['item_code']} | Qty: {actual_qty} | Valuation Rate: Rp {flt(val_rate):,.2f}")

    print("=== TAHAP 3 SELESAI DENGAN SUKSES! ===")

if __name__ == "__main__":
    run()
