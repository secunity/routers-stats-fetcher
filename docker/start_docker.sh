CONTAINER_NAME="onprem-1"

# make sure you have secunity.conf in the current folder
docker run -dit \
--name $CONTAINER_NAME \
--restart unless-stopped \
-v ${PWD}/secunity.conf:/etc/secunity/secunity.conf $IMAGE
#docker exec -it -u root onprem-1 bash

#scp -r  /home/gilad/routers-stats-fetcher/  u