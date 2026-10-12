"""PDF Invoice Data Extractor (MVP).

Batch-extract key fields from invoice PDFs into one .xlsx file:
  - Sheet "Summary": one row per invoice
  - Sheet "Items": one row per line item

Usage:
    python extractor.py --input folder_invoice/ --output hasil.xlsx
"""
import argparse
import re
from pathlib import Path

import pdfplumber
import pandas as pd

ITEM_RE = re.compile(
    r"^(.+?)\s+(\d+)\s+\$([\d,]+\.\d{2})\s+\$([\d,]+\.\d{2})\s*$"
)
TOTAL_RE = re.compile(r"Total Due:\s*\$([\d,]+\.\d{2})")
NUMBER_RE = re.compile(r"Invoice Number:\s*(.+)")
DATE_RE = re.compile(r"Invoice Date:\s*(.+)")
BILL_RE = re.compile(r"Bill To:\s*(.+)")


def money(s):
    return float(s.replace(",", ""))


def extract_one(path):
    """Return (summary_dict, [item_dicts]). Raises on failure."""
    with pdfplumber.open(path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("no extractable text (scanned image?)")

    def grab(rx):
        m = rx.search(text)
        return m.group(1).strip() if m else ""

    number = grab(NUMBER_RE)
    date = grab(DATE_RE)
    bill_to = grab(BILL_RE)
    vendor = lines[1] if len(lines) > 1 and lines[0].upper() == "INVOICE" else lines[0]

    total = 0.0
    m = TOTAL_RE.search(text)
    if m:
        total = money(m.group(1))

    # item rows sit between the table header and the Total Due line
    items = []
    in_table = False
    for ln in lines:
        if not in_table:
            if ln.startswith("Description") and "Qty" in ln:
                in_table = True
            continue
        if ln.startswith("Total Due:"):
            break
        im = ITEM_RE.match(ln)
        if im:
            desc, qty, unit, amt = im.groups()
            items.append({
                "invoice_number": number,
                "description": desc.strip(),
                "qty": int(qty),
                "unit_price": money(unit),
                "amount": money(amt),
            })

    if not number:
        raise ValueError("invoice number not found")
    if not items:
        raise ValueError("no line items found")

    summary = {
        "file": Path(path).name,
        "invoice_number": number,
        "date": date,
        "vendor": vendor,
        "bill_to": bill_to,
        "item_count": len(items),
        "total": total,
        "status": "OK",
    }
    return summary, items


def main():
    ap = argparse.ArgumentParser(description="Extract invoice PDFs to one .xlsx")
    ap.add_argument("--input", required=True, help="folder with invoice PDFs")
    ap.add_argument("--output", required=True, help="output .xlsx path")
    args = ap.parse_args()

    indir = Path(args.input)
    pdfs = sorted(indir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in {indir}")
        raise SystemExit(1)

    summaries, all_items, failed = [], [], []
    for pdf in pdfs:
        try:
            summary, items = extract_one(pdf)
            summaries.append(summary)
            all_items.extend(items)
            print(f"OK    {pdf.name} -> {summary['invoice_number']} "
                  f"({summary['item_count']} items, ${summary['total']:,.2f})")
        except Exception as e:  # noqa: BLE001 - per-file, must not stop batch
            failed.append(pdf.name)
            summaries.append({
                "file": pdf.name, "invoice_number": "", "date": "",
                "vendor": "", "bill_to": "", "item_count": 0,
                "total": 0.0, "status": f"FAILED: {e}",
            })
            print(f"FAIL  {pdf.name} ({e})")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as xw:
        pd.DataFrame(summaries).to_excel(xw, sheet_name="Summary", index=False)
        pd.DataFrame(all_items).to_excel(xw, sheet_name="Items", index=False)

    print(f"\nDone: {len(pdfs) - len(failed)} succeeded, "
          f"{len(failed)} failed, out of {len(pdfs)} files -> {out}")
    if failed:
        print("Failed files (check manually):")
        for name in failed:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
