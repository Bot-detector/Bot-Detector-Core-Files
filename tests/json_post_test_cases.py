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
                    ), # correct
                    (
                    {
                        "player_name": 8, # invalid type
                        "vote": 1,
                        "prediction": "Real_Player",
                        "confidence": 1,
                        "subject_id": 1,
                        "feedback_text": "He's a real player",
                        "proposed_label": "Real_Player"
                    }, 500
                    ), # invalid - incorrect type for player name, should be str is typed as int
                    (
                    {
                        "player_name": 'Ferrariic', # invalid type
                        "vote": 1,
                        "feedback_text": "He's a real player",
                        "proposed_label": "Real_Player"
                    }, 422
                    ), # invalid - missing non-default fields
                    (
                    {
                        "player_name": "Ferrariic", # invalid type
                        "vote": 1,
                        "prediction": "Real_Player",
                        "confidence": 10000000, # invalid range for confidence
                        "subject_id": 1,
                        "feedback_text": "He's a real player",
                        "proposed_label": "Real_Player"
                    }, 422 
                    ), # invalid - confidence range
                )

'''hiscore posts'''
post_hiscore_test_case = (
                    (
                    {
                      "player_id": 8,
                      "total": 100,
                      "Attack": 0,
                      "Defence": 0,
                      "Strength": 0,
                      "Hitpoints": 0,
                      "Ranged": 0,
                      "Prayer": 0,
                      "Magic": 0,
                      "Cooking": 0,
                      "Woodcutting": 0,
                      "Fletching": 0,
                      "Fishing": 0,
                      "Firemaking": 0,
                      "Crafting": 0,
                      "Smithing": 0,
                      "Mining": 0,
                      "Herblore": 0,
                      "Agility": 0,
                      "Thieving": 0,
                      "Slayer": 0,
                      "Farming": 0,
                      "Runecraft": 0,
                      "Hunter": 0,
                      "Construction": 0,
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
                    }, 201
                    ), # correct
                    (
                    {
                      "player_id": 'ferrariic',
                      "total": 100,
                      "Attack": 0,
                      "Defence": 0,
                      "Strength": 0,
                      "Hitpoints": 0,
                      "Ranged": 0,
                      "Prayer": 0,
                      "Magic": 0,
                      "Cooking": 0,
                      "Woodcutting": 0,
                      "Fletching": 0,
                      "Fishing": 0,
                      "Firemaking": 0,
                      "Crafting": 0,
                      "Smithing": 0,
                      "Mining": 0,
                      "Herblore": 0,
                      "Agility": 0,
                      "Thieving": 0,
                      "Slayer": 0,
                      "Farming": 0,
                      "Runecraft": 0,
                      "Hunter": 0,
                      "Construction": 0,
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
                    }, 500
                    ), # invalid - incorrect type for player id, should be int is typed as str
                    (
                    {
                      "player_id": 8,
                      "total": 100,
                      "zulrah": 0
                    }, 422
                    ), # invalid - missing non-default fields
                    (
                    {
                      "player_id": 8,
                      "total": -100000,
                      "Attack": -100000,
                      "Defence": -100000,
                      "Strength": -100000,
                      "Hitpoints": -100000,
                      "Ranged": -100000,
                      "Prayer": -100000,
                      "Magic": -100000,
                      "Cooking": -100000,
                      "Woodcutting": -100000,
                      "Fletching": -100000,
                      "Fishing": -100000,
                      "Firemaking": -100000,
                      "Crafting": -100000,
                      "Smithing": -100000,
                      "Mining": -100000,
                      "Herblore": -100000,
                      "Agility": -100000,
                      "Thieving": -100000,
                      "Slayer": -100000,
                      "Farming": -100000,
                      "Runecraft": -100000,
                      "Hunter": -100000,
                      "Construction": -100000,
                      "league": -100000,
                      "bounty_hunter_hunter": -100000,
                      "bounty_hunter_rogue": -100000,
                      "cs_all": -100000,
                      "cs_beginner": -100000,
                      "cs_easy": -100000,
                      "cs_medium": -100000,
                      "cs_hard": -100000,
                      "cs_elite": -100000,
                      "cs_master": -100000,
                      "lms_rank": -100000,
                      "soul_wars_zeal": -100000,
                      "abyssal_sire": -100000,
                      "alchemical_hydra": -100000,
                      "barrows_chests": -100000,
                      "bryophyta": -100000,
                      "callisto": -100000,
                      "cerberus": -100000,
                      "chambers_of_xeric": -100000,
                      "chambers_of_xeric_challenge_mode": -100000,
                      "chaos_elemental": -100000,
                      "chaos_fanatic": -100000,
                      "commander_zilyana": -100000,
                      "corporeal_beast": -100000,
                      "crazy_archaeologist": -100000,
                      "dagannoth_prime": -100000,
                      "dagannoth_rex": -100000,
                      "dagannoth_supreme": -100000,
                      "deranged_archaeologist": -100000,
                      "general_graardor": -100000,
                      "giant_mole": -100000,
                      "grotesque_guardians": -100000,
                      "hespori": -100000,
                      "kalphite_queen": -100000,
                      "king_black_dragon": -100000,
                      "kraken": -100000,
                      "kreearra": -100000,
                      "kril_tsutsaroth": -100000,
                      "mimic": -100000,
                      "nightmare": -100000,
                      "obor": -100000,
                      "phosanis_nightmare": -100000,
                      "sarachnis": -100000,
                      "scorpia": -100000,
                      "skotizo": -100000,
                      "tempoross": -100000,
                      "the_gauntlet": -100000,
                      "the_corrupted_gauntlet": -100000,
                      "theatre_of_blood":-100000,
                      "theatre_of_blood_hard": -100000,
                      "thermonuclear_smoke_devil": -100000,
                      "tzkal_zuk": -100000,
                      "tztok_jad": -100000,
                      "venenatis": -100000,
                      "vetion": -100000,
                      "vorkath": -100000,
                      "wintertodt": -100000,
                      "zalcano": -100000,
                      "zulrah": -100000
                    }, 500
                    ), # invalid - data ranges
                )
'''label posts'''
post_label_test_case = (
                    (
                    {
                        "label_name": "test_label"
                    }, 200
                    ), # correct
                    (
                    {
                        "label_name": 5403
                    }, 200
                    ), # invalid - incorrect type for player name, should be str is typed as int - rectify this with 400
                    (
                    {
                        "idk": "test_label"
                    }, 422
                    ), # invalid - wrong key
                )