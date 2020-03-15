#!/usr/bin/python3

import os
import requests
import csv
import urllib.request


index_code_mapping = {'US' : ('us', 'COMP'),
                      'UK' : ('gb', 'FTSE'),
                      'France' : ('fr', 'CAC'),
                      'Germany' : ('de', 'qx'),
                      'Japan': ('JP', 'N225'),
                      'Singapore': ('sg', 'STII'),
                      'China_Hongcong':('cn', 'hsi'),
                      'Taiwan':('tw', 'IXTA'),
                      'South_korea' : ('kr', 'KSPI'),
                      'China_shanghai':('cn', 'shi')}

Indian_indices = {"nifty" : "Nifty50", "bank_nifty": "Bank_Nifty", "sensex": "Sensex", "cnx_it": "IT_Nifty"}

for eachCountry, (country_code, index_code) in index_code_mapping.items():

    address_url = "https://appfeeds.moneycontrol.com/jsonapi/market/graph&format=json&ind_id=" + country_code + ";" + index_code + "&range=max"
    response = requests.get(address_url)

    if response.status_code == 200:
        result = response.json()

        print("Generating the report for " + eachCountry)

        data = result.get('graph', '{}').get('values', [])

        with open(os.path.join(os.getcwd(), eachCountry + '.csv'), 'w') as write_file:
            writer = csv.writer(write_file)

            for eachValue in data:
                writer.writerow([eachValue['_time'], eachValue['_value'], eachValue['_open'], eachValue['_high'], eachValue['_close'], eachValue['_volume'], eachValue['_chg'], eachValue['_pchg']])
    else:
        print("Could not get the response for " + eachCountry + "and the reponse code " + str(response.status_code))

for eachIndex, eachValue in Indian_indices.items():
    address_url = "https://www.moneycontrol.com/tech_charts/nse/his/" + eachIndex + ".csv"

    data_file = urllib.request.urlopen(address_url)

    print("Generating the report for " + eachIndex)

    line = data_file.readline()

    while line:
        with open(os.path.join(os.getcwd(), eachValue + '.csv'), 'ab') as file:
            file.write(line)
            line = data_file.readline()
