
# Service Semantic Enhancer

## Overview

This project aims to perform semantic analysis and enhancement of network service names by combining Large Language Models (LLMs), Latent Dirichlet Allocation (LDA), and TF-IDF techniques.  
It can automatically generate human-readable descriptions for services, determine the optimal number of service categories, extract representative keywords for each category, and produce feature vectors for subsequent machine learning tasks.

## Key Features

- **LLM Semantic Descriptions**: Uses a Large Language Model to generate detailed semantic descriptions for given service names, including application scenarios, common devices, and service types.
- **LDA Topic Modeling**:
  - Automatically determines the optimal number of service categories (topics).
  - Extracts the most representative high-frequency keywords for each category.
- **TF-IDF Vectorization**: Converts service names into TF-IDF feature vectors for use in classification, clustering, and other tasks.
- **Modular Design**: Clear code structure with functionalities split into separate modules, making it easy to maintain and extend.

## Project Structure

```

semantic_enhancer/
├── service_semantic_enhancer.py  # Main program entry and workflow orchestration
├── llm_handler.py                # Wrapper for interacting with the LLM
├── lda_model.py                  # Encapsulation of the LDA model for topic modeling
├── tfidf_model.py                # Encapsulation of the TF-IDF model for text vectorization
└── utils.py                      # Utility functions, such as text preprocessing

```

## Configuration

Before running the project, you need to configure your LLM API credentials.

Open the `service_semantic_enhancer.py` file, locate the `if __name__ == "__main__":` block, and enter your `API_KEY` and `BASE_URL`:

```python
if __name__ == "__main__":
    # Replace with your API key and base URL
    API_KEY = "YOUR_API_KEY"
    BASE_URL = "YOUR_BASE_URL"
    # ...
```

## Output Example

The program will first print the LLM-generated description for each service, then output a JSON object containing all analysis results.

```json
LLM Description for '_http._tcp.local.': ···

--- Final Result ---
{
  "best_topic_num": 2,
  "lda_topic_keywords": [
    [
      "tcp",
      "web",
      "http",
      "hosting"
    ],
    [
      "remote", 
      "office", 
      "automation",
      "printer"
    ]
  ],
  "services": [
    {
      "service_name": "_http._tcp.local.",
      "tfidf_vector": [ ... ],
      "llm_description": "The service \"_http._tcp.local.\" refers to a standard way of advertising and discovering web servers (HTTP services) on a local network using Zeroconf networking protocols like Bonjour or Avahi. ..."
    },
    {
      "service_name": "_printer._tcp.local.",
      "tfidf_vector": [ ... ],
      "llm_description": "The service `_printer._tcp.local.` is a standard service type used in Zeroconf networking (like Apple's Bonjour or the open-source Avahi) to advertise and discover printers on a local network. ..."
    }
  ]
}
```
