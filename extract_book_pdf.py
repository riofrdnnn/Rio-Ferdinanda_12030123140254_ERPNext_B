import pypdf

def analyze_pdf(pdf_path, out_txt):
    reader = pypdf.PdfReader(pdf_path)
    print(f"=== ANALYZING: {pdf_path} ===")
    print(f"Total Pages: {len(reader.pages)}")
    
    text_content = []
    for idx, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        header = f"\n--- [PAGE {idx+1}] ---\n"
        text_content.append(header + txt)
        if idx < 5:
            print(f"Page {idx+1} preview: {txt[:200]}...")
            
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(text_content))
    print(f"Saved extracted text to {out_txt}")

def run():
    analyze_pdf("/home/frappe/buku1.pdf", "/home/frappe/buku1_text.txt")
    analyze_pdf("/home/frappe/buku2.pdf", "/home/frappe/buku2_text.txt")

if __name__ == "__main__":
    run()
