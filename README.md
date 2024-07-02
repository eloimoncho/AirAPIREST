# AIR API REST for the Drone Engineering Ecosystem

## Table of Contents

1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Local set up](#local-set-up)
5. [RPi set up](#rpi-set-up)
6. [Endpoints](#endpoints)

## Introduction

The APIREST module is responsible for storing data in the air while the drone is executing a planned flight plan. The module offers a RESTful interface, so that any ground application can access the data through HTTP requests (GET, POST, PUT, DELETE), __while being connected to the access point of the drone__. Therefore, the communication between APIREST and the rest of the modules is not implemented via MQTT, but via HTTP. The data is stored in a MongoDB database.   
      
As an example, before the execution of a flight plan, it is stored into this APIREST module, together with the flight associated with it. Later, while the flight is being executed, all the information the user has requested to be obtained, such as images or videos, is stored in this APIREST module until its landing. Once the drone has landed, all the information associated to the flight is shared with the ground APIREST module, to have it available at any time.

This information is sent automatically to the ground APIREST module in the case of executing the flight plan through the Flutter Mobile App, and in the case of being executed through the Dashboard one, __the button "Save Media" needs to be selected__, as it starts this process of sending the information from the air backend, to the ground one.

![](https://github.com/JordiLlaveria/AirAPIRESTDEE/blob/manager/assets/Save%20Media.PNG)

## Requirements

Before starting with the installation, make sure you have the following software installed on your system:

- Python 3.7, use version 3.7.6 if you have any problem with others.
- MongoDB Community Edition
- MongoDB Database Tools
- MongoDB Compass (optional, but recommended for easier database management)
- PuTTY (in the case of executing the APIREST module in the RPi)
- Docker Desktop
- PyCharm (or any preferred IDE)

## Installation

You can install MongoDB and MongoDB Database Tools from the following links:
- [Install MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/)
- [Install MongoDB Database Tools](https://www.mongodb.com/docs/database-tools/)

To make it easier to work with the database, it is also recommended to install [MongoDB Compass](https://www.mongodb.com/products/compass).

To be able to create Docker images and upload them to Docker Hub, Docker Desktop needs to be downloaded, and an account in Docker Hub needs to be created:
- [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Create account in Docker Hub](https://hub.docker.com/)

## Local set up

To run and contribute, clone this repository to your local machine and install the requirements.  This set up is as same the one which is used with the ground backend, and the idea is to be able to simulate the APIREST module in a local environment, before uploading all the files into de RPi and executing them in a production environment.
    
To run the APIREST on localhost for simulation, you must edit the run/debug configuration in PyCharm, as shown in the image, in order to pass the required arguments to the script. 
You will need to change the Script path to Module name and input _uvicorn_, as well as adding the following parameters: _main:app --reload --port 9000_

![image](https://github.com/eloimoncho/AirAPIREST/assets/91852608/a7d574a9-e187-44c8-a822-921657ab9193)


![image](https://github.com/eloimoncho/AirAPIREST/assets/91852608/9aa0c00e-3104-4c8b-b2e4-d459eaa85a51)


## RPi set up

When this APIREST module has been tested locally, and the behavior is the one desired, it's time to execute it in the production environment, meaning that it's going to be executed inside the RPi of the drone. Inside of it, this APIREST module is started inside a Docker container, not isolated or runned locally, such as in local set up condition. Mainly, this means that there's a need of __creating the image__ of this APIREST module to be able to execute it inside the drone.

In order to do that, there exists the Dockerfile file, which is cloned together with the rest of the Python codes and defines the parameters of this image created.

To create the image, there's the need to have Docker Desktop installed, and once this process is complete, run the following command into de directory where Dockerfile is located:

```
docker build --platform linux/arm64/v8 -t “Docker Hub username”/”image name”:”version” .
```

Being an example:

```
docker build --platform linux/arm64/v8 -t jordillaveria/restapi_arm64:v2 .
```

__Once this image is created__, it can be found inside the Docker Desktop application, and at this moment it can be pushed into Docker Hub repository, in order to be available for download from the RPi:

```
docker push “Docker Hub username”/”image name”:”versión”
```

Following this process, the image is already available for its use inside the Docker Compose file executed inside the RPi, and requests can be made to the endpoints it contains once the container is started.

## Endpoints

Once the service has started, navigate to http://192.168.208.6:9000 in the case of the RPi set up, or http://127.0.0.1:8000 in the case of the local one, to see and try all the different API endpoints.

![](https://github.com/JordiLlaveria/AirAPIRESTDEE/blob/manager/assets/Endpoints.PNG)

You will easily see the data models involved in the different API endpoints.    
