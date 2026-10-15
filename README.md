# Dataset Praktik ERPNext - Manufaktur
**Folder:** `ERP_Rio Ferdinanda`  
**Tema:** Industri Manufaktur Furnitur & Metalworking (PT Rio Ferdinanda Manufaktur)

Folder ini berisi paket lengkap dataset sederhana dan aplikatif untuk keperluan praktikum atau simulasi implementasi ERPNext pada industri manufaktur.

## Daftar Berkas:
1. `01_Item_Group.csv`: Master kategori item (Bahan Baku, Penolong, WIP, Produk Jadi).
2. `02_Warehouse.csv`: Master gudang (Bahan Baku, WIP, Produk Jadi, Scrap).
3. `03_Item.csv`: Master data item dengan atribut harga beli & jual standar.
4. `04_Supplier.csv`: Master data vendor pemasok bahan baku.
5. `05_Customer.csv`: Master data pelanggan/toko pembeli produk.
6. `06_Workstation_dan_Operation.csv`: Master stasiun kerja & routing operasi produksi beserta tarif per jam.
7. `07_Bill_of_Materials_BOM.csv`: Formula BOM dan routing operasi untuk produk jadi.
8. `08_Opening_Stock_Stock_Entry.csv`: Data saldo awal persediaan untuk modul Stock Entry.
9. `09_Skenario_Transaksi_Praktik.csv`: 12 tahapan simulasi transaksi end-to-end.
10. `Panduan_Praktik_ERPNext_Manufaktur.md`: Panduan langkah demi langkah (tutorial lab) dari input master hingga pelaporan.

## Cara Menggunakan:
- Gunakan fitur **Data Import** pada ERPNext untuk mengimpor file CSV secara berurutan sesuai nomor awalan file.
- Atau jadikan data CSV ini sebagai acuan input manual saat praktikum.
- Ikuti alur yang dijelaskan dalam `Panduan_Praktik_ERPNext_Manufaktur.md`.
