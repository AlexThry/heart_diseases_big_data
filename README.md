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

## Database connection 

To navigate into the database easily, u can download a mongo client (mongo compass for exemple) and connect using this url: `mongodb://localhost:27017/`

On mongo compass, you'll get something like this: ![compass](./assets/image.png)




# Machine learning


## Which method use ?
The method use is XGBoost
## Which part can you use ? 
### improve_model
This function allows us to improve the model with new batch data.

To use it you need to put in input:
- The model himself
- New batch of data, as a dataframe

It will return the model updated

### Predicted_record
This function allows us to predict the output of one given record

To use it you need to put in input:
- the record that you want to predict, as a list of values (respecting the order of the mongo database)
- the model 

It will return you an int 
- 0 : No heart disease
- 1 : Heart disease

If you have any question contact me.
