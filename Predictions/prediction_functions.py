import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import datetime as dt
import numpy as np
import time
from joblib import dump, load

from sklearn.preprocessing import StandardScaler, RobustScaler, Normalizer
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA
# custom
import SQL

def logging(f):
    def wrapper(df, *args, **kwargs):
        start = dt.datetime.now()
        result = f(df, *args, **kwargs)
        end = dt.datetime.now()
        try:
            print(f'{f.__name__} took: {end - start} shape= {result.shape}')
        except:
            print(f'{f.__name__} took: {end - start}')
        return result
    return wrapper

def get_highscores():
    data = SQL.get_hiscores_of_interst()
    df_hiscore = pd.DataFrame(data)

    print(f'hiscore: {df_hiscore.shape}')
    return df_hiscore

def get_players(players=None, with_id=False):
    if players is None:
        data = SQL.get_players_of_interest()
        players = pd.DataFrame(data)

    df_players = players
    df_players.set_index('name', inplace=True)
    if with_id:
        df_players.drop(columns=['created_at','updated_at'], inplace=True)
    else:
        df_players.drop(columns=['created_at','updated_at','id'], inplace=True)

    df_players['label_id'] = df_players['label_id'].replace(37, 0) # pvm to unkown
    df_players['label_id'] = df_players['label_id'].replace(36, 0) # pvm to unkown
    df_players['label_id'] = df_players['label_id'].replace(18, 5) # mining to mining bot       #
    df_players['label_id'] = df_players['label_id'].replace(34, 5) # mining gf to mining bot    #
    df_players['label_id'] = df_players['label_id'].replace(29, 17) # alching gf to magic       #
    df_players['label_id'] = df_players['label_id'].replace(23, 17) # alching to magic          #
    df_players['label_id'] = df_players['label_id'].replace(33, 17) # magic gf to magic         #
    df_players['label_id'] = df_players['label_id'].replace(15, 16) # smithing gf to smithing   #
    df_players['label_id'] = df_players['label_id'].replace(28, 27) # zalcano gf to zalcano     #
    df_players['label_id'] = df_players['label_id'].replace(26, 5) # blastmine gf  to mining    #
    df_players['label_id'] = df_players['label_id'].replace(22, 5) # blast mine to mining       #
    df_players['label_id'] = df_players['label_id'].replace(31, 8) # herblore gf to herblore    #

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
def start_pipeline(df):
    return df.copy()

@logging
def clean_dataset(df, skills_list, minigames_list):
    # sort by timestamp, drop duplicates keep last
    df = df.sort_values('timestamp').drop_duplicates('Player_id',keep='last')

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
def f_features(df, skills_list):
    # save total column to variable
    # print(df.columns)
    total = df['total']

    # for each skill, calculate ratio
    for skill in skills_list:
        df[f'{skill}/total'] = df[skill] / total

    df['wintertodt_feature'] = (df['wintertodt']*19000-670*19000)/df['firemaking']
    df['wintertodt_feature'] = np.where(df['wintertodt_feature'] < 0, 0, df['wintertodt_feature'])
    # df['winterdtodt_flag'] = np.where(df['wintertodt']>670,1,0)

    zalcano_mining      = df['zalcano']*13500/15
    zalcano_smithing    = df['zalcano']*3000/15
    zalcano_rc          = df['zalcano']*1500/15

    df['zalcano_feature'] = (zalcano_mining/df['mining']*3 + 
                             zalcano_smithing/df['smithing']*2 + 
                             zalcano_rc/df['runecraft']*5)/10

    df['median_feature'] = df[skills_list].median(axis=1)
    df['mean_feature'] = df[skills_list].mean(axis=1)
    # replace infinities & nan
    df = df.replace([np.inf, -np.inf], 0) 
    df.fillna(0, inplace=True)

    return df

@logging
def filter_relevant_features(df, myfeatures=None):
    if myfeatures is not None:
        return df[myfeatures].copy()

    # all features
    features =  df.columns

    # take median of all columns
    bad_features = pd.DataFrame(df.median(), columns=['median'])
    
    # if a row has no data it returns -1
    # if the median of the dataset is below 0 then that feature is mostly empty
    mask = (bad_features['median'] < 1)
    bad_features = bad_features[mask].index

    # filter out bad features
    my_feature_fields = ['zalcano', 'wintertodt']
    features = [f for f in features if f not in bad_features]
    _ = [features.append(f) for f in my_feature_fields if f not in features]

    return df[features].copy()

@logging
def f_standardize(df, scaler=None):
    if scaler is None:
        print('new scaler')
        scaler = RobustScaler()
        scaler = scaler.fit(df)

        today = time.strftime('%Y-%m-%d')
        dump(value=scaler, filename=f'Predictions/models/scaler_{today}_100.joblib')
    
    X_scaled = scaler.transform(df) 
    return pd.DataFrame(X_scaled, columns=df.columns, index=df.index)

@logging
def f_normalize(df, transformer=None):
    if transformer is None:
        print('new normalizer')
        transformer = Normalizer()
        transformer = transformer.fit(df)

        today = time.strftime('%Y-%m-%d')
        dump(value=transformer, filename=f'Predictions/models/normalizer_{today}_100.joblib')

    X_normalized = transformer.transform(df)
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
    accuracy = df_files['accuracy'].iloc[0]
    return model_path, accuracy