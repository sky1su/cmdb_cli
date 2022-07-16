
import psycopg2
import yaml
from psycopg2.extras import DictCursor
from contextlib import closing

def read_config():
    with open('config.yml') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
        return config

def db_query():
    config = read_config()
    db_config = config['target']['database']
    with closing(psycopg2.connect(database=db_config['db_name'], user=db_config['db_user'], password=db_config['db_password'], host=db_config['db_host'])) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('''
                            select distinct host_name, vcpu, ram, sum(hdd_size) as hhd_size, os from vms_full_view
                            where status = 'В эксплуатации' AND 
                                  host_name ilike 'mdm30%%'
                            GROUP BY host_name, vcpu, ram, os
                            limit 10
                            ''')
            return cursor.fetchall()

if __name__ == '__main__':
    for row in db_query():
        print(row['host_name'])