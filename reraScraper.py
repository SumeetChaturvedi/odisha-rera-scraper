import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class OdishaReraScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        prefs = {"profile.default_content_setting_values.geolocation": 2}
        chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 30)
        self.driver.maximize_window()

    def close_location_popup(self):
        """Close the location popup if it appears"""
        try:
            time.sleep(2)
            ok_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Ok')]")
            ok_button.click()
            print("Closed location popup.")
            time.sleep(1)
        except Exception:
            pass

    def scrape_projects(self):
        try:
            print("Navigating to RERA website...")
            self.driver.get("https://rera.odisha.gov.in/projects/project-list")
            time.sleep(5)
            self.close_location_popup()
            self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card-body")))
            time.sleep(2)

            cards = self.driver.find_elements(By.CSS_SELECTOR, ".card-body")
            print(f"Found {len(cards)} project cards")
            projects_data = []

            for i in range(min(6, len(cards))):
                try:
                    card = self.driver.find_elements(By.CSS_SELECTOR, ".card-body")[i]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    time.sleep(1)
                    card.click()
                    print(f"Clicked project card {i+1}")
                    # Wait for details page to load (wait for a unique element on the details page)
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".project-details, .mat-card, .container-fluid")))
                    time.sleep(2)
                    project_data = self.extract_project_details(self.driver.current_url)
                    if project_data and any(v != 'Not Found' for v in project_data.values()):
                        projects_data.append(project_data)
                    else:
                        print(f"No valid data found for project {i+1}")
                    # Go back to the project list
                    self.driver.back()
                    self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".card-body")))
                    time.sleep(2)
                except Exception as e:
                    print(f"Error processing project {i+1}: {str(e)}")
                    continue

            return projects_data

        except Exception as e:
            print(f"Error in main scraping process: {str(e)}")
            return []

    def extract_project_details(self, project_url):
        try:
            print(f"Opening project URL: {project_url}")
            self.driver.get(project_url)
            time.sleep(8)

            project_data = {
                'Rera Regd. No': 'Not Found',
                'Project Name': 'Not Found',
                'Promoter Name': 'Not Found',
                'Promoter Address': 'Not Found',
                'GST No': 'Not Found'
            }

            promoter_tab_selectors = [
                "//button[contains(text(), 'Promoter')]",
                "//a[contains(text(), 'Promoter')]",
                "//div[contains(text(), 'Promoter')]",
                "//span[contains(text(), 'Promoter')]",
                "//li[contains(text(), 'Promoter')]"
            ]

            for selector in promoter_tab_selectors:
                try:
                    tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    if tab:
                        self.driver.execute_script("arguments[0].click();", tab)
                        time.sleep(3)
                        print("Clicked Promoter Details tab")
                        break
                except:
                    continue

            page_content = self.driver.find_element(By.TAG_NAME, "body").text

            # Extract RERA Registration Number
            rera_patterns = [
                r'RERA\s*Regd\.?\s*No\.?\s*:?\s*([A-Z0-9/\-]+)',
                r'Registration\s*No\.?\s*:?\s*([A-Z0-9/\-]+)',
                r'RERA\s*No\.?\s*:?\s*([A-Z0-9/\-]+)'
            ]
            for pattern in rera_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    project_data['Rera Regd. No'] = match.group(1).strip()
                    break

            # Extract Project Name
            name_patterns = [
                r'Project\s*Name\s*:?\s*([^\n\r]+)',
                r'Name\s*:?\s*([^\n\r]+)'
            ]
            for pattern in name_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    project_data['Project Name'] = match.group(1).strip()
                    break

            # Extract Promoter Name
            promoter_patterns = [
                r'Company\s*Name\s*:?\s*([^\n\r]+)',
                r'Promoter\s*Name\s*:?\s*([^\n\r]+)',
                r'Developer\s*Name\s*:?\s*([^\n\r]+)'
            ]
            for pattern in promoter_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    project_data['Promoter Name'] = match.group(1).strip()
                    break

            # Extract Promoter Address
            address_patterns = [
                r'Registered\s*Office\s*Address\s*:?\s*([^\n\r]+(?:\n[^\n\r]+)*)',
                r'Office\s*Address\s*:?\s*([^\n\r]+(?:\n[^\n\r]+)*)',
                r'Address\s*:?\s*([^\n\r]+(?:\n[^\n\r]+)*)'
            ]
            for pattern in address_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    address = match.group(1).strip()
                    address = re.sub(r'\s+', ' ', address)
                    project_data['Promoter Address'] = address
                    break

            # Extract GST Number
            gst_patterns = [
                r'GST\s*No\.?\s*:?\s*([A-Z0-9]{15})',
                r'GSTIN\s*:?\s*([A-Z0-9]{15})',
                r'GST\s*Identification\s*No\.?\s*:?\s*([A-Z0-9]{15})'
            ]
            for pattern in gst_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    project_data['GST No'] = match.group(1).strip()
                    break

            return project_data

        except Exception as e:
            print(f"Error extracting project details: {str(e)}")
            return None

    def save_to_csv(self, projects_data, filename='rera_projects.csv'):
        if projects_data and any(any(v != 'Not Found' for v in row.values()) for row in projects_data):
            df = pd.DataFrame(projects_data)
            df.to_csv(filename, index=False)
            print(f"\nData saved to {filename}")
            return True
        else:
            print("No data to save")
            return False

    def close_driver(self):
        if self.driver:
            self.driver.quit()

def main():
    scraper = OdishaReraScraper()
    try:
        print("Starting RERA project scraping...")
        projects_data = scraper.scrape_projects()
        if projects_data:
            print(f"\nSuccessfully scraped {len(projects_data)} projects:")
            print("=" * 100)
            for i, project in enumerate(projects_data, 1):
                print(f"\nProject {i}:")
                for key, value in project.items():
                    if value != 'Not Found':
                        print(f"  {key}: {value}")
                print("-" * 50)
            scraper.save_to_csv(projects_data)
        else:
            print("No projects were successfully scraped")
            print("This might be due to:")
            print("1. Website structure changes")
            print("2. Network issues")
            print("3. Content loading delays")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        input("Press Enter to close browser and exit...")
        scraper.close_driver()

if __name__ == "__main__":
    main()
