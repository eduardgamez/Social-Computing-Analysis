# Social Computing & Network Analysis

This repository contains a comprehensive social network analysis project for the **Social Computing and Personalization** course at the **Technical University of Madrid (UPM)**. The project focuses on leveraging advanced graph theory and GPU-accelerated computing to extract insights from real-world complex systems.

## Project Overview

**(...NETWROK INFO...)**

The analysis includes:

* **Topology Characterization:** Global metrics (density, diameter, average path length).
* **Centrality Analysis:** Identification of influential nodes using Degree, Betweenness, and Eigenvector centralities.
* **Community Detection:** Clustering analysis using the Louvain Method to identify functional sub-groups.
* **Robustness Testing:** Evaluating network stability against targeted attacks on high-betweenness hubs.

## Technical Stack

* **Language:** Python 3.10
* **Core Library:** [NetworkX](https://networkx.org/)
* **GPU Acceleration:** [NVIDIA RAPIDS cuGraph](https://rapids.ai/libcugraph.html) (via NetworkX Dispatching)
* **Visualization:** Gephi (static) and PyVis (interactive HTML)
* **Environment Management:** Conda

## Hardware Acceleration (RTX 50-Series Blackwell)

This project is optimized for high-performance computing. It utilizes **NetworkX Dispatching** to offload heavy graph algorithms (like Betweenness Centrality) to the GPU.

* **GPU:** NVIDIA GeForce RTX 5050 (8GB VRAM)
* **Architecture:** Blackwell
* **CUDA Version:** 13.1
* **Backend:** `nx-cugraph`

> **Note on Reproducibility:** The code is designed to be hardware-agnostic. If a compatible NVIDIA GPU is not detected, NetworkX will automatically fallback to CPU execution without any code modifications.

## Getting Started

### Prerequisites
Ensure you have [Conda](https://docs.conda.io/en/latest/) installed on your system (**WSL2** is highly recommended for Windows users to ensure full CUDA compatibility).

### Data Setup
This project uses the **[BACI International Trade Database (HS92 Revision)](https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37)**:

1) Download the raw CSV files for the desired years from CEPII BACI (click in the URL above).

2) Place the raw CSVs in data/raw/ and the country code dictionary in data/.

3) Run python src/data_processing.py to generate the optimized Parquet files.

### Installation

1) **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
   ```

2) **Create the environment from the environment.yml file:**

    ```bash
    conda env create -f environment.yml
    conda activate computacion_social
    ```

3) **(Optional) Enable GPU acceleration in your terminal:**

    ```bash
    export NETWORKX_AUTOMATIC_BACKENDS=cugraph
    ```

## Repository Structure
    data/               # Raw and processed datasets.
    notebooks/          # Exploratory Data Analysis (Jupyter Notebooks).
    results/            # Visualizations and final report.
    environment.yml     # Conda environment specification.
    README.md           # Project documentation.