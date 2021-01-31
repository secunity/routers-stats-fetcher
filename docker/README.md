# routers-stats-fetcher
Secunity's on-prem agent for network devices (mainly routers) docker image.

The on-prem agent connects based on the config file (JSON - see [routers-stats-fetcher.conf](../routers-stats-fetcher.conf))

### Config Arguments
```shell script

  -config Config file (overriding all other options).
  -logfile File to log to. default: none
  -verbose Indicates whether to log verbose data. default: false
  -host Network-device (Router) hostname/IP
  -port SSH port. default: 22
  -vendor Netwrk-device vendor (default "cisco"). options: "cisco/juniper/arista"
  -user SSH user
  -password SSH password
  -key_filename SSH Key Filename (must be copied/mounted and chmod correctly)
  -identifier Device ID (available on Secunity's web GUI')
  

```

| Name | Mandatory | Description | Default |
| --- | --- | --- | --- |
| config | | Full path to config file | /opt/routers-stats-fetcher/routers-stats-fetcher.conf |
| logfile | | Full path to log file | none |
| verbose | | Indicates whether to perform verbose logging | false |
| host | V | Network device hostname/ip | |
| port | | Port to use for SSH session | 22 |
| vendor | | The network device vendor | cisco |
| user | V | Username to use for SSH session | |
| password | | Password to use for SSH session | |
| key_filename | | Key file (full path) to use for SSH session | |
| identifier | V | Unique network device identifier as obtained from view network device | | 

* If no config file location is specified the default config file location is used
* Parameters from config file **override** command line arguments


## Running the agent

Please follow the following steps:


###### Download the latest docker image (optional)
```shell script
$ docker pull secunity/cfstats1
```

###### Download the config file
```shell script
$ curl -L https://github.com/secunity/routers-stats-fetcher/raw/master/routers-stats-fetcher.conf -o routers-stats-fetcher.conf
```

###### Edit the config file with your favorite editor
```shell script
$ vi routers-stats-fetcher.conf
```

###### Create a new container from the downloaded image.

```shell script
$ docker create -it \
--name secunity-probe \
--restart unless-stopped \
--network host \
secunity/cfstats1
```

###### Copy the edited config file inside the docker container
```shell script
$ docker cp routers-stats-fetcher.conf secunity-probe:/opt/routers-stats-fetcher
```

###### Start the container
```shell script
$ docker start secunity-probe
```
