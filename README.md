# Odisha RERA Project Scraper

This project is a Python-based web scraper that extracts project details from the Odisha Real Estate Regulatory Authority (RERA) website. It uses Selenium to automate browser actions, simulating a real user to collect data from the first 6 projects listed on the site.

## 🚀 Features
- **Automated scraping** of project details from the Odisha RERA portal
- **Handles modern JavaScript/Angular websites** by simulating real user clicks
- **Extracts key fields**: RERA Registration Number, Project Name, Promoter Name, Promoter Address, GST Number
- **Saves results to CSV** for easy analysis or reporting
- **Robust error handling** and waits for dynamic content

Install dependencies:
```bash
pip install -r requirements.txt
```

## 📦 Files
- `reraScraper.py` — Main Python script for scraping
- `requirements.txt` — Python dependencies
- `rera_projects.csv` — Output file with scraped data (created after running the script)

## ⚙️ How It Works
1. **Opens the Odisha RERA project list page** in a real Chrome browser.
2. **Waits for the project cards to load** (since the site is built with Angular and loads content dynamically).
3. **Clicks on each of the first 6 project cards** to open their details (just like a human would).
4. **Extracts required information** from the details page.
5. **Returns to the project list** and repeats for the next project.
6. **Saves all collected data to a CSV file** for your use.

## 🏃‍♂️ Usage
1. Make sure you have Google Chrome installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the scraper:
   ```bash
   python3 reraScraper.py
   ```
4. After completion, check `rera_projects.csv` for your data.

## 🛠️ Troubleshooting
- **Chrome not found:** Make sure Google Chrome is installed and up to date.
- **No data scraped:** The website structure may have changed, or your internet connection may be unstable. Try running the script again.
- **Selenium errors:** Ensure all dependencies are installed and compatible with your Python version.
- **Popups block scraping:** The script tries to close popups automatically, but if you see issues, try running in visible (non-headless) mode and close popups manually.

## 🤔 Why does the script click cards instead of following links?
The Odisha RERA website is a modern JavaScript (Angular) app. Project details are loaded only when you click a card—there are no traditional links to follow. Selenium simulates a real user by clicking the cards, waiting for the details to load, scraping, and then going back.


---
 
