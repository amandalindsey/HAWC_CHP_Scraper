#*******************************************************IMPORTS*******************************************************
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
#**********************************************************************************************************************
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
driver.get("https://cad.chp.ca.gov/Traffic.aspx")
#*************************************FIRST SCRAPE FOR ALL ACTIVE INCIDENT NUMBERS*************************************
def first_scrape():
    all_CHP_incident_nos = []

    # Wait for the dropdown to be clickable and select custom region
    input_region = wait.until(EC.element_to_be_clickable((By.NAME, 'ddlSearches')))
    select_custom_region = Select(input_region)
    select_custom_region.select_by_value("1")

    # Select all regions
    select_all_regions_element = wait.until(EC.element_to_be_clickable((By.NAME, "lstCustomRegion")))
    select_all_regions = Select(select_all_regions_element)

    for option in select_all_regions.options:
        select_all_regions.select_by_value(option.get_attribute("value"))

    # Click the 'Go' button and wait for the table to load
    go_element = wait.until(EC.element_to_be_clickable((By.NAME, "btnGo")))
    go_element.click()
    wait.until(EC.presence_of_element_located((By.ID, "gvIncidents")))

    # Turn off auto updates
    find_auto_refresh_element = wait.until(EC.element_to_be_clickable((By.ID, "chkAutoRefresh")))
    find_auto_refresh_element.click()

    # Scrape the main table
    for i in range(len(driver.find_elements(By.XPATH, "//table[@id='gvIncidents']/tbody/tr")) - 1):
        # Re-locate the rows on each iteration
        rows = driver.find_elements(By.XPATH, "//table[@id='gvIncidents']/tbody/tr")[1:]  # Skip header row
        row = rows[i]
        cells = row.find_elements(By.TAG_NAME, "td")
        incident_no = cells[1].text
        all_CHP_incident_nos.append(incident_no)
    driver.quit()
    return all_CHP_incident_nos
#*************************************SECOND SCRAPE CONSIDERING SEARCH CRITERIA*************************************
def second_scrape(custom_region_list):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    driver.get("https://cad.chp.ca.gov/Traffic.aspx")

    #SELECT CUSTOM REGIONS FROM SEARCH CRITERIA
    input_region = wait.until(EC.element_to_be_clickable((By.NAME, 'ddlSearches')))
    select_custom_region = Select(input_region)
    select_custom_region.select_by_value("1")
    #**************************************************SELECT CUSTOM REGIONS**************************************************
    select_all_regions_element = wait.until(EC.element_to_be_clickable((By.NAME, "lstCustomRegion")))
    select_all_regions = Select(select_all_regions_element)

    for option in select_all_regions.options:
        if option.get_attribute("value") in custom_region_list:
            select_all_regions.select_by_value(option.get_attribute("value"))

    #Click GO and generate table
    go_element = wait.until(EC.element_to_be_clickable((By.NAME, "btnGo")))
    go_element.click()
    wait.until(EC.presence_of_element_located((By.ID, "gvIncidents")))

    # Turn off auto updates
    find_auto_refresh_element = wait.until(EC.element_to_be_clickable((By.ID, "chkAutoRefresh")))
    find_auto_refresh_element.click()

    # Scrape the main table
    scraped_data = {}

    for i in range(len(driver.find_elements(By.XPATH, "//table[@id='gvIncidents']/tbody/tr")) - 1):
        rows = driver.find_elements(By.XPATH, "//table[@id='gvIncidents']/tbody/tr")[1:]  # Skip header row
        row = rows[i]
        cells = row.find_elements(By.TAG_NAME, "td")

        if len(cells) > 6 and cells[3].text in incident_type_criteria:
            incident_no = cells[1].text
            time = cells[2].text
            incident_type = cells[3].text
            location = cells[4].text
            location_desc = cells[5].text
            area = cells[6].text

            details_link = cells[0].find_element(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].click();", details_link)

            #scrape lat/long
            wait.until(EC.visibility_of_element_located((By.ID, "pnlDetailsHeader")))
            detail_header = driver.find_element(By.ID, 'pnlDetailsHeader')
            wait.until(EC.visibility_of_element_located((By.ID, "lblLatLon")))
            lat_long = detail_header.find_element(By.ID, 'lblLatLon').text

            # Scrape details
            wait.until(EC.visibility_of_element_located((By.ID, "pnlDetailInfo")))

            detail_table = driver.find_element(By.ID, 'tblDetails')
            detail_tbody = detail_table.find_element(By.TAG_NAME, 'tbody')
            detail_rows = detail_tbody.find_elements(By.TAG_NAME, 'tr')
            detail_table_text = ""

            for detail_row in detail_rows:
                detail_cells = detail_row.find_elements(By.TAG_NAME, 'td')
                detail_row_text = [cell.text for cell in detail_cells]
                detail_table_text += ', '.join(detail_row_text) + '\n'

            combined_info = detail_table_text.strip()

            # Add the scraped data to scraped_data dictionary
            scraped_data[incident_no] = {
                'Incident No.': incident_no,
                'Type': incident_type,
                'Time': time,
                'Location': location,
                'Location Desc': location_desc, 'Lat/Long': lat_long,
                'Area': area,
                'Detail and Unit Information': combined_info,
                'Status': ''
            }

    driver.quit()
    return scraped_data