import string
import random
import joblib
import pymongo
import config
import time
import pandas as pd
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier


def add_strokes(df: DataFrame, model: RandomForestClassifier) -> DataFrame:
    """
    Add a stroke column to a patients DataFrame
    :param df: DataFrame containing patients vitals
    :param model: model to use to generate data
    :return: a dataframe containing both patients vitals a stroke column
    """
    output = model.predict(df)
    df_output = df.copy()
    df_output["output"] = output
    return df_output


def create_correlation_dict(df: DataFrame, column1: string, column2: string, nb_bins: int = 9,) -> {string: int}:
    """
    Generate dictionaries of all the values a variable can take in function of another column
    :param df: dataframe containing all the values
    :param column1: name of the first column
    :param column2: name of the second column
    :param nb_bins: number of bins (to simplify dictionaries)
    :return: a dictionary containing all the values a variable can take in function of another column
    """
    key_column, value_column = column1, column2
    size_bins = (df[key_column].max() - df[key_column].min()) / nb_bins
    bins = []

    # on cherche les valeurs des bins pour les transformer en interfvals
    for i in range(nb_bins):
        bins.append(i * size_bins + df[key_column].min())

    # Création des bins avec les valeurs calculées précedements
    bins.append(df[key_column].max())
    df[key_column + '_bin'] = pd.cut(df[key_column], bins, include_lowest=True)

    interval_dict = {}
    for interval in df[key_column + '_bin'].unique():
        interval_dict[interval] = df[df[key_column + '_bin'] == interval][value_column].tolist()

    return interval_dict


def generate_values(df: DataFrame, column_name: string, dict_values: {string: int}) -> [int]:
    """
    Generate values in function to another
    :param df: dataframe to complete
    :param column_name: column name to generate data from
    :param dict_values: dictionary containing possible values
    :return:
    """
    values = []
    for _, row in df.iterrows():
        ref = row[column_name]
        interval_values = dict_values[next(interval for interval in dict_values if interval.left < ref <= interval.right)]
        min_value = min(interval_values)
        max_value = max(interval_values)
        values.append(random.randint(min_value, max_value))
    return values


def generate_data(path_to_dataset: string, model: RandomForestClassifier = None, nb_data: int = 20, with_results: bool = False) -> DataFrame:
    """
    Generate a dataframe with multiples lines representing patients vitals
    :param path_to_dataset: path to the original vitals dataset
    :param model: model to add stroke column to data
    :param nb_data: number of line of the dataframe
    :param with_results: add a column to know if a patient had a stroke or not
    :return: a dataframe with multiple patients vitals
    """
    df_input = pd.read_csv(path_to_dataset)
    df_columns = ['trestbps', 'chol', 'fbs', 'restecg', 'ca', 'thal']

    age_thalach = create_correlation_dict(df_input, 'age', 'thalach')
    oldpeak_slope = create_correlation_dict(df_input, 'oldpeak', 'slope', 4)
    exang_oldpeak = create_correlation_dict(df_input, 'oldpeak', 'exang', 4)
    cp_thalach = create_correlation_dict(df_input, 'thalach', 'cp')

    df = pd.DataFrame(columns=['age', 'oldpeak'])

    for i in range(nb_data):
        df.loc[i] = [random.randint(29, 77), round(random.uniform(0, 6.2), 1)]

    df['thalach'] = generate_values(df, 'age', age_thalach)
    df['cp'] = generate_values(df, 'thalach', cp_thalach)
    df['exang'] = generate_values(df, 'oldpeak', exang_oldpeak)
    df['slope'] = generate_values(df, 'oldpeak', oldpeak_slope)

    for column in df_columns:
        min_val = df_input[column].min()
        max_val = df_input[column].max()
        df[column] = [random.randint(min_val, max_val) if df_input[column].dtype == 'int64' else round(
            random.uniform(min_val, max_val), 1) for _ in range(len(df))]

    if with_results:
        return add_strokes(df, model)
    else:
        return df


if __name__ == "__main__":
    
    myclient = pymongo.MongoClient(config.MONGO_URL)
    mydb = myclient[config.DB_NAME]
    model = joblib.load(config.MODEL_PATH)

    patient_col = mydb["patients"]

    while True:
        nb_data = random.randint(5, 40)
        with_results = random.choice([True, False])

        generated_data = generate_data(config.DATASET_PATH, model, nb_data=nb_data, with_results=with_results)
        rows_as_dicts = generated_data.to_dict(orient='records')

        # Add timestamp to each record
        timestamp = int(time.time())  # Convertir en entier
        for record in rows_as_dicts:
            record['timestamp'] = timestamp
            print(record)
        print(rows_as_dicts)
        patient_col.insert_many(rows_as_dicts)

        time.sleep(config.COOLDOWN)

