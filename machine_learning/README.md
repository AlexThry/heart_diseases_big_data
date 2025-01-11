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