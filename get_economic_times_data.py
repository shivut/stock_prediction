from utils_extraction import validate_and_get_mappings, setup_logger, get_economic_times_mappings, csv_writer, get_data_economic_times
import sys
import os
import json
metrics = {"capital structure": "capitalstructure",
           "profit and loss": "profitandlose",
           "cash flow": "cashflow",
           "balance sheet": "balancesheet",
           "yearly report": "yearly",
           "share holding pattern": "shareholding"
           }

if __name__ == '__main__':

    metric_num = True

    while metric_num != "NO":

        for i, j in enumerate(metrics):
            print(str(i + 1) + " - " + j)

        metric_num = input("Enter a number a download the metric or NO to exit : ")

        try:
            metric_num = int(metric_num)
        except ValueError:
            print("Please provide a valid number between 1 and 7")    # TODO : Fix not to print when entered NO
        else:
            if 1 <= metric_num <= 7:
                break
    else:
        print("Exiting")
        sys.exit(0)

    metric = list(metrics)[metric_num - 1]

    # Just to make sure that complete data resides in a single directory and for combined logs
    mapping_path, _ = validate_and_get_mappings()

    logger = setup_logger(mapping_path)
#    mappings = get_economic_times_mappings()
    fl = open("/home/shiva/predict_stock/code/economic_times.json")
    mappings = json.load(fl)
    fl.close()


    if not os.path.exists(os.path.join(mapping_path, "Economic_times", metric)):
        os.makedirs(os.path.join(mapping_path, "Economic_times", metric))

    for each_company, each_company_code in mappings.items():
        logger.debug("Getting the Economic Times data for " + each_company)
        data = get_data_economic_times(each_company_code, metrics[metric])

        if data:
            csv_writer(os.path.join(mapping_path, "Economic_times", metric, each_company.rstrip(" Ltd.") + ".csv"), data)
