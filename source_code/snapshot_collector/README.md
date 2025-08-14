# Web Snapshot and Privacy Analysis Module

This module is designed to automatically capture snapshots of web services discovered via mDNS and analyze the captured content for potential privacy leaks.

## Features

- **Web Snapshotting**: Concurrently captures screenshots of web pages from a list of IP addresses.
- **OCR Text Extraction**: Extracts text from screenshots using EasyOCR, supporting both Chinese and English.
- **Rule-Based Privacy Analysis**: Detects common PII (Personally Identifiable Information) like names, locations, MAC addresses, public IPs, emails, and phone numbers using regular expressions and dictionaries.
- **LLM-Based Privacy Analysis**: Utilizes a Large Language Model (LLM) for deeper, context-aware privacy analysis, identifying a broader range of sensitive information.

## Directory Structure

```
snapshot_collector/
│
├── browser_automation.py   # Script for taking web snapshots
├── privacy_analyze.py      # Script for OCR and privacy analysis
├── ip_list.csv             # Input file with IP addresses to snapshot
├── English_Names_Corpus（2W）.txt # English name corpus for rule-based analysis
├── requirements.txt        # Python dependencies
├── output/                 # Directory for all output files
│   ├── screenshots/        # Stores captured PNG snapshots
│   ├── successful_ips.txt  # Log of successfully captured IPs
│   ├── ocr_results.csv     # CSV with extracted text from screenshots
│   ├── privacy_analysis_rule_based.csv # Results from rule-based analysis
│   └── privacy_analysis_llm.csv      # Results from LLM-based analysis
└── README.md               # This file
```

## How to use

### 1. Prerequisites

- Python 3.8+
- Tesseract-OCR (required by EasyOCR). Follow installation instructions for your OS.
- An API key for the Large Language Model used in `privacy_analyze.py`.

### 2. Installation

Clone the repository and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Configuration

1. **IP List**: Create an `ip_list.csv` file in the `snapshot_collector` directory.  Each row should contain one IP address.

    ```csv
    # ip_list.csv
    8.8.8.8
    1.1.1.1
    ...
    ```

2. **Name Corpus**: Ensure the `English_Names_Corpus（2W）.txt` file is present in the `snapshot_collector` directory.
3. **API Key**: Open `privacy_analyze.py` and replace `"YOUR_API_KEY"` with your actual OpenAI-compatible API key.

### 4. Output

After the scripts complete, you can find the results in the `output/` directory:
- `ocr_results.csv`: Raw text extracted from each screenshot.
- `privacy_analysis_rule_based.csv`: Structured results from the rule-based scanner.
- `privacy_analysis_llm.csv`: Structured boolean results from the LLM scanner.

