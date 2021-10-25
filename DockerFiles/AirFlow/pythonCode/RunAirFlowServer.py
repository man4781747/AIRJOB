import subprocess
import os

scheduler = subprocess.Popen(["airflow", "scheduler"])
os.system("airflow webserver -p 8080")