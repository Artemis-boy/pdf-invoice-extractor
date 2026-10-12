# PDF Invoice Data Extractor

Turn a pile of PDF invoices into ONE tidy spreadsheet. Built as a portfolio
project for Data Entry / VA work — proof that hours of manual copying can
become a one-minute command.

No API keys. No external services. Runs fully offline.

## Features

- **Key-field extraction** — invoice number, date, vendor, bill-to, line
  items (description, qty, unit price, amount), and total per PDF.
- **Batch processing** — one command processes ALL PDFs in an input folder
  into a single `.xlsx` with two sheets:
  - `Summary` — one row per invoice (file, number, date, vendor, bill-to,
    item count, total, status)
  - `Items` — one row per line item (invoice number, description, qty,
    unit price, amount)
- **Result report** — prints successes + failures with failed filenames so
  you can check them manually; failed files also get a `FAILED` row in
  `Summary` instead of stopping the batch.
- **CLI only** — no GUI/web (see Limitations for the upgrade path).

## Project structure

```text
pdf-invoice-extractor/
├── extractor.py            # the tool: python extractor.py --input DIR --output OUT.xlsx
├── make_dummy_invoices.py  # regenerates the 5 fictional sample PDFs
└── contoh/
    ├── input/              # 5 sample invoice PDFs (English, USD, fictional vendors)
    └── hasil.xlsx          # example output produced from those 5 PDFs
```

## Requirements

- Python 3.10+
- `pdfplumber`, `pandas`, `openpyxl` (extraction)
- `fpdf2` (only to regenerate the dummy samples)

## Installation

```bash
git clone https://github.com/Artemis-boy/pdf-invoice-extractor.git
cd pdf-invoice-extractor
pip install pdfplumber pandas openpyxl fpdf2
```

## Usage

```bash
# Extract every PDF in a folder into one spreadsheet
python extractor.py --input contoh/input --output contoh/hasil.xlsx
```

Example output:

```text
OK    INV-2026-001.pdf -> INV-2026-001 (3 items, $226.97)
OK    INV-2026-002.pdf -> INV-2026-002 (4 items, $112.97)
OK    INV-2026-003.pdf -> INV-2026-003 (3 items, $250.65)
OK    INV-2026-004.pdf -> INV-2026-004 (3 items, $853.00)
OK    INV-2026-005.pdf -> INV-2026-005 (3 items, $234.98)

Done: 5 succeeded, 0 failed, out of 5 files -> contoh/hasil.xlsx
```

Failed files print as `FAIL <name> (<reason>)`, get a `FAILED: ...` status
row in the `Summary` sheet, and are listed at the end for manual review.
An empty input folder exits with code 1 and `No PDF files found in <dir>`.

### As a library

```python
from extractor import extract_one

summary, items = extract_one("contoh/input/INV-2026-001.pdf")
print(summary["vendor"], summary["total"])  # Acme Office Supplies 226.97
print(items[0])  # {'invoice_number': ..., 'description': ..., 'qty': 10, ...}
```

### Regenerating the samples

```bash
python make_dummy_invoices.py   # rewrites the 5 PDFs in contoh/input/
```

## Example: input → output

Input (`contoh/input/INV-2026-001.pdf`, fictional vendor):

```text
INVOICE
Acme Office Supplies
123 Market Street, Springfield, USA
Invoice Number: INV-2026-001
Invoice Date: 2026-09-15
Bill To: Globex Retail, 456 Harbor Ave, Shelbyville, USA
Description | Qty | Unit Price | Amount
Ballpoint pens (box of 12) | 10 | $4.50 | $45.00
A4 copy paper (ream) | 20 | $6.25 | $125.00
Stapler, heavy duty | 3 | $18.99 | $56.97
Total Due: $226.97
```

Output (`contoh/hasil.xlsx`):

- `Summary`: `INV-2026-001.pdf | INV-2026-001 | 2026-09-15 | Acme Office
  Supplies | Globex Retail, ... | 3 | 226.97 | OK`
- `Items`: 3 rows, one per product above.

## Limitations

- **Fixed-label parsing**: the extractor looks for labels like
  `Invoice Number:` / `Invoice Date:` / `Total Due:` and an item table
  between the `Description Qty ...` header and the total line. Invoices in
  a different layout will land in `FAILED` — that is by design for the MVP
  (a generic/table-fallback parser is the planned upgrade).
- **Text PDFs only**: scanned/image-only PDFs have no text layer and will
  fail — they need OCR first (out of scope for this MVP).
- **English + USD samples**; the parser itself is label-driven, so other
  currencies work if the `$` format matches `1,234.56`.

## License

MIT — free for personal and commercial use.
