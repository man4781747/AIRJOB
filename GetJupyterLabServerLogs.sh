containerName=jupyter-lab-server-container

echo 'Try to get container ID which name is '$containerName

containerID=$(docker ps -a --filter "NAME=$containerName" --format "{{.ID}}")
if ["$containerID" = ""]
then
    echo "Can't find container: "$containerName
    exit 0
else
    echo "container ID: "$containerID
    sudo docker container logs $containerID --tail 10 -f
fi
exit 0