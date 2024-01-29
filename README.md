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
