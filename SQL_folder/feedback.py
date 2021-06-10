# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# custom
import SQL.functions as functions

def insert_prediction_feedback(vote_info):
    sql = (
        '''
        insert ignore into PredictionsFeedback 
            (voter_id, prediction, confidence, vote, subject_id)
        values 
            (:voter_id, :prediction, :confidence, :vote, :subject_id);
        '''
    )
    functions.execute_sql(sql, param=vote_info, debug=False, has_return=False)