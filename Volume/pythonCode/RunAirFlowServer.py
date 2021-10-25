import subprocess
import os

with open(r"/root/airflow/airflow.cfg", 'r') as f:
    S_fullString = f.read()

S_fullString = S_fullString.replace(r"/root/airflow/dags", r"/VolumeFile/dags")
S_fullString = S_fullString.replace(r"/root/airflow/logs", r"/VolumeFile/logs")

with open(r"/root/airflow/airflow.cfg", 'w') as f:
    f.write(S_fullString)
        
# "dags_folder = /root/airflow/dags"        

scheduler = subprocess.Popen(["airflow", "scheduler"])
# webserver = subprocess.Popen(["airflow","webserver","-p","8080"])
os.system("airflow webserver -p 8080")