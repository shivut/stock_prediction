import os
import requests
import csv
import urllib.request
from utils_extraction import validate_and_get_mappings, setup_logger


indices = {"International" : {'US': ('us', 'COMP'),
                      'UK': ('gb', 'FTSE'),
                      'France': ('fr', 'CAC'),
                      'Germany': ('de', 'qx'),
                      'Japan': ('JP', 'N225'),
                      'Singapore': ('sg', 'STII'),
                      'China_Hongcong': ('cn', 'hsi'),
                      'Taiwan': ('tw', 'IXTA'),
                      'South_korea': ('kr', 'KSPI'),
                      'China_shanghai': ('cn', 'shi')},
          "Indian" : {"nifty" : "Nifty50",
                      "bank_nifty": "Bank_Nifty",
                      "sensex": "Sensex",
                      "cnx_it": "IT_Nifty"}}


def get_international_index(index_map, download_path):

    for eachCountry, (country_code, index_code) in index_map.items():

        address_url = "https://appfeeds.moneycontrol.com/jsonapi/market/graph&format=json&ind_id=" + country_code + ";" + index_code + "&range=max"
        response = requests.get(address_url)

        if response.status_code == 200:

            result = response.json()
            logger.debug("Generating the report for " + eachCountry)
            data = result.get('graph', '{}').get('values', [])

            with open(os.path.join(download_path, "index", eachCountry + '.csv'), 'w') as write_file:
                writer = csv.writer(write_file)

                for eachValue in data:
                    writer.writerow([eachValue['_time'], eachValue['_value'], eachValue['_open'], eachValue['_high'], eachValue['_close'], eachValue['_volume'], eachValue['_chg'], eachValue['_pchg']])
        else:
            print("Could not get the response for " + eachCountry + "and the reponse code " + str(response.status_code))

    return True


def get_indian_index(index_map, download_path):

    for eachIndex, eachValue in index_map.items():

        address_url = "https://www.moneycontrol.com/tech_charts/nse/his/" + eachIndex + ".csv"
        data_file = urllib.request.urlopen(address_url)
        logger.debug("Generating the report for " + eachIndex)
        line = data_file.readline()

        while line:
            with open(os.path.join(download_path, "index", eachValue + '.csv'), 'ab') as file:
                file.write(line)
                line = data_file.readline()

    return True


if __name__ == "__main__":
    path, _ = validate_and_get_mappings()

    if path:
        logger = setup_logger(path)
        if not os.path.exists(os.path.join(path, "index")):
            os.makedirs(os.path.join(path, "index"))

        for each_type in indices.keys():

            if each_type == "International":
                logger.debug("****************** Getting the international indices *********************")
                _ = get_international_index(indices["International"], path)
            elif each_type == "Indian":
                logger.debug("****************** Getting the Indian indices ****************************")
                _ = get_indian_index(indices["Indian"], path)

        logger.debug(".............. Job completed ..................!!!!!")
