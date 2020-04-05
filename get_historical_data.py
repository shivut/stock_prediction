import urllib.request
import os
import requests
import csv
from get_mappings import setup_logger
import json


def get_mappings_path():

    file_path = input('Please enter the path of metrics or enter "No" to exit: \n')

    while file_path.upper() != 'NO':

        if os.path.exists(file_path):
            print("checking for the parameters file")

            for eachFile in param_files:
                fl = os.path.join(file_path, eachFile)
                if os.path.isfile(fl):
                    temp = 0
                    try:
                        with open(fl) as json_file:
                            json.load(json_file)
                    except json.decoder.JSONDecodeError:
                        print("Not a valid json file")
                    except:
                        print("Something went wrong horribly..!!")
                    else:
                        temp = 1
                    finally:
                        if not temp:
                            return 0

                else:
                    print("couldn't find all the mappings")
                    return 0
            else:
                return file_path

        else:
            file_path = input('Path not found... Enter the valid path or NO to exit: \n')
    else:
        print("exiting")

    return 0


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

                # TODO : Get the data for exception

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

                    json_path = 'https://www.moneycontrol.com/mc/widget/basicchart/get_chart_value?classic=true&' \
                                'sc_did=' + code.lower() + '&dur=max'
                    json_data = requests.get(json_path)

                    if json_data.status_code == 200:
                        result_dict = json_data.json()
                        result_keys = result_dict.keys()
                        write_file = open(os.path.join(path, key, each_com + '.csv'), 'w')
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

    param_files = ["company_code_mapping.json", "sectorwise_com.json", "sector_key_map.json"]

    param_path = get_mappings_path()

    if param_path:
        logger_obj = setup_logger(param_path)

        file_handler = []

        for each_file in param_files:
            file_handler.append(json.load(open(each_file)))

        is_success = get_stock_data(file_handler[1], file_handler[0], param_path, logger_obj)

        if is_success:
            logger_obj.debug("Completed the job successfully")

        for each_file in file_handler:
            each_file.close()

    else:
        print("Everything doesn't seems to be fine")
