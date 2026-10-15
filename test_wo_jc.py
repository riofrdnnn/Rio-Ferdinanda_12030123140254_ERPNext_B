import frappe

def run():
    wo = frappe.get_doc("Work Order", "MFG-WO-2026-00001")
    print("Work Order:", wo.name, "Status:", wo.status)
    print("Operations:", len(wo.operations))
    for op in wo.operations:
        print(f"  - op: {op.operation}, ws: {op.workstation}, time: {op.time_in_mins}")
        
    jcs = frappe.get_all("Job Card", filters={"work_order": wo.name}, fields=["name", "operation"])
    print("Job Cards before:", jcs)
    
    # Try calling create_job_card
    if not jcs:
        wo.create_job_card()
        frappe.db.commit()
        jcs = frappe.get_all("Job Card", filters={"work_order": wo.name}, fields=["name", "operation"])
        print("Job Cards after create_job_card():", jcs)
