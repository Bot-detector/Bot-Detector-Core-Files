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
from sklearn.ensemble import VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report

# custom imports
import SQL
from scraper import hiscoreScraper as highscores
from Predictions import prediction_functions as pf
from Predictions import extra_data as ed


def create_model(train_x, train_y, test_x, test_y, lbls):
    neigh = KNeighborsClassifier(n_neighbors=len(lbls), n_jobs=-1)
    neigh = neigh.fit(train_x, train_y)

    mlpc = MLPClassifier(max_iter=10000, random_state=7)
    mlpc = mlpc.fit(train_x, train_y)

    rfc = RandomForestClassifier(n_estimators=100, random_state=7, n_jobs=-1)
    rfc = rfc.fit(train_x, train_y)

    etc = ExtraTreesClassifier(n_estimators=100, random_state=7, n_jobs=-1)
    etc = etc.fit(train_x, train_y)

    sgdc = SGDClassifier(max_iter=1000, tol=1e-3, loss='modified_huber')
    sgdc = sgdc.fit(train_x, train_y)

    models = [neigh, mlpc, rfc, etc, sgdc]
    scores = [round(m.score(test_x, test_y)*100,2) for m in models]
    weights = [s**2 for s in scores]
    estimators = [(m.__class__.__name__, m) for m in models]

    _ = [print(f'Model: {m.__class__.__name__} Score: {s}') for m, s in zip(models,scores)]
    _ = [lg.debug(f'Model: {m.__class__.__name__} Score: {s}') for m, s in zip(models,scores)]

    vote = VotingClassifier(
        weights=weights,
        estimators=estimators, 
        voting='soft',
        n_jobs=-1
        )
    
    # vote = vote.fit(train_x, train_y)
    return vote


def train_model(n_pca):
    
    df =            pf.get_highscores()
    df_players =    pf.get_players()
    df_labels =     pf.get_labels() # TODO: only parent labels?

    # pandas pipeline
    df_clean = (df
        .pipe(pf.start_pipeline)
        .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
        .pipe(pf.f_features,    ed.skills_list, ed.minigames_list)
        .pipe(pf.filter_relevant_features, ed.skills_list)
    )
    df_preprocess = (df_clean
        .pipe(pf.start_pipeline)
        .pipe(pf.f_standardize)
        .pipe(pf.f_normalize)
    )


    today = time.strftime('%Y-%m-%d', time.gmtime())
    columns = df_preprocess.columns.tolist()
    dump(value=columns, filename=f'Predictions/models/features_{today}_100.joblib')
    

    df_pca, pca_model = pf.f_pca(df_preprocess, n_components=n_pca, pca=None)
    df_pca = df_preprocess
    dump(value=pca_model, filename=f'Predictions/models/pca_{today}_{n_pca}.joblib')
    print(f'pca shape: {df_pca.shape}')

    df_pca = df_pca.merge(df_players,   left_index=True,    right_index=True, how='inner')
    df_pca = df_pca.merge(df_labels,    left_on='label_id', right_index=True, how='left')
    

    # getting labels with more then 5 players
    # lbl_df = pd.DataFrame(df_pca[['label']].value_counts(), columns=['players'])
    # mask = (lbl_df['players'] > 50)
    # lbl_df = lbl_df[mask].copy()
    # lbl_df.reset_index(inplace=True)
    # lbls = lbl_df['label'].tolist()

    lbls= ['Real_Player', 'Smithing_bot', 'Mining_bot', 'Magic_bot', 'PVM_Ranged_bot', 'Wintertodt_bot', 'Fletching_bot', 'PVM_Melee_bot', 'Herblore_bot']
    print('labels: ', len(lbls), lbls)
    lg.debug('labels: ', len(lbls), lbls)

    # creating x, y data, with players that a label
    mask = ~(df_pca['label_id'] == 0) & (df_pca['label'].isin(lbls))
    df_labeled = df_pca[mask].copy()
    df_labeled.drop(columns=['confirmed_ban','confirmed_player','possible_ban','label_id'], inplace=True)
    x, y = df_labeled.iloc[:,:-1], df_labeled.iloc[:,-1]

    # save labels
    lbls = np.sort(y.unique())
    dump(value=lbls, filename=f'Predictions/models/labels_{today}_100.joblib')

    # train test split but make sure to have all the labels form y
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

    model_name = 'rfc'
    # model = RandomForestClassifier(n_estimators=100)
    model = create_model(train_x, train_y, test_x, test_y, lbls)
    model = model.fit(train_x, train_y)
    
    # print model score
    model_score = round(model.score(test_x, test_y)*100,2)
    print('Score: ',model_score)
    lg.debug(f'Score: {model_score}')

    # print more detailed model score
    print(classification_report(test_y, model.predict(test_x), target_names=lbls))
    lg.debug(classification_report(test_y, model.predict(test_x), target_names=lbls))

    # fit & save model on entire dataset
    model = model.fit(x, y)
    dump(value=model, filename=f'Predictions/models/model-{model_name}_{today}_{model_score}.joblib')


    
def predict_model(player_name=None, start=0, amount=100_000):
    # load scaler, transformer, features, pca, labels & model
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
        print(f'get_hiscores: {start}, {amount}')
        lg.debug(f'get_hiscores: {start}, {amount}')
        df = pf.get_highscores(ofinterest=False, start=start, amount=amount)
        ids = df['Player_id'].to_list()
        df_players = pf.get_players(with_id=True, ofinterest=False, ids=ids)
    else:
        player = SQL.get_player(player_name)

        if player is None:
            df = highscores.scrape_one(player_name)
            player = SQL.get_player(player_name)
        else:
            try:
                df_resf = SQL.get_prediction_player(player.id)
                df_resf = pd.DataFrame(df_resf)
                df_resf.set_index('name', inplace=True)
                df_resf.rename(columns={'Predicted_confidence': 'Predicted confidence'}, inplace=True)
                print('from db')
                lg.debug('from db')
                return df_resf
            except:
                df = SQL.get_highscores_data_oneplayer(player.id)
                print('hiscores')
                lg.debug('hiscores')

        df = pd.DataFrame(df)
        df_players = pf.get_players(players=pd.DataFrame([player]), with_id=True)

    try:
        df_clean = (df
            .pipe(pf.start_pipeline)
            .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
            .pipe(pf.f_features, ed.skills_list, ed.minigames_list)
            .pipe(pf.filter_relevant_features, ed.skills_list, myfeatures=features)
            # after feature creation in testing
        )
        del df # free up memory
    except KeyError as k:

        prediction_data = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "Stats Too Low",
            "prediction_confidence": 0,
            "secondary_predictions": []
        }

        return prediction_data
    try:
        df_preprocess = (df_clean
            .pipe(pf.start_pipeline)
            .pipe(pf.f_standardize, scaler=scaler)
            .pipe(pf.f_normalize, transformer=transformer)
        )
        del df_clean # free up memory
    except ValueError as v:
        prediction_data = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "Stats Too Low",
            "prediction_confidence": 0,
            "secondary_predictions": []
        }
        return prediction_data

    df_preprocess = df_preprocess[features].copy()

    df_pca, pca_model = pf.f_pca(df_preprocess, n_components=int(n_pca), pca=pca)
    df_pca = df_preprocess
    
    proba =         model.predict_proba(df_pca)
    df_proba_max =  proba.max(axis=1)
    pred =          model.predict(df_pca)

    df_gnb_proba_max =      pd.DataFrame(df_proba_max,  index=df_pca.index, columns=['Predicted confidence'])
    df_gnb_predictions =    pd.DataFrame(pred,          index=df_pca.index, columns=['prediction'])
    df_gnb_proba =          pd.DataFrame(proba,         index=df_pca.index, columns=labels).round(4)

    df_resf = df_players[['id']]

    df_resf = df_resf.merge(df_gnb_predictions, left_index=True, right_index=True, suffixes=('', '_prediction'),how='inner')
    df_resf = df_resf.merge(df_gnb_proba_max,   left_index=True, right_index=True, how='inner')
    df_resf = df_resf.merge(df_gnb_proba,       left_index=True, right_index=True, suffixes=('', '_probability'), how='inner')
    return df_resf


def save_model(n_pca=50):
    print(os.listdir())
    lg.debug(os.listdir())
    
    # chunking data
    limit = 10_000
    end = False
    first_run = True
    loop = 0
    train_model(n_pca)
    while not(end):
        # get predictions in chunks
        start = loop * limit
        df = predict_model(player_name=None, start=start, amount=limit)
        lg.debug(f'data shape: {df.shape}')
        # parse data to format int
        int_columns = [c for c in df.columns.tolist() if c not in ['id','prediction']]
        df[int_columns] = df[int_columns]*100
        df[int_columns] = df[int_columns].astype(int)
        df.columns = [c.replace(' ','_') for c in df.columns.tolist()]

        columns = df.columns.tolist()
        columns.remove('prediction')
        # if the first run then drop & create table
        if first_run:
            print('drop & create table')
            lg.debug('drop & create table')
            first_run = False

            table_name = 'Predictions'
            droptable = f'DROP TABLE IF EXISTS {table_name};'
            createtable = f'CREATE TABLE IF NOT EXISTS {table_name} (name varchar(12), prediction text, {" INT, ".join(columns)} INT);'
            indexname = 'ALTER TABLE playerdata.Predictions ADD UNIQUE name (name);'
            fk = 'ALTER TABLE `Predictions` ADD CONSTRAINT `FK_pred_player_id` FOREIGN KEY (`id`) REFERENCES `Players`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;'
            created = 'ALTER TABLE `Predictions` ADD `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP FIRST;'

            SQL.execute_sql(droptable,      param=None, debug=False, has_return=False)
            SQL.execute_sql(createtable,    param=None, debug=False, has_return=False)
            SQL.execute_sql(indexname,      param=None, debug=False, has_return=False)
            SQL.execute_sql(fk,             param=None, debug=False, has_return=False)
            # SQL.execute_sql(created,        param=None, debug=False, has_return=False)

        # because prediction must be first column
        ordered_columns = ['prediction'] + columns
        df = df[ordered_columns]
        df.reset_index(inplace=True)
        
        # insert rows into table
        data = df.to_dict('records')
        multi_thread(data)

        loop += 1
        if len(df) < limit:
            end = True


def insert_prediction(row):
    values = SQL.list_to_string([f':{column}' for column in list(row.keys())])
    sql_insert = f'insert ignore into Predictions values ({values});'
    SQL.execute_sql(sql_insert, param=row, debug=False, has_return=False)


def multi_thread(data):
    print('start multithread')
    lg.debug('start multithread')
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
    # train_model(n_pca=50)
    # save_model(n_pca=30)
    df = predict_model(player_name='extreme4all') # player_name='extreme4all'
    print(df.head())
