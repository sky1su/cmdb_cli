консольный клиент для работы с cmdb

usage: main.py get_vms_list [-h] [--system [SYSTEM ...]] [--fields [{cpu,ram,hdd,ip,net_mask,network,os} ...]] [--format {json,csv}]

options:
  -h, --help            show this help message and exit
  
  --system [SYSTEM ...]
                        имя информационной системы
                        
  --fields [{cpu,ram,hdd,ip,net_mask,network,os} ...]
                        Включить вывод дополнительной информации о ВМ
                        
  --format {json,csv}   Управление форматом вывод отчета: json или csv


