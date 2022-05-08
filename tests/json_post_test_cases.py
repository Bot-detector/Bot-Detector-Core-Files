import time

'''feedback posts'''
post_feedback_test_case = (
    (
        {
            "player_name": "Ferrariic",
            "vote": 1,
            "prediction": "Real_Player",
            "confidence": 1,
            "subject_id": 1,
            "feedback_text": "He's a real player",
            "proposed_label": "Real_Player"
        }, 201
    ),  # correct
    (
        {
            "player_name": 'Ferrariic',  # invalid type
            "vote": 1,
            "feedback_text": "He's a real player",
            "proposed_label": "Real_Player"
        }, 422
    ),  # invalid - missing non-default fields
    (
        {
            "player_name": "Ferrariic",  # invalid type
            "vote": 1,
            "prediction": "Real_Player",
            "confidence": 10000000,  # invalid range for confidence
            "subject_id": 1,
            "feedback_text": "He's a real player",
            "proposed_label": "Real_Player"
        }, 201
    ),  # invalid - confidence range
)
'''hiscore posts'''
post_hiscore_test_case = (
    (
        {
            "Player_id": 8,
            "total": 100,
            "attack": 0,
            "defence": 0,
            "strength": 0,
            "hitpoints": 0,
            "ranged": 0,
            "prayer": 0,
            "magic": 0,
            "cooking": 0,
            "woodcutting": 0,
            "fletching": 0,
            "fishing": 0,
            "firemaking": 0,
            "crafting": 0,
            "smithing": 0,
            "mining": 0,
            "herblore": 0,
            "agility": 0,
            "thieving": 0,
            "slayer": 0,
            "farming": 0,
            "runecraft": 0,
            "hunter": 0,
            "construction": 0,
            "league": 0,
            "bounty_hunter_hunter": 0,
            "bounty_hunter_rogue": 0,
            "cs_all": 0,
            "cs_beginner": 0,
            "cs_easy": 0,
            "cs_medium": 0,
            "cs_hard": 0,
            "cs_elite": 0,
            "cs_master": 0,
            "lms_rank": 0,
            "soul_wars_zeal": 0,
            "abyssal_sire": 0,
            "alchemical_hydra": 0,
            "barrows_chests": 0,
            "bryophyta": 0,
            "callisto": 0,
            "cerberus": 0,
            "chambers_of_xeric": 0,
            "chambers_of_xeric_challenge_mode": 0,
            "chaos_elemental": 0,
            "chaos_fanatic": 0,
            "commander_zilyana": 0,
            "corporeal_beast": 0,
            "crazy_archaeologist": 0,
            "dagannoth_prime": 0,
            "dagannoth_rex": 0,
            "dagannoth_supreme": 0,
            "deranged_archaeologist": 0,
            "general_graardor": 0,
            "giant_mole": 0,
            "grotesque_guardians": 0,
            "hespori": 0,
            "kalphite_queen": 0,
            "king_black_dragon": 0,
            "kraken": 0,
            "kreearra": 0,
            "kril_tsutsaroth": 0,
            "mimic": 0,
            "nightmare": 0,
            "nex": 0,
            "obor": 0,
            "phosanis_nightmare": 0,
            "sarachnis": 0,
            "scorpia": 0,
            "skotizo": 0,
            "tempoross": 0,
            "the_gauntlet": 0,
            "the_corrupted_gauntlet": 0,
            "theatre_of_blood": 0,
            "theatre_of_blood_hard": 0,
            "thermonuclear_smoke_devil": 0,
            "tzkal_zuk": 0,
            "tztok_jad": 0,
            "venenatis": 0,
            "vetion": 0,
            "vorkath": 0,
            "wintertodt": 0,
            "zalcano": 0,
            "zulrah": 0
        }, 200
    ),  # correct
    (
        {
            "Player_id": 'Ferrariic',
            "total": 100,
            "attack": 0,
            "defence": 0,
            "strength": 0,
            "hitpoints": 0,
            "ranged": 0,
            "prayer": 0,
            "magic": 0,
            "cooking": 0,
            "woodcutting": 0,
            "fletching": 0,
            "fishing": 0,
            "firemaking": 0,
            "crafting": 0,
            "smithing": 0,
            "mining": 0,
            "herblore": 0,
            "agility": 0,
            "thieving": 0,
            "slayer": 0,
            "farming": 0,
            "runecraft": 0,
            "hunter": 0,
            "construction": 0,
            "league": 0,
            "bounty_hunter_hunter": 0,
            "bounty_hunter_rogue": 0,
            "cs_all": 0,
            "cs_beginner": 0,
            "cs_easy": 0,
            "cs_medium": 0,
            "cs_hard": 0,
            "cs_elite": 0,
            "cs_master": 0,
            "lms_rank": 0,
            "soul_wars_zeal": 0,
            "abyssal_sire": 0,
            "alchemical_hydra": 0,
            "barrows_chests": 0,
            "bryophyta": 0,
            "callisto": 0,
            "cerberus": 0,
            "chambers_of_xeric": 0,
            "chambers_of_xeric_challenge_mode": 0,
            "chaos_elemental": 0,
            "chaos_fanatic": 0,
            "commander_zilyana": 0,
            "corporeal_beast": 0,
            "crazy_archaeologist": 0,
            "dagannoth_prime": 0,
            "dagannoth_rex": 0,
            "dagannoth_supreme": 0,
            "deranged_archaeologist": 0,
            "general_graardor": 0,
            "giant_mole": 0,
            "grotesque_guardians": 0,
            "hespori": 0,
            "kalphite_queen": 0,
            "king_black_dragon": 0,
            "kraken": 0,
            "kreearra": 0,
            "kril_tsutsaroth": 0,
            "mimic": 0,
            "nightmare": 0,
            "nex": 0,
            "obor": 0,
            "phosanis_nightmare": 0,
            "sarachnis": 0,
            "scorpia": 0,
            "skotizo": 0,
            "tempoross": 0,
            "the_gauntlet": 0,
            "the_corrupted_gauntlet": 0,
            "theatre_of_blood": 0,
            "theatre_of_blood_hard": 0,
            "thermonuclear_smoke_devil": 0,
            "tzkal_zuk": 0,
            "tztok_jad": 0,
            "venenatis": 0,
            "vetion": 0,
            "vorkath": 0,
            "wintertodt": 0,
            "zalcano": 0,
            "zulrah": 0
        }, 422
    ),  # invalid - incorrect type for player id, should be int is typed as str
    (
        {
            "Player_id": 8,
            "total": 100,
            "zulrah": 0
        }, 422
    ),  # invalid - missing non-default fields
    (
        {
            "Player_id": 8,
            "total": -10000,
            "attack": -10000,
            "defence": -10000,
            "strength": -10000,
            "hitpoints": -10000,
            "ranged": -10000,
            "prayer": -10000,
            "magic": -10000,
            "cooking": -10000,
            "woodcutting": -10000,
            "fletching": -10000,
            "fishing": -10000,
            "firemaking": -10000,
            "crafting": -10000,
            "smithing": -10000,
            "mining": -10000,
            "herblore": -10000,
            "agility": -10000,
            "thieving": -10000,
            "slayer": -10000,
            "farming": -10000,
            "runecraft": -10000,
            "hunter": -10000,
            "construction": -10000,
            "league": -10000,
            "bounty_hunter_hunter": -10000,
            "bounty_hunter_rogue": -10000,
            "cs_all": -10000,
            "cs_beginner": -10000,
            "cs_easy": -10000,
            "cs_medium": -10000,
            "cs_hard": -10000,
            "cs_elite": -10000,
            "cs_master": -10000,
            "lms_rank": -10000,
            "soul_wars_zeal": -10000,
            "abyssal_sire": -10000,
            "alchemical_hydra": -10000,
            "barrows_chests": -10000,
            "bryophyta": -10000,
            "callisto": -10000,
            "cerberus": -10000,
            "chambers_of_xeric": -10000,
            "chambers_of_xeric_challenge_mode": -10000,
            "chaos_elemental": -10000,
            "chaos_fanatic": -10000,
            "commander_zilyana": -10000,
            "corporeal_beast": -10000,
            "crazy_archaeologist": -10000,
            "dagannoth_prime": -10000,
            "dagannoth_rex": -10000,
            "dagannoth_supreme": -10000,
            "deranged_archaeologist": -10000,
            "general_graardor": -10000,
            "giant_mole": -10000,
            "grotesque_guardians": -10000,
            "hespori": -10000,
            "kalphite_queen": -10000,
            "king_black_dragon": -10000,
            "kraken": -10000,
            "kreearra": -10000,
            "kril_tsutsaroth": -10000,
            "mimic": -10000,
            "nightmare": -10000,
            "nex": -10000,
            "obor": -10000,
            "phosanis_nightmare": -10000,
            "sarachnis": -10000,
            "scorpia": -10000,
            "skotizo": -10000,
            "tempoross": -10000,
            "the_gauntlet": -10000,
            "the_corrupted_gauntlet": -10000,
            "theatre_of_blood": -10000,
            "theatre_of_blood_hard": -10000,
            "thermonuclear_smoke_devil": -10000,
            "tzkal_zuk": -10000,
            "tztok_jad": -10000,
            "venenatis": -10000,
            "vetion": -10000,
            "vorkath": -10000,
            "wintertodt": -10000,
            "zalcano": -10000,
            "zulrah": -10000
        }, 200
    ),  # invalid - data ranges
)
'''label posts'''
post_label_test_case = (
    (
        {
            "label_name": "test_label"
        }, 200
    ),  # correct
    (
        {
            "label_name": 5403
        }, 200
    ),  # invalid - incorrect type for player name, should be str is typed as int - rectify this with 400
    (
        {
            "idk": "test_label"
        }, 422
    ),  # invalid - wrong key
)
'''prediction posts'''

post_prediction_test_case = (
    (
        {
            "name": "Ferrariic",
            "Prediction": "Real_Player",
            "id": 0,
            "created": "2021-01-01 00:00:00",
            "Predicted_confidence": 0,
            "Real_Player": 100,
            "PVM_Melee_bot": 0,
            "Smithing_bot": 0,
            "Magic_bot": 0,
            "Fishing_bot": 0,
            "Mining_bot": 0,
            "Crafting_bot": 0,
            "PVM_Ranged_Magic_bot": 0,
            "PVM_Ranged_bot": 0,
            "Hunter_bot": 0,
            "Fletching_bot": 0,
            "Clue_Scroll_bot": 0,
            "LMS_bot": 0,
            "Agility_bot": 0,
            "Wintertodt_bot": 0,
            "Runecrafting_bot": 0,
            "Zalcano_bot": 0,
            "Woodcutting_bot": 0,
            "Thieving_bot": 0,
            "Soul_Wars_bot": 0,
            "Cooking_bot": 0,
            "Vorkath_bot": 0,
            "Barrows_bot": 0,
            "Herblore_bot": 0,
            "Zulrah_bot": 0
        }, 307
    ),  # correct
    (
        {
            "name": 8,
            "Prediction": "Real_Player",
            "id": 0,
            "created": "2021-01-01 00:00:00",
            "Predicted_confidence": 0,
            "Real_Player": 100,
            "PVM_Melee_bot": 0,
            "Smithing_bot": 0,
            "Magic_bot": 0,
            "Fishing_bot": 0,
            "Mining_bot": 0,
            "Crafting_bot": 0,
            "PVM_Ranged_Magic_bot": 0,
            "PVM_Ranged_bot": 0,
            "Hunter_bot": 0,
            "Fletching_bot": 0,
            "Clue_Scroll_bot": 0,
            "LMS_bot": 0,
            "Agility_bot": 0,
            "Wintertodt_bot": 0,
            "Runecrafting_bot": 0,
            "Zalcano_bot": 0,
            "Woodcutting_bot": 0,
            "Thieving_bot": 0,
            "Soul_Wars_bot": 0,
            "Cooking_bot": 0,
            "Vorkath_bot": 0,
            "Barrows_bot": 0,
            "Herblore_bot": 0,
            "Zulrah_bot": 0
        }, 307
    ),  # invalid - incorrect type for player name, should be str is typed as int - rectify this with 400
    (
        {
            "name": "Ferrariic",
            "Prediction": 1,  # invalid
            "id": 0,
            "created": "2021-01-01 00:00:00",
            "Predicted_confidence": 0,
            "Real_Player": 100,
            "PVM_Melee_bot": 0,
            "Smithing_bot": 0,
            "Magic_bot": 0,
            "Fishing_bot": 0,
            "Mining_bot": 0,
            "Crafting_bot": 0,
            "PVM_Ranged_Magic_bot": 0,
            "PVM_Ranged_bot": 0,
            "Hunter_bot": 0,
            "Fletching_bot": 0,
            "Clue_Scroll_bot": 0,
            "LMS_bot": 0,
            "Agility_bot": 0,
            "Wintertodt_bot": 0,
            "Runecrafting_bot": 0,
            "Zalcano_bot": 0,
            "Woodcutting_bot": 0,
            "Thieving_bot": 0,
            "Soul_Wars_bot": 0,
            "Cooking_bot": 0,
            "Vorkath_bot": 0,
            "Barrows_bot": 0,
            "Herblore_bot": 0,
            "Zulrah_bot": 0
        }, 307
    ),  # invalid - wrong prediction type, should be str instead of int
    (
        {
            "name": "Ferrariic",
            "Prediction": "Real_Player",  # invalid
            "id": 0,
            "created": "0000-00-00 00:00:00",  # incorrect date
            "Predicted_confidence": 0,
            "Real_Player": 100,
            "PVM_Melee_bot": 0,
            "Smithing_bot": 0,
            "Magic_bot": 0,
            "Fishing_bot": 0,
            "Mining_bot": 0,
            "Crafting_bot": 0,
            "PVM_Ranged_Magic_bot": 0,
            "PVM_Ranged_bot": 0,
            "Hunter_bot": 0,
            "Fletching_bot": 0,
            "Clue_Scroll_bot": 0,
            "LMS_bot": 0,
            "Agility_bot": 0,
            "Wintertodt_bot": 0,
            "Runecrafting_bot": 0,
            "Zalcano_bot": 0,
            "Woodcutting_bot": 0,
            "Thieving_bot": 0,
            "Soul_Wars_bot": 0,
            "Cooking_bot": 0,
            "Vorkath_bot": 0,
            "Barrows_bot": 0,
            "Herblore_bot": 0,
            "Zulrah_bot": 0
        }, 307
    ),  # invalid - wrong prediction type, should be str instead of int
    (
        {
            "name": "Ferrariic",
            "Prediction": "Real_Player",  # invalid
            "id": 0,
            "created": "2021-01-01 00:00:00",
            "Predicted_confidence": 0,
            "Real_Player": -1,  # invalid range for prediction value
            "PVM_Melee_bot": 0,
            "Smithing_bot": 0,
            "Magic_bot": 0,
            "Fishing_bot": 0,
            "Mining_bot": 0,
            "Crafting_bot": 0,
            "PVM_Ranged_Magic_bot": 0,
            "PVM_Ranged_bot": 0,
            "Hunter_bot": 0,
            "Fletching_bot": 0,
            "Clue_Scroll_bot": 0,
            "LMS_bot": 0,
            "Agility_bot": 0,
            "Wintertodt_bot": 0,
            "Runecrafting_bot": 0,
            "Zalcano_bot": 0,
            "Woodcutting_bot": 0,
            "Thieving_bot": 0,
            "Soul_Wars_bot": 0,
            "Cooking_bot": 0,
            "Vorkath_bot": 0,
            "Barrows_bot": 0,
            "Herblore_bot": 0,
            "Zulrah_bot": 0
        }, 307
    ),  # invalid real_player prediction range
    (
        {
            "name": "Ferrariic",
            "Prediction": "Real_Player",
            "id": 0,
            "created": "2021-01-01 00:00:00",
            "Predicted_confidence": 0,
            "Zulrah_bot": 0
        }, 307
    ),  # invalid - missing keys
)

