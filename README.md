# Instructions


## Start

Open a terminal in the root of the project then run the command 
```bash
docker-compose up 
```
Add the `-d` flag to run the containers in background.

To access the database from the terminal, run 
```bash
docker exec -it mongo_container mongosh
``` 

## Stop

To end the process properly, run the command 
```bash
docker-compose down
```

