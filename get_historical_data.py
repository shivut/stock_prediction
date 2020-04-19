import urllib.request
from utils_extraction import validate_and_get_mappings, setup_logger
import os
import requests
import csv


def convert_misc_data_format(data):
    final_dict = {}

    for eachVal in data:
        final_dict[eachVal.get('date')] = eachVal.get('ratio')

    return final_dict


def get_stock_data(sectorwise_com, company_code_mapping, path, logger):

    for key, value in sectorwise_com.items():
        logger.debug(" **************** Downloading the data for the sector **************** " + str(key))

        if value:

            if not os.path.exists(os.path.join(path, 'historical_data', key)):
                os.makedirs(os.path.join(path, 'historical_data', key))

            for each_com in value:
                code = company_code_mapping.get(each_com)

                # TODO : Get the data for exception

                if code == 'ITD03':
                    continue
                logger.debug('Generating the data for {}'.format(each_com))
                ip_ad = 'https://www.moneycontrol.com/tech_charts/nse/his/' + code.lower() + '.csv'

                try:
                    data_file = urllib.request.urlopen(ip_ad)
                    line = data_file.readline()

                    with open(os.path.join(path, 'historical_data', key, each_com + '.csv'), 'wb') as file:

                        while line:
                            file.write(line)
                            line = data_file.readline()

                except urllib.error.HTTPError:

                    json_path = 'https://www.moneycontrol.com/mc/widget/basicchart/get_chart_value?classic=true&' \
                                'sc_did=' + code.lower() + '&dur=max'
                    json_data = requests.get(json_path)

                    if json_data.status_code == 200:
                        result_dict = json_data.json()
                        result_keys = result_dict.keys()
                        write_file = open(os.path.join(path, 'historical_data', key, each_com + '.csv'), 'w')
                        writer = csv.writer(write_file)

                        if "g1" in result_keys and result_dict['g1']:
                            data_map = result_dict['g1']
                            data_map_misc = result_dict['data'] if result_dict['data'] else {}
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
                                writer.writerow([date, open_value, high, low, close, volume, bonus, dividend,
                                                 rights, split])

                        write_file.close()
                        continue
                    else:
                        logger.debug()
                except:
                    logger.debug("!!!!!!!!!!!!!!!!!! Could not get the data for " + each_com)

    return True


if __name__ == '__main__':

    mapping_path, mapping_obj = validate_and_get_mappings()

    if mapping_path:
        logger_obj = setup_logger(os.path.join(mapping_path, 'historical_data'))

        is_success = get_stock_data(mapping_obj["sectorwise_com"], mapping_obj["company_code_mapping"], mapping_path, logger_obj)

        if is_success:
            logger_obj.debug("Completed the job successfully")

    else:
        print("Everything doesn't seems to be fine")
