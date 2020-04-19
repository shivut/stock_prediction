import os
from utils_extraction import csv_writer, get_financial_data, setup_logger, validate_and_get_mappings


def get_ratios_sheet(sectorwise_com, company_code_mapping, path, logger):

    for each_sector, each_sector_companies in sectorwise_com.items():
        logger.debug(" **************** Downloading the data for the sector **************** " + str(each_sector))

        if each_sector_companies:
            if not os.path.exists(os.path.join(path, "ratios", each_sector)):
                os.makedirs(os.path.join(path, "ratios", each_sector))

            for each_com in each_sector_companies:
                logger.debug("getting the ratios data for " + each_com)

                for each_division in range(1, 6):

                    each_division_table_data = get_financial_data(each_com.replace(" ", ""), company_code_mapping.get(each_com), "ratios", each_division)

                    if each_division_table_data:
                        csv_writer(os.path.join(path, "ratios", each_sector, each_com + "_" + str(each_division) + ".csv"), each_division_table_data)
                    else:
                        break

    return True


if __name__ == '__main__':

    mapping_path, mapping_obj = validate_and_get_mappings()

    if mapping_path:
        logger_obj = setup_logger(mapping_path)
        logger_obj.debug("Got the sector mapping and company code mapping")

        is_success = get_ratios_sheet(mapping_obj["sectorwise_com"], mapping_obj["company_code_mapping"], mapping_path, logger_obj)

        if is_success:
            logger_obj.debug("Completed the job successfully")
