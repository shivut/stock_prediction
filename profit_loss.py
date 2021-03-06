from bs4 import BeautifulSoup
import os
import requests
import json
from get_historical_data import get_mappings_path
from get_mappings import setup_logger
import csv


def csv_writer(file_name, data):
    fl = open(file_name, 'w')
    csvwriter = csv.writer(fl)
    csvwriter.writerows(data)
    fl.close()


def get_balance_sheet(sectorwise_com, company_code_mapping, path, logger):

    for each_sector, each_sector_companies in sectorwise_com.items():
        logger.debug(" **************** Downloading the data for the sector **************** " + str(each_sector))

        if each_sector_companies:
            if not os.path.exists(os.path.join(path, "profit-loss", each_sector)):
                os.makedirs(os.path.join(path, "profit-loss", each_sector))

            for each_com in each_sector_companies:
                logger.debug("getting the profit-loss statement for " + each_com)

                for each_division in range(1, 6):

                    url = 'https://www.moneycontrol.com/financials/' + each_com.replace(" ", "") + '/profit-lossVI/'\
                          + company_code_mapping.get(each_com) + "/" + str(each_division)
                    soup_obj = BeautifulSoup((requests.get(url)).content, 'html.parser')

                    table_obj = soup_obj.find_all(class_="mctable1")

                    if table_obj:
                        final_data = []

                        for i in table_obj[0].select('tr'):
                            table_data = []
                            for k in i.find_all('td'):
                                table_data.append(k.text.strip())
                            final_data.append(table_data)
                        csv_writer(os.path.join(path, "profit-loss", each_sector ,each_com + "_" + str(each_division) + ".csv"), final_data)
                    else:
                        break

    return True


if __name__ == '__main__':

    mapping_path = get_mappings_path()

    if mapping_path:
        logger_obj = setup_logger(mapping_path)
        logger_obj.debug("Got the sector mapping and company code mapping")

        param_files = ["company_code_mapping.json", "sectorwise_com.json", "sector_key_map.json"]
        file_handler = []

        for each_file in param_files:
            file_handler.append(json.load(open(each_file)))

        is_success = get_balance_sheet(file_handler[1], file_handler[0], mapping_path, logger_obj)

        if is_success:
            logger_obj.debug("Completed the job successfully")

        for each_file in file_handler:
            each_file.close()
