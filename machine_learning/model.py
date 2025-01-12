import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.model_selection import RandomizedSearchCV
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix
import pickle


def model(iterations):
    df = pd.read_csv('../data/heart_dataset.csv')
    X = df.drop('output', axis=1)
    y = df['output']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1234567)
    parameters = {
        "eta": [0.001, 0.01, 0.05, 0.1, 0.3, 0.5],
        "gamma": [0, 0.1, 0.5, 1, 3, 5],
        "max_depth": [5, 10, 15, 25, 50, 100],
        "min_child_weight": [1, 3, 5, 10, 20, 30],
        "subsample": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1],
        "lambda": [0, 1, 2, 5, 10, 20],
        "alpha": [0, 0.1, 0.5, 1, 5, 10],
        "objective": ["binary:logistic","binary:logitraw"],
    }
    xgb_model = xgb.XGBClassifier()
    n_iter_search = iterations  # Number of random parameter configurations to try
    random_search = RandomizedSearchCV(
        xgb_model,
        param_distributions=parameters,
        n_iter=n_iter_search,
        scoring='neg_mean_squared_error',
        cv=5,
        n_jobs=-1
    )
    random_search.fit(X_train, y_train)

    # Get the best parameters and model
    best_params = random_search.best_params_
    print(f"Best Parameters: {best_params}")
    print(f"Best Score: {random_search.best_score_}")

    # Save the trained model
    trained_model = random_search.best_estimator_

    # Make predictions on the test set
    y_pred_with_xgb = trained_model.predict(X_test)
    
    return trained_model, best_params, y_pred_with_xgb


def predicted_record(record,model):
    #reshape the record
    record = np.array(record).reshape(1, -1)
    prediction = model.predict(record)
    if prediction == 0:
        prediction = 0
    else:
        prediction = 1
    return prediction

def improve_model(model, new_batch):
    """
    Improve an existing XGBClassifier model using new data.
    
    Args:
        model: Trained XGBClassifier model from the first training.
        new_batch: Dataframe with new data to train on.
        parameters: Dictionary of hyperparameters to ensure consistent training.
    
    Returns:
        updated_model: The updated XGBClassifier model.
    """
    parameters = {
        "eta": [0.001, 0.01, 0.05, 0.1, 0.3, 0.5],
        "gamma": [0, 0.1, 0.5, 1, 3, 5],
        "max_depth": [5, 10, 15, 25, 50, 100],
        "min_child_weight": [1, 3, 5, 10, 20, 30],
        "subsample": [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1],
        "lambda": [0, 1, 2, 5, 10, 20],
        "alpha": [0, 0.1, 0.5, 1, 5, 10],
        "objective": ["binary:logistic","binary:logitraw"],
    }
    X_new = new_batch.drop('output', axis=1)
    y_new = new_batch['output']

    # Convert the new data into a DMatrix
    dtrain_new = xgb.DMatrix(data=X_new, label=y_new)

    # Reduce the learning rate for fine-tuning
    parameters['learning_rate'] = parameters.get('learning_rate', 0.1) * 0.5

    # Update the model with new data
    booster = model.get_booster()  # Get the underlying Booster
    booster.update(dtrain_new, iteration=10)  # Incremental update for 10 iterations

    # Save the updated booster back to the XGBClassifier model
    updated_model = model
    updated_model._Booster = booster

    return updated_model

if __name__ == '__main__':
    model = model(200)[0]
    print(model)
    # Save the model to a file
    with open('trained_model.pkl', 'wb') as file:
        pickle.dump(model, file)