"""Generate 3 dummy English/USD sample invoices (fictional vendors only)."""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pathlib import Path

OUT = Path(__file__).parent / "contoh" / "input"
OUT.mkdir(parents=True, exist_ok=True)

INVOICES = [
    {
        "file": "INV-2026-001.pdf",
        "vendor": "Acme Office Supplies",
        "vendor_addr": "123 Market Street, Springfield, USA",
        "number": "INV-2026-001",
        "date": "2026-09-15",
        "bill_to": "Globex Retail, 456 Harbor Ave, Shelbyville, USA",
        "items": [
            ("Ballpoint pens (box of 12)", 10, 4.50),
            ("A4 copy paper (ream)", 20, 6.25),
            ("Stapler, heavy duty", 3, 18.99),
        ],
    },
    {
        "file": "INV-2026-002.pdf",
        "vendor": "Nimbus Web Services",
        "vendor_addr": "77 Cloud Blvd, Austin, USA",
        "number": "INV-2026-002",
        "date": "2026-09-28",
        "bill_to": "Initech LLC, 101 Main St, Ogdenville, USA",
        "items": [
            ("Cloud hosting, Pro plan (monthly)", 1, 49.00),
            ("Extra storage 500 GB", 2, 9.99),
            ("Domain renewal example-shop.com", 1, 14.99),
            ("SSL certificate, 1 year", 1, 29.00),
        ],
    },
    {
        "file": "INV-2026-003.pdf",
        "vendor": "Harbor Freight & Tools Co.",
        "vendor_addr": "9 Dockside Rd, Portland, USA",
        "number": "INV-2026-003",
        "date": "2026-10-05",
        "bill_to": "Umbrella Repair Shop, 5 Elm St, Capital City, USA",
        "items": [
            ("Cordless drill 18V", 2, 89.95),
            ("Drill bit set (29 pc)", 1, 34.50),
            ("Safety goggles", 5, 7.25),
        ],
    },
    {
        "file": "INV-2026-004.pdf",
        "vendor": "Bluebird Catering Co.",
        "vendor_addr": "400 Park Avenue, New York, USA",
        "number": "INV-2026-004",
        "date": "2026-10-08",
        "bill_to": "Stark Events, 200 Broadway, New York, USA",
        "items": [
            ("Buffet lunch service (per guest)", 50, 12.75),
            ("Coffee break package", 2, 85.00),
            ("Birthday cake, chocolate 2kg", 1, 45.50),
        ],
    },
    {
        "file": "INV-2026-005.pdf",
        "vendor": "Pixel Print Studio",
        "vendor_addr": "88 Lantern Way, Seattle, USA",
        "number": "INV-2026-005",
        "date": "2026-10-11",
        "bill_to": "Wayne Design Office, 12 Hill Rd, Gotham, USA",
        "items": [
            ("Business cards, matte (500 pcs)", 2, 29.99),
            ("A3 poster print, color", 10, 5.50),
            ("Logo design revision", 1, 120.00),
        ],
    },
]


def build(inv):
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(True, 20)
    pdf.add_page()
    W = pdf.epw

    def para(text, size=11, bold=False):
        pdf.set_x(15)
        pdf.set_font("Helvetica", "B" if bold else "", size)
        pdf.multi_cell(w=W, h=6, text=text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    para("INVOICE", size=20, bold=True)
    pdf.ln(2)
    para(inv["vendor"], size=13, bold=True)
    para(inv["vendor_addr"])
    pdf.ln(2)
    para(f"Invoice Number: {inv['number']}")
    para(f"Invoice Date: {inv['date']}")
    para(f"Bill To: {inv['bill_to']}")
    pdf.ln(4)

    # items table header
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_x(15)
    col = [W * 0.55, W * 0.15, W * 0.15, W * 0.15]
    for txt, w in zip(["Description", "Qty", "Unit Price", "Amount"], col):
        pdf.cell(w=w, h=7, text=txt, border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 11)
    total = 0.0
    for desc, qty, price in inv["items"]:
        amt = qty * price
        total += amt
        pdf.set_x(15)
        pdf.cell(w=col[0], h=7, text=desc, border=1)
        pdf.cell(w=col[1], h=7, text=str(qty), border=1)
        pdf.cell(w=col[2], h=7, text=f"${price:,.2f}", border=1)
        pdf.cell(w=col[3], h=7, text=f"${amt:,.2f}", border=1)
        pdf.ln()

    pdf.ln(4)
    para(f"Total Due: ${total:,.2f}", size=13, bold=True)
    para("Payment due within 30 days. Thank you for your business!")
    pdf.output(OUT / inv["file"])
    print("wrote", inv["file"], f"total=${total:,.2f}")


for inv in INVOICES:
    build(inv)
