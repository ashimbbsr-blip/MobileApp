"""Find the chapter headings for each code group in the FCT PDF."""
import pdfplumber, sys, re
sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\FCT_10_2_14_final_version.pdf'
CODE_RE = re.compile(r'(\d{2}_\d{4})')

with pdfplumber.open(PDF_PATH) as pdf:
    prev_prefix = None
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ''
        codes = CODE_RE.findall(text)
        if not codes:
            continue
        prefix = codes[0][:2]
        if prefix != prev_prefix:
            # Print the page before the data starts (chapter intro)
            if i > 0:
                prev_text = pdf.pages[i-1].extract_text() or ''
                print(f"\n=== New group: {prefix}_xxxx (page {i+1}) ===")
                print(prev_text[:200])
                print(f"  First item from text: {text[:300]}")
            prev_prefix = prefix
