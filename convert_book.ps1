$sourceHtml = "C:\Users\Windows 10\.gemini\antigravity\scratch\ERP_Rio Ferdinanda\Buku_Pembelajaran_Rio_Ferdinanda.html"
$destDocx1 = "C:\Users\Windows 10\.gemini\antigravity\scratch\ERP_Rio Ferdinanda\BUKU_PEMBELAJARAN_ERPNEXT_RIO_FERDINANDA_12030123140254.docx"
$destDocx2 = "C:\Users\Windows 10\Downloads\Buku Pembelajaran\BUKU_PEMBELAJARAN_ERPNEXT_RIO_FERDINANDA_12030123140254.docx"
$destPdf1  = "C:\Users\Windows 10\.gemini\antigravity\scratch\ERP_Rio Ferdinanda\BUKU_PEMBELAJARAN_ERPNEXT_RIO_FERDINANDA_12030123140254.pdf"
$destPdf2  = "C:\Users\Windows 10\Downloads\Buku Pembelajaran\BUKU_PEMBELAJARAN_ERPNEXT_RIO_FERDINANDA_12030123140254.pdf"

Write-Host "Starting Word Application..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

Write-Host "Opening HTML source: $sourceHtml"
$doc = $word.Documents.Open($sourceHtml)

Write-Host "Saving as DOCX to scratch folder..."
$doc.SaveAs([ref]$destDocx1, [ref]16)

Write-Host "Saving as DOCX to Downloads/Buku Pembelajaran..."
$doc.SaveAs([ref]$destDocx2, [ref]16)

Write-Host "Exporting to PDF..."
try {
    $doc.SaveAs([ref]$destPdf1, [ref]17)
    $doc.SaveAs([ref]$destPdf2, [ref]17)
    Write-Host "PDF exported successfully!"
} catch {
    Write-Host "PDF export warning: $_"
}

$doc.Close()
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($doc) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host "Conversion completed successfully!"
Get-ChildItem $destDocx1, $destDocx2, $destPdf1, $destPdf2 -ErrorAction SilentlyContinue | Select-Object FullName, Length
