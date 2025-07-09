# Telegram Data Analytical Platform

A well-designed data platform significantly enhances data analysis. This project implements an end-to-end data pipeline to answer key business questions from Telegram data, such as:

- **Top 10 most frequently mentioned medical products or drugs across all channels**
- **Price or availability variations of specific products across channels**
- **Channels with the most visual content (e.g., images of pills vs. creams)**
- **Daily and weekly trends in posting volume for health-related topics**

To achieve this, the project uses a modern ELT (Extract, Load, Transform) framework:

- **Extract**: Scrape raw data from Telegram channels.
- **Load**: Store raw data in a Data Lake, then load into a PostgreSQL data warehouse.
- **Transform**: Clean and remodel data using dbt into a dimensional star schema for analytics.
- **Enrich**: Apply object detection (YOLO) on images for advanced insights.
- **Expose**: Serve analytical insights via a FastAPI-powered API.

## Features
- Reproducible project environment and secure pipeline
- Data scraping and collection pipeline
- Dimensional data modeling (star schema) in PostgreSQL
- Data cleaning and transformation with dbt
- Data enrichment using YOLO object detection
- Analytical API for querying insights (FastAPI)

## Project Structure
```
├── src/            # Core source code (core, models, services, utils)
├── scripts/        # Utility scripts
├── examples/       # Example usage and sample data
├── notebooks/      # Jupyter notebooks for analysis
├── config/         # Configuration files
├── data/           # Data lake and intermediate storage
├── tests/          # Unit and integration tests
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd Telegram-Data-to-an-Analytical-API
   ```
2. Create and activate a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy and configure the `.env` file as needed.

## Usage
- **Data Extraction:**
  - Run the scraping pipeline to collect Telegram data into the data lake.
- **Data Loading:**
  - Load raw data into PostgreSQL using provided scripts.
- **Transformation:**
  - Use dbt to run data cleaning and modeling jobs.
- **Enrichment:**
  - Run YOLO object detection scripts on image data.
- **API:**
  - Start the FastAPI server to expose analytical endpoints.

Example commands and detailed instructions can be found in the `examples/` and `notebooks/` directories.

## Configuration
- Edit the `.env` file to set up your database credentials, Telegram API keys, and other environment variables.
- Adjust configuration files in the `config/` directory as needed.

## Testing
- Run unit and integration tests with:
  ```bash
  pytest tests/
  ```

## License
[MIT](LICENSE)

---

For more information, see the documentation in the `docs/` folder or contact the project maintainer.
