#!/bin/bash


IMAGE_NAME="secunity/onprem-agent"
IMAGE_TAG="1.0.0"
IMAGE="$IMAGE_NAME/$IMAGE_TAG"

docker pull python:3.7
docker build --rm -f Dockerfile -t "$IMAGE" .

  GNU nano 4.8                                                                                      build.sh

NAME="probe-1"
CONF="secunity.conf"


IMAGE="secunity/onorem-agent"
FOLDER="/data/$NAME"

docker rm --force $NAME
rm -rf $FOLDER

mkdir -p $FOLDER/etc/secunity
mkdir -p $FOLDER/var/log/secunity


cp secunity.conf $FOLDER/etc/secunity



# make sure you have secunity.conf in the current folder
docker create -it \
--name $NAME \
--restart unless-stopped \
-v $FOLDER/etc/secunity:/etc/secunity \
-v $FOLDER/var/log/secunity:/var/log/secunity \
$IMAGE:latest

cp secunity.conf $FOLDER/etc/secunity

docker start $NAME

exit


IMAGE="secunity/onorem-agent"
TAG="1.0.0"

docker rmi $IMAGE:latest
docker rmi $IMAGE:$TAG

docker image prune -f -a

docker builder prune -f -a

docker build --rm -f Dockerfile -t $IMAGE:$TAG .

docker tag $IMAGE:$TAG $IMAGE:latest


