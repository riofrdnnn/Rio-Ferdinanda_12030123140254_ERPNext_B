import frappe

def run():
    bom = frappe.get_doc("BOM", "BOM-PROD-MEJA-01-001")
    print("BOM with_operations:", bom.with_operations)
    print("BOM operations count:", len(bom.operations))
    for op in bom.operations:
        print(f"  - op: {op.operation}, ws: {op.workstation}, time: {op.time_in_mins}, hour_rate: {op.hour_rate}")
        
    company = frappe.get_doc("Company", "PT Rio Ferdinanda Manufaktur")
    print("Current default_operating_cost_account:", company.default_operating_cost_account)
    company.default_operating_cost_account = "Expenses Included In Valuation - RFM"
    company.expenses_added_to_stock_account = "Expenses Included In Valuation - RFM"
    company.save(ignore_permissions=True)
    frappe.db.commit()
    print("Updated default_operating_cost_account:", company.default_operating_cost_account)
