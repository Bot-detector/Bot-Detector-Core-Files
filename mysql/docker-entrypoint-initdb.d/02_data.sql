USE playerdata;

-- Insert data into the Players table
DELIMITER $$

CREATE PROCEDURE InsertRandomPlayers(IN NUM INT, IN possible_ban BOOL, IN confirmed_ban BOOL, IN confirmed_player BOOL)
BEGIN
    DECLARE i INT DEFAULT 1;

    WHILE i <= NUM DO
        INSERT INTO Players (
            name,
            created_at,
            updated_at,
            possible_ban,
            confirmed_ban,
            confirmed_player,
            label_id,
            label_jagex,
            ironman,
            hardcore_ironman,
            ultimate_ironman,
            normalized_name
        )
        SELECT
            UUID() AS name, -- updated later
            NOW() AS created_at, -- updated later
            NOW() AS updated_at, -- updated later
            possible_ban,
            confirmed_ban,
            confirmed_player,
            0 AS label_id,
            ROUND(RAND() * 1) AS label_jagex, -- doesn't matter?
            null AS ironman,
            null AS hardcore_ironman,
            null AS ultimate_ironman,
            UUID() AS normalized_name -- updated later
        FROM dual;

        SET i = i + 1;
    END WHILE;
END $$

DELIMITER ;


call InsertRandomPlayers(100, 1,0,0);
call InsertRandomPlayers(100, 1,1,0);
call InsertRandomPlayers(100, 0,0,1);

UPDATE Players
SET
    name = CONCAT('player', id),
    normalized_name = CONCAT('player', id)
;

INSERT INTO skills (skill_name) VALUES 
	-- ('total'), 
	('attack'), 
	('defence'), 
	('strength'), 
	('hitpoints'), 
	('ranged'), 
	('prayer'), 
	('magic'), 
	('cooking'), 
	('woodcutting'), 
	('fletching'), 
	('fishing'), 
	('firemaking'), 
	('crafting'), 
	('smithing'), 
	('mining'), 
	('herblore'), 
	('agility'), 
	('thieving'), 
	('slayer'), 
	('farming'), 
	('runecraft'), 
	('hunter'), 
	('construction')
;


INSERT INTO activities (activity_name) VALUES 
	('abyssal_sire'),
	('alchemical_hydra'),
	('artio'),
	('barrows_chests'),
	('bounty_hunter_hunter'),
	('bounty_hunter_rogue'),
	('bryophyta'),
	('callisto'),
	('calvarion'),
	('cerberus'),
	('chambers_of_xeric'),
	('chambers_of_xeric_challenge_mode'),
	('chaos_elemental'),
	('chaos_fanatic'),
	('commander_zilyana'),
	('corporeal_beast'),
	('crazy_archaeologist'),
	('cs_all'),
	('cs_beginner'),
	('cs_easy'),
	('cs_elite'),
	('cs_hard'),
	('cs_master'),
	('cs_medium'),
	('dagannoth_prime'),
	('dagannoth_rex'),
	('dagannoth_supreme'),
	('deranged_archaeologist'),
	('duke_sucellus'),
	('general_graardor'),
	('giant_mole'),
	('grotesque_guardians'),
	('hespori'),
	('kalphite_queen'),
	('king_black_dragon'),
	('kraken'),
	('kreearra'),
	('kril_tsutsaroth'),
	('league'),
	('lms_rank'),
	('mimic'),
	('nex'),
	('nightmare'),
	('obor'),
	('phantom_muspah'),
	('phosanis_nightmare'),
	('rifts_closed'),
	('sarachnis'),
	('scorpia'),
	('skotizo'),
	('soul_wars_zeal'),
	('spindel'),
	('tempoross'),
	('the_corrupted_gauntlet'),
	('the_gauntlet'),
	('the_leviathan'),
	('the_whisperer'),
	('theatre_of_blood'),
	('theatre_of_blood_hard'),
	('thermonuclear_smoke_devil'),
	('tombs_of_amascut'),
	('tombs_of_amascut_expert'),
	('tzkal_zuk'),
	('tztok_jad'),
	('vardorvis'),
	('venenatis'),
	('vetion'),
	('vorkath'),
	('wintertodt'),
	('zalcano'),
	('zulrah')
;