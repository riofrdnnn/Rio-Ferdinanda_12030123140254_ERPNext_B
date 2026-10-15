import frappe

def run():
    print("=== MEMULAI TAHAP 2: SETUP MANUFAKTUR (WORKSTATIONS, OPERATIONS, BOM) ===")
    company_name = "PT Rio Ferdinanda Manufaktur"
    
    # 1. SETUP WORKSTATIONS
    workstations = [
        {
            "name": "WS-POTONG",
            "workstation_name": "Stasiun Kerja Pemotongan Kayu & Besi",
            "hour_rate": 60000,
            "description": "Area mesin potong gerinda duduk dan table saw"
        },
        {
            "name": "WS-LAS",
            "workstation_name": "Stasiun Kerja Pengelasan & Rangka",
            "hour_rate": 65000,
            "description": "Area pengelasan rangka besi dan perataan sudut"
        },
        {
            "name": "WS-CAT",
            "workstation_name": "Stasiun Kerja Finishing & Pengecatan",
            "hour_rate": 55000,
            "description": "Bilik semprot spray gun cat anti karat dan oven pengering"
        },
        {
            "name": "WS-RAKIT",
            "workstation_name": "Stasiun Kerja Perakitan & Quality Control",
            "hour_rate": 50000,
            "description": "Meja perakitan akhir kayu dan kaki besi serta pengecekan QC"
        }
    ]

    ws_map = {}
    for ws in workstations:
        ws_doc = None
        # Check by name or workstation_name
        if frappe.db.exists("Workstation", ws["workstation_name"]):
            ws_doc = frappe.get_doc("Workstation", ws["workstation_name"])
            print(f"Workstation exists: {ws_doc.name}")
        elif frappe.db.exists("Workstation", ws["name"]):
            ws_doc = frappe.get_doc("Workstation", ws["name"])
            print(f"Workstation exists: {ws_doc.name}")
        else:
            ws_doc = frappe.get_doc({
                "doctype": "Workstation",
                "workstation_name": ws["workstation_name"],
                "hour_rate": ws["hour_rate"],
                "description": ws["description"]
            })
            ws_doc.insert(ignore_permissions=True)
            print(f"Workstation created: {ws_doc.name}")
        ws_map[ws["name"]] = ws_doc.name
        ws_map[ws["workstation_name"]] = ws_doc.name
    frappe.db.commit()

    # 2. SETUP OPERATIONS
    operations = [
        {
            "name": "Pemotongan Bahan Baku (Cutting)",
            "description": "Proses memotong papan kayu dan memotong pipa besi sesuai ukuran desain",
            "default_ws": ws_map["WS-POTONG"]
        },
        {
            "name": "Pengelasan Rangka (Welding)",
            "description": "Proses menyambung potongan pipa besi menjadi rangka kokoh",
            "default_ws": ws_map["WS-LAS"]
        },
        {
            "name": "Pengecatan dan Finishing (Coating)",
            "description": "Proses pelapisan anti karat dan semprot cat hitam doff",
            "default_ws": ws_map["WS-CAT"]
        },
        {
            "name": "Perakitan Akhir & QC (Assembly)",
            "description": "Pemasangan daun meja kayu ke rangka besi dengan baut dan uji stabilitas",
            "default_ws": ws_map["WS-RAKIT"]
        }
    ]

    for op in operations:
        if not frappe.db.exists("Operation", op["name"]):
            op_doc = frappe.get_doc({
                "doctype": "Operation",
                "name": op["name"],
                "workstation": op["default_ws"],
                "description": op["description"]
            })
            op_doc.insert(ignore_permissions=True)
            print(f"Operation created: {op['name']}")
        else:
            print(f"Operation exists: {op['name']}")
    frappe.db.commit()

    # 3. SETUP BOM FOR PROD-MEJA-01
    meja_item = "PROD-MEJA-01"
    existing_meja_bom = frappe.db.get_value("BOM", {"item": meja_item, "is_active": 1, "docstatus": 1}, "name")
    if not existing_meja_bom:
        # Check if draft exists
        draft_bom = frappe.db.get_value("BOM", {"item": meja_item, "docstatus": 0}, "name")
        if draft_bom:
            bom_doc = frappe.get_doc("BOM", draft_bom)
        else:
            bom_doc = frappe.get_doc({
                "doctype": "BOM",
                "item": meja_item,
                "company": company_name,
                "quantity": 1.0,
                "uom": "Nos",
                "with_operations": 1,
                "is_active": 1,
                "is_default": 1,
                "currency": "IDR",
                "rm_cost_as_per": "Valuation Rate",
                "items": [
                    {"item_code": "RAW-KAYU-01", "qty": 1.0, "rate": 85000, "uom": "Nos"},
                    {"item_code": "RAW-PIPA-01", "qty": 0.5, "rate": 110000, "uom": "Nos"},
                    {"item_code": "RAW-BAUT-01", "qty": 8.0, "rate": 1000, "uom": "Nos"},
                    {"item_code": "RAW-CAT-01", "qty": 0.25, "rate": 45000, "uom": "Nos"},
                    {"item_code": "RAW-KAKI-01", "qty": 4.0, "rate": 2500, "uom": "Nos"},
                    {"item_code": "RAW-AMPLAS-01", "qty": 1.0, "rate": 4000, "uom": "Nos"}
                ],
                "operations": [
                    {
                        "operation": "Pemotongan Bahan Baku (Cutting)",
                        "workstation": ws_map["WS-POTONG"],
                        "time_in_mins": 15,
                        "hour_rate": 60000
                    },
                    {
                        "operation": "Pengelasan Rangka (Welding)",
                        "workstation": ws_map["WS-LAS"],
                        "time_in_mins": 20,
                        "hour_rate": 65000
                    },
                    {
                        "operation": "Pengecatan dan Finishing (Coating)",
                        "workstation": ws_map["WS-CAT"],
                        "time_in_mins": 15,
                        "hour_rate": 55000
                    },
                    {
                        "operation": "Perakitan Akhir & QC (Assembly)",
                        "workstation": ws_map["WS-RAKIT"],
                        "time_in_mins": 20,
                        "hour_rate": 50000
                    }
                ]
            })
            bom_doc.insert(ignore_permissions=True)
        bom_doc.submit()
        print(f"BOM Meja created and submitted: {bom_doc.name}")
    else:
        print(f"BOM Meja already exists and active: {existing_meja_bom}")
    frappe.db.commit()

    # 4. SETUP BOM FOR PROD-RAK-01
    rak_item = "PROD-RAK-01"
    existing_rak_bom = frappe.db.get_value("BOM", {"item": rak_item, "is_active": 1, "docstatus": 1}, "name")
    if not existing_rak_bom:
        draft_rak_bom = frappe.db.get_value("BOM", {"item": rak_item, "docstatus": 0}, "name")
        if draft_rak_bom:
            bom_doc = frappe.get_doc("BOM", draft_rak_bom)
        else:
            bom_doc = frappe.get_doc({
                "doctype": "BOM",
                "item": rak_item,
                "company": company_name,
                "quantity": 1.0,
                "uom": "Nos",
                "with_operations": 1,
                "is_active": 1,
                "is_default": 1,
                "currency": "IDR",
                "rm_cost_as_per": "Valuation Rate",
                "items": [
                    {"item_code": "RAW-KAYU-01", "qty": 0.75, "rate": 85000, "uom": "Nos"},
                    {"item_code": "RAW-PIPA-01", "qty": 0.4, "rate": 110000, "uom": "Nos"},
                    {"item_code": "RAW-BAUT-01", "qty": 12.0, "rate": 1000, "uom": "Nos"},
                    {"item_code": "RAW-CAT-01", "qty": 0.2, "rate": 45000, "uom": "Nos"},
                    {"item_code": "RAW-KAKI-01", "qty": 4.0, "rate": 2500, "uom": "Nos"}
                ],
                "operations": [
                    {
                        "operation": "Pemotongan Bahan Baku (Cutting)",
                        "workstation": ws_map["WS-POTONG"],
                        "time_in_mins": 15,
                        "hour_rate": 60000
                    },
                    {
                        "operation": "Pengelasan Rangka (Welding)",
                        "workstation": ws_map["WS-LAS"],
                        "time_in_mins": 15,
                        "hour_rate": 65000
                    },
                    {
                        "operation": "Pengecatan dan Finishing (Coating)",
                        "workstation": ws_map["WS-CAT"],
                        "time_in_mins": 12,
                        "hour_rate": 55000
                    },
                    {
                        "operation": "Perakitan Akhir & QC (Assembly)",
                        "workstation": ws_map["WS-RAKIT"],
                        "time_in_mins": 15,
                        "hour_rate": 50000
                    }
                ]
            })
            bom_doc.insert(ignore_permissions=True)
        bom_doc.submit()
        print(f"BOM Rak created and submitted: {bom_doc.name}")
    else:
        print(f"BOM Rak already exists and active: {existing_rak_bom}")
    frappe.db.commit()

    print("=== TAHAP 2 SELESAI DENGAN SUKSES! ===")

if __name__ == "__main__":
    run()
