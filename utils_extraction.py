import csv
import os
import logging
import requests
from bs4 import BeautifulSoup
import json
from urllib.request import Request, urlopen


def csv_writer(file_name, data):
    fl = open(file_name, 'w')
    csvwriter = csv.writer(fl)
    csvwriter.writerows(data)
    fl.close()

    return True


def get_financial_data(company_name, company_code, metric_name, section_num):

    if metric_name == "yearly":
        url = 'https://www.moneycontrol.com/financials/' + company_name + '/results/' + metric_name + '/' \
              + company_code + '/' + str(section_num)
    else:
        url = 'https://www.moneycontrol.com/financials/' + company_name + '/' + metric_name + 'VI/' \
              + company_code + '/' + str(section_num)

    soup_obj = BeautifulSoup((requests.get(url)).content, 'html.parser')
    table_data = soup_obj.find_all(class_="mctable1")
    final_data = []

    if table_data:

        for each_row in table_data[0].select('tr'):
            each_row_data = []
            for each_element in each_row.find_all('td'):
                each_row_data.append(each_element.text.strip())
            final_data.append(each_row_data)

    return final_data


def validate_and_get_mappings():

    file_path = input('Please enter the path of metrics or enter "No" to exit: \n')
    param_files = ["company_code_mapping.json", "sectorwise_com.json", "sector_key_map.json"]

    while file_path.upper() != 'NO':

        if os.path.exists(file_path):
            print("checking for the parameters file")

            for eachFile in param_files:
                fl = os.path.join(file_path, eachFile)
                if os.path.isfile(fl):
                    is_valid = True
                    try:
                        with open(fl) as json_file:
                            json.load(json_file)
                    except json.decoder.JSONDecodeError:
                        print("Not a valid JSON file")
                        is_valid = False
                    except:
                        is_valid = False
                        print("Something went wrong horribly..!!")
                    finally:
                        if not is_valid:
                            return False, False
                else:
                    print("couldn't find all the mappings")
                    return False, False
            else:
                json_data_map = {}

                for each_file in param_files:
                    with open(each_file) as fl:
                        json_data_map[each_file.rstrip(".json")] = json.load(fl)

                return file_path, json_data_map

        else:
            file_path = input('Path not found... Enter the valid path or NO to exit: \n')
    else:
        print("exiting")

    return False, False


def setup_logger(data_path, name='getMappings', level=logging.DEBUG):
    log_path = os.path.join(data_path, 'logs')

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_path = os.path.join(log_path, 'getMappings.log')
    logger = logging.getLogger(name)
    logger.setLevel(level)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s : %(message)s"))
    terminal_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s : %(message)s"))
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(terminal_handler)
    logger.addHandler(file_handler)

    return logger


def get_economic_times_mappings():

    range_limit = [(1, 10), (65, 91)]
    mappings = {}
    base_url = "http://economictimes.indiatimes.com/markets/stocks/stock-quotes?ticker="

    for each_lower_bound, each_upper_bound in range_limit:

        for eachAsciiValue in range(each_lower_bound, each_upper_bound):
            print(eachAsciiValue)
            if eachAsciiValue > 9:
                url = base_url + chr(eachAsciiValue)
            else:
                url = base_url + str(eachAsciiValue)

            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup_obj = BeautifulSoup(urlopen(req).read(), 'html.parser')

            a = soup_obj.find_all(class_="companyList")

            if len(a) == 3:
                b = a[0].find_all('li')

                for i in b:
                    mappings[i.text] = i.a.get("href")

    return mappings


def get_data_economic_times(company, metric):
    base_url_web = "https://economictimes.indiatimes.com"
    req = Request(base_url_web + company.replace("stocks", metric), headers={'User-Agent': 'Mozilla/5.0'})
    soup_obj = BeautifulSoup(urlopen(req).read(), 'html.parser')
    table_data = soup_obj.find_all("table", {"class": "tblData1"})
    final_data = []

    if table_data:
        for eachElement in table_data[0].find_all('tr'):
            if len(eachElement) > 1:
                csv_element = []
                for eachElementData in eachElement.find_all('td'):
                    csv_element.append(eachElementData.text.strip())
                final_data.append(csv_element)

    return final_data
