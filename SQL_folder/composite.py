# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# custom
import SQL.functions as functions



def get_report_stats():
    sql = (
        '''
        SELECT
            sum(bans) bans,
            sum(false_reports) false_reports,
            sum(bans) + sum(false_reports) total_reports,
            sum(bans)/ (sum(bans) + sum(false_reports)) accuracy
        FROM (
            SELECT 
                confirmed_ban,
                sum(confirmed_ban) bans,
                sum(confirmed_player) false_reports
            FROM Players
            GROUP BY
                confirmed_ban
            ) a;
    ''')
    data = functions.execute_sql(sql, param=None, debug=False)
    return data

# TODO: use contributor


def get_contributions(contributor):
    sql = ('''
        SELECT 
            rptr.name reporter_name,
            rptd.name reported_name,
            rptd.confirmed_ban,
            rptd.possible_ban
        from Reports rpts
        inner join Players rptr on(rpts.reportingID = rptr.id)
        inner join Players rptd on(rpts.reportedID = rptd.id)
        WHERE 1=1
        	and rptr.name = :contributor
        ;
    ''')

    param = {"contributor": contributor}

    data = functions.execute_sql(sql=sql, param=param, debug=False)

    return data


# Number of times an account has been manually reported by our users.
def get_times_manually_reported(reportedName):

    sql = (
        '''
        SELECT 
            SUM(manual_detect) manual_reports
        from Reports rpts
        inner join Players rptd on(rpts.reportedID = rptd.id)
        WHERE manual_detect = 1
        	and rptd.name = :reportedName;
        '''
    )

    param = {'reportedName': reportedName}

    data = functions.execute_sql(sql, param=param, debug=False)
    return data


def get_region_report_stats():

    sql = (
        '''
        SELECT * FROM `reportedRegion` ORDER BY `reportedRegion`.`region_id` ASC;
        '''
    )

    data = functions.execute_sql(sql, param=None, debug=False)
    return data

def get_possible_ban():
    sql = 'Select * from Players where possible_ban = 1 and confirmed_ban = 0'
    data = functions.execute_sql(sql, param=None, debug=False)
    return data


def get_player_report_locations(players):
    sql = (
        '''
        SELECT distinct
            pl.name,
            pl.id,
            rin.region_name,
            rp.region_id,
            rp.x_coord,
            rp.y_coord,
            rp.timestamp
        FROM Reports rp
        INNER JOIN Players pl ON (rp.reportedID = pl.id)
        INNER JOIN regionIDNames rin ON (rp.region_id = rin.region_ID)
        where 1
            and pl.name in :players
        ORDER BY
            rp.timestamp DESC
        LIMIT 100000
        '''
    )

    param = {'players': players}

    data = functions.execute_sql(sql, param=param, debug=True)
    return data
    

def get_region_search(regionName):
    sql = "SELECT * FROM regionIDNames WHERE region_name LIKE :region;"

    param = {'region': f'%{regionName}%'}

    data = functions.execute_sql(sql, param=param, debug=True)
    return data

def get_report_data_heatmap(region_id):

    sql = ('''
    SELECT DISTINCT
        rpts2.*,
        rpts.x_coord,
        rpts.y_coord,
        rpts.region_id
    FROM Reports rpts
        INNER JOIN (
            SELECT 
                max(rp.id) id,
                pl.name,
                pl.confirmed_player,
                pl.possible_ban,
                pl.confirmed_ban
            FROM Players pl
            inner join Reports rp on (pl.id = rp.reportedID)
            WHERE 1
                and (pl.confirmed_ban = 1 or pl.possible_ban = 1 or pl.confirmed_ban = 0)
                and rp.region_id = :region_id
            GROUP BY
                pl.name,
                pl.confirmed_player,
                pl.confirmed_ban
        ) rpts2
    ON (rpts.id = rpts2.id)
    ''')

    param = {'region_id': region_id}

    data = functions.execute_sql(sql, param=param, debug=True)
    return data


def get_player_banned_bots(player_name):
    sql = (
        '''
        SELECT 
            pl1.name reporter,
            pl2.name reported,
            lbl.label,
            hdl.*
        FROM Reports rp
        INNER JOIN Players pl1 ON (rp.reportingID = pl1.id)
        INNER JOIN Players pl2 on (rp.reportedID = pl2.id) 
        INNER JOIN Labels lbl ON (pl2.label_id = lbl.id)
        INNER JOIN playerHiscoreDataLatest hdl on (pl2.id = hdl.Player_id)
        where 1=1
            and lower(pl1.name) = :player_name
            and pl2.confirmed_ban = 1
            and pl2.possible_ban = 1
        '''
    )

    param = {'player_name': player_name}

    data = functions.execute_sql(sql, param=param, debug=True)
    return data
  
def get_possible_ban_predicted():
    sql = 'SELECT * FROM playerPossibleBanPrediction;'
    data = functions.execute_sql(sql, param=None, debug=False)
    return data