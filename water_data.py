import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

div_id = "__gvMainBodyContent_dvSubmissions__div"
href_id_1 = "MainBodyContent_AppSummaryControl1_fvAppSummary_hlnkInitialForm"
href_id_2 = "MainBodyContent_AppSummaryControl1_fvAppSummary_hlnkAdditionalForm"
initial_form_date_id = "MainBodyContent_AppSummaryControl1_fvAppSummary_DateFormSubmittedInitialLabel"
additional_form_date_id = "MainBodyContent_AppSummaryControl1_fvAppSummary_DateFormSubmittedAdditionalLabel"
url = "https://apps.dca.ga.gov/DRI/Submissions.aspx"
dataframe_list = []
dataframe = {}

def main_rendered_html():
    driver = webdriver.Chrome()
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, div_id)))
    page = driver.page_source
    driver.close()
    driver.quit()
    return page

def application_details_rendered_html(details_url):
    driver = webdriver.Chrome()
    driver.get(details_url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, href_id_1)))
    page = driver.page_source
    driver.close()
    driver.quit()
    return page

def additional_form_rendered_html(details_url):
    driver = webdriver.Chrome()
    driver.get(details_url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, href_id_2)))
    page = driver.page_source
    driver.close()
    driver.quit()
    return page


def main_page():
    soup = BeautifulSoup(main_rendered_html(), "html.parser")
    div = soup.find("div", id= div_id)
    if (div != None):
        tbody = div.find("tbody")
        rows = tbody.find_all("tr")
        column = tbody.find_all("th")
        raw_urls = tbody.find_all("a", href = True)
    else:
        print("div not found")
        return
    
    urls = [a["href"] for a in raw_urls]
    final_urls = urls[10:]

    headers = []
    for header in column:
        headers.append(header.text.strip())

    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        row_data = [col.text.strip() for col in cols]
        data.append(row_data)
    
    df = pd.DataFrame(data, columns = headers)
    #print("urls: ", final_urls)
    crawler(final_urls)
    for i, df in enumerate(dataframe_list):
        df["Field"] = df["Field"].apply(lambda x: " ".join(str(x).strip().split()))
        #df["Field"] = df["Field"].str.replace(r"\s+", " ", regex=True).str.strip()
        #df["Value"] = df["Value"].str.replace(r"\s+", " ", regex=True).str.strip()
        df["Value"] = df["Value"].apply(lambda x: " ".join(str(x).strip().split()))

        if i != 0 and i % 2 == 1:
            df = df.drop(0)
            empty_row = pd.DataFrame([["", ""]], columns=df.columns)
            df = pd.concat([df, empty_row], ignore_index = True)
        df["Value"] = df["Value"].astype(str)
        df = df.reset_index(drop=True)
        mode = 'w' if i == 0 else 'a'
        #df.to_csv("dri_data.csv", mode='a', header=(i==0), index=False)
        df.to_csv("dri_data.csv", mode= mode, header=(i==0), index=False)
    #print(df)
    
def crawler(urls):
    for details_url in urls[:3]:
        website_header = "https://apps.dca.ga.gov/DRI/"
        application_detail = website_header + details_url
        #print("details url", details_url)
        #print("new url: ", application_detail)
        soup = BeautifulSoup(application_details_rendered_html(application_detail), "html.parser")
        href1 = soup.find("a", id = href_id_1)
        initial_forms_url = href1["href"]
        initial_forms_url = website_header + initial_forms_url
        #print("Initial forms url: ", initial_forms_url)
        initial_form_date = soup.find("span", id = initial_form_date_id).text
        #initial_form_date = initial_form_date_exist
        if initial_form_date:
            raw_data = fetch_initial_forms_data(initial_forms_url)
            project_details = make_neat(raw_data)
            #print(project_details)
            dataframe_list.append(project_details)
        else:
            print("Initial form has not been filled out yet")
        
        href2 = soup.find("a", id = href_id_2)
        additional_form_url = href2["href"]
        additional_form_url = website_header + additional_form_url
        #print(additional_form_url)
        additional_form_date = soup.find("span", id = additional_form_date_id).text
        if additional_form_date:
            raw_additional_details = fetch_additional_form_data(additional_form_url)
            additional_details = make_neat(raw_additional_details)
            #print(additional_details)
            dataframe_list.append(additional_details)
        else:
            print("Additional form has not been filled out yet")
            data = {"Field" : ["Additional form has not been filled out yet"], "Value" : ["Additional form has not been filled out yet"]}
            temp_df = pd.DataFrame(data)
            dataframe_list.append(temp_df)
            #temp_row = pd.DataFrame([["Additional form has not been filled out yet", "Additional form has not been filled out yet"]], columns=df.columns)


def fetch_initial_forms_data(initial_forms_url):
    response = requests.get(initial_forms_url)
    if response.status_code == 200:
        soup2 = BeautifulSoup(response.text, "html.parser")
        rows = soup2.find_all("tr")
        subset = rows[18:22]
        project_details = []
        for row in subset:
            td = row.find_all("td")
            raw_data = [element.get_text(strip = True) for element in td]
            project_details.append(raw_data)
        return project_details
    else:
        print("bad link")

def fetch_additional_form_data(additional_form_url):
    response = requests.get(additional_form_url)
    if response.status_code == 200:
        soup3 = BeautifulSoup(response.text, "html.parser")
        rows = soup3.find_all("tr")
        subset = rows[17:23] + rows[29:50]
        project_details = []
        for row in subset:
            td = row.find_all("td")
            radio_buttons = row.find_all('input', {'type': 'radio'})
            
            input_tag = row.find("input")
            raw_data = [element.text.strip() for element in td]
            if radio_buttons:
                radio_values = [rb.get('value') for rb in radio_buttons]
                #raw_data.append(radio_values)
                #radio_button_value
                radio_button_value = ""
                if radio_values[0] == 'True':
                    radio_button_value = "Not Selected"
                elif radio_values[1] == 'True':
                    radio_button_value = "Yes"
                elif radio_values[2] == 'True':
                    radio_button_value = "No"
                raw_data = [td[0].text.strip(), radio_button_value]

            elif (input_tag != None):
                input_value = input_tag.get("value")
                #project_details.append(input_value)
                #print("Input value: ", input_value)
                raw_data = [td[0].text.strip(), input_value]
                #raw_data.append(input_value)
                #del raw_data[1]
                #print("Raw Data: ", raw_data)
            
            project_details.append(raw_data)
            #print(project_details)
        return project_details
    else:
        print("bad link")

def make_neat(details):
    project_info = {}
    for row in details:
        if len(row) == 2:
            label = ' '.join(row[0].split())
            #label = row[0].strip()
            value = row[1].strip()
            project_info[label] = value
    return pd.DataFrame(list(project_info.items()), columns=["Field", "Value"])

    



main_page()



