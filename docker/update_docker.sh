NAME=mikrotik-probe-1
NAME=mikrotik
docker start $NAME

# sleep 1s
docker exec -t -u root $NAME supervisorctl stop secunity_executables

# docker exec -t -u secunity $NAME python3 -m pip install --upgrade pip setuptools
# docker exec -t -u root $NAME python3 -m pip install --upgrade pip setuptools

docker exec -t -u secunity $NAME git checkout .
docker exec -t -u secunity$NAME git fetch --all
docker exec -t -u secunity $NAME git pull
docker exec -t -u secunity $NAME git checkout $BRANCH
#docker exec -t -u secunity mikrotik-probe-1 git checkout mikrotik


docker exec -t -u root $NAME bash -x /opt/upgrade_secunity.sh
