import frappe
from frappe.utils import flt, fmt_money

def run():
    print("======================================================================")
    print("=== TAHAP 6: ANALISIS LAPORAN MANUFAKTUR, PERSEDIAAN & KEUANGAN ===")
    print("======================================================================")
    
    company_name = "PT Rio Ferdinanda Manufaktur"
    
    # 1. LAPORAN POSISI STOK GUDANG (STOCK BALANCE)
    print("\n" + "="*50)
    print("1. LAPORAN POSISI PERSEDIAAN GUDANG (STOCK BALANCE)")
    print("="*50)
    
    bins = frappe.db.sql("""
        select b.warehouse, b.item_code, i.item_name, i.item_group, b.actual_qty, b.valuation_rate, b.stock_value
        from `tabBin` b
        join `tabItem` i on i.name = b.item_code
        join `tabWarehouse` w on w.name = b.warehouse
        where w.company = %s and (b.actual_qty != 0 or b.stock_value != 0)
        order by b.warehouse, b.item_code
    """, (company_name,), as_dict=True)
    
    current_wh = ""
    total_inventory_value = 0.0
    for b in bins:
        if b.warehouse != current_wh:
            current_wh = b.warehouse
            print(f"\n[GUDANG]: {current_wh}")
            print(f"{'Kode Item':<16} | {'Nama Barang':<35} | {'Stok':<8} | {'Hrg Satuan':<15} | {'Total Nilai'}")
            print("-" * 95)
        print(f"{b.item_code:<16} | {b.item_name[:35]:<35} | {b.actual_qty:<8.1f} | Rp {b.valuation_rate:>11,.2f} | Rp {b.stock_value:>12,.2f}")
        total_inventory_value += flt(b.stock_value)
        
    print("-" * 95)
    print(f"TOTAL NILAI ASET PERSEDIAAN AKHIR GUDANG: Rp {total_inventory_value:,.2f}")

    # 2. LAPORAN BIAYA PRODUKSI & HPP (MANUFACTURING COST ANALYTICS)
    print("\n" + "="*50)
    print("2. LAPORAN BIAYA PRODUKSI & HPP (MANUFACTURING COST)")
    print("="*50)
    
    wo = frappe.get_doc("Work Order", "MFG-WO-2026-00001")
    bom = frappe.get_doc("BOM", wo.bom_no)
    mfg_entry = frappe.get_doc("Stock Entry", "MAT-STE-2026-00003")
    
    print(f"Work Order ID         : {wo.name}")
    print(f"Produk Dihasilkan     : {wo.production_item} ({wo.qty} Nos)")
    print(f"BOM Referensi         : {wo.bom_no}")
    print(f"Stock Entry Finish    : {mfg_entry.name}")
    print(f"Biaya Bahan Baku Baku : Rp {bom.raw_material_cost * wo.qty:,.2f}")
    print(f"Biaya Operasi WS      : Rp {bom.operating_cost * wo.qty:,.2f}")
    print(f"Total Biaya Produksi  : Rp {(bom.raw_material_cost + bom.operating_cost) * wo.qty:,.2f}")
    
    fg_row = [it for it in mfg_entry.items if it.item_code == wo.production_item][0]
    print(f"HPP Satuan per Meja   : Rp {fg_row.basic_rate:,.2f} / unit")

    # 3. LAPORAN LABA RUGI (PROFIT AND LOSS STATEMENT)
    print("\n" + "="*50)
    print("3. LAPORAN LABA RUGI PENJUALAN (PROFIT & LOSS STATEMENT)")
    print("="*50)
    
    # Query GL Entries
    gl_entries = frappe.db.sql("""
        select gle.account, a.root_type, sum(gle.debit) as total_debit, sum(gle.credit) as total_credit
        from `tabGL Entry` gle
        join `tabAccount` a on a.name = gle.account
        where gle.company = %s and gle.is_cancelled = 0 and a.root_type in ('Income', 'Expense')
        group by gle.account, a.root_type
        order by a.root_type desc, gle.account
    """, (company_name,), as_dict=True)
    
    total_income = 0.0
    total_expense = 0.0
    
    print("\n--- PENDAPATAN (INCOME) ---")
    for gle in gl_entries:
        if gle.root_type == "Income":
            net = flt(gle.total_credit) - flt(gle.total_debit)
            total_income += net
            print(f"  {gle.account:<40} : Rp {net:>14,.2f}")
            
    print(f"TOTAL PENDAPATAN PENJUALAN                : Rp {total_income:>14,.2f}")

    print("\n--- BEBAN & HARGA POKOK PENJUALAN (EXPENSE & COGS) ---")
    cogs_amount = 0.0
    for gle in gl_entries:
        if gle.root_type == "Expense":
            net = flt(gle.total_debit) - flt(gle.total_credit)
            total_expense += net
            print(f"  {gle.account:<40} : Rp {net:>14,.2f}")
            if "Cost of Goods Sold" in gle.account:
                cogs_amount = net
                
    gross_profit = total_income - cogs_amount
    net_profit = total_income - total_expense
    gross_margin_pct = (gross_profit / total_income * 100) if total_income else 0
    
    print("-" * 65)
    print(f"TOTAL BEBAN / HPP OPERASIONAL             : Rp {total_expense:>14,.2f}")
    print(f"LABA KOTOR PENJUALAN (GROSS PROFIT)       : Rp {gross_profit:>14,.2f}")
    print(f"GROSS PROFIT MARGIN                       : {gross_margin_pct:.2f}%")
    print(f"LABA BERSIH OPERASIONAL (NET PROFIT)      : Rp {net_profit:>14,.2f}")

    # 4. LAPORAN SALDO KAS & BANK
    print("\n" + "="*50)
    print("4. POSISI SALDO KAS & BANK (CASH & BANK POSITION)")
    print("="*50)
    bank_gl = frappe.db.sql("""
        select sum(debit - credit) as balance
        from `tabGL Entry`
        where account = 'Bank BCA - RFM' and is_cancelled = 0
    """, as_dict=True)
    bank_balance = flt(bank_gl[0].balance) if bank_gl else 0.0
    print(f"Saldo Rekening Bank BCA - RFM             : Rp {bank_balance:>14,.2f} (Lunas)")

    print("\n======================================================================")
    print("=== TAHAP 6 SELESAI DENGAN SUKSES! SELURUH SIKLUS TERSELESAIKAN ===")
    print("======================================================================")

if __name__ == "__main__":
    run()
