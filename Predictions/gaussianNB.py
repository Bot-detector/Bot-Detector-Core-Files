import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from joblib import dump, load
import time
# custom imports
import SQL
import highscores
from Predictions import prediction_functions as pf
from Predictions import extra_data as ed


def train_model():
    
    df =            pf.get_highscores()
    df_players =    pf.get_players()
    df_labels =     pf.get_labels()

    # pandas pipeline
    df_preprocess = (df
        .pipe(pf.start_pipeline)
        .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
        .pipe(pf.filter_relevant_features)
        .pipe(pf.features, ed.skills_list)
        .pipe(pf.f_standardize)
        .pipe(pf.f_normalize)
    )

    today = time.strftime('%Y-%m-%d', time.gmtime())
    columns = df_preprocess.columns.tolist()
    dump(value=columns, filename=f'Predictions/models/features_{today}_100.joblib')
    

    #TODO: save pca to file
    df_pca, pca_model = pf.f_pca(df_preprocess, n_components=20, pca=None)
    dump(value=pca_model, filename=f'Predictions/models/pca_{today}_100.joblib')

    df_pca = df_pca.merge(df_players, left_index=True, right_index=True, how='inner')
    df_pca = df_pca.merge(df_labels, left_on='label_id', right_index=True, how='left')


    # getting labels with more then 5 players
    lbl_df = pd.DataFrame(df_pca[['label']].value_counts(), columns=['players'])
    mask = (lbl_df['players'] > 5)
    lbl_df = lbl_df[mask].copy()
    lbl_df.reset_index(inplace=True)
    lbls = lbl_df['label'].tolist()


    # creating x, y data, with players that a label
    mask = ~(df_pca['label_id'] == 0) & (df_pca['label'].isin(lbls))
    df_labeled = df_pca[mask].copy()
    df_labeled.drop(columns=['confirmed_ban','confirmed_player','possible_ban','label_id'], inplace=True)
    x, y = df_labeled.iloc[:,:-1], df_labeled.iloc[:,-1]


    lbls = np.sort(y.unique())
    dump(value=lbls, filename=f'Predictions/models/labels_{today}_100.joblib')

    # train test split but make sure to have all the labels form y
    train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)

    # gaussian model
    gnb = GaussianNB()
    gnb.fit(train_x, train_y)
    model_score = round(gnb.score(test_x, test_y),4) *100
    dump(value=gnb, filename=f'Predictions/models/gnb_{today}_{model_score}.joblib')


def predict_model(player_name=None):
    features = pf.best_file_path(startwith='features', dir='Predictions/models')
    features = load(features)

    pca = pf.best_file_path(startwith='pca', dir='Predictions/models')
    pca = load(pca)

    labels = pf.best_file_path(startwith='labels', dir='Predictions/models')
    labels = load(labels)

    gnb = pf.best_file_path(startwith='gnb', dir='Predictions/models')
    gnb = load(gnb)

    if player_name is None:
        df = pf.get_highscores()
    else:
        player = SQL.get_player(player_name)

        if player is None:
            df = highscores.scrape_one(player_name)
        else:
            df = SQL.get_highscores_data_oneplayer(player.id)
        df = pd.DataFrame(df)
    
    df_preprocess = (df
        .pipe(pf.start_pipeline)
        .pipe(pf.clean_dataset, ed.skills_list, ed.minigames_list)
        #.pipe(pf.filter_relevant_features)
        .pipe(pf.features, ed.skills_list)
        .pipe(pf.f_standardize)
        .pipe(pf.f_normalize)
    )
    df_preprocess = df_preprocess[features].copy()
    df_pca, pca_model = pf.f_pca(df_preprocess, n_components=20, pca=pca)

    gnb_proba = gnb.predict_proba(df_pca)
    df_gnb_proba_max = gnb_proba.max(axis=1)
    gnb_pred = gnb.predict(df_pca)

    df_gnb_proba_max =      pd.DataFrame(df_gnb_proba_max,  index=df_pca.index, columns=['Predicted confidence'])
    df_gnb_predictions =    pd.DataFrame(gnb_pred,          index=df_pca.index, columns=['prediction'])
    df_gnb_proba =          pd.DataFrame(gnb_proba,         index=df_pca.index, columns=labels).round(4)

    result = df_gnb_predictions
    result = result.merge(df_gnb_proba_max, left_index=True, right_index=True)
    result = result.merge(df_gnb_proba, left_index=True, right_index=True)
    print(result.head())

    #TODO: wtie to database

if __name__ == '__main__':
    # train_model()
    predict_model(player_name='extreme4all')
