# AIRJOB

包含2大部分container
1. Airflow
    - 此部分因HAP環境要使用Spark的資源的話，不能用container的方式架設，因此正式上HAP環境時Airflow要直接架設在本機環境
    - 保留docker file是為了在GCP上架設測試用的Airflow環境
2. Web Server
    - AIRJOB主體都在這
    - 使用nginx架設伺服器，配合uwsgi啟動Django server，參考資源:
        - https://medium.com/工程隨寫筆記/flask-app-加上-wsgi-及-nginx-服務-b8bdc60d1dc7
        - https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04
        - https://github.com/twtrubiks/docker-django-nginx-uwsgi-postgres-tutorial
        - https://github.com/tiangolo/uwsgi-nginx-flask-docker
        - https://www.maxlist.xyz/2020/06/18/flask-nginx/
        - https://www.maxlist.xyz/2020/06/18/flask-nginx/
    - the web client <-> the web server （ Nginx ）<-> uWSGI <-> Django

