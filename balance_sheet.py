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

    return os.path.join(file_path, 'balance_sheet')


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

                logger.debug("Acting on the file " + each_com)

                a = BeautifulSoup((requests.get(r'https://www.moneycontrol.com/financials/' +
                                                each_com.replace(' ', '') + '/balance-sheetVI/' + company_code_mapping[each_com])).content,
                                  'html5lib')
                b = (a.find_all('table', class_="mctable1"))[0]
                e = b.find_all('table',
                               attrs={'cellpadding': "0", 'cellspacing': "0", 'class': "table4", 'width': "744"})

                with open(os.path.join(path,  key, each_com + '.csv'), 'w') as fl:
                    for i in e[1].select('tr'):
                        for j in i.find_all('td', attrs={'colspan': "2"}):
                            break
                        else:
                            for k in i.find_all('td'):
                                print(k.text, end='|', file=fl)
                        print('\n', file=fl)

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
    # sectorwise_com, company_code_mapping = get_sector_data(logger)
    logger.debug("\n")
    sectorwise_com = {'Aluminium': ['Hindalco', 'Maan Aluminium', 'Manaksia Alumin', 'NALCO' ]}
    company_code_mapping = {'Century Extr': 'CE02', 'Hindalco': 'HI', 'Maan Aluminium': 'MA03',
                            'Manaksia Alumin': 'MAC03', 'NALCO': 'NAC'}

    logger.debug("Got the sector mapping and company code mapping")
    is_success = get_stock_data(sectorwise_com, company_code_mapping, path, logger)

    if (is_success):
        logger.debug("Completed the Job")
