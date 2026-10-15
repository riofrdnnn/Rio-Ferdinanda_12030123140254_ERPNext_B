import frappe
from frappe.utils import flt

def run():
    print("==========================================================================")
    print("=== TAHAP 6: LEMBAR EVALUASI & PENCOCOKAN KUNCI JAWABAN (ASSESSMENT) ===")
    print("==========================================================================")
    company_name = "PT Terang Maju Manufaktur"
    abbr = "TMM"
    
    # Helper to get account balance from GL Entry
    def get_gl_balance(acc_sub):
        res = frappe.db.sql("""
            select sum(gle.debit) as deb, sum(gle.credit) as cred, a.root_type
            from `tabGL Entry` gle
            join `tabAccount` a on a.name = gle.account
            where gle.company = %s and gle.account like %s and gle.is_cancelled = 0
            group by a.root_type
        """, (company_name, f"%{acc_sub}%"), as_dict=True)
        if not res:
            return 0.0
        deb = flt(res[0].deb)
        cred = flt(res[0].cred)
        root = res[0].root_type
        if root in ['Asset', 'Expense']:
            return deb - cred
        else: # Liability, Equity, Income
            return cred - deb

    # 1. AMBIL SALDO AKUN REAL DARI ERPNEXT
    val_1141 = get_gl_balance("1141 - Persediaan Bahan Baku")
    val_1144 = get_gl_balance("1144 - Persediaan Barang Jadi")
    val_4110 = get_gl_balance("4110 - Pendapatan Penjualan Produk Jadi")
    val_5110 = get_gl_balance("5110 - Harga Pokok Penjualan")
    gross_profit = val_4110 - val_5110
    val_5310 = get_gl_balance("5310 - Beban Listrik & Utilitas Pabrik")
    net_profit = gross_profit - val_5310

    # 2. DEFINISI KUNCI JAWABAN (BENCHMARK SOAL)
    assessment = [
        {
            "no": 1,
            "parameter": "Persediaan Bahan Baku (1141)",
            "formula": "Sisa Stock RM-001 & RM-002",
            "kunci": 12500000.0,
            "real": val_1141
        },
        {
            "no": 2,
            "parameter": "Persediaan Barang Jadi (1144)",
            "formula": "Sisa Stock 5 Unit FG-001",
            "kunci": 1750000.0,
            "real": val_1144
        },
        {
            "no": 3,
            "parameter": "Total Pendapatan Penjualan (4110)",
            "formula": "5 Unit @ Rp 750.000",
            "kunci": 3750000.0,
            "real": val_4110
        },
        {
            "no": 4,
            "parameter": "Total Harga Pokok Penjualan (5110)",
            "formula": "5 Unit @ Rp 350.000",
            "kunci": 1750000.0,
            "real": val_5110
        },
        {
            "no": 5,
            "parameter": "Laba Kotor (Gross Profit)",
            "formula": "Pendapatan - HPP",
            "kunci": 2000000.0,
            "real": gross_profit
        },
        {
            "no": 6,
            "parameter": "Beban Utilitas Pabrik (5310)",
            "formula": "Beban Operasional",
            "kunci": 500000.0,
            "real": val_5310
        },
        {
            "no": 7,
            "parameter": "Laba Bersih Operasional (Net Profit)",
            "formula": "Laba Kotor - Beban",
            "kunci": 1500000.0,
            "real": net_profit
        }
    ]

    # 3. CETAK TABEL PENCOCOKAN EVALUASI
    print(f"{'No':<3} | {'Parameter / Akun':<38} | {'Kunci Jawaban':<16} | {'Nilai Real ERP':<16} | {'Status'}")
    print("-" * 88)
    all_matched = True
    for item in assessment:
        kunci_str = f"Rp {item['kunci']:>12,.2f}"
        real_str = f"Rp {item['real']:>12,.2f}"
        diff = item['real'] - item['kunci']
        status = "SESUAI 100% [V]" if diff == 0 else f"SELISIH ({diff:,.2f})"
        if diff != 0:
            all_matched = False
        print(f"{item['no']:<3} | {item['parameter']:<38} | {kunci_str:<16} | {real_str:<16} | {status}")
    print("-" * 88)

    # 4. RINCIAN POSISI FISIK GUDANG
    print("\n--- Rincian Verifikasi Fisik Gudang (Stock Ledger) ---")
    bins = frappe.db.sql("""
        select b.warehouse, b.item_code, i.item_name, b.actual_qty, b.valuation_rate, (b.actual_qty * b.valuation_rate) as total_val
        from `tabBin` b
        join `tabItem` i on i.name = b.item_code
        join `tabWarehouse` w on w.name = b.warehouse
        where w.company = %s and b.actual_qty > 0
        order by b.warehouse, b.item_code
    """, (company_name,), as_dict=True)
    
    current_wh = ""
    for b in bins:
        if b.warehouse != current_wh:
            current_wh = b.warehouse
            print(f"\n[GUDANG]: {current_wh}")
        print(f"  * {b.item_code:<8} - {b.item_name:<25} : {b.actual_qty:<5.1f} unit @ Rp {b.valuation_rate:>10,.2f} = Rp {b.total_val:>12,.2f}")

    print("\n==========================================================================")
    if all_matched:
        print("HASIL EVALUASI: SELURUH PARAMETER TERVERIFIKASI 100% COCOK DENGAN KUNCI JAWABAN!")
    else:
        print("HASIL EVALUASI: TERDAPAT PENYESUAIAN PADA BEBERAPA AKUN.")
    print("==========================================================================")

if __name__ == "__main__":
    run()
