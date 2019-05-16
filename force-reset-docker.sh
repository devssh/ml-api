docker rm $(docker ps -aq) --force
docker image rm $(docker images) --force
docker volume rm $(docker volume ls)


