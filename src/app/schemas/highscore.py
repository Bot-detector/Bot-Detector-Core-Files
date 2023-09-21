from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional


class PlayerHiscoreData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    timestamp: datetime = datetime.utcnow()
    ts_date: Optional[date] = None
    Player_id: int
    total: int
    attack: int
    defence: int
    strength: int
    hitpoints: int
    ranged: int
    prayer: int
    magic: int
    cooking: int
    woodcutting: int
    fletching: int
    fishing: int
    firemaking: int
    crafting: int
    smithing: int
    mining: int
    herblore: int
    agility: int
    thieving: int
    slayer: int
    farming: int
    runecraft: int
    hunter: int
    construction: int
    league: int
    bounty_hunter_hunter: int
    bounty_hunter_rogue: int
    cs_all: int
    cs_beginner: int
    cs_easy: int
    cs_medium: int
    cs_hard: int
    cs_elite: int
    cs_master: int
    lms_rank: int
    soul_wars_zeal: int
    abyssal_sire: int
    alchemical_hydra: int
    barrows_chests: int
    bryophyta: int
    callisto: int
    cerberus: int
    chambers_of_xeric: int
    chambers_of_xeric_challenge_mode: int
    chaos_elemental: int
    chaos_fanatic: int
    commander_zilyana: int
    corporeal_beast: int
    crazy_archaeologist: int
    dagannoth_prime: int
    dagannoth_rex: int
    dagannoth_supreme: int
    deranged_archaeologist: int
    general_graardor: int
    giant_mole: int
    grotesque_guardians: int
    hespori: int
    kalphite_queen: int
    king_black_dragon: int
    kraken: int
    kreearra: int
    kril_tsutsaroth: int
    mimic: int
    nightmare: int
    nex: int = 0
    phosanis_nightmare: int
    obor: int
    phantom_muspah: int = 0
    sarachnis: int
    scorpia: int
    skotizo: int
    tempoross: int = 0
    the_gauntlet: int
    the_corrupted_gauntlet: int
    theatre_of_blood: int
    theatre_of_blood_hard: int = 0
    thermonuclear_smoke_devil: int
    tombs_of_amascut: int = 0
    tombs_of_amascut_expert: int = 0
    tzkal_zuk: int
    tztok_jad: int
    venenatis: int
    vetion: int
    vorkath: int
    wintertodt: int
    zalcano: int
    zulrah: int
    rifts_closed: int = 0
    artio: int = 0
    calvarion: int = 0
    duke_sucellus: int = 0
    spindel: int = 0
    the_leviathan: int = 0
    the_whisperer: int = 0
    vardorvis: int = 0
