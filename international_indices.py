#!/usr/bin/python3

import os
import requests
import csv

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
