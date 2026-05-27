import pdfplumber, sys
sys.stdout.reconfigure(encoding='utf-8')
with pdfplumber.open(r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\FCT_10_2_14_final_version.pdf') as pdf:
    page = pdf.pages[27]
    words = page.extract_words()
    for w in words[:40]:
        print(f"x={w['x0']:.0f} y={w['top']:.0f}: {w['text']}")
