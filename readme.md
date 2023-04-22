# Консольный клиент для работы с cmdb
Использование: main.py get_vms_list [-h] [--system [SYSTEM ...]] [--fields [{cpu,ram,hdd,ip,net_mask,network,os, is_name} ...]] [--format {json,csv}]
для **get_vms_list** доступные опции:
```    -h, --help            вывод справки и выход из программы
    --system [SYSTEM ...] имя информационной системы
    --fields [{cpu, ram,hdd, ip,net_mask,network,os, is_name} ...] Включить вывод дополнительной информации о ВМ                   
    --format {json,csv}   Управление форматом вывод отчета: json или [csv]
```
**main.py get_vms_list** выведет информацию по всем ВМ: host_name,vcpu,ram,ip

# Установка
## Linux/MacOS
```    
git clone https://github.com/sky1su/cmdb_cli.git
cd cmbd_cli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x main.py
cp config_sample.yml config.yml
#edit config.yml for db cred
./main.py get_vms_list
```
# Windows
> у вас должен быть установлен [git](https://git-scm.com) и [python3](https://www.python.org)

в окне терминала powershell выполнить:
```
git clone https://github.com/sky1su/cmdb_cli.git
cd .\cmdb_cli
python3.exe -m venv venv
.\venv\scripts\activate.ps1
pip install -r .\requirements.txt
copy config_sample.yml config.yml
python3.exe main.py get_vms_list

```


> если получили ошибку выполнения сценария - нужно активировать политику разрешаюшую выполнять скрипты 
> и повторно выполнить активацию виртульного окружения python
> 
```Set-ExecutionPolicy -ExecutionPolicy bypass -Scope CurrentUser```

> для установки psycopg2-binary пожалуйста ознакомьтесь с [документацией](https://www.psycopg.org/docs/install.html)
> возможно вам потребуется локальная установка PostgreSQL


