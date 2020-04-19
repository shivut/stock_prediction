import urllib.request
from bs4 import BeautifulSoup
import os
import simplejson
from utils_extraction import setup_logger


def get_path():
    file_path = input('Please enter the base directory path or enter "No" to exit: \n')

    while file_path.upper() != 'NO':

        if os.path.exists(file_path):
            break
        else:
            file_path = input('Path not found... Enter the valid path or NO to exit: \n')
    else:
        print("exiting")
        return False

    return os.path.join(file_path)


def get_mappings(path, logger):

    logger.debug("**********  Started to get the mappings  *************")

    company_code_mapping = {}
    sectorwise_com = {}
    sector_key_map = {}

    soup_obj = BeautifulSoup(urllib.request.urlopen(r'http://www.moneycontrol.com/stocks/data-bank/standalone/'
                                                    r'banks-private-sector.html'), 'html.parser')
    all_sectors_parser = soup_obj.find("select", {"id": "chg_sector"})
    sectors = all_sectors_parser.find_all("option")

    for eachSector in sectors:
        sector_key_map[eachSector.text] = eachSector.get("value")

    for eachSector, eachSectorKey in sector_key_map.items():

        if eachSectorKey:

            logger.debug("Getting the mappings for " + eachSectorKey)
            url = "http://www.moneycontrol.com/stocks/data-bank/standalone/" + eachSectorKey + ".html"
            soup_each_sector = BeautifulSoup(urllib.request.urlopen(url), 'html.parser')
            company_code_parser = soup_each_sector.findAll("a", attrs={'class': 'bl_14'})
            sectorwise_com[eachSector] = []

            for eachElement in company_code_parser:
                company_code_mapping[eachElement.text] = eachElement.get('href').split("/")[-1]
                sectorwise_com[eachSector].append(eachElement.text)

    logger.debug("Writing the meta to json file")

    with open(os.path.join(path, "sector_key_map.json"), 'w') as fl:
        fl.write(simplejson.dumps(sector_key_map, sort_keys=True, indent=4 * ' '))

    with open(os.path.join(path, "company_code_mapping.json"), 'w') as fl:
        fl.write(simplejson.dumps(company_code_mapping, sort_keys=True, indent=4 * ' '))

    with open(os.path.join(path, "sectorwise_com.json"), 'w') as fl:
        fl.write(simplejson.dumps(sectorwise_com, sort_keys=True, indent=4 * ' '))

    return True


if __name__ == '__main__':

    obj_path = get_path()
    if obj_path:
        logger_obj = setup_logger(obj_path)

        is_success = get_mappings(obj_path, logger_obj)

        if is_success:
            logger_obj.debug("*********************** Completed ******************************")
