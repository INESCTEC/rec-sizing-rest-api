![alt text](figures/logo_Enershare.png)
```
  _____   ______  _____    _____  _       _                 _____   ______   _____  _______             _____  _____ 
 |  __ \ |  ____|/ ____|  / ____|(_)     (_)               |  __ \ |  ____| / ____||__   __|     /\    |  __ \|_   _|
 | |__) || |__  | |      | (___   _  ____ _  _ __    __ _  | |__) || |__   | (___     | |       /  \   | |__) | | |  
 |  _  / |  __| | |       \___ \ | ||_  /| || '_ \  / _` | |  _  / |  __|   \___ \    | |      / /\ \  |  ___/  | |  
 | | \ \ | |____| |____   ____) || | / / | || | | || (_| | | | \ \ | |____  ____) |   | |     / ____ \ | |     _| |_ 
 |_|  \_\|______|\_____| |_____/ |_|/___||_||_| |_| \__, | |_|  \_\|______||_____/    |_|    /_/    \_\|_|    |_____|
                                                     __/ |                                                           
                                                    |___/                                                            
```
Welcome to INESC TEC Renewable Energy Community (REC) Sizing API.

A REST API for **sizing and planning the long-term operation** of a Renewable Energy Community (REC) or
Citizen Energy Community (CEC) that can promote the minimization of the members’ operation cost with energy.
This tool was developed under the *Enershare* project.

Developers // Contacts:

* Armando Moreno (armando.moreno@inesctec.pt)
* Pedro Macedo (pedro.m.macedo@inesctec.pt)
* Ricardo Silva (ricardo.emanuel@inesctec.pt)


# Run API
Run the API locally with uvicorn:
```shell
$ uvicorn main:app 
```
(For development, you can include the ```--reload``` tag at the end).

# Swagger and Redoc
To access the interactive API docs, include the following at the end of the URL where uvicorn is running: 
- ```/docs``` (Swagger format);
- ```/redoc``` (ReDoc format);

# Docker
A dockerfile and docker-compose.yml file have been prepared for and 
easy deployment of the service on any server.

On a server with docker engine, docker-compose and git installed:

- clone this repository to the server;
- create the ```.env``` file on the project's base directory
- run the command ```docker-compose up -d --build``` (Windows) / 
```sudo docker compose up -d --build``` (Linux)

# Notes about hardcoded information
This API is specifically designed for interacting with the rec_sizing library (https://github.com/INESCTEC/rec-sizing) 
within the context of the ENERSHARE project. Several configurations required to describe the two REC within the project, 
SEL and IN-DATA are hardcoded. Given the sensitive nature of those static parameters, which includes the geographic 
location of the REC meters and the contracts celebrated with their respective retailers, the hardcoded values are 
fictitious. Such information can, nonetheless be edited in the following scripts:
- ```/helpers/indata_shelly_info.py``` ----- required configurations for requesting data from IN-DATA connector
- ```/helpers/meter_contracted_power.py``` - meters' maximum allowed contracted power, in kVA
- ```/helpers/meter_installed_pv.py``` ----- meters' installed PV capacity, in kWp
- ```/helpers/meter_locations.py``` -------- meters' geographic location, provided as latitude and longitude coordinates
- ```/helpers/meter_tariff_cycles.py``` ---- meters' contracted fixed tariff cycle, from ("simples", "bi-horárias", 
"tri-horárias")
- ```/helpers/sel_shelly_info.py``` -------- required configurations for requesting data from SEL connector
