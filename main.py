from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import constants
import time
import regex as re

"""Obtains a list of unique internship opportunities and the companies that it's available at.
"""


driver = webdriver.Firefox()
SEARCHES = ['Software Engineering Internship', 'Data Engineering Internship']

def main():
        
    driver.implicitly_wait(10)
    all_companies = []
    # all_companies = glass_door(driver, all_companies, SEARCHES)
    all_companies = linked_in(driver, all_companies, SEARCHES)
    get_companies(all_companies)
            
    driver.quit()

def linked_in(driver, all_companies: list = [], searches: list= []):
    driver.get("https://www.linkedin.com/home")
    driver.find_element(By.ID, "session_key").send_keys(constants.LINKED_IN_EMAIL)
    driver.find_element(By.ID, "session_password").send_keys(constants.LINKED_IN_PASSWORD)
    driver.find_element(By.XPATH, "//button[@class='sign-in-form__submit-button']").click()
    
    for search in searches:
        
        search_field =  driver.find_element(By.XPATH, "//input[@class='search-global-typeahead__input']")
        search_field.clear()
        search_field.send_keys(search)
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        driver.find_element(By.XPATH, "//button[contains(., 'Jobs')]").click()
        
        find_pages = driver.find_elements(By.XPATH, "//button[starts-with(@aria-label, 'Page')]")
        total_pages = 0
        for page in find_pages:
            total_pages = max(total_pages, int(page.text))  
          
            
        try:    
            
            for current_page in range(1, total_pages+1):
                find_companies = driver.find_elements(By.XPATH, "//li[starts-with(@class, 'ember-view')]")
                for company in find_companies:
                    driver.execute_script("arguments[0].scrollIntoView();", company)
                    company_info = company.text.splitlines()
                    try:
                        if company_info[1] not in [c.name for c in all_companies]:
                                all_companies.append(Company(company_info[1], company_info[0]))
                        else:
                            all_companies[[c.name for c in all_companies].index(company_info[1])].add_role(company_info[0])
                    except IndexError:
                        pass
        except Exception:
            pass
                
        if current_page != total_pages:
            driver.find_element(By.XPATH, f"//button[starts-with(@aria-label, 'Page {current_page+1}')]").click()
            time.sleep(3)
        
        print(f"Page {current_page} of {total_pages}")
    
    return all_companies
        
    

def glass_door(driver, all_companies: list = [], searches: list = []):
    driver.get("https://www.glassdoor.sg/index.htm")
    driver.find_element(By.ID, "inlineUserEmail").send_keys(constants.GLASS_DOOR_EMAIL)
    driver.find_element(By.XPATH, "//button[@name='submit']").click()
    driver.find_element(By.ID, "inlineUserPassword").send_keys(constants.GLASS_DOOR_PASSWORD)
    driver.find_element(By.XPATH, "//button[@name='submit']").click()
    
    for search in searches:
        search_field = driver.find_element(By.ID, 'sc.keyword')
        search_field.clear()
        search_field.send_keys(search)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[name()='svg' and @class='SVGInline-svg modal_closeIcon-svg']"))).click()
        except Exception:
            pass
        
        pages = driver.find_element(By.XPATH, "//div[@class='paginationFooter']").text
        total_pages = int(re.match(r".+(\d+)$", pages).group(1))   
        print("Total Pages:", total_pages)
        
        for current_page in range(1, total_pages+1):
            wait.until(EC.presence_of_element_located((By.XPATH, "//li[starts-with(@class, 'react-job-listing')]")))
            find_companies = driver.find_elements(By.XPATH, "//li[starts-with(@class, 'react-job-listing')]")
            for company in find_companies:
                company_info = company.text.splitlines()
                if company_info[1] not in [c.name for c in all_companies]:
                    all_companies.append(Company(company_info[1], company_info[2]))
                else:
                    all_companies[[c.name for c in all_companies].index(company_info[1])].add_role(company_info[2])
                    

            pages = driver.find_element(By.XPATH, "//div[@class='paginationFooter']").text
            driver.find_element(By.XPATH, "//button[starts-with(@class, 'nextButton')]").click()
            time.sleep(2)
            print(f"Page {current_page} of {total_pages}")
    
    return all_companies

def get_companies(all_companies: list):
    for company in all_companies:
        print(f"{company.name} has the following roles: ")
        
        for role in set(company.roles):
            print(f"\t{role}")

class Company:
    def __init__(self, name, role):
        self.name = name
        self.roles = [role]
        
    def add_role(self, role):
        self.roles.append(role)

if __name__ == "__main__":
    main()