#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import ipaddress
import json
import re
from contextlib import closing

import pandas as pd
import psycopg2
import yaml
from psycopg2 import sql
from psycopg2.extras import DictCursor
import os


def clean_net_str(string_for_clean):
    result = re.search('(\d+\.\d+\.\d+\.\d+)', string_for_clean)
    if(result == None):
        return "0.0.0.0"
    return result.group(1)

def get_ip_net(ipaddr):
    net_str = ipaddress.ip_interface(ipaddr).network
    return (str(net_str))

def convert_field(arg):
    """Возвращает значение словаря по переданному ключу"""
    convert_dict = {'cpu': 'vcpu',
                    'ram': 'ram',
                    'hdd': 'hdd_size',
                    'ip': 'ip_address',
                    'net_mask': 'net_subnet',
                    'os': 'os',
                    'network': 'network',
                    'is_name': 'is_name',
                    'dc': 'dc'
                    }
    return convert_dict[arg]

def convert_fields(args):
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
                result.append(convert_field(item))
    return result

def read_config():
    home = str(os.path.dirname(os.path.abspath(__file__)))
    with open(f'{home}/config.yml') as conf_file:
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

def get_uniq_key(data):
    key_list=set()
    for record in data:
        for key in record.keys():
            key_list.add(key)
    return (key_list)

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

    uniq_keys = get_uniq_key(data)
    merged_data = {}
    flag_hdd=0
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
                                    flag_hdd=1
                                    tmp_var = merged_data[uniq_key]['hdd'] + tmp_value
                                    merged_data[uniq_key].update({f'{tmp_key}':tmp_var})
        if flag_hdd == 1:
            for record_name, record_value in merged_data.items():
                hdd_sum=0
                for item in record_value['hdd']:
                    hdd_sum=int(hdd_sum)+int(list(item.values())[0])
                merged_data[record_name]['hdd_sum'] = hdd_sum

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
                            (clean_net_str(row["ip_address"]),
                             clean_net_str(row["net_subnet"]))
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
    if args.format == 'csv':
        pd_obj = pd.read_json(json.dumps(merge_dict(data)), orient='index')
        print(pd_obj.to_csv(index=False))
    else:
        print(json.dumps(merge_dict(data)))
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="cmdb cli")
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='description')

    parser_vms = subparsers.add_parser('vms', help='получить список виртуальных машин в системе')
    parser_vms.add_argument('--system', nargs='*',
                            help='имя информационной системы',
                            default='%')
    parser_vms.add_argument('--fields',
                            dest='fields',
                            choices=['cpu','ram','hdd','ip','net_mask','network','os', 'is_name', 'dc'],
                            help='Включить вывод дополнительной информации о ВМ',
                            nargs="*",
                            default=['ip']
                            )
    parser_vms.add_argument('--format',
                            dest='format',
                            choices=['json','csv'],
                            help='Управление форматом вывод отчета: json или csv',
                            default='csv')
    parser_vms.set_defaults(func=get_vm_list)

    args = parser.parse_args()

    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
