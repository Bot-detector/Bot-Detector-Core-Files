import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import datetime as dt
import numpy as np
from sklearn.preprocessing import StandardScaler 
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
# custom
import SQL

def logging(f):
    def wrapper(df, *args, **kwargs):
        start = dt.datetime.now()
        result = f(df, *args, **kwargs)
        end = dt.datetime.now()
        print(f'{f.__name__} took: {end - start} shape= {result.shape}')
        return result
    return wrapper

def get_highscores():
    data = SQL.get_highscores_data()
    df_hiscore = pd.DataFrame(data)

    print(f'hiscore: {df_hiscore.shape}')
    return df_hiscore

def get_players():
    data = SQL.get_player_names()
    players = pd.DataFrame(data)

    df_players = players
    df_players.set_index('name', inplace=True)
    df_players.drop(columns=['created_at','updated_at','id'], inplace=True)
    
    print(f'players: {df_players.shape}')
    return df_players

def get_labels():
    data = SQL.get_player_labels()
    labels = pd.DataFrame(data)
    df_labels = labels.set_index('id')

    print(f'labels: {df_labels.shape}')
    return df_labels

@logging
def start_pipeline(df):
    return df.copy()

@logging
def clean_dataset(df, skills_list, minigames_list):
    # sort by timestamp, drop duplicates keep last
    df.sort_values('timestamp', inplace=True)
    # df.drop_duplicates('Player_id', keep='last', inplace=True)

    # drop unrelevant columns
    df.drop(columns=['id','timestamp','ts_date','Player_id'], inplace=True)

    # set unique index
    df.set_index(['name'],inplace=True)

    # total is sum of all skills
    df['total'] = df[skills_list].sum(axis=1)

    # replace -1 values
    df[skills_list] = df[skills_list].replace(-1, 1)
    df[minigames_list] = df[minigames_list].replace(-1, 0)

    return df

@logging
def features(df, skills_list):
    # save total column to variable

    total = df['total']

    # for each skill, calculate ratio
    for skill in skills_list:
        df[f'{skill}/total'] = df[skill] / total

    # df['pvm_median'] =  df[['attack','defence','strength','hitpoints','ranged','magic']].median(axis=1)/total
    # df['pvm_mean'] =    df[['attack','defence','strength','hitpoints','ranged','magic']].mean(axis=1)/total
    # replace infinities & nan
    df = df.replace([np.inf, -np.inf], 0) 
    df.fillna(0, inplace=True)

    return df

@logging
def filter_relevant_features(df):
    # all features
    features =  df.columns

    # take median of all columns
    bad_features = pd.DataFrame(df.median(), columns=['median'])
    
    # if a row has no data it returns -1
    # if the median of the dataset is below 0 then that feature is mostly empty
    mask = (bad_features['median'] < 10)
    bad_features = bad_features[mask].index

    # filter out bad features
    features = [f for f in features if f not in bad_features]

    return df[features].copy()

@logging
def f_standardize(df):
    scaler = StandardScaler() 
    X_scaled = scaler.fit_transform(df) 
    return pd.DataFrame(X_scaled, columns=df.columns, index=df.index)

@logging
def f_normalize(df):
    X_normalized = normalize(df)
    return pd.DataFrame(X_normalized, columns=df.columns, index=df.index)

def f_pca(df, n_components=2, pca=None):
    if pca is None:
        pca = PCA(n_components = n_components) 
        pca = pca.fit(df)

    # Apply dimensionality reduction to X.
    X_principal = pca.transform(df)
    # rename columns and put in dataframe
    columns = [f'P{c}' for c in range(n_components)]
    df = pd.DataFrame(X_principal, columns=columns, index=df.index) 
    df.dropna(inplace=True)
    return df, pca

def best_file_path(startwith, dir='Predictions/models'):
    files = []
    for f in os.listdir(dir):
        if f.endswith(".joblib") and f.startswith(startwith):
            # accuracy is in filename, so we have to parse it
            model_file = f.replace('.joblib','')
            model_file = model_file.split(sep='_')
            # save to dict
            d ={
                'path': f'{dir}/{f}',
                'model': model_file[0],
                'date': model_file[1],
                'accuracy': model_file[2]
            }
            # add dict to array
            files.append(d)
    # array of dict can be used for pandas dataframe
    df_files = pd.DataFrame(files)
    df_files.sort_values(by=['date'], ascending=False, inplace=True)
    model_path = df_files['path'].iloc[0]
    return model_path