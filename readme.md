**Консольный клиент для работы с cmdb**

Использование: main.py get_vms_list [-h] [--system [SYSTEM ...]] [--fields [{cpu,ram,hdd,ip,net_mask,network,os, is_name} ...]] [--format {json,csv}]

для **get_vms_list** доступные опции:

    -h, --help            вывод справки и выход из программы
    --system [SYSTEM ...] имя информационной системы
    --fields [{cpu, ram,hdd, ip,net_mask,network,os, is_name} ...] Включить вывод дополнительной информации о ВМ                   
    --format {json,csv}   Управление форматом вывод отчета: json или [csv]

**main.py get_vms_list** выведет информацию по всем ВМ: host_name,vcpu,ram,ip

**Установка**
git clone https://github.com/sky1su/cmdb_cli.git
cd cmbd
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x main.py
