import frappe

def run():
    print("=== MEMULAI TAHAP 1: SETUP DATA MASTER ===")

    # 0. SETUP PREREQUISITES
    # Warehouse Types
    wh_types = ["Transit", "Stores", "Work In Progress", "Finished Goods", "Scrap", "Sub Assembly"]
    for wht in wh_types:
        if not frappe.db.exists("Warehouse Type", wht):
            frappe.get_doc({
                "doctype": "Warehouse Type",
                "name": wht
            }).insert(ignore_permissions=True)
            print(f"Warehouse Type created: {wht}")
    frappe.db.commit()

    # Root Item Group
    if not frappe.db.exists("Item Group", "All Item Groups"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "All Item Groups",
            "is_group": 1
        }).insert(ignore_permissions=True)
        print("Root Item Group created: All Item Groups")
        frappe.db.commit()

    # Root Customer Group
    if not frappe.db.exists("Customer Group", "All Customer Groups"):
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "All Customer Groups",
            "is_group": 1
        }).insert(ignore_permissions=True)
        print("Root Customer Group created: All Customer Groups")
        frappe.db.commit()

    # Root Supplier Group
    if not frappe.db.exists("Supplier Group", "All Supplier Groups"):
        frappe.get_doc({
            "doctype": "Supplier Group",
            "supplier_group_name": "All Supplier Groups",
            "is_group": 1
        }).insert(ignore_permissions=True)
        print("Root Supplier Group created: All Supplier Groups")
        frappe.db.commit()

    # Root Territory
    if not frappe.db.exists("Territory", "All Territories"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "All Territories",
            "is_group": 1
        }).insert(ignore_permissions=True)
        print("Root Territory created: All Territories")
        frappe.db.commit()

    # 1. SETUP COMPANY
    company_name = "PT Rio Ferdinanda Manufaktur"
    abbr = "RFM"
    if not frappe.db.exists("Company", company_name):
        print(f"Creating Company: {company_name}")
        company = frappe.get_doc({
            "doctype": "Company",
            "company_name": company_name,
            "abbr": abbr,
            "default_currency": "IDR",
            "country": "Indonesia"
        })
        company.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Company created: {company.name}")
    else:
        print(f"Company already exists: {company_name}")

    frappe.db.set_default("company", company_name)
    frappe.db.commit()

    # 2. SETUP ITEM GROUPS
    item_groups = [
        {"name": "Bahan Baku", "parent": "All Item Groups"},
        {"name": "Bahan Penolong", "parent": "All Item Groups"},
        {"name": "Barang Dalam Proses", "parent": "All Item Groups"},
        {"name": "Produk Jadi", "parent": "All Item Groups"}
    ]
    for ig in item_groups:
        if not frappe.db.exists("Item Group", ig["name"]):
            doc = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": ig["name"],
                "parent_item_group": ig["parent"],
                "is_group": 0
            })
            doc.insert(ignore_permissions=True)
            print(f"Item Group created: {ig['name']}")
        else:
            print(f"Item Group exists: {ig['name']}")
    frappe.db.commit()

    # 3. SETUP WAREHOUSES
    parent_wh = f"All Warehouses - {abbr}"
    if not frappe.db.exists("Warehouse", parent_wh):
        existing_wh = frappe.db.get_value("Warehouse", {"company": company_name, "is_group": 1}, "name")
        if existing_wh:
            parent_wh = existing_wh
        else:
            parent_wh = None

    warehouses = [
        {"warehouse_name": "Gudang Bahan Baku - RF", "type": "Stores", "desc": "Penyimpanan material mentah kayu dan besi"},
        {"warehouse_name": "Gudang WIP Produksi - RF", "type": "Work In Progress", "desc": "Tempat transit barang dalam proses perakitan"},
        {"warehouse_name": "Gudang Barang Jadi - RF", "type": "Finished Goods", "desc": "Penyimpanan produk jadi siap kirim"},
        {"warehouse_name": "Gudang Scrap Rusak - RF", "type": "Scrap", "desc": "Penyimpanan sisa potongan atau barang reject"}
    ]
    for wh in warehouses:
        full_wh_name = f"{wh['warehouse_name']} - {abbr}"
        if not frappe.db.exists("Warehouse", full_wh_name) and not frappe.db.exists("Warehouse", wh["warehouse_name"]):
            wh_doc = {
                "doctype": "Warehouse",
                "warehouse_name": wh["warehouse_name"],
                "warehouse_type": wh["type"],
                "company": company_name,
                "is_group": 0
            }
            if parent_wh:
                wh_doc["parent_warehouse"] = parent_wh
            doc = frappe.get_doc(wh_doc)
            doc.insert(ignore_permissions=True)
            print(f"Warehouse created: {doc.name}")
        else:
            print(f"Warehouse exists: {wh['warehouse_name']}")
    frappe.db.commit()

    # 4. SETUP UOM
    for uom in ["Nos", "Meter", "Kaleng", "Lembar"]:
        if not frappe.db.exists("UOM", uom):
            doc = frappe.get_doc({"doctype": "UOM", "uom_name": uom})
            doc.insert(ignore_permissions=True)
            print(f"UOM created: {uom}")
    frappe.db.commit()

    # 5. SETUP ITEMS
    items = [
        {
            "item_code": "RAW-KAYU-01",
            "item_name": "Papan Kayu Solid Pinus 120x60x2cm",
            "item_group": "Bahan Baku",
            "stock_uom": "Nos",
            "valuation_rate": 85000,
            "standard_rate": 95000,
            "description": "Papan kayu pinus olahan untuk daun meja belajar",
            "is_stock_item": 1
        },
        {
            "item_code": "RAW-PIPA-01",
            "item_name": "Pipa Besi Hollow 4x4 Tebal 1.6mm (Batang 6m)",
            "item_group": "Bahan Baku",
            "stock_uom": "Nos",
            "valuation_rate": 110000,
            "standard_rate": 125000,
            "description": "Bahan dasar rangka meja dan kaki kursi",
            "is_stock_item": 1
        },
        {
            "item_code": "RAW-BAUT-01",
            "item_name": "Baut & Mur Hex Galvanis M6x30",
            "item_group": "Bahan Penolong",
            "stock_uom": "Nos",
            "valuation_rate": 1000,
            "standard_rate": 1500,
            "description": "Baut perakit rangka besi dan kayu",
            "is_stock_item": 1
        },
        {
            "item_code": "RAW-CAT-01",
            "item_name": "Cat Anti Karat Black Doff (Kaleng 1L)",
            "item_group": "Bahan Penolong",
            "stock_uom": "Nos",
            "valuation_rate": 45000,
            "standard_rate": 50000,
            "description": "Cat pelapis rangka besi anti korosi",
            "is_stock_item": 1
        },
        {
            "item_code": "RAW-KAKI-01",
            "item_name": "Karet Pelindung Alas Kaki 4x4cm",
            "item_group": "Bahan Penolong",
            "stock_uom": "Nos",
            "valuation_rate": 2500,
            "standard_rate": 3500,
            "description": "Karet penutup ujung pipa besi peredam lantai",
            "is_stock_item": 1
        },
        {
            "item_code": "RAW-AMPLAS-01",
            "item_name": "Kertas Amplas Kayu No 240",
            "item_group": "Bahan Penolong",
            "stock_uom": "Nos",
            "valuation_rate": 4000,
            "standard_rate": 5000,
            "description": "Kertas amplas untuk finishing kayu",
            "is_stock_item": 1
        },
        {
            "item_code": "WIP-RANGKA-01",
            "item_name": "Sub-Assembly Rangka Besi Meja RF-100",
            "item_group": "Barang Dalam Proses",
            "stock_uom": "Nos",
            "valuation_rate": 130000,
            "standard_rate": 150000,
            "description": "Rangka meja yang sudah dipotong dan dilas sebelum dicat",
            "is_stock_item": 1
        },
        {
            "item_code": "PROD-MEJA-01",
            "item_name": "Meja Belajar Minimalis RF-100",
            "item_group": "Produk Jadi",
            "stock_uom": "Nos",
            "valuation_rate": 245000,
            "standard_rate": 475000,
            "description": "Meja belajar minimalis kayu solid dengan rangka besi hollow",
            "is_stock_item": 1
        },
        {
            "item_code": "PROD-RAK-01",
            "item_name": "Rak Buku Sudut Industrial RF-200",
            "item_group": "Produk Jadi",
            "stock_uom": "Nos",
            "valuation_rate": 180000,
            "standard_rate": 350000,
            "description": "Rak buku susun 3 bergaya industrial kombinasi kayu dan besi",
            "is_stock_item": 1
        }
    ]

    for item_data in items:
        code = item_data["item_code"]
        if not frappe.db.exists("Item", code):
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": code,
                "item_name": item_data["item_name"],
                "item_group": item_data["item_group"],
                "stock_uom": item_data["stock_uom"],
                "is_stock_item": item_data["is_stock_item"],
                "include_item_in_manufacturing": 1 if "RAW" in code or "WIP" in code else 0,
                "valuation_rate": item_data["valuation_rate"],
                "standard_rate": item_data["standard_rate"],
                "description": item_data["description"]
            })
            doc.insert(ignore_permissions=True)
            print(f"Item created: {code} - {item_data['item_name']}")
        else:
            print(f"Item exists: {code}")
    frappe.db.commit()

    # 6. SETUP SUPPLIERS
    for sg in ["Raw Material", "Hardware"]:
        if not frappe.db.exists("Supplier Group", sg):
            frappe.get_doc({
                "doctype": "Supplier Group",
                "supplier_group_name": sg,
                "parent_supplier_group": "All Supplier Groups",
                "is_group": 0
            }).insert(ignore_permissions=True)

    suppliers = [
        {"name": "PT Kayu Rimba Perkasa", "group": "Raw Material", "type": "Company", "country": "Indonesia"},
        {"name": "CV Logam Baja Nusantara", "group": "Raw Material", "type": "Company", "country": "Indonesia"},
        {"name": "Toko Baut Citra Fastener", "group": "Hardware", "type": "Individual", "country": "Indonesia"},
        {"name": "UD Cahaya Cat Finishing", "group": "Hardware", "type": "Individual", "country": "Indonesia"}
    ]
    for s in suppliers:
        if not frappe.db.exists("Supplier", s["name"]):
            doc = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": s["name"],
                "supplier_group": s["group"],
                "supplier_type": s["type"],
                "country": s["country"]
            })
            doc.insert(ignore_permissions=True)
            print(f"Supplier created: {s['name']}")
        else:
            print(f"Supplier exists: {s['name']}")
    frappe.db.commit()

    # 7. SETUP CUSTOMERS
    for cg in ["Commercial", "Individual"]:
        if not frappe.db.exists("Customer Group", cg):
            frappe.get_doc({
                "doctype": "Customer Group",
                "customer_group_name": cg,
                "parent_customer_group": "All Customer Groups",
                "is_group": 0
            }).insert(ignore_permissions=True)

    # Territory
    if not frappe.db.exists("Territory", "Indonesia"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "Indonesia",
            "parent_territory": "All Territories",
            "is_group": 0
        }).insert(ignore_permissions=True)

    default_territory = "Indonesia" if frappe.db.exists("Territory", "Indonesia") else "All Territories"

    customers = [
        {"name": "Toko Furnitur Sejahtera Abadi", "group": "Commercial", "type": "Company"},
        {"name": "CV Karya Mandiri Edukasi", "group": "Commercial", "type": "Company"},
        {"name": "Bpk. Budi Santoso (Home Office)", "group": "Individual", "type": "Individual"},
        {"name": "Ibu Rina Wijaya (Interior Studio)", "group": "Individual", "type": "Individual"}
    ]
    for c in customers:
        c_name = c["name"]
        if not frappe.db.exists("Customer", c_name):
            doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": c_name,
                "customer_group": c["group"],
                "customer_type": c["type"],
                "territory": default_territory
            })
            doc.insert(ignore_permissions=True)
            print(f"Customer created: {c_name}")
        else:
            print(f"Customer exists: {c_name}")
    frappe.db.commit()

    print("=== TAHAP 1 SELESAI DENGAN SUKSES! ===")

if __name__ == "__main__":
    run()
