import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
import numpy as np
from joblib import dump, load
import concurrent.futures as cf

from sklearn.ensemble import VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.calibration import CalibratedClassifierCV

# custom imports
import SQL, Config
from scraper import hiscoreScraper as highscores
from Predictions import prediction_functions as pf
from Predictions import extra_data as ed


def create_model(train_x, train_y, test_x, test_y, lbls):
    # neigh = KNeighborsClassifier(n_neighbors=len(lbls), n_jobs=-1)
    # neigh = neigh.fit(train_x, train_y)

    # mlpc = MLPClassifier(max_iter=10000, random_state=7)
    # mlpc = mlpc.fit(train_x, train_y)

    # rfc = RandomForestClassifier(n_estimators=100, random_state=7, n_jobs=-1)
    # rfc = rfc.fit(train_x, train_y)

    # etc = ExtraTreesClassifier(n_estimators=100, random_state=7, n_jobs=-1)
    # etc = etc.fit(train_x, train_y)

    # sgdc = SGDClassifier(max_iter=1000, tol=1e-3, loss='modified_huber')
    # sgdc = sgdc.fit(train_x, train_y)

    # models = [neigh, mlpc, rfc, etc, sgdc]
    # scores = [round(m.score(test_x, test_y)*100,2) for m in models]
    # weights = [s**2 for s in scores]
    # estimators = [(m.__class__.__name__, m) for m in models]

    # _ = [Config.debug(f'Model: {m.__class__.__name__} Score: {s}') for m, s in zip(models,scores)]

    # vote = VotingClassifier(
    #     weights=weights,
    #     estimators=estimators, 
    #     voting='soft',
    #     n_jobs=-1
    #     )
    # return vote
    rfc = RandomForestClassifier(n_estimators=100, random_state=7, n_jobs=-1)
    rfc = rfc.fit(train_x, train_y)
    return rfc


def train_model(n_pca):
    
    df =            pf.get_highscores()
    df_players =    pf.get_players()
    df_labels =     pf.get_labels() 

    # pandas pipeline
    df_clean = (df
        .pipe(pf.start_pipeline)
        .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
        .pipe(pf.f_features,    ed.skills_list, ed.minigames_list)
        # .pipe(pf.filter_relevant_features, ed.skills_list)
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
    dump(value=pca_model, filename=f'Predictions/models/pca_{today}_{n_pca}.joblib')

    df_pca = df_preprocess # no pca
    Config.debug(f'pca shape: {df_pca.shape}')

    df_pca = df_pca.merge(df_players,   left_index=True,    right_index=True, how='inner')
    df_pca = df_pca.merge(df_labels,    left_on='label_id', right_index=True, how='left')

    lbls = [
        'Real_Player', 'Smithing_bot', 'Mining_bot', 
        'Magic_bot', 'PVM_Ranged_bot', 'Wintertodt_bot', 
        'Fletching_bot', 'PVM_Melee_bot', 'Herblore_bot',
        'Thieving_bot','Crafting_bot', 'PVM_Ranged_Magic_bot',
        'Hunter_bot','Runecrafting_bot','Fishing_bot','Agility_bot',
        'Cooking_bot', 'FarmBird_bot', 'mort_myre_fungus_bot',
        'Woodcutting_bot'
    ]

    Config.debug(f'labels: {len(lbls)}, {lbls}')

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

    model_name = 'vote'
    model = create_model(train_x, train_y, test_x, test_y, lbls)
    model = model.fit(train_x, train_y)

    # works on colab not on my pc: ValueError: Invalid prediction method: _predict_proba 
    # # https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html#sklearn.calibration.CalibratedClassifierCV
    # does not work in current version, issue created https://github.com/scikit-learn/scikit-learn/issues/20053
    # model = CalibratedClassifierCV(base_estimator=model, cv='prefit')
    # model = model.fit(test_x, test_y) # docu says to calibrate on test?

    # print model score
    model_score = round(model.score(test_x, test_y)*100,2)
    Config.debug(f'Score: {model_score}')

    # print more detailed model score
    Config.debug(classification_report(test_y, model.predict(test_x), target_names=lbls))

    # fit & save model on entire dataset
    model = model.fit(x, y)
    dump(value=model, filename=f'Predictions/models/model-{model_name}_{today}_{model_score}.joblib')
    return

    
def predict_model(player_name=None, start=0, amount=100_000):
    # load scaler, transformer, features, pca, labels & model
    try:
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
    except Exception as e:
        Config.debug(f'Error loading: {e}')
        prediction_data = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "Error: The machine is learning",
            "prediction_confidence": 0,
            "secondary_predictions": []
        }


        return prediction_data

    # if no player name is given, take all players
    # if a player name is given, check if we have a record for this player else scrape that player
    if player_name is None:
        Config.debug(f'get_hiscores: {start}, {amount}')

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

                columns = [c for c in df_resf.columns.tolist() if not(c in ['id','prediction'])]
                df_resf.loc[:, columns]= df_resf[columns].astype(float)/100
                print('from db')
                Config.debug('from db')

                return df_resf
            except Exception as e:
                df = SQL.get_highscores_data_oneplayer(player.id)
                print('hiscores')

                Config.debug('hiscores')

        df = pd.DataFrame(df)
        df_players = pf.get_players(players=pd.DataFrame([player]), with_id=True)

    try:
        df_clean = (df
            .pipe(pf.start_pipeline)
            .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
            .pipe(pf.f_features, ed.skills_list, ed.minigames_list)
            # .pipe(pf.filter_relevant_features, ed.skills_list, myfeatures=features)
            # after feature creation in testing
        )
        del df # free up memory
    except Exception as k:
        Config.debug(f'Error cleaning: {k}')

        prediction_data = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "Not In Our Database",
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
    except Exception as v:
        Config.debug(f'Error normalizing: {v}')

        prediction_data = {
            "player_id": -1,
            "player_name": player_name,
            "prediction_label": "Not In Our Database",
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
    Config.debug(os.listdir())
    
    # chunking data
    limit = 5_000
    end = False
    first_run = True
    loop = 0

    train_model(n_pca)

    # get predictions in chunks
    while not(end):
        start = loop * limit
        df = predict_model(player_name=None, start=start, amount=limit)
        Config.debug(f'data shape: {df.shape}')

        # parse predictions to int
        int_columns = [c for c in df.columns.tolist() if c not in ['id','prediction']]
        df[int_columns] = df[int_columns]*100
        df[int_columns] = df[int_columns].astype(float)

        # replace spaces in column names to _
        df.columns = [c.replace(' ','_') for c in df.columns.tolist()]

        # remove predictioin because this is text
        columns = df.columns.tolist()
        columns.remove('prediction')
        columns.remove('id')

        # if the first run then drop & create table
        if first_run:
            Config.debug('drop & create table')
            first_run = False

            table_name = 'Predictions'
            droptable = f'DROP TABLE IF EXISTS {table_name};'
            createtable = f'CREATE TABLE IF NOT EXISTS {table_name} (name varchar(12), prediction varchar(50), id INT, {" DEC(3,2), ".join(columns)} DEC(3,2));'
            indexname = 'ALTER TABLE playerdata.Predictions ADD UNIQUE name (name);'
            fk = 'ALTER TABLE `Predictions` ADD CONSTRAINT `FK_pred_player_id` FOREIGN KEY (`id`) REFERENCES `Players`(`id`) ON DELETE RESTRICT ON UPDATE RESTRICT;'

            SQL.execute_sql(droptable,      param=None, debug=False, has_return=False)
            SQL.execute_sql(createtable,    param=None, debug=False, has_return=False)
            SQL.execute_sql(indexname,      param=None, debug=False, has_return=False)
            SQL.execute_sql(fk,             param=None, debug=False, has_return=False)

        # add prediction back as first field
        ordered_columns = ['prediction'] + columns
        df = df[ordered_columns]
        df.reset_index(inplace=True)
        
        # insert rows into table
        data = df.to_dict('records')
        length = len(df)
        del df

        multi_thread(data)
        del data

        loop += 1

        if length < limit:
            end = True

    return


def insert_prediction(row):
    values = SQL.list_to_string([f':{column}' for column in list(row.keys())])
    sql_insert = f'insert ignore into Predictions values ({values});'
    SQL.execute_sql(sql_insert, param=row, debug=False, has_return=False)
    return


def multi_thread(data):
    Config.debug('start multithread')
    # create a list of tasks to multithread
    tasks = []
    for row in data:
        tasks.append(([row]))

    del data # memory optimalization

    # multithreaded executor
    with cf.ProcessPoolExecutor() as executor:
        # submit each task to be executed
        futures = {executor.submit(insert_prediction, task[0]): task[0] for task in tasks}

        del tasks # memory optimalization

        # get start time
        for future in cf.as_completed(futures):
            _ = futures[future]
            _ = future.result()

    del futures, future # memory optimalization
    return

if __name__ == '__main__':
    train_model(n_pca=50)
    # save_model(n_pca=30)
    df = predict_model(player_name='extreme4all') # player_name='extreme4all'
    print(df.head())
