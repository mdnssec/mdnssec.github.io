
# mDNS/DNS-SD Scanner Module

## Overview

This module provides a set of tools for scanning and analyzing mDNS/DNS-SD services.  
It can discover hosts on the network that respond to DNS Service Discovery (DNS-SD) queries, perform scans in different modes, and measure response amplification factors.

## Directory Structure

```
├── scanner/
│   ├── scanner.py # Contains all core scanning logic, including aggregate scanning, separate scanning, concurrency testing, and batch processing functions.
│   ├── utils.py # `utils.py`: Contains utility functions, mainly for writing scan results (such as discovered services and amplification factors) to CSV files.
│   └── README.md # This file.
```

## Core Functions

### `scanner.py`

- `dnssd_scan()`: Performs **aggregate mode** scanning. It first sends a general service discovery request, then aggregates all discovered service names into a single request to query their details at once. This is the default and more efficient approach.
- `separate_send()`: Performs **separate mode** scanning. After discovering all service names, it sends a separate query request for each service. Mainly used for performance comparison tests.
- `magnify_test()`: Reads an IP list from an Excel file and scans them to test amplification factors.
- `model_test()`: Compares the scanning performance of aggregate mode and separate mode, and writes the results to a CSV file.
- `speed_test()`, `thread_test()`: Used to evaluate scanning speed and packet loss rates under different concurrency levels.

### `utils.py`

- `write_scan_log()`: Records detailed information of discovered services (such as target IP, service name, port, and record type) to `service.csv`.
- `get_magnify()`: Records amplification factor information for each request (such as request size, response size, and amplification factor) to `service_magnify.csv`.

## How to Use

### 1. Import as a Module

You can place the `scanner` directory in your project and import the scanning functions into other Python scripts.

```python
# Assuming your script is at the same level as the scanner/ directory
from scanner import scanner

# Perform aggregate scanning on a single IP
target_ip = "192.168.1.1" # Replace with your target IP
result = scanner.dnssd_scan(target_ip)

if result != -1 and result != 0:
    print(f"Aggregate scan successful: {target_ip}")
    print(f"  - Initial DNS-SD amplification factor: {result[0]}")
    print(f"  - Overall mDNS amplification factor: {result[1]:.2f}")
else:
    print(f"Scan failed or no services found: {target_ip}")

# Perform separate scanning on a single IP
result_sep = scanner.separate_send(target_ip)
if result_sep != -1:
    print(f"Separate scan successful: {target_ip}")
```

### 2. Run Directly

You can also run the `scanner.py` module directly to execute a built-in scanning example.
By default, it will perform both aggregate and separate scans on a single IP address (`8.8.8.8`) and print a summary of the results.

Run the following command from the **parent directory** of `scanner/`:

```bash
python -m scanner.py
```

### 3. Dependencies

This project relies on the following Python libraries:

* `scapy`
* `pandas`
* `openpyxl`

You can install them via pip:
```
pip install scapy pandas openpyxl
```
