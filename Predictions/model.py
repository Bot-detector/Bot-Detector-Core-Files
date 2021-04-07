import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import dump, load
import time
import concurrent.futures as cf
import logging as lg
# custom imports
import SQL
# import highscores
from scraper import hiscoreScraper as highscores
from Predictions import prediction_functions as pf
from Predictions import extra_data as ed

def train_model(n_pca):
    
    df =            pf.get_highscores()
    df_players =    pf.get_players()
    df_labels =     pf.get_labels() # TODO: only parent labels?

    # pandas pipeline
    df_clean = (df
        .pipe(pf.start_pipeline)
        .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
        .pipe(pf.filter_relevant_features)
        .pipe(pf.f_features, ed.skills_list)
    )
    df_preprocess = (df_clean
        .pipe(pf.start_pipeline)
        .pipe(pf.f_standardize)
        .pipe(pf.f_normalize)
    )



    today = time.strftime('%Y-%m-%d', time.gmtime())
    columns = df_preprocess.columns.tolist()
    dump(value=columns, filename=f'Predictions/models/features_{today}_100.joblib')
    

    #TODO: save pca to file
    df_pca, pca_model = pf.f_pca(df_preprocess, n_components=n_pca, pca=None)
    dump(value=pca_model, filename=f'Predictions/models/pca_{today}_{n_pca}.joblib')
    print(f'pca shape: {df_pca.shape}')

    df_pca = df_pca.merge(df_players,   left_index=True,    right_index=True, how='inner')
    df_pca = df_pca.merge(df_labels,    left_on='label_id', right_index=True, how='left')
    

    # getting labels with more then 5 players
    lbl_df = pd.DataFrame(df_pca[['label']].value_counts(), columns=['players'])
    mask = (lbl_df['players'] > 50)
    lbl_df = lbl_df[mask].copy()
    lbl_df.reset_index(inplace=True)
    lbls = lbl_df['label'].tolist()
    print('labels: ', len(lbls), lbls)

    # creating x, y data, with players that a label
    mask = ~(df_pca['label_id'] == 0) & (df_pca['label'].isin(lbls))
    df_labeled = df_pca[mask].copy()
    df_labeled.drop(columns=['confirmed_ban','confirmed_player','possible_ban','label_id'], inplace=True)
    x, y = df_labeled.iloc[:,:-1], df_labeled.iloc[:,-1]


    lbls = np.sort(y.unique())
    dump(value=lbls, filename=f'Predictions/models/labels_{today}_100.joblib')

    # train test split but make sure to have all the labels form y
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

    # model = GaussianNB()
    model_name = 'rfc'
    model = RandomForestClassifier(n_estimators=100)
    model = model.fit(train_x, train_y)
    
    model_score = round(model.score(test_x, test_y)*100,2)
    model = model.fit(x, y)

    dump(value=model, filename=f'Predictions/models/model-{model_name}_{today}_{model_score}.joblib')
    print('Score: ',model_score)
    lg.debug(f'Score: {model_score}')

    

def predict_model(player_name=None):
    scaler, _ = pf.best_file_path(startwith='scaler', dir='Predictions/models')
    scaler = load(scaler)

    transformer, _ = pf.best_file_path(startwith='normalizer', dir='Predictions/models')
    transformer = load(transformer)

    features, _ = pf.best_file_path(startwith='features', dir='Predictions/models')
    features = load(features)

    pca, n_pca = pf.best_file_path(startwith='pca', dir='Predictions/models')
    pca = load(pca)

    labels, _ = pf.best_file_path(startwith='labels', dir='Predictions/models')
    labels = load(labels)

    model, _ = pf.best_file_path(startwith='model', dir='Predictions/models')
    model = load(model)

    # if no player name is given, take all players
    # if a player name is given, check if we have a record for this player else scrape that player
    if player_name is None:
        df = pf.get_highscores()
        df_players =  pf.get_players(with_id=True)
    else:
        player = SQL.get_player(player_name)

        if player is None:
            df = highscores.scrape_one(player_name)
            player = SQL.get_player(player_name)
        else:
            df = SQL.get_highscores_data_oneplayer(player.id)

        df = pd.DataFrame(df)
        df_players = pf.get_players(players=pd.DataFrame([player]), with_id=True)
        
    
    df_clean = (df
        .pipe(pf.start_pipeline)
        .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
        .pipe(pf.f_features, ed.skills_list)
        .pipe(pf.filter_relevant_features, myfeatures=features) # after feature creation in testing
    )
    df_preprocess = (df_clean
        .pipe(pf.start_pipeline)
        .pipe(pf.f_standardize, scaler=scaler)
        .pipe(pf.f_normalize, transformer=transformer)
    )

    df_preprocess = df_preprocess[features].copy()

    df_pca, pca_model = pf.f_pca(df_preprocess, n_components=int(n_pca), pca=pca)

    proba = model.predict_proba(df_pca)
    df_proba_max = proba.max(axis=1)
    pred = model.predict(df_pca)

    df_gnb_proba_max =      pd.DataFrame(df_proba_max,  index=df_pca.index, columns=['Predicted confidence'])
    df_gnb_predictions =    pd.DataFrame(pred,          index=df_pca.index, columns=['prediction'])
    df_gnb_proba =          pd.DataFrame(proba,         index=df_pca.index, columns=labels).round(4)

    df_resf = df_players[['id']]
    df_resf = df_resf.merge(df_gnb_predictions, left_index=True, right_index=True, suffixes=('','_prediction'), how='inner')
    df_resf = df_resf.merge(df_gnb_proba_max,   left_index=True, right_index=True, how='inner')
    df_resf = df_resf.merge(df_gnb_proba,       left_index=True, right_index=True, suffixes=('','_probability'), how='inner')
    # df_resf = df_resf.merge(df_clean,           left_index=True, right_index=True, how='left')
    return df_resf

def save_model(n_pca=50):
    print(os.listdir())
    lg.debug(os.listdir())
    
    train_model(n_pca=50)
    df = predict_model(player_name=None)

    # parse data to format int
    int_columns = [c for c in df.columns.tolist() if c not in ['id','prediction']]
    df[int_columns] = df[int_columns]*100
    df[int_columns] = df[int_columns].astype(int)
    df.columns = [c.replace(' ','_') for c in df.columns.tolist()]
    print(df.head())

    # create table
    columns = df.columns.tolist()
    columns.remove('prediction')

    table_name = 'Predictions'
    droptable = f'DROP TABLE IF EXISTS {table_name};'
    createtable = f'CREATE TABLE IF NOT EXISTS {table_name} (name varchar(12), prediction text, {" INT, ".join(columns)} INT);'
    indexname = 'ALTER TABLE playerdata.Predictions ADD UNIQUE name (name);'

    SQL.execute_sql(droptable,      param=None, debug=False, has_return=False)
    SQL.execute_sql(createtable,    param=None, debug=False, has_return=False)
    SQL.execute_sql(indexname,      param=None, debug=False, has_return=False)

    #because prediction must be first column
    ordered_columns = ['prediction'] + columns
    df = df[ordered_columns]
    df.reset_index(inplace=True)
    
    # insert rowss
    data = df.to_dict('records')
    multi_thread(data)

def insert_prediction(row):
        values = SQL.list_to_string([f':{column}' for column in list(row.keys())])
        sql_insert = f'insert ignore into Predictions values ({values});'
        SQL.execute_sql(sql_insert,      param=row, debug=False, has_return=False)

def multi_thread(data):
    # create a list of tasks to multithread
    tasks = []
    for row in data:
        tasks.append(([row]))

    # multithreaded executor
    with cf.ProcessPoolExecutor() as executor:

        # submit each task to be executed
        futures = {executor.submit(insert_prediction, task[0]): task[0] for task in tasks} # get_data

        # get start time
        for future in cf.as_completed(futures):
            _ = futures[future]
            _ = future.result()

if __name__ == '__main__':
    # train_model(n_pca=35)
    save_model()
    # df = predict_model(player_name='extreme4all') # player_name='extreme4all'
