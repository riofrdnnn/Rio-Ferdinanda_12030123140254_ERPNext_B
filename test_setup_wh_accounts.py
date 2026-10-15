import frappe

def run():
    company = "PT Terang Maju Manufaktur"
    abbr = "TMM"
    parent = f"Stock Assets - {abbr}"
    
    # 1. Buat akun-akun persediaan spesifik sesuai soal jika belum ada
    acc_map = {
        "1141 - Persediaan Bahan Baku": "Gudang Bahan Baku - TMM",
        "1143 - Persediaan Barang Dalam Proses (WIP)": "Gudang WIP - TMM",
        "1144 - Persediaan Barang Jadi": "Gudang Barang Jadi - TMM"
    }
    
    for acc_name, wh_name in acc_map.items():
        full_acc = f"{acc_name} - {abbr}"
        if not frappe.db.exists("Account", full_acc):
            frappe.get_doc({
                "doctype": "Account",
                "account_name": acc_name,
                "company": company,
                "parent_account": parent,
                "account_type": "Stock",
                "root_type": "Asset",
                "is_group": 0
            }).insert(ignore_permissions=True)
            print(f"Created account: {full_acc}")
        else:
            print(f"Account exists: {full_acc}")
            
        # Update warehouse account
        try:
            wh = frappe.get_doc("Warehouse", wh_name)
            if not wh.account:
                wh.account = full_acc
                wh.save(ignore_permissions=True)
                print(f"Linked {wh_name} -> {full_acc}")
        except Exception as e:
            print(f"Could not link {wh_name} to {full_acc}: {e}")
            
    frappe.db.commit()
