# ⚽ Premier League Market Value Tracker (Zero-Cost ELT Pipeline)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![DuckDB](https://img.shields.io/badge/DuckDB-1.5.4-yellow)
![Streamlit](https://img.shields.io/badge/Streamlit-1.26.0-red)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-brightgreen)

An automated, fully serverless data engineering pipeline that tracks and analyzes the weekly market valuations of all Premier League football players. 

**🔴 Live Dashboard:** [https://footballvaluetracker-2fx8ypspcetwdf6f8dq3ig.streamlit.app/]

---

## 🏗 Architecture & Data Flow

This project utilizes a modern "Zero-Dollar Data Stack," proving that enterprise-grade automation and analytics can be achieved with lightweight, serverless tools.

1. **Extraction (GitHub Actions & ScraperAPI):** A weekly cron job triggers a Python script that utilizes residential proxies to bypass enterprise bot protection (Cloudflare) and scrape dynamic HTML tables from Transfermarkt.
2. **Storage (Parquet):** Raw extracted data is transformed using Pandas and compressed locally into the columnar Parquet format, reducing file size by ~80% compared to CSV.
3. **Load & Transform (MotherDuck/DuckDB):** The Parquet file is instantly loaded into a serverless MotherDuck cloud data warehouse.
4. **Visualization (Streamlit):** A decoupled front-end queries the cloud data warehouse in real-time to serve an interactive dashboard.

---

## 🧠 Engineering Challenges Solved

### 1. Bypassing Enterprise Bot Protection
* **Problem:** Transfermarkt heavily utilizes Cloudflare to block automated requests from known data center IPs (like Microsoft Azure, where GitHub Actions are hosted).
* **Solution:** Integrated **ScraperAPI** to route extraction requests through residential proxies, ensuring the CI/CD runner could successfully extract the HTML payloads without triggering captchas or IP bans.

### 2. Compute & Storage Optimization
* **Problem:** Traditional cloud data warehouses (Snowflake, BigQuery) have high idle costs and are over-engineered for megabyte-scale scraping pipelines.
* **Solution:** Leveraged **DuckDB** and **MotherDuck** to infer schemas directly from Parquet files and execute blazing-fast OLAP queries serverlessly, keeping infrastructure costs at exactly $0.00.

### 3. Environment Dependency Decoupling
* **Problem:** Deploying the Streamlit dashboard failed due to out-of-memory errors when the Linux server attempted to build heavy backend libraries (like `pyarrow`).
* **Solution:** Decoupled the environment into `requirements.txt` (lightweight frontend UI dependencies) and `scraper_requirements.txt` (heavy backend data processing dependencies), ensuring reliable and fast cloud deployments.

### 4. Secret Management & Incident Response
* **Problem:** Cloud database tokens must be protected from public GitHub exposure.
* **Solution:** Implemented robust secret management using GitHub Repository Secrets for the backend CI/CD runner, Streamlit Cloud Secrets for the frontend, and local `.env`/`secrets.toml` files ignored via strict `.gitignore` policies.

---

## 🚀 How to Run Locally

If you want to clone this repository and run the pipeline on your own machine:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)[Your GitHub Username]/football_value_tracker.git
   cd football_value_tracker
Set up a virtual environment and install dependencies:

Bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
pip install -r scraper_requirements.txt
Configure Secrets:

Create a folder named .streamlit and a file inside named secrets.toml.

Add your MotherDuck token: MOTHERDUCK_TOKEN = "your_token_here"

Run the Dashboard:

Bash
python -m streamlit run app.py

Developed by [Shashwat Shrivastava] - Connect with me on [https://www.linkedin.com/in/shashwat-shrivastava-141044215/]
