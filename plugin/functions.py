# set path to 1 folder up
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import Config
from SQL import functions as sqlf
from SQL import players, reports

def custom_hiscore(detection):
    # input validation
    bad_name = False
    detection['reporter'], bad_name = sqlf.name_check(detection['reporter'])
    detection['reported'], bad_name = sqlf.name_check(detection['reported'])

    if bad_name:
        Config.debug(f"bad name: reporter: {detection['reporter']} reported: {detection['reported']}")
        del detection
        return

    # get reporter & reported
    reporter = players.get_player(detection['reporter'])
    reported = players.get_player(detection['reported'])

    # if reporter or reported is None (=player does not exist), create player
    if reporter is None:
        reporter = players.insert_player(detection['reporter'])

    if reported is None:
        reported = players.insert_player(detection['reported'])

    # change in detection
    detection['reported'] = int(reported.id)
    detection['reporter'] = int(reporter.id)

    # insert into reports
    reports.insert_report(detection)
    del detection, reporter, reported
    return


def insync_detect(detections, manual_detect):
    for idx, detection in enumerate(detections):
        detection['manual_detect'] = manual_detect
        custom_hiscore(detection)
        if idx % 500 == 0 and idx != 0:
            Config.debug(f'      Completed {idx}/{len(detections)}')

    Config.debug(f'      Done: Completed {idx} detections')
    del idx, detection, detections, manual_detect
    return