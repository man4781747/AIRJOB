dockerfolderPath=$(pwd)/DockerFiles/DjangoServer
dockerfilePath=$dockerfolderPath/Dockerfile

if [ -f $dockerfilePath ]; then
    cd $dockerfolderPath
else
    echo 'dockerfile not exists :'$dockerfilePath
    exit 1
fi

containerName=airjob-server-container
port_out=8893
port_in=8000
djangoFilePath=$(pwd)/../../Volume/DjangoServer/mydjango
airflowFolder=$(pwd)/../../Airflow_Volume
# echo $djangofilePath

if [ -d $djangoFilePath ]; then
    echo 'Django folder exists :'$containerName
else
    echo 'Django folder not exists :'$containerName
    exit 1
fi

if [ -d $airflowFolder/dags ]; then
    echo 'airflow dags folder exists :'$containerName
else
    echo 'airflow dags folder not exists :'$airflowFolder/dags
    exit 1
fi

containerID=$(docker ps -a --filter "NAME=$containerName" --format "{{.ID}}")
if ["$containerID" = ""]
then
    echo "Can't find container: $containerName"
else
    echo "container ID: "$containerID
    echo "Stop server..."
    docker rm -f $containerID
    echo "Stop server DONE"
fi

docker network create my-net

echo "Try to reboot server..."
docker run -tid --name $containerName -p $port_out:$port_in \
--network my-net \
-v $djangoFilePath:/code \
-v $airflowFolder/dags:/airflowDagsFolder \
-v $airflowFolder/deleteDags:/deletedDag \
-v $airflowFolder/tarFolder:/tarFolder \
airjob-server:latest sudo python manage.py runserver 0.0.0.0:$port_in --insecure

echo "Reboot server DONE"

exit 0