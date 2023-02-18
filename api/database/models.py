from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    text,
    DECIMAL,
)
from sqlalchemy.dialects.mysql import TEXT, TINYINT, TINYTEXT, VARCHAR
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class LabelJagex(Base):
    __tablename__ = "LabelJagex"

    id = Column(Integer, primary_key=True)
    label = Column(String(50), nullable=False)


class Labels(Base):
    __tablename__ = "Labels"
    __table_args__ = (Index("Unique_label", "label", unique=True),)

    id = Column(Integer, primary_key=True)
    label = Column(VARCHAR(50), nullable=False)

    Players = relationship("Players", back_populates="label")


class PlayersChanges(Base):
    __tablename__ = "PlayersChanges"
    __table_args__ = (Index("FK_label_id", "label_id"),)

    id = Column(Integer, primary_key=True)
    ChangeDate = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    player_id = Column(Integer, nullable=False)
    name = Column(String(15), nullable=False)
    created_at = Column(DateTime, nullable=False)
    possible_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_player = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    label_id = Column(Integer, nullable=False, server_default=text("'0'"))
    label_jagex = Column(Integer, nullable=False, server_default=text("'0'"))
    updated_at = Column(DateTime)


class Tokens(Base):
    __tablename__ = "Tokens"

    id = Column(Integer, primary_key=True)
    player_name = Column(VARCHAR(50), nullable=False)
    token = Column(String(50), nullable=False)
    request_highscores = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    verify_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    create_token = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    verify_players = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    discord_general = Column(TINYINT(1), nullable=False, server_default=text("'0'"))

    PredictionsFeedback = relationship("PredictionsFeedback", back_populates="reviewer")


class ApiPermissions(Base):
    __tablename__ = "apiPermissions"

    id = Column(Integer, primary_key=True)
    permission = Column(Text, nullable=False)

    apiUserPerms = relationship("ApiUserPerms", back_populates="permission")


class ApiUser(Base):
    __tablename__ = "apiUser"

    id = Column(Integer, primary_key=True)
    username = Column(TINYTEXT, nullable=False)
    token = Column(TINYTEXT, nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    ratelimit = Column(Integer, nullable=False, server_default=text("'100'"))
    is_active = Column(TINYINT(1), nullable=False, server_default=text("'1'"))
    last_used = Column(DateTime)

    apiUsage = relationship("ApiUsage", back_populates="user")
    apiUserPerms = relationship("ApiUserPerms", back_populates="user")


class RegionIDNames(Base):
    __tablename__ = "regionIDNames"
    __table_args__ = (Index("region_ID", "region_ID", unique=True),)

    entry_ID = Column(Integer, primary_key=True)
    region_ID = Column(Integer, nullable=False)
    region_name = Column(Text, nullable=False)
    z_axis = Column(Integer, server_default=text("'0'"))


class ReportLatest(Base):
    __tablename__ = "reportLatest"

    reported_id = Column(Integer, primary_key=True)
    region_id = Column(Integer, nullable=False)
    x_coord = Column(Integer, nullable=False)
    y_coord = Column(Integer, nullable=False)
    z_coord = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    report_id = Column(BigInteger)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
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


class StgReports(Base):
    __tablename__ = "stgReports"

    ID = Column(BigInteger, primary_key=True)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    reportedID = Column(Integer, nullable=False)
    reportingID = Column(Integer, nullable=False)
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


class Players(Base):
    __tablename__ = "Players"
    __table_args__ = (
        ForeignKeyConstraint(
            ["label_id"],
            ["Labels.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_label_id",
        ),
        Index("FK_label_id", "label_id"),
        Index("Unique_name", "name", unique=True),
        Index("confirmed_ban_idx", "confirmed_ban"),
        Index("normal_name_index", "normalized_name"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    possible_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_ban = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    confirmed_player = Column(TINYINT(1), nullable=False, server_default=text("'0'"))
    label_id = Column(Integer, nullable=False, server_default=text("'0'"))
    label_jagex = Column(Integer, nullable=False, server_default=text("'0'"))
    updated_at = Column(DateTime)
    ironman = Column(TINYINT)
    hardcore_ironman = Column(TINYINT)
    ultimate_ironman = Column(TINYINT)
    normalized_name = Column(Text)

    label = relationship("Labels", back_populates="Players")
    PredictionsFeedback = relationship(
        "PredictionsFeedback",
        foreign_keys="[PredictionsFeedback.subject_id]",
        back_populates="subject",
    )
    PredictionsFeedback_ = relationship(
        "PredictionsFeedback",
        foreign_keys="[PredictionsFeedback.voter_id]",
        back_populates="voter",
    )
    Reports = relationship(
        "Reports", foreign_keys="[Reports.reportedID]", back_populates="Players_"
    )
    Reports_ = relationship(
        "Reports", foreign_keys="[Reports.reportingID]", back_populates="Players1"
    )
    playerHiscoreData = relationship("PlayerHiscoreData", back_populates="Player")
    playerHiscoreDataLatest = relationship(
        "PlayerHiscoreDataLatest", back_populates="Player"
    )
    playerHiscoreDataXPChange = relationship(
        "PlayerHiscoreDataXPChange", back_populates="Player"
    )


class ApiUsage(Base):
    __tablename__ = "apiUsage"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["apiUser.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_apiUsage_apiUser",
        ),
        Index("FK_apiUsage_apiUser", "user_id"),
    )

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    route = Column(Text)

    user = relationship("ApiUser", back_populates="apiUsage")


class ApiUserPerms(Base):
    __tablename__ = "apiUserPerms"
    __table_args__ = (
        ForeignKeyConstraint(
            ["permission_id"],
            ["apiPermissions.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_apiUserPerms_apiPermission",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["apiUser.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_apiUserPerms_apiUser",
        ),
        Index("FK_apiUserPerms_apiPermission", "permission_id"),
        Index("FK_apiUserPerms_apiUser", "user_id"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    permission_id = Column(Integer, nullable=False)

    permission = relationship("ApiPermissions", back_populates="apiUserPerms")
    user = relationship("ApiUser", back_populates="apiUserPerms")


class PredictionsFeedback(Base):
    __tablename__ = "PredictionsFeedback"
    __table_args__ = (
        ForeignKeyConstraint(
            ["reviewer_id"],
            ["Tokens.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="Reviewer_ID",
        ),
        ForeignKeyConstraint(
            ["subject_id"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="Subject_ID",
        ),
        ForeignKeyConstraint(
            ["voter_id"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="Voter_ID",
        ),
        Index("Reviewer_ID", "reviewer_id"),
        Index("Subject_ID", "subject_id"),
        Index("Unique_Vote", "prediction", "subject_id", "voter_id", unique=True),
        Index("Voter_ID", "voter_id"),
    )

    id = Column(Integer, primary_key=True)
    ts = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    voter_id = Column(Integer, nullable=False)
    subject_id = Column(Integer, nullable=False)
    prediction = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    vote = Column(Integer, nullable=False, server_default=text("'0'"))
    reviewed = Column(TINYINT, nullable=False, server_default=text("'0'"))
    user_notified = Column(TINYINT, nullable=False, server_default=text("'0'"))
    feedback_text = Column(TEXT)
    reviewer_id = Column(Integer)
    proposed_label = Column(String(50))

    reviewer = relationship("Tokens", back_populates="PredictionsFeedback")
    subject = relationship(
        "Players", foreign_keys=[subject_id], back_populates="PredictionsFeedback"
    )
    voter = relationship(
        "Players", foreign_keys=[voter_id], back_populates="PredictionsFeedback_"
    )


class Reports(Base):
    __tablename__ = "Reports"
    __table_args__ = (
        ForeignKeyConstraint(
            ["reportedID"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_Reported_Players_id",
        ),
        ForeignKeyConstraint(
            ["reportingID"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_Reporting_Players_id",
        ),
        Index(
            "Unique_Report",
            "reportedID",
            "reportingID",
            "region_id",
            "manual_detect",
            unique=True,
        ),
        Index("idx_heatmap", "reportedID", "timestamp", "region_id"),
        Index("idx_reportedID_regionDI", "reportedID", "region_id"),
        Index("idx_reportingID", "reportingID"),
    )

    ID = Column(BigInteger, primary_key=True)
    created_at = Column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    reportedID = Column(Integer, nullable=False)
    reportingID = Column(Integer, nullable=False)
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

    Players_ = relationship(
        "Players", foreign_keys=[reportedID], back_populates="Reports"
    )
    Players1 = relationship(
        "Players", foreign_keys=[reportingID], back_populates="Reports_"
    )


class PlayerHiscoreData(Base):
    __tablename__ = "playerHiscoreData"
    __table_args__ = (
        ForeignKeyConstraint(
            ["Player_id"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_Players_id",
        ),
        Index("Unique_player_date", "Player_id", "ts_date", unique=True),
        Index("Unique_player_time", "timestamp", "Player_id", unique=True),
    )

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    Player_id = Column(Integer, nullable=False)
    ts_date = Column(Date)
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
    nex = Column(Integer)
    nightmare = Column(Integer)
    phosanis_nightmare = Column(Integer, server_default=text("'0'"))
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

    Player = relationship("Players", back_populates="playerHiscoreData")


class PlayerHiscoreDataLatest(Base):
    __tablename__ = "playerHiscoreDataLatest"
    __table_args__ = (
        ForeignKeyConstraint(
            ["Player_id"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_latest_player",
        ),
        Index("Unique_player", "Player_id", unique=True),
    )

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    Player_id = Column(Integer, nullable=False)
    Tempoross = Column(Integer, nullable=False)
    ts_date = Column(Date)
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
    nex = Column(Integer)
    nightmare = Column(Integer)
    phosanis_nightmare = Column(Integer)
    obor = Column(Integer)
    phantom_muspah = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
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

    Player = relationship("Players", back_populates="playerHiscoreDataLatest")


class PlayerHiscoreDataXPChange(Base):
    __tablename__ = "playerHiscoreDataXPChange"
    __table_args__ = (
        ForeignKeyConstraint(
            ["Player_id"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="fk_phd_xp_pl",
        ),
        Index("fk_phd_xp_pl", "Player_id"),
    )

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    Player_id = Column(Integer, nullable=False)
    ts_date = Column(Date)
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
    nex = Column(Integer)
    nightmare = Column(Integer)
    obor = Column(Integer)
    phantom_muspah = Column(Integer)
    phosanis_nightmare = Column(Integer)
    sarachnis = Column(Integer)
    scorpia = Column(Integer)
    skotizo = Column(Integer)
    Tempoross = Column(Integer)
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

    Player = relationship("Players", back_populates="playerHiscoreDataXPChange")


class XXStats(Base):
    __tablename__ = "xx_stats"
    player_count = Column(BigInteger, nullable=False, server_default="0")
    confirmed_ban = Column(TINYINT(1), nullable=False, server_default="0")
    confirmed_player = Column(TINYINT(1), nullable=False, server_default="0")
    created = Column(
        DateTime, nullable=False, server_default="CURRENT_TIMESTAMP", primary_key=True
    )


class Predictions(Base):
    __tablename__ = "Predictions"
    table_args = (
        ForeignKeyConstraint(
            ["id"],
            ["Players.id"],
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            name="FK_pred_player_id",
        ),
        Index("FK_pred_player_id", "id"),
        Index("name", "name", unique=True),
    )

    name = Column(String(12))
    prediction = Column(String(50))
    id = Column(Integer, primary_key=True)
    created = Column(TIMESTAMP)
    Predicted_confidence = Column(DECIMAL(5, 2))
    Real_Player = Column(DECIMAL(5, 2))
    Unknown_bot = Column(DECIMAL(5, 2), server_default="0.00")
    PVM_Melee_bot = Column(DECIMAL(5, 2))
    Smithing_bot = Column(DECIMAL(5, 2))
    Magic_bot = Column(DECIMAL(5, 2))
    Fishing_bot = Column(DECIMAL(5, 2))
    Mining_bot = Column(DECIMAL(5, 2))
    Crafting_bot = Column(DECIMAL(5, 2))
    PVM_Ranged_Magic_bot = Column(DECIMAL(5, 2))
    PVM_Ranged_bot = Column(DECIMAL(5, 2))
    Hunter_bot = Column(DECIMAL(5, 2))
    Fletching_bot = Column(DECIMAL(5, 2))
    Clue_Scroll_bot = Column(DECIMAL(5, 2))
    LMS_bot = Column(DECIMAL(5, 2))
    Agility_bot = Column(DECIMAL(5, 2))
    Wintertodt_bot = Column(DECIMAL(5, 2))
    Runecrafting_bot = Column(DECIMAL(5, 2))
    Zalcano_bot = Column(DECIMAL(5, 2))
    Woodcutting_bot = Column(DECIMAL(5, 2))
    Thieving_bot = Column(DECIMAL(5, 2))
    Soul_Wars_bot = Column(DECIMAL(5, 2))
    Cooking_bot = Column(DECIMAL(5, 2))
    Vorkath_bot = Column(DECIMAL(5, 2))
    Barrows_bot = Column(DECIMAL(5, 2))
    Herblore_bot = Column(DECIMAL(5, 2))
    Zulrah_bot = Column(DECIMAL(5, 2))
