# routers-stats-fetcher
Secunity's DDoS Inhibitor on-prem agent for network devices (mainly routers).

The on-prem agent requires a python (at least 3.6) script to run continuously on a linux machine. The script has a few dependencies (see [requirements.txt](requirements.txt)) with several dependencies:
- paramiko - used to connect to the device
- APScheduler - used to schedule a period network device check
- requests - used to send data back to Secunity's DDoS Inhibitor

The python script can be initialized with a config file (JSON - see [routers-stats-fetcher.conf](routers-stats-fetcher.conf)) or by passing command line parameters

### Script/Config Arguments
```bash
$ ./worker.py -h
usage: worker.py [-h] [-c CONFIG] [-l LOGFILE] [-v VERBOSE] [-s HOST]
                 [-p PORT] [-u USER] [-w PASSWORD] [-k KEY_FILENAME]
                 [--identifier IDENTIFIER] [--url URL]
                 [--url_scheme URL_SCHEME] [--url_host URL_HOST]
                 [--url_port URL_PORT] [--url_path URL_PATH]
                 [--url_method URL_METHOD]

Secunity DDoS Inhibitor On-Prem Agent

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config file (overriding all other options)
  -l LOGFILE, --logfile LOGFILE
                        File to log to. default:
  -v VERBOSE, --verbose VERBOSE
                        Indicates whether to log verbose data
  -s HOST, --host HOST, --ip HOST
                        Router IP
  -p PORT, --port PORT  SSH port
  -u USER, --user USER, --username USER
                        SSH user
  -w PASSWORD, --password PASSWORD
                        SSH password
  -k KEY_FILENAME, --key_filename KEY_FILENAME
                        SSH Key Filename
  --identifier IDENTIFIER, --id IDENTIFIER
                        Device ID
  --url URL             The URL to use for remove server
  --url_scheme URL_SCHEME
                        Remote server URL scheme
  --url_host URL_HOST   Remote server URL hostname
  --url_port URL_PORT   Remote server URL port
  --url_path URL_PATH   Remote server URL path
  --url_method URL_METHOD
                        Remote server URL method

```

| Name | Mandatory | Description | Default |
| --- | --- | --- | --- |
| config | | Full path to config file | /opt/routers-stats-fetcher/routers-stats-fetcher.conf |
| logfile | | Full path to log file | no file is used |
| verbose | | Indicates whether to perform verbose logging | false |
| host | V | Network device hostname/ip | |
| port | | Port to use for SSH session | 22 |
| user | V | Username to use for SSH session | |
| password | | Password to use for SSH session | |
| key_filename | | Key file (full path) to use for SSH session | |
| identifier | V | Unique network device identifier as obtained from view network device | | 
| url | | The URL to use for sending information back to DDoS Inhibitor |

* If no config file location is specified the default config file location is used
* Parameters from config file **override** command line arguments


## Running the agent

**[Running a Pre-Built Docker Image](#Running-a-Pre-Built-Docker-Image)**<br>
**[Building and Running a Docker Container](#Building-and-Running-a-Docker-Container)**<br>
**[Run on a host using a python virtual environment](#virtualenv)**

### Running a Pre-Built Docker Image
TODO:

### Building and Running a Docker Container
This is the recommended method at the moment as it does not require keeping the config file on the host machine.

1. Download the Dockerfile from which to build the local image (see [Dockerfile](Dockerfile))
```bash
$ curl -L https://github.com/secunity/routers-stats-fetcher/raw/master/Dockerfile -o Dockerfile
```
2. Build the local image (replace *IMAGE_NAME*)
```
$ docker build --rm -t IMAGE_NAME .
```
3. Download the config file
```bash
$ curl -L https://github.com/secunity/routers-stats-fetcher/raw/master/routers-stats-fetcher.conf -o routers-stats-fetcher.conf
```
4. Edit the config file with your favorite editor
```bash
$ vi routers-stats-fetcher.conf
```
5. Create a new container from the local image (replace *CONTAINER_NAME*)
```bash
$ docker create -it \
--name CONTAINER_NAME \
IMAGE_NAME
```
6. Copy the edited config file inside the docker container
```bash
$ docker cp routers-stats-fetcher.conf CONTAINER_NAME:/opt/routers-stats-fetcher/routers-stats-fetcher.conf
```
7. Start the container
```bash
$ docker start
```
