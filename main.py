#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import ipaddress
import json
from contextlib import closing

import psycopg2
import yaml
from psycopg2 import sql
from psycopg2.extras import DictCursor
import re
import pandas as pd




def clean_ip_str(str):
    return re.sub(r"\t","", str)

def get_ip_net(ipaddr):
    net_str = ipaddress.ip_interface(clean_ip_str(ipaddr)).network
    return (str(net_str))

def convert_fields(args):
    convert_dict = {'cpu': 'vcpu',
                    'ram': 'ram',
                    'hdd': 'hdd_size',
                    'ip': 'ip_address',
                    'net_mask': 'net_subnet',
                    'os': 'os',
                    }
    result = ['host_name', 'server_id']
    for item in args:
        if item == 'network':
            result.append('ip_address')
            result.append('net_subnet')
        else:
            if item == 'hdd':
                result.append('hdd_number')
                result.append('hdd_size')
            else:
                result.append(convert_dict[item])
    return result

def convert_field(arg):
    convert_dict = {'cpu': 'vcpu',
                    'ram': 'ram',
                    'hdd': 'hdd_size',
                    'ip': 'ip_address',
                    'net_mask': 'net_subnet',
                    'os': 'os',
                    'network': 'network'
                    }
    return convert_dict[arg]

def read_config():
    with open('config.yml') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
        return config

def db_query_string(columns):
    query_string = sql.SQL("SELECT distinct {} FROM {} WHERE is_name ilike %s ORDER BY host_name").format(
            sql.SQL(',').join(map(sql.Identifier, columns)),
            sql.Identifier('vms_full_view2'),)
    return query_string

def db_query(query_string,is_name='%'):
    config = read_config()
    db_config = config['target']['database']
    with closing(psycopg2.connect(
            database=db_config['db_name'],
            user=db_config['db_user'],
            password=db_config['db_password'],
            host=db_config['db_host'])) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query_string,(is_name,))
            return cursor.fetchall()

def merge_dict (data):
    """"
    функция для объединения словарей. Объединение проводится для ключей hdd, ip.
    При запросе соответствующих полей может возвращаться несколько значений.

    пока не придумал ничего лучше, чем собрать информацию о том, какие ключи (server_id) сколько раз встречаются.
    дальше собирается новый словарь, в котором дополняются значения, которые могут иметь несколько значений.
    для hdd так же выполняется суммирование значений.
    Если у машины несколько дисков и несколько ip адресов - для корректного подсчета дисков в данных не должно быть
    ip адресов!
    """
    def get_uniq_key(data):
        key_list=set()
        for record in data:
            for key in record.keys():
                key_list.add(key)
        return (key_list)
    uniq_keys = get_uniq_key(data)
    merged_data = {}
    for uniq_key in uniq_keys:
        count = 0
        for record in data:
            if uniq_key in record:
                if count == 0:
                    for value in record.values():
                        merged_data.setdefault(f'{uniq_key}',dict(value))
                    count += 1
                else:
                    for value in record.values():
                            for tmp_key, tmp_value in value.items():
                                if tmp_key == 'hdd':
                                    tmp_var = merged_data[uniq_key]['hdd'] + tmp_value
                                    for hdd1_size in merged_data[uniq_key]['hdd']:
                                        hdd1 = list(hdd1_size.values())[0]
                                    for hdd2_size in tmp_value:
                                        hdd2 = list(hdd2_size.values())[0]
                                    hdd_sum = float(hdd1) + float(hdd2)
                                    tmp_var.append({'hdd_sum': f'{hdd_sum}'})
                                    merged_data[uniq_key].update({f'{tmp_key}':tmp_var})
    return merged_data

def get_vm_list(args):
    query_string = db_query_string(convert_fields(args.fields))
    vm_list = db_query(query_string, args.system[0])
    data = []
    for row in vm_list:
        data_record = {'host_name': row['host_name'],}
        for field in args.fields:
            if field == 'network':
                data_record.update(
                    {
                        f'{field}': get_ip_net("/".join(
                            (row["ip_address"],
                             row["net_subnet"])
                        )
                        )
                }
                )
            elif field == 'hdd':
                hdd = {f'{row["hdd_number"]}': f'{row["hdd_size"]}'}
                data_record.update({
                            f'{field}': [hdd]
                        }
                    )
            else:
                data_record.update({
                    f'{field}': f'{row[convert_field(field)]}'
                    }
                )
        data.append({f'{row["server_id"]}':data_record})
    if args.format[0] == 'csv':
        pd_obj = pd.read_json(json.dumps(merged_data), orient='index')
        print (pd_obj.to_csv(index=False))
    else:
        print(json.dumps(merge_dict(data)))
    # print (json.dumps(merged_data))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="cmdb cli")
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='description')

    create_parser = subparsers.add_parser('get_vms_list', help='получить список виртуальных машин в системе')
    create_parser.add_argument('--system', nargs='*', help='имя информационной системы')
    create_parser.add_argument('--fields',
                               dest='fields',
                               choices=['cpu','ram','hdd','ip','net_mask','network', 'os'],
                               help='Включить вывод дополнительной информации о ВМ',
                               nargs="*"
                               )
    create_parser.add_argument('--format',
                               dest='format',
                               choices=['json','csv'],
                               help='Управление форматом вывод отчета: json или csv',
                               default='csv')
    create_parser.set_defaults(func=get_vm_list)

    args = parser.parse_args()

    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
