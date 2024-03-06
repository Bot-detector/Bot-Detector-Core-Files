from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.mysql import TEXT, TINYINT, VARCHAR
from sqlalchemy.dialects.mysql.types import TINYTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# generated with sqlacodegen
Base = declarative_base()
metadata = Base.metadata


class Prediction(Base):
    __tablename__ = "Predictions"

    name = Column(String(50), primary_key=True)
    Prediction = Column(String(50))
    id = Column(ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"))
    created = Column(TIMESTAMP)

    Predicted_confidence = Column(Float)
    Real_Player = Column(Float)
    PVM_Melee_bot = Column(Float)
    Smithing_bot = Column(Float)
    Magic_bot = Column(Float)
    Fishing_bot = Column(Float)
    Mining_bot = Column(Float)
    Crafting_bot = Column(Float)
    PVM_Ranged_Magic_bot = Column(Float)
    PVM_Ranged_bot = Column(Float)
    Hunter_bot = Column(Float)
    Fletching_bot = Column(Float)
    Clue_Scroll_bot = Column(Float)
    LMS_bot = Column(Float)
    Agility_bot = Column(Float)
    Wintertodt_bot = Column(Float)
    Runecrafting_bot = Column(Float)
    Zalcano_bot = Column(Float)
    Woodcutting_bot = Column(Float)
    Thieving_bot = Column(Float)
    Soul_Wars_bot = Column(Float)
    Cooking_bot = Column(Float)
    Vorkath_bot = Column(Float)
    Barrows_bot = Column(Float)
    Herblore_bot = Column(Float)
    Zulrah_bot = Column(Float)
    Unknown_bot = Column(Float)
    Gauntlet_bot = Column(Float)
    Nex_bot = Column(Float)


class Clan(Base):
    __tablename__ = "Clan"

    id = Column(Integer, primary_key=True)
    member_id = Column(BigInteger, nullable=False)
    rank_id = Column(Integer, nullable=False)
    killcount = Column(Integer)


class LabelJagex(Base):
    __tablename__ = "LabelJagex"

    id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False)


class Label(Base):
    __tablename__ = "Labels"

    id = Column(Integer, primary_key=True)
    label = Column(VARCHAR(50), nullable=False, unique=True)


class PlayerBotConfirmation(Base):
    __tablename__ = "PlayerBotConfirmation"
    __table_args__ = (
        Index("Unique_player_label_bot", "player_id", "label_id", "bot", unique=True),
    )

    id = Column(Integer, primary_key=True)
    ts = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    player_id = Column(Integer, nullable=False)
    label_id = Column(Integer, nullable=False)
    bot = Column(TINYINT(1), nullable=False)


class PlayersChange(Base):
    __tablename__ = "PlayersChanges"

    id = Column(Integer, primary_key=True)
    ChangeDate = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    player_id = Column(Integer, nullable=False)
    name = Column(String(15), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
    possible_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_player = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    label_id = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    label_jagex = Column(Integer, nullable=False, server_default=text("'0'"))


class Token(Base):
    __tablename__ = "Tokens"

    id = Column(Integer, primary_key=True)
    player_name = Column(VARCHAR(50), nullable=False)
    token = Column(String(50), nullable=False)
    request_highscores = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    verify_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    create_token = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    verify_players = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    discord_general = Column(TINYINT(1), nullable=False, server_default=text("'0'"))


"""
    API token handling
"""


class ApiPermission(Base):
    __tablename__ = "apiPermissions"

    id = Column(Integer, primary_key=True)
    permission = Column(Text, nullable=False)


class ApiUser(Base):
    __tablename__ = "apiUser"

    id = Column(Integer, primary_key=True)
    username = Column(TINYTEXT, nullable=False)
    token = Column(TINYTEXT, nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    last_used = Column(DateTime)
    ratelimit = Column(Integer, nullable=False, server_default=text("'100'"))
    is_active = Column(TINYINT(1), nullable=False, server_default=text("'1'"))


class ApiUsage(Base):
    __tablename__ = "apiUsage"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(
        ForeignKey("apiUser.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    timestamp = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    route = Column(Text, nullable=False)

    user = relationship("ApiUser")


class ApiUserPerm(Base):
    __tablename__ = "apiUserPerms"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        ForeignKey("apiUser.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    permission_id = Column(
        ForeignKey("apiPermissions.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )

    permission = relationship("ApiPermission")
    user = relationship("ApiUser")


class PlayerHiscoreDataChange(Base):
    __tablename__ = "playerHiscoreDataChanges"

    id = Column(Integer, primary_key=True)
    playerHiscoreDataID = Column(Integer, nullable=False)
    old_player_id = Column(Integer, nullable=False)
    new_player_id = Column(Integer, nullable=False)
    old_total = Column(Integer, nullable=False)
    new_total = Column(Integer, nullable=False)
    change_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class RegionIDName(Base):
    __tablename__ = "regionIDNames"

    entry_ID = Column(Integer, primary_key=True)
    region_ID = Column(Integer, nullable=False, unique=True)
    z_axis = Column(Integer, server_default=text("'0'"))
    region_name = Column(Text, nullable=False)


class ReportLatest(Base):
    __tablename__ = "reportLatest"

    report_id = Column(BigInteger)
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


class SentToJagex(Base):
    __tablename__ = "sentToJagex"

    entry = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)


class Player(Base):
    __tablename__ = "Players"

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(DateTime)
    possible_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_ban = Column(
        TINYINT(1), nullable=False, index=True, server_default=text("'0'")
    )
    confirmed_player = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    label_id = Column(
        ForeignKey("Labels.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )
    label_jagex = Column(Integer, nullable=False, server_default=text("'0'"))
    ironman = Column(TINYINT)
    hardcore_ironman = Column(TINYINT)
    ultimate_ironman = Column(TINYINT)
    normalized_name = Column(Text)

    label = relationship("Label")


class PredictionsFeedback(Base):
    __tablename__ = "PredictionsFeedback"
    __table_args__ = (
        Index("Unique_Vote", "prediction", "subject_id", "voter_id", unique=True),
    )

    id = Column(Integer, primary_key=True)
    ts = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    voter_id = Column(
        ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    subject_id = Column(
        ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    prediction = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    vote = Column(Integer, nullable=False, server_default=text("'0'"))
    feedback_text = Column(TEXT)
    reviewed = Column(TINYINT, nullable=False, server_default=text("'0'"))
    reviewer_id = Column(
        ForeignKey("Tokens.id", ondelete="RESTRICT", onupdate="RESTRICT"), index=True
    )
    user_notified = Column(TINYINT, nullable=False, server_default=text("'0'"))
    proposed_label = Column(String(50))

    reviewer = relationship("Token")
    subject = relationship(
        "Player", primaryjoin="PredictionsFeedback.subject_id == Player.id"
    )
    voter = relationship(
        "Player", primaryjoin="PredictionsFeedback.voter_id == Player.id"
    )


class Report(Base):
    __tablename__ = "Reports"
    __table_args__ = (
        Index(
            "Unique_Report",
            "reportedID",
            "reportingID",
            "region_id",
            "manual_detect",
            unique=True,
        ),
        Index("reportedID", "reportedID", "region_id"),
    )

    ID = Column(BigInteger, primary_key=True)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    reportedID = Column(
        ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    reportingID = Column(
        ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
    region_id = Column(Integer, nullable=False)
    x_coord = Column(Integer, nullable=False)
    y_coord = Column(Integer, nullable=False)
    z_coord = Column(Integer, nullable=False)
    timestamp = Column(
        TIMESTAMP, nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP")
    )
    manual_detect = Column(TINYINT(1))
    on_members_world = Column(Integer)
    on_pvp_world = Column(TINYINT)
    world_number = Column(Integer, index=True)
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

    Player = relationship("Player", primaryjoin="Report.reportedID == Player.id")
    Player1 = relationship("Player", primaryjoin="Report.reportingID == Player.id")


class stgReport(Base):
    __tablename__ = "stgReports"

    ID = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    reportedID = Column(nullable=False)
    reportingID = Column(nullable=False)
    region_id = Column(Integer, nullable=False)
    x_coord = Column(Integer, nullable=False)
    y_coord = Column(Integer, nullable=False)
    z_coord = Column(Integer, nullable=False)
    timestamp = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
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


class playerHiscoreData(Base):
    __tablename__ = "playerHiscoreData"
    __table_args__ = (
        Index("Unique_player_time", "Player_id", "timestamp", unique=True),
        Index("Unique_player_date", "Player_id", "ts_date", unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    ts_date = Column(Date)
    Player_id = Column(
        ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )
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
    nex = Column(Integer)
    phosanis_nightmare = Column(Integer)
    obor = Column(Integer)
    phantom_muspah = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
    tempoross = Column(Integer)
    the_gauntlet = Column(Integer)
    the_corrupted_gauntlet = Column(Integer)
    theatre_of_blood = Column(Integer)
    theatre_of_blood_hard = Column(Integer)
    thermonuclear_smoke_devil = Column(Integer)
    tombs_of_amascut = Column(Integer)
    tombs_of_amascut_expert = Column(Integer)
    tzkal_zuk = Column(Integer)
    tztok_jad = Column(Integer)
    venenatis = Column(Integer)
    vetion = Column(Integer)
    vorkath = Column(Integer)
    wintertodt = Column(Integer)
    zalcano = Column(Integer)
    zulrah = Column(Integer)

    # New columns added
    rifts_closed = Column(Integer, default=0)
    artio = Column(Integer, default=0)
    calvarion = Column(Integer, default=0)
    duke_sucellus = Column(Integer, default=0)
    spindel = Column(Integer, default=0)
    the_leviathan = Column(Integer, default=0)
    the_whisperer = Column(Integer, default=0)
    vardorvis = Column(Integer, default=0)

    Player = relationship("Player")


class PlayerHiscoreDataLatest(Base):
    __tablename__ = "playerHiscoreDataLatest"

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    ts_date = Column(Date)
    Player_id = Column(
        ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        unique=True,
    )
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
    nex = Column(Integer)
    phosanis_nightmare = Column(Integer)
    obor = Column(Integer)
    phantom_muspah = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
    Tempoross = Column(Integer, nullable=False)
    the_gauntlet = Column(Integer)
    the_corrupted_gauntlet = Column(Integer)
    theatre_of_blood = Column(Integer)
    theatre_of_blood_hard = Column(Integer)
    thermonuclear_smoke_devil = Column(Integer)
    tombs_of_amascut = Column(Integer)
    tombs_of_amascut_expert = Column(Integer)
    tzkal_zuk = Column(Integer)
    tztok_jad = Column(Integer)
    venenatis = Column(Integer)
    vetion = Column(Integer)
    vorkath = Column(Integer)
    wintertodt = Column(Integer)
    zalcano = Column(Integer)
    zulrah = Column(Integer)

    Player = relationship("Player")


class PlayerHiscoreDataXPChange(Base):
    __tablename__ = "playerHiscoreDataXPChange"

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    ts_date = Column(Date)
    Player_id = Column(
        ForeignKey("Players.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
        index=True,
    )
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
    nex = Column(Integer)
    obor = Column(Integer)
    phantom_muspah = Column(Integer)
    phosanis_nightmare = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
    Tempoross = Column(Integer, nullable=False)
    the_gauntlet = Column(Integer)
    the_corrupted_gauntlet = Column(Integer)
    theatre_of_blood = Column(Integer)
    theatre_of_blood_hard = Column(Integer)
    thermonuclear_smoke_devil = Column(Integer)
    tombs_of_amascut = Column(Integer)
    tombs_of_amascut_expert = Column(Integer)
    tzkal_zuk = Column(Integer)
    tztok_jad = Column(Integer)
    venenatis = Column(Integer)
    vetion = Column(Integer)
    vorkath = Column(Integer)
    wintertodt = Column(Integer)
    zalcano = Column(Integer)
    zulrah = Column(Integer)

    Player = relationship("Player")


class playerReports(Base):
    __tablename__ = "playerReports"
    reporting_id = Column(Integer, ForeignKey("Players.id"), primary_key=True)
    reported_id = Column(Integer, ForeignKey("Players.id"), primary_key=True)

    reporting_player = relationship(
        "Player", primaryjoin="playerReports.reporting_id == Player.id"
    )
    reported_player = relationship(
        "Player", primaryjoin="playerReports.reported_id == Player.id"
    )


class playerReportsManual(Base):
    __tablename__ = "playerReportsManual"

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    reporting_id = Column(Integer, ForeignKey("Players.id"), primary_key=True)
    reported_id = Column(Integer, ForeignKey("Players.id"), primary_key=True)

    reporting_player = relationship(
        "Player", primaryjoin="playerReportsManual.reporting_id == Player.id"
    )
    reported_player = relationship(
        "Player", primaryjoin="playerReportsManual.reported_id == Player.id"
    )
