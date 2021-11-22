dockerfolderPath=$(pwd)/DockerFiles/JupyterLabServer
dockerfilePath=$dockerfolderPath/Dockerfile

if [ -f $dockerfilePath ]; then
    cd $dockerfolderPath
else
    echo 'dockerfile not exists :'$dockerfilePath
    exit 1
fi

containerName=jupyter-lab-server-container
port_out=5567
port_in=5567
jupyterFolder=$(pwd)/../../Jupyter_Volume

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

echo "Try to reboot server..."
docker run -tid --name $containerName -p $port_out:$port_in \
-v $jupyterFolder:/jupyterLabFolder \
airjob_jupyter-lab:latest jupyter lab --port $port_in --ip 0.0.0.0 --NotebookApp.token=password --allow-root

echo "Reboot server DONE"

exit 0