import frappe

def run():
    print("=== CHECKING WORKSTATION, OPERATION, BOM FIELDS ===")
    ws_meta = frappe.get_meta("Workstation")
    print("Workstation fields:", [df.fieldname for df in ws_meta.fields if df.fieldname])
    
    op_meta = frappe.get_meta("Operation")
    print("Operation fields:", [df.fieldname for df in op_meta.fields if df.fieldname])
    
    bom_meta = frappe.get_meta("BOM")
    print("BOM fields:", [df.fieldname for df in bom_meta.fields if df.fieldname])
    
    bom_item_meta = frappe.get_meta("BOM Item")
    print("BOM Item fields:", [df.fieldname for df in bom_item_meta.fields if df.fieldname])
    
    bom_op_meta = frappe.get_meta("BOM Operation")
    print("BOM Operation fields:", [df.fieldname for df in bom_op_meta.fields if df.fieldname])
