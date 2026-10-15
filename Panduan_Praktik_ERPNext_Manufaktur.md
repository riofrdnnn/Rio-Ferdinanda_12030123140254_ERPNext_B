# PANDUAN LENGKAP PRAKTIK ERPNEXT: MODUL MANUFAKTUR
**Perusahaan Simulasi:** PT Rio Ferdinanda Manufaktur (Industri Furnitur Metal & Kayu)  
**Tujuan Praktik:** Memahami siklus menyeluruh proses manufaktur (Make-to-Order / Make-to-Stock) pada ERPNext, mulai dari pengadaan bahan baku, manajemen gudang, pembuatan BOM (Bill of Materials) & Routing, eksekusi Work Order & Job Cards, hingga penjualan produk jadi.

---

## 1. Struktur Folder Dataset `ERP_Rio Ferdinanda`

Semua file dataset berformat CSV siap impor dan panduan ini tersimpan di:
`C:\Users\Windows 10\.gemini\antigravity\scratch\ERP_Rio Ferdinanda\`

| No | File | Deskripsi & Doctype ERPNext |
|---|---|---|
| 1 | `01_Item_Group.csv` | Master Kategori Barang (*Item Group*) |
| 2 | `02_Warehouse.csv` | Master Gudang Penyimpanan (*Warehouse*) |
| 3 | `03_Item.csv` | Master Barang Bahan Baku, Penolong, WIP, dan Produk Jadi (*Item*) |
| 4 | `04_Supplier.csv` | Master Pemasok Bahan Baku (*Supplier*) |
| 5 | `05_Customer.csv` | Master Pelanggan Produk Jadi (*Customer*) |
| 6 | `06_Workstation_dan_Operation.csv` | Master Stasiun Kerja (*Workstation*) & Jenis Pekerjaan (*Operation*) |
| 7 | `07_Bill_of_Materials_BOM.csv` | Struktur Komposisi Produk & Waktu Operasi (*BOM*) |
| 8 | `08_Opening_Stock_Stock_Entry.csv` | Saldo Awal Persediaan Gudang (*Stock Entry - Material Receipt*) |
| 9 | `09_Skenario_Transaksi_Praktik.csv` | Rangkaian Alur Transaksi Simulasi Praktik |

---

## 2. Profil Perusahaan Simulasi
- **Nama Perusahaan:** PT Rio Ferdinanda Manufaktur (atau disesuaikan dengan setting ERPNext Anda)
- **Bidang Usaha:** Manufaktur Furnitur Industrial (Kombinasi Kayu Solid & Rangka Besi Hollow)
- **Produk Unggulan:**
  1. `PROD-MEJA-01`: Meja Belajar Minimalis RF-100 (Harga Jual Standar: Rp 475.000)
  2. `PROD-RAK-01`: Rak Buku Sudut Industrial RF-200 (Harga Jual Standar: Rp 350.000)

---

## 3. Langkah-Langkah Praktik ERPNext (Step-by-Step)

### TAHAP 1: Setup Master Data
1. **Item Group**:
   - Menu: **Stock > Item Group**
   - Buat 4 grup: `Bahan Baku`, `Bahan Penolong`, `Barang Dalam Proses`, `Produk Jadi` (di bawah `All Item Groups`).
2. **Warehouse (Gudang)**:
   - Menu: **Stock > Warehouse**
   - Buat 3 gudang utama:
     - `Gudang Bahan Baku - RF` (Tipe: Stores)
     - `Gudang WIP Produksi - RF` (Tipe: Work In Progress)
     - `Gudang Barang Jadi - RF` (Tipe: Finished Goods)
3. **Item**:
   - Menu: **Stock > Item**
   - Masukkan seluruh item dari `03_Item.csv`.
   - *Penting:* Untuk bahan baku, pastikan centang `Is Stock Item`. Untuk produk jadi, pastikan centang `Allow Production Order / Include in Manufacturing`.
4. **Supplier & Customer**:
   - Menu: **Buying > Supplier** & **Selling > Customer**
   - Masukkan mitra dari `04_Supplier.csv` dan `05_Customer.csv`.

---

### TAHAP 2: Setup Manufaktur (Operations, Workstations & BOM)
1. **Workstations**:
   - Menu: **Manufacturing > Workstation**
   - Buat 4 stasiun kerja: `WS-POTONG`, `WS-LAS`, `WS-CAT`, `WS-RAKIT`. Masukkan tarif per jam (Hour Rate).
2. **Operations**:
   - Menu: **Manufacturing > Operation**
   - Buat 4 operasi: `Pemotongan Bahan Baku`, `Pengelasan Rangka`, `Pengecatan dan Finishing`, `Perakitan Akhir & QC`.
3. **Bill of Materials (BOM)**:
   - Menu: **Manufacturing > Bill of Materials**
   - Buat BOM baru untuk `PROD-MEJA-01`:
     - **Item Quantity:** 1 Nos
     - **With Operations:** Centang (Aktifkan Routing)
     - **Items Table:** Masukkan bahan baku:
       - `RAW-KAYU-01`: 1 Nos
       - `RAW-PIPA-01`: 0.5 Batang
       - `RAW-BAUT-01`: 8 Nos
       - `RAW-CAT-01`: 0.25 Kaleng
       - `RAW-KAKI-01`: 4 Nos
       - `RAW-AMPLAS-01`: 1 Lembar
     - **Operations Table:**
       - Pemotongan (WS-POTONG, 15 menit)
       - Pengelasan (WS-LAS, 20 menit)
       - Pengecatan (WS-CAT, 15 menit)
       - Perakitan (WS-RAKIT, 20 menit)
     - Klik **Save** dan **Submit**.

---

### TAHAP 3: Input Saldo Awal Persediaan
- Menu: **Stock > Stock Entry**
- Type: **Material Receipt**
- Target Warehouse: `Gudang Bahan Baku - RF`
- Masukkan item dan kuantitas sesuai `08_Opening_Stock_Stock_Entry.csv`.
- Klik **Submit**. Cek laporan **Stock Ledger** atau **Stock Balance** untuk memastikan stok bertambah.

---

### TAHAP 4: Siklus Produksi (Work Order & Job Cards)
1. **Sales Order (Pesanan Masuk)**:
   - Menu: **Selling > Sales Order**
   - Customer: `Toko Furnitur Sejahtera Abadi`
   - Item: `PROD-MEJA-01`, Qty: 10 Nos @ Rp 475.000.
   - Klik **Save** dan **Submit**.
2. **Work Order (SPK Produksi)**:
   - Dari Sales Order yang telah di-submit, klik **Create > Work Order** (atau melalui **Manufacturing > Work Order**).
   - Quantity to Manufacture: 10
   - Source Warehouse: `Gudang Bahan Baku - RF`
   - WIP Warehouse: `Gudang WIP Produksi - RF`
   - FG Warehouse: `Gudang Barang Jadi - RF`
   - Klik **Save** dan **Submit**.
3. **Transfer Bahan Baku ke Lantai Pabrik**:
   - Di dalam Work Order, klik **Start > Transfer Material for Manufacture**.
   - ERPNext akan membuat **Stock Entry** yang memindahkan bahan dari `Gudang Bahan Baku - RF` ke `Gudang WIP Produksi - RF`.
   - Periksa ketersediaan dan klik **Submit**.
4. **Eksekusi Job Card (Operasi di Setiap Stasiun Kerja)**:
   - Buka menu **Manufacturing > Job Card**.
   - Terdapat 4 Job Card untuk pesanan 10 meja ini.
   - Buka tiap Job Card secara berurutan, klik **Start Job**, isi waktu kerja, lalu klik **Complete Job**.
5. **Penyelesaian Barang Jadi (Manufacture Stock Entry)**:
   - Kembali ke Work Order, klik **Finish > Manufacture**.
   - Sistem akan mencatat pemakaian bahan baku dari WIP dan menambahkan 10 unit `PROD-MEJA-01` ke `Gudang Barang Jadi - RF`.
   - ERPNext akan menghitung total HPP (Harga Pokok Produksi) termasuk biaya bahan + biaya operasional stasiun kerja secara otomatis.
   - Klik **Submit**. Status Work Order berubah menjadi **Completed**.

---

### TAHAP 5: Pengiriman & Penjualan (Delivery & Invoicing)
1. **Delivery Note (Surat Jalan)**:
   - Buka Sales Order sebelumnya, klik **Create > Delivery**.
   - Set Warehouse: `Gudang Barang Jadi - RF`.
   - Submit Delivery Note (Stok barang jadi berkurang 10 unit).
2. **Sales Invoice (Faktur Penjualan)**:
   - Dari Delivery Note, klik **Create > Invoice**.
   - Total tagihan: Rp 4.750.000. Submit invoice.
3. **Payment Entry (Penerimaan Uang)**:
   - Klik **Make > Payment**, terima pembayaran ke akun Kas/Bank.

---

### TAHAP 6: Analisis Laporan Manufaktur
Buka dan pelajari laporan berikut di ERPNext:
- **Manufacturing > Reports > Production Analytics**
- **Manufacturing > Reports > BOM Cost Tool**
- **Stock > Reports > Stock Balance** (Memantau mutasi stok di ketiga gudang)
- **Accounts > Reports > Profit and Loss Statement** (Melihat Margin Keuntungan dari penjualan produk manufaktur)
