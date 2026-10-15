import frappe

def main():
    frappe.init(site="frontend", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    print("SUCCESS: Connected to site", frappe.local.site)

if __name__ == "__main__":
    main()
