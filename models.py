# coding: utf-8
from sqlalchemy import BigInteger, Column, DECIMAL, Date, DateTime, Float, ForeignKey, Index, Integer, String, TIMESTAMP, Table, Text, text
from sqlalchemy.dialects.mysql import TEXT, TINYINT, TINYTEXT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class LabelJagex(Base):
    __tablename__ = 'LabelJagex'

    id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False)


class Label(Base):
    __tablename__ = 'Labels'

    id = Column(Integer, primary_key=True, unique=True)
    label = Column(VARCHAR(50), nullable=False)


class PlayerBotConfirmation(Base):
    __tablename__ = 'PlayerBotConfirmation'
    __table_args__ = (
        Index('Unique_player_label_bot', 'player_id', 'label_id', 'bot', unique=True),
    )

    id = Column(Integer, primary_key=True)
    ts = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    player_id = Column(Integer, nullable=False)
    label_id = Column(Integer, nullable=False)
    bot = Column(TINYINT(1), nullable=False)


class PlayersChange(Base):
    __tablename__ = 'PlayersChanges'

    id = Column(Integer, primary_key=True)
    ChangeDate = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    player_id = Column(Integer, nullable=False)
    name = Column(String(15), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
    possible_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_player = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    label_id = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    label_jagex = Column(Integer, nullable=False, server_default=text("'0'"))


t_ReportTabelStats = Table(
    'ReportTabelStats', metadata,
    Column('DATE(created_at)', Date),
    Column('COUNT(ID)', BigInteger, server_default=text("'0'"))
)


class Token(Base):
    __tablename__ = 'Tokens'

    id = Column(Integer, primary_key=True)
    player_name = Column(VARCHAR(50), nullable=False)
    token = Column(String(50), nullable=False)
    request_highscores = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    verify_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    create_token = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    verify_players = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    discord_general = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


t_hiscoreTableLatest = Table(
    'hiscoreTableLatest', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('timestamp', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('ts_date', Date),
    Column('Player_id', Integer),
    Column('total', BigInteger),
    Column('attack', Integer),
    Column('defence', Integer),
    Column('strength', Integer),
    Column('hitpoints', Integer),
    Column('ranged', Integer),
    Column('prayer', Integer),
    Column('magic', Integer),
    Column('cooking', Integer),
    Column('woodcutting', Integer),
    Column('fletching', Integer),
    Column('fishing', Integer),
    Column('firemaking', Integer),
    Column('crafting', Integer),
    Column('smithing', Integer),
    Column('mining', Integer),
    Column('herblore', Integer),
    Column('agility', Integer),
    Column('thieving', Integer),
    Column('slayer', Integer),
    Column('farming', Integer),
    Column('runecraft', Integer),
    Column('hunter', Integer),
    Column('construction', Integer),
    Column('league', Integer),
    Column('bounty_hunter_hunter', Integer),
    Column('bounty_hunter_rogue', Integer),
    Column('cs_all', Integer),
    Column('cs_beginner', Integer),
    Column('cs_easy', Integer),
    Column('cs_medium', Integer),
    Column('cs_hard', Integer),
    Column('cs_elite', Integer),
    Column('cs_master', Integer),
    Column('lms_rank', Integer),
    Column('soul_wars_zeal', Integer),
    Column('abyssal_sire', Integer),
    Column('alchemical_hydra', Integer),
    Column('barrows_chests', Integer),
    Column('bryophyta', Integer),
    Column('callisto', Integer),
    Column('cerberus', Integer),
    Column('chambers_of_xeric', Integer),
    Column('chambers_of_xeric_challenge_mode', Integer),
    Column('chaos_elemental', Integer),
    Column('chaos_fanatic', Integer),
    Column('commander_zilyana', Integer),
    Column('corporeal_beast', Integer),
    Column('crazy_archaeologist', Integer),
    Column('dagannoth_prime', Integer),
    Column('dagannoth_rex', Integer),
    Column('dagannoth_supreme', Integer),
    Column('deranged_archaeologist', Integer),
    Column('general_graardor', Integer),
    Column('giant_mole', Integer),
    Column('grotesque_guardians', Integer),
    Column('hespori', Integer),
    Column('kalphite_queen', Integer),
    Column('king_black_dragon', Integer),
    Column('kraken', Integer),
    Column('kreearra', Integer),
    Column('kril_tsutsaroth', Integer),
    Column('mimic', Integer),
    Column('nightmare', Integer),
    Column('obor', Integer),
    Column('sarachnis', Integer),
    Column('scorpia', Integer),
    Column('skotizo', Integer),
    Column('the_gauntlet', Integer),
    Column('the_corrupted_gauntlet', Integer),
    Column('theatre_of_blood', Integer),
    Column('thermonuclear_smoke_devil', Integer),
    Column('tzkal_zuk', Integer),
    Column('tztok_jad', Integer),
    Column('venenatis', Integer),
    Column('vetion', Integer),
    Column('vorkath', Integer),
    Column('wintertodt', Integer),
    Column('zalcano', Integer),
    Column('zulrah', Integer),
    Column('name', Text)
)


t_hiscoreTableLatestDiff = Table(
    'hiscoreTableLatestDiff', metadata,
    Column('Player_id', Integer, server_default=text("'0'")),
    Column('name', Text),
    Column('ts_date', Date),
    Column('total_diff', BigInteger),
    Column('attack_diff', BigInteger),
    Column('defence_diff', BigInteger),
    Column('strength_diff', BigInteger),
    Column('hitpoints_diff', BigInteger),
    Column('ranged_diff', BigInteger),
    Column('prayer_diff', BigInteger),
    Column('magic_diff', BigInteger),
    Column('cooking_diff', BigInteger),
    Column('woodcutting_diff', BigInteger),
    Column('fletching_diff', BigInteger),
    Column('fishing_diff', BigInteger),
    Column('firemaking_diff', BigInteger),
    Column('crafting_diff', BigInteger),
    Column('smithing_diff', BigInteger),
    Column('mining_diff', BigInteger),
    Column('herblore_diff', BigInteger),
    Column('agility_diff', BigInteger),
    Column('thieving_diff', BigInteger),
    Column('slayer_diff', BigInteger),
    Column('farming_diff', BigInteger),
    Column('runecraft_diff', BigInteger),
    Column('hunter_diff', BigInteger),
    Column('construction_diff', BigInteger),
    Column('league_diff', BigInteger),
    Column('bounty_hunter_hunter_diff', BigInteger),
    Column('bounty_hunter_rogue_diff', BigInteger),
    Column('cs_all_diff', BigInteger),
    Column('cs_beginner_diff', BigInteger),
    Column('cs_easy_diff', BigInteger),
    Column('cs_medium_diff', BigInteger),
    Column('cs_hard_diff', BigInteger),
    Column('cs_elite_diff', BigInteger),
    Column('cs_master_diff', BigInteger),
    Column('lms_rank_diff', BigInteger),
    Column('soul_wars_zeal_diff', BigInteger),
    Column('abyssal_sire_diff', BigInteger),
    Column('alchemical_hydra_diff', BigInteger),
    Column('barrows_chests_diff', BigInteger),
    Column('bryophyta_diff', BigInteger),
    Column('callisto_diff', BigInteger),
    Column('cerberus_diff', BigInteger),
    Column('chambers_of_xeric_diff', BigInteger),
    Column('chambers_of_xeric_challenge_mode_diff', BigInteger),
    Column('chaos_elemental_diff', BigInteger),
    Column('chaos_fanatic_diff', BigInteger),
    Column('commander_zilyana_diff', BigInteger),
    Column('corporeal_beast_diff', BigInteger),
    Column('crazy_archaeologist_diff', BigInteger),
    Column('dagannoth_prime_diff', BigInteger),
    Column('dagannoth_rex_diff', BigInteger),
    Column('dagannoth_supreme_diff', BigInteger),
    Column('deranged_archaeologist_diff', BigInteger),
    Column('general_graardor_diff', BigInteger),
    Column('giant_mole_diff', BigInteger),
    Column('grotesque_guardians_diff', BigInteger),
    Column('hespori_diff', BigInteger),
    Column('kalphite_queen_diff', BigInteger),
    Column('king_black_dragon_diff', BigInteger),
    Column('kraken_diff', BigInteger),
    Column('kreearra_diff', BigInteger),
    Column('kril_tsutsaroth_diff', BigInteger),
    Column('mimic_diff', BigInteger),
    Column('nightmare_diff', BigInteger),
    Column('obor_diff', BigInteger),
    Column('sarachnis_diff', BigInteger),
    Column('scorpia_diff', BigInteger),
    Column('skotizo_diff', BigInteger),
    Column('the_gauntlet_diff', BigInteger),
    Column('the_corrupted_gauntlet_diff', BigInteger),
    Column('theatre_of_blood_diff', BigInteger),
    Column('thermonuclear_smoke_devil_diff', BigInteger),
    Column('tzkal_zuk_diff', BigInteger),
    Column('tztok_jad_diff', BigInteger),
    Column('venenatis_diff', BigInteger),
    Column('vetion_diff', BigInteger),
    Column('vorkath_diff', BigInteger),
    Column('wintertodt_diff', BigInteger),
    Column('zalcano_diff', BigInteger),
    Column('zulrah_diff', BigInteger)
)


t_hiscoreTableStats = Table(
    'hiscoreTableStats', metadata,
    Column('hiscore_Players_checked', BigInteger, server_default=text("'0'")),
    Column('hiscore_checked_date', Date)
)


t_labelParents = Table(
    'labelParents', metadata,
    Column('child_label', String(50)),
    Column('parent_label', String(50))
)


class PlayerHiscoreDataChange(Base):
    __tablename__ = 'playerHiscoreDataChanges'

    id = Column(Integer, primary_key=True)
    playerHiscoreDataID = Column(Integer, nullable=False)
    old_player_id = Column(Integer, nullable=False)
    new_player_id = Column(Integer, nullable=False)
    old_total = Column(Integer, nullable=False)
    new_total = Column(Integer, nullable=False)
    change_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


t_playerPossibleBanPrediction = Table(
    'playerPossibleBanPrediction', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('name', Text),
    Column('created_at', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('updated_at', DateTime),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'")),
    Column('label_id', Integer, server_default=text("'0'")),
    Column('label_jagex', Integer, server_default=text("'0'")),
    Column('prediction', String(50))
)


t_playerTableStats = Table(
    'playerTableStats', metadata,
    Column('Players_checked', BigInteger, server_default=text("'0'")),
    Column('last_checked_date', Date)
)


t_player_updates_hour = Table(
    'player_updates_hour', metadata,
    Column('date', Date),
    Column('hour', Integer),
    Column('player_updated_at', BigInteger, server_default=text("'0'"))
)


t_playersJagexLabeledWrong = Table(
    'playersJagexLabeledWrong', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('name', Text),
    Column('created_at', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('updated_at', DateTime),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'")),
    Column('label_id', Integer, server_default=text("'0'")),
    Column('label_jagex', Integer, server_default=text("'0'"))
)


t_playersOfInterest = Table(
    'playersOfInterest', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('name', Text),
    Column('created_at', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('updated_at', DateTime),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'")),
    Column('label_id', Integer, server_default=text("'0'"))
)


t_playersToBan = Table(
    'playersToBan', metadata,
    Column('player_id', Integer, server_default=text("'0'")),
    Column('name', Text),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('label_jagex', Integer, server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('Last_Seen_Time', TIMESTAMP),
    Column('Last_Seen_unix', BigInteger, server_default=text("'0'")),
    Column('Last_Seen_region', Text),
    Column('region_ID', Integer),
    Column('prediction', String(50)),
    Column('Predicted_confidence', DECIMAL(5, 2)),
    Column('total', BigInteger),
    Column('attack', Integer),
    Column('defence', Integer),
    Column('strength', Integer),
    Column('hitpoints', Integer),
    Column('ranged', Integer),
    Column('prayer', Integer),
    Column('magic', Integer),
    Column('cooking', Integer),
    Column('woodcutting', Integer),
    Column('fletching', Integer),
    Column('fishing', Integer),
    Column('firemaking', Integer),
    Column('crafting', Integer),
    Column('smithing', Integer),
    Column('mining', Integer),
    Column('herblore', Integer),
    Column('agility', Integer),
    Column('thieving', Integer),
    Column('slayer', Integer),
    Column('farming', Integer),
    Column('runecraft', Integer),
    Column('hunter', Integer),
    Column('construction', Integer),
    Column('league', Integer),
    Column('bounty_hunter_hunter', Integer),
    Column('bounty_hunter_rogue', Integer),
    Column('cs_all', Integer),
    Column('cs_beginner', Integer),
    Column('cs_easy', Integer),
    Column('cs_medium', Integer),
    Column('cs_hard', Integer),
    Column('cs_elite', Integer),
    Column('cs_master', Integer),
    Column('lms_rank', Integer),
    Column('soul_wars_zeal', Integer),
    Column('abyssal_sire', Integer),
    Column('alchemical_hydra', Integer),
    Column('barrows_chests', Integer),
    Column('bryophyta', Integer),
    Column('callisto', Integer),
    Column('cerberus', Integer),
    Column('chambers_of_xeric', Integer),
    Column('chambers_of_xeric_challenge_mode', Integer),
    Column('chaos_elemental', Integer),
    Column('chaos_fanatic', Integer),
    Column('commander_zilyana', Integer),
    Column('corporeal_beast', Integer),
    Column('crazy_archaeologist', Integer),
    Column('dagannoth_prime', Integer),
    Column('dagannoth_rex', Integer),
    Column('dagannoth_supreme', Integer),
    Column('deranged_archaeologist', Integer),
    Column('general_graardor', Integer),
    Column('giant_mole', Integer),
    Column('grotesque_guardians', Integer),
    Column('hespori', Integer),
    Column('kalphite_queen', Integer),
    Column('king_black_dragon', Integer),
    Column('kraken', Integer),
    Column('kreearra', Integer),
    Column('kril_tsutsaroth', Integer),
    Column('mimic', Integer),
    Column('nightmare', Integer),
    Column('obor', Integer),
    Column('sarachnis', Integer),
    Column('scorpia', Integer),
    Column('skotizo', Integer),
    Column('Tempoross', Integer),
    Column('the_gauntlet', Integer),
    Column('the_corrupted_gauntlet', Integer),
    Column('theatre_of_blood', Integer),
    Column('thermonuclear_smoke_devil', Integer),
    Column('tzkal_zuk', Integer),
    Column('tztok_jad', Integer),
    Column('venenatis', Integer),
    Column('vetion', Integer),
    Column('vorkath', Integer),
    Column('wintertodt', Integer),
    Column('zalcano', Integer),
    Column('zulrah', Integer)
)


t_playersToReport = Table(
    'playersToReport', metadata,
    Column('name', Text),
    Column('created_at', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('updated_at', DateTime),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('prediction', String(50)),
    Column('Predicted_confidence', DECIMAL(5, 2)),
    Column('id', Integer, server_default=text("'0'")),
    Column('timestamp', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('ts_date', Date),
    Column('Player_id', Integer),
    Column('total', BigInteger),
    Column('attack', Integer),
    Column('defence', Integer),
    Column('strength', Integer),
    Column('hitpoints', Integer),
    Column('ranged', Integer),
    Column('prayer', Integer),
    Column('magic', Integer),
    Column('cooking', Integer),
    Column('woodcutting', Integer),
    Column('fletching', Integer),
    Column('fishing', Integer),
    Column('firemaking', Integer),
    Column('crafting', Integer),
    Column('smithing', Integer),
    Column('mining', Integer),
    Column('herblore', Integer),
    Column('agility', Integer),
    Column('thieving', Integer),
    Column('slayer', Integer),
    Column('farming', Integer),
    Column('runecraft', Integer),
    Column('hunter', Integer),
    Column('construction', Integer),
    Column('league', Integer),
    Column('bounty_hunter_hunter', Integer),
    Column('bounty_hunter_rogue', Integer),
    Column('cs_all', Integer),
    Column('cs_beginner', Integer),
    Column('cs_easy', Integer),
    Column('cs_medium', Integer),
    Column('cs_hard', Integer),
    Column('cs_elite', Integer),
    Column('cs_master', Integer),
    Column('lms_rank', Integer),
    Column('soul_wars_zeal', Integer),
    Column('abyssal_sire', Integer),
    Column('alchemical_hydra', Integer),
    Column('barrows_chests', Integer),
    Column('bryophyta', Integer),
    Column('callisto', Integer),
    Column('cerberus', Integer),
    Column('chambers_of_xeric', Integer),
    Column('chambers_of_xeric_challenge_mode', Integer),
    Column('chaos_elemental', Integer),
    Column('chaos_fanatic', Integer),
    Column('commander_zilyana', Integer),
    Column('corporeal_beast', Integer),
    Column('crazy_archaeologist', Integer),
    Column('dagannoth_prime', Integer),
    Column('dagannoth_rex', Integer),
    Column('dagannoth_supreme', Integer),
    Column('deranged_archaeologist', Integer),
    Column('general_graardor', Integer),
    Column('giant_mole', Integer),
    Column('grotesque_guardians', Integer),
    Column('hespori', Integer),
    Column('kalphite_queen', Integer),
    Column('king_black_dragon', Integer),
    Column('kraken', Integer),
    Column('kreearra', Integer),
    Column('kril_tsutsaroth', Integer),
    Column('mimic', Integer),
    Column('nightmare', Integer),
    Column('obor', Integer),
    Column('sarachnis', Integer),
    Column('scorpia', Integer),
    Column('skotizo', Integer),
    Column('Tempoross', Integer),
    Column('the_gauntlet', Integer),
    Column('the_corrupted_gauntlet', Integer),
    Column('theatre_of_blood', Integer),
    Column('thermonuclear_smoke_devil', Integer),
    Column('tzkal_zuk', Integer),
    Column('tztok_jad', Integer),
    Column('venenatis', Integer),
    Column('vetion', Integer),
    Column('vorkath', Integer),
    Column('wintertodt', Integer),
    Column('zalcano', Integer),
    Column('zulrah', Integer)
)


t_playersToReview = Table(
    'playersToReview', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('name', Text),
    Column('created_at', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('updated_at', DateTime),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'")),
    Column('label_id', Integer, server_default=text("'0'")),
    Column('label_jagex', Integer, server_default=text("'0'")),
    Column('prediction', String(50)),
    Column('Predicted_confidence', DECIMAL(5, 2)),
    Column('total', BigInteger),
    Column('attack', Integer),
    Column('defence', Integer),
    Column('strength', Integer),
    Column('hitpoints', Integer),
    Column('ranged', Integer),
    Column('prayer', Integer),
    Column('magic', Integer),
    Column('cooking', Integer),
    Column('woodcutting', Integer),
    Column('fletching', Integer),
    Column('fishing', Integer),
    Column('firemaking', Integer),
    Column('crafting', Integer),
    Column('smithing', Integer),
    Column('mining', Integer),
    Column('herblore', Integer),
    Column('agility', Integer),
    Column('thieving', Integer),
    Column('slayer', Integer),
    Column('farming', Integer),
    Column('runecraft', Integer),
    Column('hunter', Integer),
    Column('construction', Integer),
    Column('attack_ratio', DECIMAL(14, 4)),
    Column('defence_ratio', DECIMAL(14, 4)),
    Column('strength_ratio', DECIMAL(14, 4)),
    Column('hitpoints_ratio', DECIMAL(14, 4)),
    Column('ranged_ratio', DECIMAL(14, 4)),
    Column('prayer_ratio', DECIMAL(14, 4)),
    Column('magic_ratio', DECIMAL(14, 4)),
    Column('cooking_ratio', DECIMAL(14, 4)),
    Column('woodcutting_ratio', DECIMAL(14, 4)),
    Column('fletching_ratio', DECIMAL(14, 4)),
    Column('fishing_ratio', DECIMAL(14, 4)),
    Column('firemaking_ratio', DECIMAL(14, 4)),
    Column('crafting_ratio', DECIMAL(14, 4)),
    Column('smithing_ratio', DECIMAL(14, 4)),
    Column('mining_ratio', DECIMAL(14, 4)),
    Column('herblore_ratio', DECIMAL(14, 4)),
    Column('agility_ratio', DECIMAL(14, 4)),
    Column('thieving_ratio', DECIMAL(14, 4)),
    Column('slayer_ratio', DECIMAL(14, 4)),
    Column('farming_ratio', DECIMAL(14, 4)),
    Column('runecrafting_ratio', DECIMAL(14, 4)),
    Column('hunter_ratio', DECIMAL(14, 4)),
    Column('construction_ratio', DECIMAL(14, 4)),
    Column('league', Integer),
    Column('bounty_hunter_hunter', Integer),
    Column('bounty_hunter_rogue', Integer),
    Column('cs_all', Integer),
    Column('cs_beginner', Integer),
    Column('cs_easy', Integer),
    Column('cs_medium', Integer),
    Column('cs_hard', Integer),
    Column('cs_elite', Integer),
    Column('cs_master', Integer),
    Column('lms_rank', Integer),
    Column('soul_wars_zeal', Integer),
    Column('abyssal_sire', Integer),
    Column('alchemical_hydra', Integer),
    Column('barrows_chests', Integer),
    Column('bryophyta', Integer),
    Column('callisto', Integer),
    Column('cerberus', Integer),
    Column('chambers_of_xeric', Integer),
    Column('chambers_of_xeric_challenge_mode', Integer),
    Column('chaos_elemental', Integer),
    Column('chaos_fanatic', Integer),
    Column('commander_zilyana', Integer),
    Column('corporeal_beast', Integer),
    Column('crazy_archaeologist', Integer),
    Column('dagannoth_prime', Integer),
    Column('dagannoth_rex', Integer),
    Column('dagannoth_supreme', Integer),
    Column('deranged_archaeologist', Integer),
    Column('general_graardor', Integer),
    Column('giant_mole', Integer),
    Column('grotesque_guardians', Integer),
    Column('hespori', Integer),
    Column('kalphite_queen', Integer),
    Column('king_black_dragon', Integer),
    Column('kraken', Integer),
    Column('kreearra', Integer),
    Column('kril_tsutsaroth', Integer),
    Column('mimic', Integer),
    Column('nightmare', Integer),
    Column('obor', Integer),
    Column('sarachnis', Integer),
    Column('scorpia', Integer),
    Column('skotizo', Integer),
    Column('Tempoross', Integer),
    Column('the_gauntlet', Integer),
    Column('the_corrupted_gauntlet', Integer),
    Column('theatre_of_blood', Integer),
    Column('thermonuclear_smoke_devil', Integer),
    Column('tzkal_zuk', Integer),
    Column('tztok_jad', Integer),
    Column('venenatis', Integer),
    Column('vetion', Integer),
    Column('vorkath', Integer),
    Column('wintertodt', Integer),
    Column('zalcano', Integer),
    Column('zulrah', Integer)
)


t_playersToScrape = Table(
    'playersToScrape', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('name', Text),
    Column('created_at', DateTime, server_default=text("'CURRENT_TIMESTAMP'")),
    Column('updated_at', DateTime),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'")),
    Column('label_id', Integer, server_default=text("'0'")),
    Column('label_jagex', Integer, server_default=text("'0'"))
)


class RegionIDName(Base):
    __tablename__ = 'regionIDNames'

    entry_ID = Column(Integer, primary_key=True)
    region_ID = Column(Integer, nullable=False, unique=True)
    z_axis = Column(Integer, server_default=text("'0'"))
    region_name = Column(Text, nullable=False)


t_regionTrainingData = Table(
    'regionTrainingData', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'")),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('label_id', Integer, server_default=text("'0'")),
    Column('region_id', Integer),
    Column('COUNT(rp.region_id)', BigInteger, server_default=text("'0'"))
)


t_reportBanLocations = Table(
    'reportBanLocations', metadata,
    Column('id', Integer, server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'")),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('label_id', Integer, server_default=text("'0'")),
    Column('region_id', Integer),
    Column('COUNT(rp.region_id)', BigInteger, server_default=text("'0'"))
)


class ReportLatest(Base):
    __tablename__ = 'reportLatest'

    report_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    reported_id = Column(Integer, primary_key=True)
    region_id = Column(Integer, nullable=False)
    x_coord = Column(Integer, nullable=False)
    y_coord = Column(Integer, nullable=False)
    z_coord = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    on_members_world = Column(Integer)
    world_number = Column(Integer)
    equip_head_id = Column(Integer)
    equip_amulet_id = Column(Integer)
    equip_torso_id = Column(Integer)
    equip_legs_id = Column(Integer)
    equip_boots_id = Column(Integer)
    equip_cape_id = Column(Integer)
    equip_hands_id = Column(Integer)
    equip_weapon_id = Column(Integer)
    equip_shield_id = Column(Integer)
    equip_ge_value = Column(BigInteger)


t_reportedRegion = Table(
    'reportedRegion', metadata,
    Column('region_id', Integer),
    Column('reports', BigInteger, server_default=text("'0'")),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'"))
)


t_reportingScores = Table(
    'reportingScores', metadata,
    Column('reporter', Text),
    Column('reported', BigInteger, server_default=text("'0'")),
    Column('possible_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_ban', TINYINT(1), server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), server_default=text("'0'"))
)


class SentToJagex(Base):
    __tablename__ = 'sentToJagex'

    entry_id = Column(Integer, primary_key=True)
    created_on = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    name = Column(Text, nullable=False)


t_topLocationData = Table(
    'topLocationData', metadata,
    Column('name', Text, nullable=False),
    Column('label_id', Integer, nullable=False, server_default=text("'0'")),
    Column('player_id', Integer, nullable=False),
    Column('x1', DECIMAL(18, 8)),
    Column('y1', DECIMAL(18, 8)),
    Column('x2', DECIMAL(18, 8)),
    Column('y2', DECIMAL(18, 8)),
    Column('x3', DECIMAL(18, 8)),
    Column('y3', DECIMAL(18, 8)),
    Column('x4', DECIMAL(18, 8)),
    Column('y4', DECIMAL(18, 8)),
    Column('x5', DECIMAL(18, 8)),
    Column('y5', DECIMAL(18, 8))
)


t_xpWeekDiff = Table(
    'xpWeekDiff', metadata,
    Column('Player_id', Integer, nullable=False, server_default=text("'0'")),
    Column('name', Text, nullable=False),
    Column('confirmed_ban', TINYINT(1), nullable=False, server_default=text("'0'")),
    Column('confirmed_player', TINYINT(1), nullable=False, server_default=text("'0'")),
    Column('possible_ban', TINYINT(1), nullable=False, server_default=text("'0'")),
    Column('label_id', Integer, nullable=False, server_default=text("'0'")),
    Column('label_jagex', Integer, nullable=False, server_default=text("'0'")),
    Column('ts_date', Date),
    Column('total_diff', DECIMAL(24, 4)),
    Column('attack_diff', DECIMAL(15, 4)),
    Column('defence_diff', DECIMAL(15, 4)),
    Column('strength_diff', DECIMAL(15, 4)),
    Column('hitpoints_diff', DECIMAL(15, 4)),
    Column('ranged_diff', DECIMAL(15, 4)),
    Column('prayer_diff', DECIMAL(15, 4)),
    Column('magic_diff', DECIMAL(15, 4)),
    Column('cooking_diff', DECIMAL(15, 4)),
    Column('woodcutting_diff', DECIMAL(15, 4)),
    Column('fletching_diff', DECIMAL(15, 4)),
    Column('fishing_diff', DECIMAL(15, 4)),
    Column('firemaking_diff', DECIMAL(15, 4)),
    Column('crafting_diff', DECIMAL(15, 4)),
    Column('smithing_diff', DECIMAL(15, 4)),
    Column('mining_diff', DECIMAL(15, 4)),
    Column('herblore_diff', DECIMAL(15, 4)),
    Column('agility_diff', DECIMAL(15, 4)),
    Column('thieving_diff', DECIMAL(15, 4)),
    Column('slayer_diff', DECIMAL(15, 4)),
    Column('farming_diff', DECIMAL(15, 4)),
    Column('runecraft_diff', DECIMAL(15, 4)),
    Column('hunter_diff', DECIMAL(15, 4)),
    Column('construction_diff', DECIMAL(15, 4)),
    Column('league_diff', DECIMAL(15, 4)),
    Column('bounty_hunter_hunter_diff', DECIMAL(15, 4)),
    Column('bounty_hunter_rogue_diff', DECIMAL(15, 4)),
    Column('cs_all_diff', DECIMAL(15, 4)),
    Column('cs_beginner_diff', DECIMAL(15, 4)),
    Column('cs_easy_diff', DECIMAL(15, 4)),
    Column('cs_medium_diff', DECIMAL(15, 4)),
    Column('cs_hard_diff', DECIMAL(15, 4)),
    Column('cs_elite_diff', DECIMAL(15, 4)),
    Column('cs_master_diff', DECIMAL(15, 4)),
    Column('lms_rank_diff', DECIMAL(15, 4)),
    Column('soul_wars_zeal_diff', DECIMAL(15, 4)),
    Column('abyssal_sire_diff', DECIMAL(15, 4)),
    Column('alchemical_hydra_diff', DECIMAL(15, 4)),
    Column('barrows_chests_diff', DECIMAL(15, 4)),
    Column('bryophyta_diff', DECIMAL(15, 4)),
    Column('callisto_diff', DECIMAL(15, 4)),
    Column('cerberus_diff', DECIMAL(15, 4)),
    Column('chambers_of_xeric_diff', DECIMAL(15, 4)),
    Column('chambers_of_xeric_challenge_mode_diff', DECIMAL(15, 4)),
    Column('chaos_elemental_diff', DECIMAL(15, 4)),
    Column('chaos_fanatic_diff', DECIMAL(15, 4)),
    Column('commander_zilyana_diff', DECIMAL(15, 4)),
    Column('corporeal_beast_diff', DECIMAL(15, 4)),
    Column('crazy_archaeologist_diff', DECIMAL(15, 4)),
    Column('dagannoth_prime_diff', DECIMAL(15, 4)),
    Column('dagannoth_rex_diff', DECIMAL(15, 4)),
    Column('dagannoth_supreme_diff', DECIMAL(15, 4)),
    Column('deranged_archaeologist_diff', DECIMAL(15, 4)),
    Column('general_graardor_diff', DECIMAL(15, 4)),
    Column('giant_mole_diff', DECIMAL(15, 4)),
    Column('grotesque_guardians_diff', DECIMAL(15, 4)),
    Column('hespori_diff', DECIMAL(15, 4)),
    Column('kalphite_queen_diff', DECIMAL(15, 4)),
    Column('king_black_dragon_diff', DECIMAL(15, 4)),
    Column('kraken_diff', DECIMAL(15, 4)),
    Column('kreearra_diff', DECIMAL(15, 4)),
    Column('kril_tsutsaroth_diff', DECIMAL(15, 4)),
    Column('mimic_diff', DECIMAL(15, 4)),
    Column('nightmare_diff', DECIMAL(15, 4)),
    Column('obor_diff', DECIMAL(15, 4)),
    Column('sarachnis_diff', DECIMAL(15, 4)),
    Column('scorpia_diff', DECIMAL(15, 4)),
    Column('skotizo_diff', DECIMAL(15, 4)),
    Column('the_gauntlet_diff', DECIMAL(15, 4)),
    Column('the_corrupted_gauntlet_diff', DECIMAL(15, 4)),
    Column('theatre_of_blood_diff', DECIMAL(15, 4)),
    Column('thermonuclear_smoke_devil_diff', DECIMAL(15, 4)),
    Column('tzkal_zuk_diff', DECIMAL(15, 4)),
    Column('tztok_jad_diff', DECIMAL(15, 4)),
    Column('venenatis_diff', DECIMAL(15, 4)),
    Column('vetion_diff', DECIMAL(15, 4)),
    Column('vorkath_diff', DECIMAL(15, 4)),
    Column('wintertodt_diff', DECIMAL(15, 4)),
    Column('zalcano_diff', DECIMAL(15, 4)),
    Column('zulrah_diff', DECIMAL(15, 4))
)


t_xp_banned = Table(
    'xp_banned', metadata,
    Column('Attack', DECIMAL(32, 0)),
    Column('Defence', DECIMAL(32, 0)),
    Column('Strength', DECIMAL(32, 0)),
    Column('Hitpoints', DECIMAL(32, 0)),
    Column('Ranged', DECIMAL(32, 0)),
    Column('Prayer', DECIMAL(32, 0)),
    Column('Magic', DECIMAL(32, 0)),
    Column('Cooking', DECIMAL(32, 0)),
    Column('Woodcutting', DECIMAL(32, 0)),
    Column('Fletching', DECIMAL(32, 0)),
    Column('Fishing', DECIMAL(32, 0)),
    Column('Firemaking', DECIMAL(32, 0)),
    Column('Crafting', DECIMAL(32, 0)),
    Column('Smithing', DECIMAL(32, 0)),
    Column('Mining', DECIMAL(32, 0)),
    Column('Herblore', DECIMAL(32, 0)),
    Column('Agility', DECIMAL(32, 0)),
    Column('Thieving', DECIMAL(32, 0)),
    Column('Slayer', DECIMAL(32, 0)),
    Column('Farming', DECIMAL(32, 0)),
    Column('Runecraft', DECIMAL(32, 0)),
    Column('Hunter', DECIMAL(32, 0)),
    Column('Construction', DECIMAL(32, 0)),
    Column('total_xp_banned', DECIMAL(54, 0))
)


class LabelSubGroup(Base):
    __tablename__ = 'LabelSubGroup'

    id = Column(Integer, primary_key=True)
    parent_label = Column(ForeignKey('Labels.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    child_label = Column(ForeignKey('Labels.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)

    Label = relationship('Label', primaryjoin='LabelSubGroup.child_label == Label.id')
    Label1 = relationship('Label', primaryjoin='LabelSubGroup.parent_label == Label.id')


class Player(Base):
    __tablename__ = 'Players'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime)
    possible_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_ban = Column(TINYINT(1), nullable=False, index=True, server_default=text("'0'"))
    confirmed_player = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    label_id = Column(ForeignKey('Labels.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True, server_default=text("'0'"))
    label_jagex = Column(Integer, nullable=False, server_default=text("'0'"))

    label = relationship('Label')


t_Predictions = Table(
    'Predictions', metadata,
    Column('name', String(12), unique=True),
    Column('prediction', String(50)),
    Column('id', ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), index=True),
    Column('created', TIMESTAMP),
    Column('Predicted_confidence', DECIMAL(5, 2)),
    Column('Agility_bot', DECIMAL(5, 2)),
    Column('Cooking_bot', DECIMAL(5, 2)),
    Column('Crafting_bot', DECIMAL(5, 2)),
    Column('Firemaking_bot', DECIMAL(5, 2)),
    Column('Fishing_Cooking_bot', DECIMAL(5, 2)),
    Column('Fishing_bot', DECIMAL(5, 2)),
    Column('Fletching_bot', DECIMAL(5, 2)),
    Column('Herblore_bot', DECIMAL(5, 2)),
    Column('Hunter_bot', DECIMAL(5, 2)),
    Column('Magic_bot', DECIMAL(5, 2)),
    Column('Mining_bot', DECIMAL(5, 2)),
    Column('PVM_Melee_bot', DECIMAL(5, 2)),
    Column('PVM_Ranged_Magic_bot', DECIMAL(5, 2)),
    Column('PVM_Ranged_bot', DECIMAL(5, 2)),
    Column('Real_Player', DECIMAL(5, 2)),
    Column('Runecrafting_bot', DECIMAL(5, 2)),
    Column('Smithing_bot', DECIMAL(5, 2)),
    Column('Thieving_bot', DECIMAL(5, 2)),
    Column('Woodcutting_bot', DECIMAL(5, 2)),
    Column('mort_myre_fungus_bot', DECIMAL(5, 2))
)


class PredictionsFeedback(Base):
    __tablename__ = 'PredictionsFeedback'
    __table_args__ = (
        Index('UNIQUE_VOTE', 'voter_id', 'prediction', 'subject_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    ts = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    voter_id = Column(ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    subject_id = Column(ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    prediction = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    vote = Column(Integer, nullable=False, server_default=text("'0'"))
    feedback_text = Column(TEXT)

    subject = relationship('Player', primaryjoin='PredictionsFeedback.subject_id == Player.id')
    voter = relationship('Player', primaryjoin='PredictionsFeedback.voter_id == Player.id')


class Report(Base):
    __tablename__ = 'Reports'
    __table_args__ = (
        Index('Unique_Report', 'reportedID', 'reportingID', 'region_id', 'manual_detect', unique=True),
        Index('reportedID', 'reportedID', 'region_id')
    )

    ID = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    reportedID = Column(ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    reportingID = Column(ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    region_id = Column(Integer, nullable=False)
    x_coord = Column(Integer, nullable=False)
    y_coord = Column(Integer, nullable=False)
    z_coord = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    manual_detect = Column(TINYINT(1))
    on_members_world = Column(Integer)
    on_pvp_world = Column(TINYINT)
    world_number = Column(Integer)
    equip_head_id = Column(Integer)
    equip_amulet_id = Column(Integer)
    equip_torso_id = Column(Integer)
    equip_legs_id = Column(Integer)
    equip_boots_id = Column(Integer)
    equip_cape_id = Column(Integer)
    equip_hands_id = Column(Integer)
    equip_weapon_id = Column(Integer)
    equip_shield_id = Column(Integer)
    equip_ge_value = Column(BigInteger)

    Player = relationship('Player', primaryjoin='Report.reportedID == Player.id')
    Player1 = relationship('Player', primaryjoin='Report.reportingID == Player.id')


class PlayerChatHistory(Base):
    __tablename__ = 'playerChatHistory'

    entry_id = Column(Integer, primary_key=True)
    reportedID = Column(ForeignKey('Players.id'), nullable=False, index=True)
    chat = Column(TINYTEXT, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    reportingID = Column(ForeignKey('Players.id'), nullable=False, index=True)

    Player = relationship('Player', primaryjoin='PlayerChatHistory.reportedID == Player.id')
    Player1 = relationship('Player', primaryjoin='PlayerChatHistory.reportingID == Player.id')


class PlayerHiscoreDatum(Base):
    __tablename__ = 'playerHiscoreData'
    __table_args__ = (
        Index('Unique_player_date', 'Player_id', 'ts_date', unique=True),
        Index('Unique_player_time', 'timestamp', 'Player_id', unique=True)
    )

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    ts_date = Column(Date)
    Player_id = Column(ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False)
    total = Column(BigInteger)
    attack = Column(Integer)
    defence = Column(Integer)
    strength = Column(Integer)
    hitpoints = Column(Integer)
    ranged = Column(Integer)
    prayer = Column(Integer)
    magic = Column(Integer)
    cooking = Column(Integer)
    woodcutting = Column(Integer)
    fletching = Column(Integer)
    fishing = Column(Integer)
    firemaking = Column(Integer)
    crafting = Column(Integer)
    smithing = Column(Integer)
    mining = Column(Integer)
    herblore = Column(Integer)
    agility = Column(Integer)
    thieving = Column(Integer)
    slayer = Column(Integer)
    farming = Column(Integer)
    runecraft = Column(Integer)
    hunter = Column(Integer)
    construction = Column(Integer)
    league = Column(Integer)
    bounty_hunter_hunter = Column(Integer)
    bounty_hunter_rogue = Column(Integer)
    cs_all = Column(Integer)
    cs_beginner = Column(Integer)
    cs_easy = Column(Integer)
    cs_medium = Column(Integer)
    cs_hard = Column(Integer)
    cs_elite = Column(Integer)
    cs_master = Column(Integer)
    lms_rank = Column(Integer)
    soul_wars_zeal = Column(Integer)
    abyssal_sire = Column(Integer)
    alchemical_hydra = Column(Integer)
    barrows_chests = Column(Integer)
    bryophyta = Column(Integer)
    callisto = Column(Integer)
    cerberus = Column(Integer)
    chambers_of_xeric = Column(Integer)
    chambers_of_xeric_challenge_mode = Column(Integer)
    chaos_elemental = Column(Integer)
    chaos_fanatic = Column(Integer)
    commander_zilyana = Column(Integer)
    corporeal_beast = Column(Integer)
    crazy_archaeologist = Column(Integer)
    dagannoth_prime = Column(Integer)
    dagannoth_rex = Column(Integer)
    dagannoth_supreme = Column(Integer)
    deranged_archaeologist = Column(Integer)
    general_graardor = Column(Integer)
    giant_mole = Column(Integer)
    grotesque_guardians = Column(Integer)
    hespori = Column(Integer)
    kalphite_queen = Column(Integer)
    king_black_dragon = Column(Integer)
    kraken = Column(Integer)
    kreearra = Column(Integer)
    kril_tsutsaroth = Column(Integer)
    mimic = Column(Integer)
    nightmare = Column(Integer)
    obor = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
    tempoross = Column(Integer)
    the_gauntlet = Column(Integer)
    the_corrupted_gauntlet = Column(Integer)
    theatre_of_blood = Column(Integer)
    theatre_of_blood_hard = Column(Integer)
    thermonuclear_smoke_devil = Column(Integer)
    tzkal_zuk = Column(Integer)
    tztok_jad = Column(Integer)
    venenatis = Column(Integer)
    vetion = Column(Integer)
    vorkath = Column(Integer)
    wintertodt = Column(Integer)
    zalcano = Column(Integer)
    zulrah = Column(Integer)

    Player = relationship('Player')


class PlayerHiscoreDataLatest(Base):
    __tablename__ = 'playerHiscoreDataLatest'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    ts_date = Column(Date)
    Player_id = Column(ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, unique=True)
    total = Column(BigInteger)
    attack = Column(Integer)
    defence = Column(Integer)
    strength = Column(Integer)
    hitpoints = Column(Integer)
    ranged = Column(Integer)
    prayer = Column(Integer)
    magic = Column(Integer)
    cooking = Column(Integer)
    woodcutting = Column(Integer)
    fletching = Column(Integer)
    fishing = Column(Integer)
    firemaking = Column(Integer)
    crafting = Column(Integer)
    smithing = Column(Integer)
    mining = Column(Integer)
    herblore = Column(Integer)
    agility = Column(Integer)
    thieving = Column(Integer)
    slayer = Column(Integer)
    farming = Column(Integer)
    runecraft = Column(Integer)
    hunter = Column(Integer)
    construction = Column(Integer)
    league = Column(Integer)
    bounty_hunter_hunter = Column(Integer)
    bounty_hunter_rogue = Column(Integer)
    cs_all = Column(Integer)
    cs_beginner = Column(Integer)
    cs_easy = Column(Integer)
    cs_medium = Column(Integer)
    cs_hard = Column(Integer)
    cs_elite = Column(Integer)
    cs_master = Column(Integer)
    lms_rank = Column(Integer)
    soul_wars_zeal = Column(Integer)
    abyssal_sire = Column(Integer)
    alchemical_hydra = Column(Integer)
    barrows_chests = Column(Integer)
    bryophyta = Column(Integer)
    callisto = Column(Integer)
    cerberus = Column(Integer)
    chambers_of_xeric = Column(Integer)
    chambers_of_xeric_challenge_mode = Column(Integer)
    chaos_elemental = Column(Integer)
    chaos_fanatic = Column(Integer)
    commander_zilyana = Column(Integer)
    corporeal_beast = Column(Integer)
    crazy_archaeologist = Column(Integer)
    dagannoth_prime = Column(Integer)
    dagannoth_rex = Column(Integer)
    dagannoth_supreme = Column(Integer)
    deranged_archaeologist = Column(Integer)
    general_graardor = Column(Integer)
    giant_mole = Column(Integer)
    grotesque_guardians = Column(Integer)
    hespori = Column(Integer)
    kalphite_queen = Column(Integer)
    king_black_dragon = Column(Integer)
    kraken = Column(Integer)
    kreearra = Column(Integer)
    kril_tsutsaroth = Column(Integer)
    mimic = Column(Integer)
    nightmare = Column(Integer)
    obor = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
    Tempoross = Column(Integer, nullable=False)
    the_gauntlet = Column(Integer)
    the_corrupted_gauntlet = Column(Integer)
    theatre_of_blood = Column(Integer)
    theatre_of_blood_hard = Column(Integer)
    thermonuclear_smoke_devil = Column(Integer)
    tzkal_zuk = Column(Integer)
    tztok_jad = Column(Integer)
    venenatis = Column(Integer)
    vetion = Column(Integer)
    vorkath = Column(Integer)
    wintertodt = Column(Integer)
    zalcano = Column(Integer)
    zulrah = Column(Integer)

    Player = relationship('Player')


class PlayerHiscoreDataXPChange(Base):
    __tablename__ = 'playerHiscoreDataXPChange'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    ts_date = Column(Date)
    Player_id = Column(ForeignKey('Players.id', ondelete='RESTRICT', onupdate='RESTRICT'), nullable=False, index=True)
    total = Column(BigInteger)
    attack = Column(Integer)
    defence = Column(Integer)
    strength = Column(Integer)
    hitpoints = Column(Integer)
    ranged = Column(Integer)
    prayer = Column(Integer)
    magic = Column(Integer)
    cooking = Column(Integer)
    woodcutting = Column(Integer)
    fletching = Column(Integer)
    fishing = Column(Integer)
    firemaking = Column(Integer)
    crafting = Column(Integer)
    smithing = Column(Integer)
    mining = Column(Integer)
    herblore = Column(Integer)
    agility = Column(Integer)
    thieving = Column(Integer)
    slayer = Column(Integer)
    farming = Column(Integer)
    runecraft = Column(Integer)
    hunter = Column(Integer)
    construction = Column(Integer)
    league = Column(Integer)
    bounty_hunter_hunter = Column(Integer)
    bounty_hunter_rogue = Column(Integer)
    cs_all = Column(Integer)
    cs_beginner = Column(Integer)
    cs_easy = Column(Integer)
    cs_medium = Column(Integer)
    cs_hard = Column(Integer)
    cs_elite = Column(Integer)
    cs_master = Column(Integer)
    lms_rank = Column(Integer)
    soul_wars_zeal = Column(Integer)
    abyssal_sire = Column(Integer)
    alchemical_hydra = Column(Integer)
    barrows_chests = Column(Integer)
    bryophyta = Column(Integer)
    callisto = Column(Integer)
    cerberus = Column(Integer)
    chambers_of_xeric = Column(Integer)
    chambers_of_xeric_challenge_mode = Column(Integer)
    chaos_elemental = Column(Integer)
    chaos_fanatic = Column(Integer)
    commander_zilyana = Column(Integer)
    corporeal_beast = Column(Integer)
    crazy_archaeologist = Column(Integer)
    dagannoth_prime = Column(Integer)
    dagannoth_rex = Column(Integer)
    dagannoth_supreme = Column(Integer)
    deranged_archaeologist = Column(Integer)
    general_graardor = Column(Integer)
    giant_mole = Column(Integer)
    grotesque_guardians = Column(Integer)
    hespori = Column(Integer)
    kalphite_queen = Column(Integer)
    king_black_dragon = Column(Integer)
    kraken = Column(Integer)
    kreearra = Column(Integer)
    kril_tsutsaroth = Column(Integer)
    mimic = Column(Integer)
    nightmare = Column(Integer)
    obor = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
    Tempoross = Column(Integer, nullable=False)
    the_gauntlet = Column(Integer)
    the_corrupted_gauntlet = Column(Integer)
    theatre_of_blood = Column(Integer)
    theatre_of_blood_hard = Column(Integer)
    thermonuclear_smoke_devil = Column(Integer)
    tzkal_zuk = Column(Integer)
    tztok_jad = Column(Integer)
    venenatis = Column(Integer)
    vetion = Column(Integer)
    vorkath = Column(Integer)
    wintertodt = Column(Integer)
    zalcano = Column(Integer)
    zulrah = Column(Integer)

    Player = relationship('Player')
