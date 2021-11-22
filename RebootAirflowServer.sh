dockerfolderPath=$(pwd)/DockerFiles/AirFlow
dockerfilePath=$dockerfolderPath/Dockerfile

if [ -f $dockerfilePath ]; then
    cd $dockerfolderPath
else
    echo 'dockerfile not exists :'$dockerfilePath
    exit 1
fi

containerName=airflow-container
port_out=8890
port_in=8080
airflowFolder=$(pwd)/../../Airflow_Volume



echo 'Try to get container ID which name is '$containerName

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

echo "Try to reboot airflow server..."
docker run -tid --name $containerName -p $port_out:$port_in \
--network my-net \
-v $airflowFolder:/root/airflow \
-v $dockerfolderPath/pythonCode:/code \
airjob_airflow python3 /code/RunAirFlowServer.py

echo "Reboot server DONE"

exit 0