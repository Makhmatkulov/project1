import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# List of user agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
]

keywords = [
    'Backend+developer', 'Frontend+developer', 'Data+analyst', 'Data+engineer', 'Data+scientist',
    'AI+engineer', 'Android+developer', 'IOS+developer', 'Game+developer', 'DevOps+engineer',
    'IT+project+manager', 'Network+engineer', 'Cybersecurity+Analyst', 'Full+stack+developer',
    'Cloud+Architect'
]

# Function to set a random User-Agent
def set_random_user_agent(driver):
    user_agent = random.choice(user_agents)
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})

# Initialize Chrome WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Remove this line if you want to see the browser
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to scrape job listings on a page
def scrape_jobs_on_page(driver):
    jobs = driver.find_elements(By.CSS_SELECTOR, 'div.vacancy-info--umZA61PpMY07JVJtomBA')
    job_data = []
    for job in jobs:
        try:
            title = job.find_element(By.CSS_SELECTOR, 'span[data-qa="serp-item__title-text"]').text
            company_elements = job.find_elements(By.CSS_SELECTOR, 'span[data-qa="vacancy-serp__vacancy-employer-text"]')
            company = ' '.join([element.text.replace('\xa0', ' ') for element in company_elements])
            location = job.find_element(By.CSS_SELECTOR, 'span[data-qa="vacancy-serp__vacancy-address"]').text
            job_link = job.find_element(By.CSS_SELECTOR, 'h2.bloko-header-section-2 a').get_attribute('href')

            job_data.append({
                'title': title,
                'company': company,
                'location': location,
                'job_link': job_link
            })
        except Exception as e:
            print(f"Error scraping job: {e}")
    return job_data

# Function to scrape all pages for a keyword
def scrape_all_pages(driver, base_url, total_pages, keyword):
    all_jobs = []
    for page in range(total_pages):
        set_random_user_agent(driver)  # Rotate user-agent for each page
        url = f"{base_url}&page={page}"
        driver.get(url)
        time.sleep(2)

        jobs_on_page = scrape_jobs_on_page(driver)
        for job in jobs_on_page:
            job['keyword'] = keyword.replace('+', ' ')
        all_jobs.extend(jobs_on_page)
        print(f"Scraped {len(jobs_on_page)} jobs on page {page + 1} for keyword: {keyword.replace('+', ' ')}")
    return all_jobs

# Function to scrape detailed job data
def scrape_job_details(driver, job_link):
    try:
        if not isinstance(job_link, str) or not job_link.startswith("http"):
            print(f"Invalid job link: {job_link}")
            return None
        driver.get(job_link)
        time.sleep(2)

        salary = None
        salary_element = driver.find_elements(By.CSS_SELECTOR, 'span[data-qa="vacancy-salary-compensation-type-net"]')
        if salary_element:
            salary = salary_element[0].text.replace('\xa0', ' ')

        required_experience = driver.find_element(By.CSS_SELECTOR, 'span[data-qa="vacancy-experience"]').text
        skills_elements = driver.find_elements(By.CSS_SELECTOR, 'li[data-qa="skills-element"]')
        skills = [skill.text.replace('\xa0', ' ') for skill in skills_elements]

        time_posted_element = driver.find_elements(By.CSS_SELECTOR, 'span[data-sentry-source-file="index.tsx"]')
        time_posted = time_posted_element[0].text.replace('\xa0', ' ') if time_posted_element else None

        return {
            'salary': salary,
            'required_experience': required_experience,
            'skills': skills,
            'time_posted': time_posted,
            'link': job_link
        }
    except Exception as e:
        print(f"Error fetching job details: {e}")
        return None

# Function to save data to CSV
def save_to_csv(filename, jobs):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'company', 'location', 'salary', 'required_experience', 'skills', 'time_posted', 'link', 'keyword'])
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)

# Main function
def main():
    base_url_template = "https://hh.ru/search/vacancy?text={keyword}&salary=&ored_clusters=true&items_on_page=100&order_by=publication_time&search_field=name&search_period=3&area=97&hhtmFrom=vacancy_search_list&hhtmFromLabel=vacancy_search_line"
    total_pages = 1
    filename = 'scraped_jobs.csv'

    driver = init_driver()

    try:
        all_jobs = []
        for keyword in keywords:
            print(f"Scraping jobs for keyword: {keyword.replace('+', ' ')}")
            base_url = base_url_template.format(keyword=keyword)
            jobs = scrape_all_pages(driver, base_url, total_pages, keyword)
            all_jobs.extend(jobs)

        detailed_jobs = []
        for job in all_jobs:
            print(f"Scraping details for: {job['title']}")
            details = scrape_job_details(driver, job['job_link'])
            if details:
                detailed_jobs.append({
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'salary': details['salary'],
                    'required_experience': details['required_experience'],
                    'skills': ', '.join(details['skills']),
                    'time_posted': details['time_posted'],
                    'link': details['link'],
                    'keyword': job['keyword']
                })

        save_to_csv(filename, detailed_jobs)
        print(f"Data saved to {filename}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
