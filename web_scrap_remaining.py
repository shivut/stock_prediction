#!/usr/bin/python3

import urllib.request
from bs4 import BeautifulSoup
import logging
import os
import sys
import requests
import csv


def get_path():
    file_path = input('Please enter the path where you want to download data or enter "No" to exit: \n')

    while file_path.upper() != 'NO':

        if os.path.exists(file_path):
            if not os.path.exists(os.path.join(file_path, 'data')):
                os.makedirs(os.path.join(file_path, 'data'))
            break
        else:
            file_path = input('Path not found... Enter the valid path or NO to exit: \n')

            if file_path.upper() == 'NO':
                sys.exit(0)

    return os.path.join(file_path, 'data')


def get_sector_data(logger):

    sectors = dict()
    company_code_mapping = dict()
    sectorwise_com = dict()

    soup = BeautifulSoup(urllib.request.urlopen(r'http://www.moneycontrol.com/stocks/sectors'), 'html5lib')

    parser = soup.find_all('ul', class_='sec_comp_nm')[2].find_all('li')

    for i in parser:
        sectors[i.text] = str(i).lstrip('<li><a href=').rstrip('</a></li>').split('>')[0].replace('"', '')

    logger.debug(sectors)

    for key, value in sectors.items():
        logger.debug('Generating the data for ' + key + ' sector')
        soup = BeautifulSoup(urllib.request.urlopen(sectors[key]), 'html5lib')
        parser = BeautifulSoup(str(soup.find_all(class_='pricePertable')), 'html5lib')
        company_codes = parser.find_all('td', class_='left')
        companies = []

        for i in company_codes:
            company_code_mapping[i.text] = str(i).lstrip('<td class="left"><a href=').split('>')[0].split('/')[
                -1].replace('"', '')
            companies.append(i.text)
        else:
            sectorwise_com[key] = companies

    logger.debug("company_code_mapping " + str(company_code_mapping))
    logger.debug("sectorwise_com " + str(sectorwise_com))

    return sectorwise_com, company_code_mapping


def convert_misc_data_format(data):
    final_dict = {}
    for eachVal in data:
        final_dict[eachVal.get('date')] = eachVal.get('ratio')

    return final_dict


def get_stock_data(sectorwise_com, company_code_mapping, path, logger):

    for key, value in sectorwise_com.items():
        logger.debug(" **************** Downloading the data for the sector **************** " + str(key))

        if value:

            if not os.path.exists(os.path.join(path, key)):
                os.makedirs(os.path.join(path, key))

            for each_com in value:

                code = company_code_mapping.get(each_com)

                if code == 'ITD03':
                    continue
                logger.debug('Generating the data for {}'.format(each_com))
                ip_ad = 'https://www.moneycontrol.com/tech_charts/nse/his/' + code.lower() + '.csv'

                try:
                    data_file = urllib.request.urlopen(ip_ad)

                    line = data_file.readline()

                    while line:
                        with open(os.path.join(path, key, each_com + '.csv'), 'ab') as file:
                            file.write(line)
                            line = data_file.readline()

                except urllib.error.HTTPError:
                    print("In the JSON Section")
                    json_path = 'https://www.moneycontrol.com/mc/widget/basicchart/get_chart_value?classic=true&sc_did=' + code.lower() + '&dur=max'
                    json_data = requests.get(json_path)
                    # print(json_data.json())

                    if json_data.status_code == 200:

                        result_dict = json_data.json()
                        result_keys = result_dict.keys()

                        write_file = open(os.path.join(path, key, each_com + '.csv'), 'w')
                        writer = csv.writer(write_file)

                        if "g1" in result_keys and result_dict['g1']:
                            data_map = result_dict['g1']
                            data_map_misc = result_dict['data'] if result_dict['data'] else  {}

                            data_map_dividends = convert_misc_data_format(data_map_misc.get('dividends', [{}]))
                            data_map_splits = convert_misc_data_format(data_map_misc.get('splits', [{}]))
                            data_map_bonus = convert_misc_data_format(data_map_misc.get('bonus', [{}]))
                            data_map_rights = convert_misc_data_format(data_map_misc.get('rights', [{}]))

                            for eachValue in data_map:
                                date = eachValue['date']
                                open_value = eachValue['open']
                                close = eachValue['close']
                                high = eachValue['high']
                                low = eachValue['low']
                                volume = eachValue['volume']
                                date_format = date.replace("-", ", ")
                                bonus = data_map_bonus.get(date_format)
                                dividend = data_map_dividends.get(date_format)
                                rights = data_map_rights.get(date_format)
                                split = data_map_splits.get(date_format)

                                writer.writerow([date, open_value, high, low, close, volume, bonus, dividend, rights, split])

                        write_file.close()
                        continue
                except:
                    logger.debug("!!!!!!!!!!!!!!!!!! Could not get the data for " + each_com)
                    continue

    return True


def setup_logger(path, name='downloadData', level=logging.DEBUG):
    log_path = os.path.join(path, 'logs')

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    logger_path = os.path.join(log_path, 'download_data.log')
    logger = logging.getLogger(name)
    logger.setLevel(level)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s : %(message)s"))
    terminal_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(logger_path, mode='w')
    file_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s %(filename)s:%(lineno)s : %(message)s"))
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(terminal_handler)
    logger.addHandler(file_handler)
    return logger


if __name__ == '__main__':

    path = get_path()
    logger = setup_logger(path)
    sectorwise_com, company_code_mapping = get_sector_data(logger)
    logger.debug("\n")
    # sectorwise_com = {'Aluminium': ['test', 'Hindalco', 'Maan Aluminium', 'Manaksia Alumin', 'NALCO' ]}
    # company_code_mapping = {'Century Extr': 'CE02', 'Hindalco': 'HI', 'Maan Aluminium': 'MA03',
                            # 'Manaksia Alumin': 'MAC03', 'NALCO': 'NAC', 'test' : 'JNI02'}

    logger.debug("Got the sector mapping and company code mapping")
    is_success = get_stock_data(sectorwise_com, company_code_mapping, path, logger)

    if (is_success):
        logger.debug("Completed the Job")
