<img width="105" height="29" alt="image" src="https://github.com/user-attachments/assets/5b8c62a8-45a1-4ccc-af21-e2608d51cb8e" /># ScrapPaper-Abstract-Fetcher

A lightweight Python script that reads [ScrapPaper](https://github.com/rafsanlab/ScrapPaper) CSV output and automatically fetches the abstract of each paper, saving each abstract as an individual `.txt` file named after the paper title.

> **Currently supports: PubMed only.**

---

## How It Works

This script is designed as a downstream companion to [ScrapPaper](https://github.com/rafsanlab/ScrapPaper). The workflow is:

```
ScrapPaper  →  CSV file  →  ScrapPaper-Abstract-Fetcher  →  .txt files (one per paper)
```

1. Run **ScrapPaper** on a PubMed search to generate a CSV file
2. Feed that CSV into this script
3. The script visits each paper's link, extracts the abstract, and saves it as a `.txt` file named after the paper title

---

## Prerequisites

### Step 1 — Run ScrapPaper first

This script depends on the CSV output produced by [ScrapPaper](https://github.com/rafsanlab/ScrapPaper). Please follow ScrapPaper's instructions to generate your CSV before using this script.

The expected CSV format (produced by ScrapPaper) is:

| Column      | Description                           |
|-------------|---------------------------------------|
| `Title`     | Paper title (used as output filename) |
| `Links`     | URL to the paper page                 |  
| `References`| Citation information                  |

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python abstract_fetcher.py --input your_scrappaper_output.csv
```

Output `.txt` files will be saved in the current directory, each named after the paper title.

---

## Output Example

Given a paper titled `"CRISPR-Cas9 in cancer therapy"`, the script produces:

```
CRISPR-Cas9 in cancer therapy.txt
```

Contents:
```
CRISPR-Cas9 has emerged as a powerful tool for cancer therapy...
```

---

## Limitations

- Currently only supports **PubMed** links from ScrapPaper output
- Google Scholar support is not implemented
- Web scraping may be affected by rate limiting or page structure changes

---

## Acknowledgements

This project is built on top of [ScrapPaper](https://github.com/rafsanlab/ScrapPaper) by [@rafsanlab](https://github.com/rafsanlab).

> Rafsanjani, M. R. (2022). ScrapPaper: A web scrapping method to extract journal information from PubMed and Google Scholar search result using Python. *bioRxiv*. https://doi.org/10.1101/2022.03.08.483427

---

## License

MIT License
