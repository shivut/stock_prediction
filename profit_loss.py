#!/usr/bin/python3

import urllib.request
from bs4 import BeautifulSoup
import logging
import os
import sys
import requests
import csv
import json

def get_path():
    # file_path = input('Please enter the path where you want to download data or enter "No" to exit: \n')
    file_path = "/home/shiva/predict_stock/test/profit_loss"

    while file_path.upper() != 'NO':

        if os.path.exists(file_path):
            if not os.path.exists(os.path.join(file_path, 'data')):
                os.makedirs(os.path.join(file_path, 'data'))
            break
        else:
            file_path = input('Path not found... Enter the valid path or NO to exit: \n')

            if file_path.upper() == 'NO':
                sys.exit(0)

    return os.path.join(file_path, 'profit_loss')


def get_stock_data(sectorwise_com, company_code_mapping, path, logger):

    for key, value in sectorwise_com.items():
        logger.debug(" **************** Downloading the data for the sector **************** " + str(key))

        if value:

            if not os.path.exists(os.path.join(path, key)):
                os.makedirs(os.path.join(path, key))

            for each_com in value:

                print(each_com)
                for eachDision in range(1,6):

                    a = BeautifulSoup((requests.get(
                        r'https://www.moneycontrol.com/financials/' + each_com.replace(" ", "") + '/profit-lossVI/' + company_code_mapping.get(each_com) + "/" + str(eachDision))).content,
                                      'html.parser')
                    try:
                        b = a.find_all(class_="mctable1")[0]
                    except:
                        break

                    e = b.find_all('table',
                                   attrs={'cellpadding': "0", 'cellspacing': "0", 'class': "table4", 'width': "744"})

                    with open(os.path.join(path, key, each_com + "_" + str(eachDision)+ '.txt'), 'w') as fl:
                        for i in b.select('tr'):
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
    logger.debug("\n")
    sectorwise_com = {'Aluminium': ['Hindalco', 'Maan Aluminium', 'Manaksia Alumin', 'NALCO' ]}
    company_code_mapping = {'Century Extr': 'CE02', 'Hindalco': 'HI', 'Maan Aluminium': 'MA03',
                            'Manaksia Alumin': 'MAC03', 'NALCO': 'NAC'}
    # sectorwise_com = json.loads(open("/home/shiva/predict_stock/sector_com_mapping.json").read().strip("\n"))
    # company_code_mapping= json.loads(open("/home/shiva/predict_stock/company_code_mapping.json").read().strip("\n"))

    logger.debug("Got the sector mapping and company code mapping")
    is_success = get_stock_data(sectorwise_com, company_code_mapping, path, logger)

    if (is_success):
        logger.debug("Completed the Job")

