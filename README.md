
# mDNS/DNS-SD Research Toolkit

## Overview

This repository contains a collection of tools for scanning, analyzing, and simulating attacks on mDNS/DNS-SD services.
It is designed for security research, measurement studies, and proof-of-concept attack simulations.
The toolkit is organized into four independent but complementary modules:

1. **mDNS/DNS-SD Scanner** – Scans and analyzes network services responding to DNS-SD queries, supporting multiple scanning modes and amplification measurement.
2. **Service Semantic Enhancer** – Performs semantic analysis of service names using LLMs, LDA, and TF-IDF to produce meaningful descriptions and features.
3. **Attack Simulator** – Generates and replays mDNS query traffic to simulate reflection amplification attacks.
4. **Web Snapshot and Privacy Analysis Module** – Captures HTTP/HTTPS pages linked from discovered mDNS services for further analysis.

---

## Directory Structure

```
├── scanner/                  # mDNS/DNS-SD scanning and amplification measurement
│   ├── scanner.py             # Core scanning logic
│   ├── utils.py               # Helper functions for CSV logging
│   └── README.md

├── semantic_enhancer/         # Service name semantic analysis
│   ├── service_semantic_enhancer.py
│   ├── llm_handler.py
│   ├── lda_model.py
│   ├── tfidf_model.py
│   ├── utils.py
│   └── README.md

├── attack_simulator/          # Traffic generation and replay for attack simulation
│   ├── packet_gen.py
│   ├── replay.sh
│   ├── output/
│   └── README.md

snapshot_collector/
│
├── browser_automation.py   # Script for taking web snapshots
├── privacy_analyze.py      # Script for OCR and privacy analysis
├── requirements.txt        # Python dependencies
├── output/                 # Directory for all output files
└── README.md               # This file
```

---

## Module Highlights

### **1. mDNS/DNS-SD Scanner**

* Supports aggregate and separate scanning modes.
* Measures amplification factors of services.
* Exports detailed scan logs and metrics to CSV.

### **2. Service Semantic Enhancer**

* Generates human-readable service descriptions via LLM.
* Performs LDA topic modeling to categorize services.
* Uses TF-IDF vectorization for ML tasks.

### **3. Attack Simulator**

* Creates spoofed mDNS query packets in `.pcap` format.
* Batch replays traffic with configurable parameters.
* Collects and logs replay statistics.

### **4. Web Snapshot and Privacy Analysis Module**

* Web Snapshotting: Concurrently captures screenshots of web pages from a list of IP addresses.
* OCR Text Extraction: Extracts text from screenshots using EasyOCR, supporting both Chinese and English.
* Rule-Based Privacy Analysis: Detects common PII (Personally Identifiable Information) like names, locations, MAC addresses, public IPs, emails, and phone numbers using regular expressions and dictionaries.
* LLM-Based Privacy Analysis: Utilizes a Large Language Model (LLM) for deeper, context-aware privacy analysis, identifying a broader range of sensitive information.

---

## Dependencies

* Python 3.8+
* `scapy`, `pandas`, `openpyxl`
* Additional tools: `tcpreplay`, `tcpdump`, `bc` (for attack simulation)
* LLM API access for semantic analysis module.

---

## Usage
Each module contains its own `README.md` with detailed instructions.

---
