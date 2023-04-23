#!/usr/bin/env python3
import json
import pandas as pd
from collections import ChainMap
from itertools import chain


def get_uniq_key(data):
    key_list = set()
    for record in data:
        for key in record.keys():
            key_list.add(key)
    return (key_list)

# with open('json_data.json', 'r') as f:
#     json_data = json.load(f)
#     print(json_data)
#     dict_keys = get_uniq_key(json_data)
#     result = {}
#     for item in dict_keys:
#         for record in json_data:
#             for key in record.keys():
#                 if item == key:
#                     print(f'item: {item}, record: {key}')
#                     result[item].add(result[item] | record[key])
    # print(json_data['CI00150426'])

# dict_1 = {'CI00150423': {'host_name': 'kkd-rmq02p', 'ip': '10.207.19.124', 'cpu': '2', 'ram': '2','hdd': [{'0:0': '50'}]}}
# dict_2 = {'CI00150423': {'host_name': 'kkd-rmq02p', 'ip': '10.207.19.7', 'cpu': '2', 'ram': '2', 'hdd': [{'0:0': '50'}]}}

dict_1 = {"CI00168848": {"host_name": "kkd-dmz-rmq02p","ip": "10.207.33.187","cpu": "2","ram": "2","hdd": [{"0:0": "50"}]}}
dict_2 = {"CI00168848": {"host_name": "kkd-dmz-rmq02p","ip": "10.207.33.187","cpu": "2","ram": "2","hdd": [{"0:1": "75"}]}}
# m_dict = dict_1['CI00168848'.'hdd'].update(dict_2['CI00168848'.'hdd'])
# print(m_dict)

# d3=dict(ChainMap(dict_1,dict_2))
# print(d3)
#
# d4=dict(chain(dict_1.items(),dict_2.items()))
# print(d4)

tmp_1=dict_1['CI00168848']['hdd']
tmp_2=dict_2['CI00168848']['hdd']
result_dict=dict_1 | dict_2
result_dict['CI00168848']['hdd']=tmp_1+tmp_2
print(result_dict)
#
# df = pd.DataFrame(data=[dict_1, dict_2])
# print(df)

