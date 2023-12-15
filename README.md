![alt text](figures/logo_Enershare.png)
```
  _____                          _                                 ____   _____  ____   ____   _       _                    _     ____  ___ 
 | ____| _ __    ___  _ __  ___ | |__    __ _  _ __  ___          |  _ \ | ____|/ ___| / ___| (_) ____(_) _ __    __ _     / \   |  _ \|_ _|
 |  _|  | '_ \  / _ \| '__|/ __|| '_ \  / _` || '__|/ _ \  _____  | |_) ||  _| | |     \___ \ | ||_  /| || '_ \  / _` |   / _ \  | |_) || | 
 | |___ | | | ||  __/| |   \__ \| | | || (_| || |  |  __/ |_____| |  _ < | |___| |___   ___) || | / / | || | | || (_| |  / ___ \ |  __/ | | 
 |_____||_| |_| \___||_|   |___/|_| |_| \__,_||_|   \___|         |_| \_\|_____|\____| |____/ |_|/___||_||_| |_| \__, | /_/   \_\|_|   |___|
                                                                                                                 |___/                      
```

Welcome to INESC TEC Renewable Energy Community (REC) Sizing API.

A REST API for sizing and **planning the operation** of a Renewable Energy Community (REC) or
Citizen Energy Community (CEC) that can promote the minimization of the members’ operation cost with energy.
This REST API provides endpoints for calculating, under the *Enershare* project.

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
