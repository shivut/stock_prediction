import urllib.request
from bs4 import BeautifulSoup
import logging
import os
import sys
import simplejson


def get_path():
    file_path = input('Please enter the path where you want to download data or enter "No" to exit: \n')

    while file_path.upper() != 'NO':

        if os.path.exists(file_path):
            if not os.path.exists(os.path.join(file_path, 'data')):
                os.makedirs(os.path.join(file_path, 'data'))
            break
        else:
            file_path = input('Path not found... Enter the valid path or NO to exit: \n')
    else:
        print("Exiting")
        sys.exit(0)

    return file_path


def get_mappings(data_path, logger):

    company_code_mapping = dict()
    sectorwise_com = dict()
    sector_key_map = {}
    soup_obj = BeautifulSoup(urllib.request.urlopen(r'http://www.moneycontrol.com/stocks/data-bank/standalone'
                                                r'/banks-private-sector.html'), 'html.parser')

    all_sectors_parser = soup_obj.find("select", {"id": "chg_sector"})
    all_sectors = all_sectors_parser.find_all("option")

    for eachSector in all_sectors:
        sector_key_map[eachSector.text] = eachSector.get("value")

    logger.debug("*********** Start of the main Logic ********************")

    for eachSector, eachSectorKey in sector_key_map.items():

        if eachSectorKey:

            logger.debug("Getting the data for " + eachSectorKey)
            url = "http://www.moneycontrol.com/stocks/data-bank/standalone/" + eachSectorKey + ".html"
            each_sector_soup_obj = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')
            each_sector_parser = each_sector_soup_obj.findAll("a", attrs={'class': 'bl_14'})
            sectorwise_com[eachSector] = []

            for eachElement in each_sector_parser:
                company_code_mapping[eachElement.text] = eachElement.get('href').split("/")[-1]
                sectorwise_com[eachSector].append(eachElement.text)

    with open(os.path.join(data_path, "sector_key_map.json"), 'w') as fl:
        fl.write(simplejson.dumps(sector_key_map, sort_keys=True, indent=4 * ' '))

    with open(os.path.join(data_path, "company_code_mapping.json"), 'w') as fl:
        fl.write(simplejson.dumps(company_code_mapping, sort_keys=True, indent=4 * ' '))

    with open(os.path.join(data_path, "sectorwise_com.json"), 'w') as fl:
        fl.write(simplejson.dumps(sectorwise_com, sort_keys=True, indent=4 * ' '))

    return True


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

    file_handler = logging.FileHandler(log_path, mode='w')
    file_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s : %(message)s"))
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(terminal_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':

    path = get_path()
    logger_obj = setup_logger(path)

    is_success = get_mappings(path, logger_obj)

    if is_success:
        logger_obj.debug("*******************  Successfully got the mappings *************************")

    for eachLogger in list(logger_obj.handlers):

        logger_obj.removeHandler(eachLogger)
        eachLogger.flush()
        eachLogger.close()

    print("Completed the job")
