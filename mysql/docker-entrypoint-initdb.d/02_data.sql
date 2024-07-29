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


-- Insert data into the Reports table
INSERT INTO
    Reports (
        created_at,
        reportedID,
        reportingID,
        region_id,
        x_coord,
        y_coord,
        z_coord,
        timestamp,
        manual_detect,
        on_members_world,
        on_pvp_world,
        world_number,
        equip_head_id,
        equip_amulet_id,
        equip_torso_id,
        equip_legs_id,
        equip_boots_id,
        equip_cape_id,
        equip_hands_id,
        equip_weapon_id,
        equip_shield_id,
        equip_ge_value
    )
SELECT
    NOW() - INTERVAL FLOOR(RAND(42) * 365) DAY AS created_at,
    p1.id AS reportedID,
    p2.id AS reportingID,
    ROUND(RAND(42) * 1000) AS region_id,
    -- Random region_id
    ROUND(RAND(42) * 1000) AS x_coord,
    -- Random x_coord
    ROUND(RAND(42) * 1000) AS y_coord,
    -- Random y_coord
    ROUND(RAND(42) * 1000) AS z_coord,
    -- Random z_coord
    NOW() - INTERVAL FLOOR(RAND(42) * 365) DAY AS timestamp,
    ROUND(RAND(42)) AS manual_detect,
    -- Random manual_detect (0 or 1)
    ROUND(RAND(42) * 1000) AS on_members_world,
    -- Random on_members_world
    ROUND(RAND(42)) AS on_pvp_world,
    -- Random on_pvp_world (0 or 1)
    ROUND(RAND(42) * 100) AS world_number,
    -- Random world_number
    ROUND(RAND(42) * 1000) AS equip_head_id,
    -- Random equip_head_id
    ROUND(RAND(42) * 1000) AS equip_amulet_id,
    -- Random equip_amulet_id
    ROUND(RAND(42) * 1000) AS equip_torso_id,
    -- Random equip_torso_id
    ROUND(RAND(42) * 1000) AS equip_legs_id,
    -- Random equip_legs_id
    ROUND(RAND(42) * 1000) AS equip_boots_id,
    -- Random equip_boots_id
    ROUND(RAND(42) * 1000) AS equip_cape_id,
    -- Random equip_cape_id
    ROUND(RAND(42) * 1000) AS equip_hands_id,
    -- Random equip_hands_id
    ROUND(RAND(42) * 1000) AS equip_weapon_id,
    -- Random equip_weapon_id
    ROUND(RAND(42) * 1000) AS equip_shield_id,
    -- Random equip_shield_id
    ROUND(RAND(42) * 10000) AS equip_ge_value -- Random equip_ge_value
FROM Players p1
    CROSS JOIN Players p2
WHERE
    p1.id <> p2.id -- Ensure reportedID and reportingID are different
ORDER BY
    RAND(42) -- Randomize the order of the combinations
LIMIT
    10000 -- Limit the number of combinations to insert
;

INSERT INTO Predictions (name, predicted_confidence, prediction, created)
SELECT 
    name, 
    FLOOR(RAND(6)*(100-1)+1),
    CASE FLOOR(RAND(6)*(25-1)+1)
        WHEN 1 THEN 'real_player'
        WHEN 2 THEN 'pvm_melee_bot'
        WHEN 3 THEN 'smithing_bot'
        WHEN 4 THEN 'magic_bot'
        WHEN 5 THEN 'fishing_bot'
        WHEN 6 THEN 'mining_bot'
        WHEN 7 THEN 'crafting_bot'
        WHEN 8 THEN 'pvm_ranged_magic_bot'
        WHEN 9 THEN 'pvm_ranged_bot'
        WHEN 10 THEN 'hunter_bot'
        WHEN 11 THEN 'fletching_bot'
        WHEN 12 THEN 'clue_scroll_bot'
        WHEN 13 THEN 'lms_bot'
        WHEN 14 THEN 'agility_bot'
        WHEN 15 THEN 'wintertodt_bot'
        WHEN 16 THEN 'runecrafting_bot'
        WHEN 17 THEN 'zalcano_bot'
        WHEN 18 THEN 'woodcutting_bot'
        WHEN 19 THEN 'thieving_bot'
        WHEN 20 THEN 'soul_wars_bot'
        WHEN 21 THEN 'cooking_bot'
        WHEN 22 THEN 'vorkath_bot'
        WHEN 23 THEN 'barrows_bot'
        WHEN 24 THEN 'herblore_bot'
        ELSE 'unknown_bot'
    END ,
    FROM_UNIXTIME(
        TIMESTAMPDIFF(SECOND, '2020-01-01 00:00:00', '2022-12-31 23:59:59') * RAND(42) 
        + UNIX_TIMESTAMP('2020-01-01 00:00:00')
    )
FROM `Players`
where 1=1
    AND name not LIKE 'anonymoususer%'
ORDER BY RAND(42) 
LIMIT 250
;

INSERT INTO playerdata.Labels (label) VALUES
    ('Agility_bot'),
    ('Barrows_bot'),
    ('Blast_mine_bot'),
    ('Clue_Scroll_bot'),
    ('Construction_Magic_bot'),
    ('Cooking_bot'),
    ('Crafting_bot'),
    ('Fishing_bot'),
    ('Fishing_Cooking_bot'),
    ('Fletching_bot'),
    ('Herblore_bot'),
    ('Hunter_bot'),
    ('LMS_bot'),
    ('Mage_Guild_Store_bot'),
    ('Magic_bot'),
    ('Mining_bot'),
    ('mort_myre_fungus_bot'),
    ('Phosani_bot'),
    ('PVM_Melee_bot'),
    ('PVM_Ranged_bot'),
    ('PVM_Ranged_Magic_bot'),
    ('Real_Player'),
    ('Runecrafting_bot'),
    ('Smithing_bot'),
    ('Soul_Wars_bot'),
    ('temp_real_player'),
    ('test_label'),
    ('Thieving_bot'),
    ('Unknown'),
    ('Unknown_bot'),
    ('Vorkath_bot'),
    ('Wintertodt_bot'),
    ('Woodcutting_bot'),
    ('Woodcutting_Firemaking_bot'),
    ('Woodcutting_Mining_bot'),
    ('Zalcano_bot'),
    ('Zulrah_bot')
;

INSERT INTO PredictionsFeedback (voter_id, subject_id, prediction, confidence, feedback_text, vote, proposed_label)
SELECT 
    pl1.id AS voter_id, 
    pl2.id AS subject_id,
    pr.prediction,
    FLOOR(RAND(6)*(100-1)+1)/100 AS confidence, -- Generate a random confidence value between 0 and 1
    "" AS feedback_text,
    CASE 
        WHEN FLOOR(RAND(6)*(100-1)+1) < 33 THEN -1
        WHEN FLOOR(RAND(6)*(100-1)+1) < 66 THEN 0
        ELSE 1
    END AS vote,
    (SELECT label FROM Labels ORDER BY RAND(42) LIMIT 1) AS proposed_label
FROM (SELECT * FROM Players ORDER BY RAND(42) LIMIT 1000) pl1
JOIN (SELECT * FROM Players ORDER BY RAND(42) LIMIT 1000) pl2 ON pl1.id <> pl2.id
JOIN Predictions pr ON pr.id = pl2.id
ORDER BY RAND(42)
LIMIT 100;

UPDATE PredictionsFeedback
    SET proposed_label = prediction
WHERE 1=1
    AND vote = 1
;

DELIMITER $$

INSERT INTO Players (
    name,
    created_at,
    updated_at,
    possible_ban,
    confirmed_ban,
    confirmed_player,
    label_id,
    label_jagex
) VALUES 
    ("anonymoususer 382e728f 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e7259 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e7221 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e71ee 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e71bb 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e7179 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e7133 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e70ef 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e7089 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0),
    ("anonymoususer 382e6def 87ea 11ee aab6 0242ac120002", NOW(), NOW(), 0, 0, 0, 0, 0)
;

UPDATE `Players`
SET
    created_at = NOW() - INTERVAL FLOOR(RAND(42) * 365) DAY,
    updated_at = NOW() - INTERVAL FLOOR(RAND(41) * 365) DAY
;
UPDATE `Players`
SET
    name=replace(name,'-',' '),
    normalized_name=replace(name,'-',' ')
WHERE name LIKE 'anonymoususer%'
;