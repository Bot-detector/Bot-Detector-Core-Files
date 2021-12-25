from typing import Optional

from api.database.database import EngineType, get_session
from api.database.functions import sqlalchemy_result, verify_token
from api.database.models import (PlayerHiscoreDataLatest,
                                 PlayerHiscoreDataXPChange, playerHiscoreData, Player)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.sql.expression import insert, select

router = APIRouter()


class hiscore(BaseModel):
    '''
        Hiscore entry data
    '''
    player_id: int
    total: int
    Attack: int
    Defence: int
    Strength: int
    Hitpoints: int
    Ranged: int
    Prayer: int
    Magic: int
    Cooking: int
    Woodcutting: int
    Fletching: int
    Fishing: int
    Firemaking: int
    Crafting: int
    Smithing: int
    Mining: int
    Herblore: int
    Agility: int
    Thieving: int
    Slayer: int
    Farming: int
    Runecraft: int
    Hunter: int
    Construction: int
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
    obor: int
    phosanis_nightmare : int
    sarachnis: int
    scorpia: int
    skotizo: int
    tempoross: int
    the_gauntlet: int
    the_corrupted_gauntlet: int
    theatre_of_blood: int
    theatre_of_blood_hard: int
    thermonuclear_smoke_devil: int
    tzkal_zuk: int
    tztok_jad: int
    venenatis: int
    vetion: int
    vorkath: int
    wintertodt: int
    zalcano: int
    zulrah: int


@router.get("/v1/hiscore/", tags=["Hiscore"])
async def get_player_hiscore_data(
    token: str,
    player_id: Optional[int] = None,
    total: Optional[int] = None,
    Attack: Optional[int] = None,
    Defence: Optional[int] = None,
    Strength: Optional[int] = None,
    Hitpoints: Optional[int] = None,
    Ranged: Optional[int] = None,
    Prayer: Optional[int] = None,
    Magic: Optional[int] = None,
    Cooking: Optional[int] = None,
    Woodcutting: Optional[int] = None,
    Fletching: Optional[int] = None,
    Fishing: Optional[int] = None,
    Firemaking: Optional[int] = None,
    Crafting: Optional[int] = None,
    Smithing: Optional[int] = None,
    Mining: Optional[int] = None,
    Herblore: Optional[int] = None,
    Agility: Optional[int] = None,
    Thieving: Optional[int] = None,
    Slayer: Optional[int] = None,
    Farming: Optional[int] = None,
    Runecraft: Optional[int] = None,
    Hunter: Optional[int] = None,
    Construction: Optional[int] = None,
    league: Optional[int] = None,
    bounty_hunter_hunter: Optional[int] = None,
    bounty_hunter_rogue: Optional[int] = None,
    cs_all: Optional[int] = None,
    cs_beginner: Optional[int] = None,
    cs_easy: Optional[int] = None,
    cs_medium: Optional[int] = None,
    cs_hard: Optional[int] = None,
    cs_elite: Optional[int] = None,
    cs_master: Optional[int] = None,
    lms_rank: Optional[int] = None,
    soul_wars_zeal: Optional[int] = None,
    abyssal_sire: Optional[int] = None,
    alchemical_hydra: Optional[int] = None,
    barrows_chests: Optional[int] = None,
    bryophyta: Optional[int] = None,
    callisto: Optional[int] = None,
    cerberus: Optional[int] = None,
    chambers_of_xeric: Optional[int] = None,
    chambers_of_xeric_challenge_mode: Optional[int] = None,
    chaos_elemental: Optional[int] = None,
    chaos_fanatic: Optional[int] = None,
    commander_zilyana: Optional[int] = None,
    corporeal_beast: Optional[int] = None,
    crazy_archaeologist: Optional[int] = None,
    dagannoth_prime: Optional[int] = None,
    dagannoth_rex: Optional[int] = None,
    dagannoth_supreme: Optional[int] = None,
    deranged_archaeologist: Optional[int] = None,
    general_graardor: Optional[int] = None,
    giant_mole: Optional[int] = None,
    grotesque_guardians: Optional[int] = None,
    hespori: Optional[int] = None,
    kalphite_queen: Optional[int] = None,
    king_black_dragon: Optional[int] = None,
    kraken: Optional[int] = None,
    kreearra: Optional[int] = None,
    kril_tsutsaroth: Optional[int] = None,
    mimic: Optional[int] = None,
    nightmare: Optional[int] = None,
    obor: Optional[int] = None,
    phosanis_nightmare : Optional[int] = None,
    sarachnis: Optional[int] = None,
    scorpia: Optional[int] = None,
    skotizo: Optional[int] = None,
    tempoross: Optional[int] = None,
    the_gauntlet: Optional[int] = None,
    the_corrupted_gauntlet: Optional[int] = None,
    theatre_of_blood: Optional[int] = None,
    theatre_of_blood_hard: Optional[int] = None,
    thermonuclear_smoke_devil: Optional[int] = None,
    tzkal_zuk: Optional[int] = None,
    tztok_jad: Optional[int] = None,
    venenatis: Optional[int] = None,
    vetion: Optional[int] = None,
    vorkath: Optional[int] = None,
    wintertodt: Optional[int] = None,
    zalcano: Optional[int] = None,
    zulrah: Optional[int] = None,
    row_count: int = 100_000,
    page: int = 1
):
    '''
        Select daily scraped hiscore data by player_id
    '''
    # verify token
    await verify_token(token, verification='verify_ban', route='[GET]/v1/hiscore')

    # query
    table = playerHiscoreData
    sql = select(table)
    
    if player_id == total == Attack == Defence == Strength == Hitpoints == Ranged == Prayer == Magic == Cooking == Woodcutting == Fletching == Fishing == Firemaking == Crafting == Smithing == Mining == Herblore == Agility == Thieving == Slayer == Farming == Runecraft == Hunter == Construction == league == bounty_hunter_hunter == bounty_hunter_rogue == cs_all == cs_beginner == cs_easy == cs_medium == cs_hard == cs_elite == cs_master == lms_rank == soul_wars_zeal == abyssal_sire == alchemical_hydra == barrows_chests == bryophyta == callisto == cerberus == chambers_of_xeric == chambers_of_xeric_challenge_mode == chaos_elemental == chaos_fanatic == commander_zilyana == corporeal_beast == crazy_archaeologist == dagannoth_prime == dagannoth_rex == dagannoth_supreme == deranged_archaeologist == general_graardor == giant_mole == grotesque_guardians == hespori == kalphite_queen == king_black_dragon == kraken == kreearra == kril_tsutsaroth == mimic == nightmare == obor == phosanis_nightmare  == sarachnis == scorpia == skotizo == tempoross == the_gauntlet == the_corrupted_gauntlet == theatre_of_blood == theatre_of_blood_hard == thermonuclear_smoke_devil == tzkal_zuk == tztok_jad == venenatis == vetion == vorkath == wintertodt == zalcano == zulrah == None:
        raise HTTPException(status_code=404, detail="No param given")
    
    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)
    if not total == None:
        sql = sql.where(table.total == total)
    if not Attack == None:
        sql = sql.where(table.Attack == Attack)
    if not Defence == None:
        sql = sql.where(table.Defence == Defence)
    if not Strength == None:
        sql = sql.where(table.Strength == Strength)
    if not Hitpoints == None:
        sql = sql.where(table.Hitpoints == Hitpoints)
    if not Ranged == None:
        sql = sql.where(table.Ranged == Ranged)
    if not Prayer == None:
        sql = sql.where(table.Prayer == Prayer)
    if not Magic == None:
        sql = sql.where(table.Magic == Magic)
    if not Cooking == None:
        sql = sql.where(table.Cooking == Cooking)
    if not Woodcutting == None:
        sql = sql.where(table.Woodcutting == Woodcutting)
    if not Fletching == None:
        sql = sql.where(table.Fletching == Fletching)
    if not Fishing == None:
        sql = sql.where(table.Fishing == Fishing)
    if not Firemaking == None:
        sql = sql.where(table.Firemaking == Firemaking)
    if not Crafting == None:
        sql = sql.where(table.Crafting == Crafting)
    if not Smithing == None:
        sql = sql.where(table.Smithing == Smithing)
    if not Mining == None:
        sql = sql.where(table.Mining == Mining)
    if not Herblore == None:
        sql = sql.where(table.Herblore == Herblore)
    if not Agility == None:
        sql = sql.where(table.Agility == Agility)
    if not Thieving == None:
        sql = sql.where(table.Thieving == Thieving)
    if not Slayer == None:
        sql = sql.where(table.Slayer == Slayer)
    if not Farming == None:
        sql = sql.where(table.Farming == Farming)
    if not Runecraft == None:
        sql = sql.where(table.Runecraft == Runecraft)
    if not Hunter == None:
        sql = sql.where(table.Hunter == Hunter)
    if not Construction == None:
        sql = sql.where(table.Construction == Construction)
    if not league == None:
        sql = sql.where(table.league == league)
    if not bounty_hunter_hunter == None:
        sql = sql.where(table.bounty_hunter_hunter == bounty_hunter_hunter)
    if not bounty_hunter_rogue == None:
        sql = sql.where(table.bounty_hunter_rogue == bounty_hunter_rogue)
    if not cs_all == None:
        sql = sql.where(table.cs_all == cs_all)
    if not cs_beginner == None:
        sql = sql.where(table.cs_beginner == cs_beginner)
    if not cs_easy == None:
        sql = sql.where(table.cs_easy == cs_easy)
    if not cs_medium == None:
        sql = sql.where(table.cs_medium == cs_medium)
    if not cs_hard == None:
        sql = sql.where(table.cs_hard == cs_hard)
    if not cs_elite == None:
        sql = sql.where(table.cs_elite == cs_elite)
    if not cs_master == None:
        sql = sql.where(table.cs_master == cs_master)
    if not lms_rank == None:
        sql = sql.where(table.lms_rank == lms_rank)
    if not soul_wars_zeal == None:
        sql = sql.where(table.soul_wars_zeal == soul_wars_zeal)
    if not abyssal_sire == None:
        sql = sql.where(table.abyssal_sire == abyssal_sire)
    if not alchemical_hydra == None:
        sql = sql.where(table.alchemical_hydra == alchemical_hydra)
    if not barrows_chests == None:
        sql = sql.where(table.barrows_chests == barrows_chests)
    if not bryophyta == None:
        sql = sql.where(table.bryophyta == bryophyta)
    if not callisto == None:
        sql = sql.where(table.callisto == callisto)
    if not cerberus == None:
        sql = sql.where(table.cerberus == cerberus)
    if not chambers_of_xeric == None:
        sql = sql.where(table.chambers_of_xeric == chambers_of_xeric)
    if not chambers_of_xeric_challenge_mode == None:
        sql = sql.where(table.chambers_of_xeric_challenge_mode == chambers_of_xeric_challenge_mode)
    if not chaos_elemental == None:
        sql = sql.where(table.chaos_elemental == chaos_elemental)
    if not chaos_fanatic == None:
        sql = sql.where(table.chaos_fanatic == chaos_fanatic)
    if not commander_zilyana == None:
        sql = sql.where(table.commander_zilyana == commander_zilyana)
    if not corporeal_beast == None:
        sql = sql.where(table.corporeal_beast == corporeal_beast)
    if not crazy_archaeologist == None:
        sql = sql.where(table.crazy_archaeologist == crazy_archaeologist)
    if not dagannoth_prime == None:
        sql = sql.where(table.dagannoth_prime == dagannoth_prime)
    if not dagannoth_rex == None:
        sql = sql.where(table.dagannoth_rex == dagannoth_rex)
    if not dagannoth_supreme == None:
        sql = sql.where(table.dagannoth_supreme == dagannoth_supreme)
    if not deranged_archaeologist == None:
        sql = sql.where(table.deranged_archaeologist == deranged_archaeologist)
    if not general_graardor == None:
        sql = sql.where(table.general_graardor == general_graardor)
    if not giant_mole == None:
        sql = sql.where(table.giant_mole == giant_mole)
    if not grotesque_guardians == None:
        sql = sql.where(table.grotesque_guardians == grotesque_guardians)
    if not hespori == None:
        sql = sql.where(table.hespori == hespori)
    if not kalphite_queen == None:
        sql = sql.where(table.kalphite_queen == kalphite_queen)
    if not king_black_dragon == None:
        sql = sql.where(table.king_black_dragon == king_black_dragon)
    if not kraken == None:
        sql = sql.where(table.kraken == kraken)
    if not kreearra == None:
        sql = sql.where(table.kreearra == kreearra)
    if not kril_tsutsaroth == None:
        sql = sql.where(table.kril_tsutsaroth == kril_tsutsaroth)
    if not mimic == None:
        sql = sql.where(table.mimic == mimic)
    if not nightmare == None:
        sql = sql.where(table.nightmare == nightmare)
    if not obor == None:
        sql = sql.where(table.obor == obor)
    if not phosanis_nightmare  == None:
        sql = sql.where(table.phosanis_nightmare  == phosanis_nightmare )
    if not sarachnis == None:
        sql = sql.where(table.sarachnis == sarachnis)
    if not scorpia == None:
        sql = sql.where(table.scorpia == scorpia)
    if not skotizo == None:
        sql = sql.where(table.skotizo == skotizo)
    if not tempoross == None:
        sql = sql.where(table.tempoross == tempoross)
    if not the_gauntlet == None:
        sql = sql.where(table.the_gauntlet == the_gauntlet)
    if not the_corrupted_gauntlet == None:
        sql = sql.where(table.the_corrupted_gauntlet == the_corrupted_gauntlet)
    if not theatre_of_blood == None:
        sql = sql.where(table.theatre_of_blood == theatre_of_blood)
    if not theatre_of_blood_hard == None:
        sql = sql.where(table.theatre_of_blood_hard == theatre_of_blood_hard)
    if not thermonuclear_smoke_devil == None:
        sql = sql.where(table.thermonuclear_smoke_devil == thermonuclear_smoke_devil)
    if not tzkal_zuk == None:
        sql = sql.where(table.tzkal_zuk == tzkal_zuk)
    if not tztok_jad == None:
        sql = sql.where(table.tztok_jad == tztok_jad)
    if not venenatis == None:
        sql = sql.where(table.venenatis == venenatis)
    if not vetion == None:
        sql = sql.where(table.vetion == vetion)
    if not vorkath == None:
        sql = sql.where(table.vorkath == vorkath)
    if not wintertodt == None:
        sql = sql.where(table.wintertodt == wintertodt)
    if not zalcano == None:
        sql = sql.where(table.zalcano == zalcano)
    if not zulrah == None:
        sql = sql.where(table.zulrah == zulrah)
        
    # paging
    sql = sql.limit(row_count).offset(row_count*(page-1))

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/hiscore/Latest", tags=["Hiscore"])
async def get_latest_hiscore_data_for_an_account(
    token: str,
    player_id: Optional[int] = None,
    total: Optional[int] = None,
    Attack: Optional[int] = None,
    Defence: Optional[int] = None,
    Strength: Optional[int] = None,
    Hitpoints: Optional[int] = None,
    Ranged: Optional[int] = None,
    Prayer: Optional[int] = None,
    Magic: Optional[int] = None,
    Cooking: Optional[int] = None,
    Woodcutting: Optional[int] = None,
    Fletching: Optional[int] = None,
    Fishing: Optional[int] = None,
    Firemaking: Optional[int] = None,
    Crafting: Optional[int] = None,
    Smithing: Optional[int] = None,
    Mining: Optional[int] = None,
    Herblore: Optional[int] = None,
    Agility: Optional[int] = None,
    Thieving: Optional[int] = None,
    Slayer: Optional[int] = None,
    Farming: Optional[int] = None,
    Runecraft: Optional[int] = None,
    Hunter: Optional[int] = None,
    Construction: Optional[int] = None,
    league: Optional[int] = None,
    bounty_hunter_hunter: Optional[int] = None,
    bounty_hunter_rogue: Optional[int] = None,
    cs_all: Optional[int] = None,
    cs_beginner: Optional[int] = None,
    cs_easy: Optional[int] = None,
    cs_medium: Optional[int] = None,
    cs_hard: Optional[int] = None,
    cs_elite: Optional[int] = None,
    cs_master: Optional[int] = None,
    lms_rank: Optional[int] = None,
    soul_wars_zeal: Optional[int] = None,
    abyssal_sire: Optional[int] = None,
    alchemical_hydra: Optional[int] = None,
    barrows_chests: Optional[int] = None,
    bryophyta: Optional[int] = None,
    callisto: Optional[int] = None,
    cerberus: Optional[int] = None,
    chambers_of_xeric: Optional[int] = None,
    chambers_of_xeric_challenge_mode: Optional[int] = None,
    chaos_elemental: Optional[int] = None,
    chaos_fanatic: Optional[int] = None,
    commander_zilyana: Optional[int] = None,
    corporeal_beast: Optional[int] = None,
    crazy_archaeologist: Optional[int] = None,
    dagannoth_prime: Optional[int] = None,
    dagannoth_rex: Optional[int] = None,
    dagannoth_supreme: Optional[int] = None,
    deranged_archaeologist: Optional[int] = None,
    general_graardor: Optional[int] = None,
    giant_mole: Optional[int] = None,
    grotesque_guardians: Optional[int] = None,
    hespori: Optional[int] = None,
    kalphite_queen: Optional[int] = None,
    king_black_dragon: Optional[int] = None,
    kraken: Optional[int] = None,
    kreearra: Optional[int] = None,
    kril_tsutsaroth: Optional[int] = None,
    mimic: Optional[int] = None,
    nightmare: Optional[int] = None,
    obor: Optional[int] = None,
    phosanis_nightmare : Optional[int] = None,
    sarachnis: Optional[int] = None,
    scorpia: Optional[int] = None,
    skotizo: Optional[int] = None,
    tempoross: Optional[int] = None,
    the_gauntlet: Optional[int] = None,
    the_corrupted_gauntlet: Optional[int] = None,
    theatre_of_blood: Optional[int] = None,
    theatre_of_blood_hard: Optional[int] = None,
    thermonuclear_smoke_devil: Optional[int] = None,
    tzkal_zuk: Optional[int] = None,
    tztok_jad: Optional[int] = None,
    venenatis: Optional[int] = None,
    vetion: Optional[int] = None,
    vorkath: Optional[int] = None,
    wintertodt: Optional[int] = None,
    zalcano: Optional[int] = None,
    zulrah: Optional[int] = None,
):
    '''
        Select the latest hiscore of a player.
    '''
    # verify token
    await verify_token(token, verification='verify_ban', route='[GET]/v1/hiscore/Latest')

    # query
    table = PlayerHiscoreDataLatest
    sql = select(table)

    if player_id == total == Attack == Defence == Strength == Hitpoints == Ranged == Prayer == Magic == Cooking == Woodcutting == Fletching == Fishing == Firemaking == Crafting == Smithing == Mining == Herblore == Agility == Thieving == Slayer == Farming == Runecraft == Hunter == Construction == league == bounty_hunter_hunter == bounty_hunter_rogue == cs_all == cs_beginner == cs_easy == cs_medium == cs_hard == cs_elite == cs_master == lms_rank == soul_wars_zeal == abyssal_sire == alchemical_hydra == barrows_chests == bryophyta == callisto == cerberus == chambers_of_xeric == chambers_of_xeric_challenge_mode == chaos_elemental == chaos_fanatic == commander_zilyana == corporeal_beast == crazy_archaeologist == dagannoth_prime == dagannoth_rex == dagannoth_supreme == deranged_archaeologist == general_graardor == giant_mole == grotesque_guardians == hespori == kalphite_queen == king_black_dragon == kraken == kreearra == kril_tsutsaroth == mimic == nightmare == obor == phosanis_nightmare  == sarachnis == scorpia == skotizo == tempoross == the_gauntlet == the_corrupted_gauntlet == theatre_of_blood == theatre_of_blood_hard == thermonuclear_smoke_devil == tzkal_zuk == tztok_jad == venenatis == vetion == vorkath == wintertodt == zalcano == zulrah == None:
        raise HTTPException(status_code=404, detail="No param given")
    
    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)
    if not total == None:
        sql = sql.where(table.total == total)
    if not Attack == None:
        sql = sql.where(table.Attack == Attack)
    if not Defence == None:
        sql = sql.where(table.Defence == Defence)
    if not Strength == None:
        sql = sql.where(table.Strength == Strength)
    if not Hitpoints == None:
        sql = sql.where(table.Hitpoints == Hitpoints)
    if not Ranged == None:
        sql = sql.where(table.Ranged == Ranged)
    if not Prayer == None:
        sql = sql.where(table.Prayer == Prayer)
    if not Magic == None:
        sql = sql.where(table.Magic == Magic)
    if not Cooking == None:
        sql = sql.where(table.Cooking == Cooking)
    if not Woodcutting == None:
        sql = sql.where(table.Woodcutting == Woodcutting)
    if not Fletching == None:
        sql = sql.where(table.Fletching == Fletching)
    if not Fishing == None:
        sql = sql.where(table.Fishing == Fishing)
    if not Firemaking == None:
        sql = sql.where(table.Firemaking == Firemaking)
    if not Crafting == None:
        sql = sql.where(table.Crafting == Crafting)
    if not Smithing == None:
        sql = sql.where(table.Smithing == Smithing)
    if not Mining == None:
        sql = sql.where(table.Mining == Mining)
    if not Herblore == None:
        sql = sql.where(table.Herblore == Herblore)
    if not Agility == None:
        sql = sql.where(table.Agility == Agility)
    if not Thieving == None:
        sql = sql.where(table.Thieving == Thieving)
    if not Slayer == None:
        sql = sql.where(table.Slayer == Slayer)
    if not Farming == None:
        sql = sql.where(table.Farming == Farming)
    if not Runecraft == None:
        sql = sql.where(table.Runecraft == Runecraft)
    if not Hunter == None:
        sql = sql.where(table.Hunter == Hunter)
    if not Construction == None:
        sql = sql.where(table.Construction == Construction)
    if not league == None:
        sql = sql.where(table.league == league)
    if not bounty_hunter_hunter == None:
        sql = sql.where(table.bounty_hunter_hunter == bounty_hunter_hunter)
    if not bounty_hunter_rogue == None:
        sql = sql.where(table.bounty_hunter_rogue == bounty_hunter_rogue)
    if not cs_all == None:
        sql = sql.where(table.cs_all == cs_all)
    if not cs_beginner == None:
        sql = sql.where(table.cs_beginner == cs_beginner)
    if not cs_easy == None:
        sql = sql.where(table.cs_easy == cs_easy)
    if not cs_medium == None:
        sql = sql.where(table.cs_medium == cs_medium)
    if not cs_hard == None:
        sql = sql.where(table.cs_hard == cs_hard)
    if not cs_elite == None:
        sql = sql.where(table.cs_elite == cs_elite)
    if not cs_master == None:
        sql = sql.where(table.cs_master == cs_master)
    if not lms_rank == None:
        sql = sql.where(table.lms_rank == lms_rank)
    if not soul_wars_zeal == None:
        sql = sql.where(table.soul_wars_zeal == soul_wars_zeal)
    if not abyssal_sire == None:
        sql = sql.where(table.abyssal_sire == abyssal_sire)
    if not alchemical_hydra == None:
        sql = sql.where(table.alchemical_hydra == alchemical_hydra)
    if not barrows_chests == None:
        sql = sql.where(table.barrows_chests == barrows_chests)
    if not bryophyta == None:
        sql = sql.where(table.bryophyta == bryophyta)
    if not callisto == None:
        sql = sql.where(table.callisto == callisto)
    if not cerberus == None:
        sql = sql.where(table.cerberus == cerberus)
    if not chambers_of_xeric == None:
        sql = sql.where(table.chambers_of_xeric == chambers_of_xeric)
    if not chambers_of_xeric_challenge_mode == None:
        sql = sql.where(table.chambers_of_xeric_challenge_mode == chambers_of_xeric_challenge_mode)
    if not chaos_elemental == None:
        sql = sql.where(table.chaos_elemental == chaos_elemental)
    if not chaos_fanatic == None:
        sql = sql.where(table.chaos_fanatic == chaos_fanatic)
    if not commander_zilyana == None:
        sql = sql.where(table.commander_zilyana == commander_zilyana)
    if not corporeal_beast == None:
        sql = sql.where(table.corporeal_beast == corporeal_beast)
    if not crazy_archaeologist == None:
        sql = sql.where(table.crazy_archaeologist == crazy_archaeologist)
    if not dagannoth_prime == None:
        sql = sql.where(table.dagannoth_prime == dagannoth_prime)
    if not dagannoth_rex == None:
        sql = sql.where(table.dagannoth_rex == dagannoth_rex)
    if not dagannoth_supreme == None:
        sql = sql.where(table.dagannoth_supreme == dagannoth_supreme)
    if not deranged_archaeologist == None:
        sql = sql.where(table.deranged_archaeologist == deranged_archaeologist)
    if not general_graardor == None:
        sql = sql.where(table.general_graardor == general_graardor)
    if not giant_mole == None:
        sql = sql.where(table.giant_mole == giant_mole)
    if not grotesque_guardians == None:
        sql = sql.where(table.grotesque_guardians == grotesque_guardians)
    if not hespori == None:
        sql = sql.where(table.hespori == hespori)
    if not kalphite_queen == None:
        sql = sql.where(table.kalphite_queen == kalphite_queen)
    if not king_black_dragon == None:
        sql = sql.where(table.king_black_dragon == king_black_dragon)
    if not kraken == None:
        sql = sql.where(table.kraken == kraken)
    if not kreearra == None:
        sql = sql.where(table.kreearra == kreearra)
    if not kril_tsutsaroth == None:
        sql = sql.where(table.kril_tsutsaroth == kril_tsutsaroth)
    if not mimic == None:
        sql = sql.where(table.mimic == mimic)
    if not nightmare == None:
        sql = sql.where(table.nightmare == nightmare)
    if not obor == None:
        sql = sql.where(table.obor == obor)
    if not phosanis_nightmare  == None:
        sql = sql.where(table.phosanis_nightmare  == phosanis_nightmare )
    if not sarachnis == None:
        sql = sql.where(table.sarachnis == sarachnis)
    if not scorpia == None:
        sql = sql.where(table.scorpia == scorpia)
    if not skotizo == None:
        sql = sql.where(table.skotizo == skotizo)
    if not tempoross == None:
        sql = sql.where(table.tempoross == tempoross)
    if not the_gauntlet == None:
        sql = sql.where(table.the_gauntlet == the_gauntlet)
    if not the_corrupted_gauntlet == None:
        sql = sql.where(table.the_corrupted_gauntlet == the_corrupted_gauntlet)
    if not theatre_of_blood == None:
        sql = sql.where(table.theatre_of_blood == theatre_of_blood)
    if not theatre_of_blood_hard == None:
        sql = sql.where(table.theatre_of_blood_hard == theatre_of_blood_hard)
    if not thermonuclear_smoke_devil == None:
        sql = sql.where(table.thermonuclear_smoke_devil == thermonuclear_smoke_devil)
    if not tzkal_zuk == None:
        sql = sql.where(table.tzkal_zuk == tzkal_zuk)
    if not tztok_jad == None:
        sql = sql.where(table.tztok_jad == tztok_jad)
    if not venenatis == None:
        sql = sql.where(table.venenatis == venenatis)
    if not vetion == None:
        sql = sql.where(table.vetion == vetion)
    if not vorkath == None:
        sql = sql.where(table.vorkath == vorkath)
    if not wintertodt == None:
        sql = sql.where(table.wintertodt == wintertodt)
    if not zalcano == None:
        sql = sql.where(table.zalcano == zalcano)
    if not zulrah == None:
        sql = sql.where(table.zulrah == zulrah)

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/hiscore/Latest/bulk", tags=["Hiscore"])
async def get_latest_hiscore_data_by_player_features(
    token: str,
    row_count: int = 100_000,
    page: int = 1,
    possible_ban: Optional[int] = None,
    confirmed_ban: Optional[int] = None,
    confirmed_player: Optional[int] = None,
    label_id: Optional[int] = None,
    label_jagex: Optional[int] = None,
):
    '''
        Select the latest hiscore data of multiple players by filtering on the player features.
    '''
    # verify token
    await verify_token(token, verification='verify_ban', route='[GET]/v1/hiscore/Latest/bulk')

    if None == possible_ban == confirmed_ban == confirmed_player == label_id == label_jagex:
        raise HTTPException(status_code=404, detail="No param given")

    # query
    sql = select(PlayerHiscoreDataLatest)

    # filters
    if not possible_ban is None:
        sql = sql.where(Player.possible_ban == possible_ban)

    if not confirmed_ban is None:
        sql = sql.where(Player.confirmed_ban == confirmed_ban)

    if not confirmed_player is None:
        sql = sql.where(Player.confirmed_player == confirmed_player)

    if not label_id is None:
        sql = sql.where(Player.label_id == label_id)

    if not label_jagex is None:
        sql = sql.where(Player.label_jagex == label_jagex)

    # paging
    sql = sql.limit(row_count).offset(row_count*(page-1))

    # join
    sql = sql.join(Player)

    # execute query
    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.get("/v1/hiscore/XPChange", tags=["Hiscore"])
async def get_account_hiscore_xp_change(
    token: str,
    player_id: int,
    row_count: int = 100_000,
    page: int = 1
):
    '''
        Select daily scraped differential in hiscore data, by player_id
    '''
    # verify token
    await verify_token(token, verification='verify_ban', route='[GET]/v1/hiscore/XPChange')

    # query
    table = PlayerHiscoreDataXPChange
    sql = select(table)

    # filters
    if not player_id == None:
        sql = sql.where(table.Player_id == player_id)

    # paging
    sql = sql.limit(row_count).offset(row_count*(page-1))

    async with get_session(EngineType.PLAYERDATA) as session:
        data = await session.execute(sql)

    data = sqlalchemy_result(data)
    return data.rows2dict()


@router.post("/v1/hiscore", tags=["Hiscore"])
async def post_hiscore_data_to_database(hiscores: hiscore, token: str):
    '''
        Insert hiscore data.
    '''
    await verify_token(token, verification='verify_ban', route='[POST]/v1/hiscore')

    values = hiscores.dict()

    # query
    table = playerHiscoreData
    sql_insert = insert(table).values(values)
    sql_insert = sql_insert.prefix_with('ignore')

    async with get_session(EngineType.PLAYERDATA) as session:
        await session.execute(sql_insert)
        await session.commit()

    return {'ok': 'ok'}
