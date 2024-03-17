USE playerdata;

CREATE TABLE Players (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    possible_ban BOOLEAN,
    confirmed_ban BOOLEAN,
    confirmed_player BOOLEAN,
    label_id INTEGER,
    label_jagex INTEGER,
    ironman BOOLEAN,
    hardcore_ironman BOOLEAN,
    ultimate_ironman BOOLEAN,
    normalized_name TEXT
);

-- playerdata.playerHiscoreData definition

CREATE TABLE `playerHiscoreData` (
  `id` int NOT NULL AUTO_INCREMENT,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ts_date` date DEFAULT NULL,
  `Player_id` int NOT NULL,
  `total` bigint DEFAULT '0',
  `attack` int DEFAULT '0',
  `defence` int DEFAULT '0',
  `strength` int DEFAULT '0',
  `hitpoints` int DEFAULT '0',
  `ranged` int DEFAULT '0',
  `prayer` int DEFAULT '0',
  `magic` int DEFAULT '0',
  `cooking` int DEFAULT '0',
  `woodcutting` int DEFAULT '0',
  `fletching` int DEFAULT '0',
  `fishing` int DEFAULT '0',
  `firemaking` int DEFAULT '0',
  `crafting` int DEFAULT '0',
  `smithing` int DEFAULT '0',
  `mining` int DEFAULT '0',
  `herblore` int DEFAULT '0',
  `agility` int DEFAULT '0',
  `thieving` int DEFAULT '0',
  `slayer` int DEFAULT '0',
  `farming` int DEFAULT '0',
  `runecraft` int DEFAULT '0',
  `hunter` int DEFAULT '0',
  `construction` int DEFAULT '0',
  `league` int DEFAULT '0',
  `bounty_hunter_hunter` int DEFAULT '0',
  `bounty_hunter_rogue` int DEFAULT '0',
  `cs_all` int DEFAULT '0',
  `cs_beginner` int DEFAULT '0',
  `cs_easy` int DEFAULT '0',
  `cs_medium` int DEFAULT '0',
  `cs_hard` int DEFAULT '0',
  `cs_elite` int DEFAULT '0',
  `cs_master` int DEFAULT '0',
  `lms_rank` int DEFAULT '0',
  `soul_wars_zeal` int DEFAULT '0',
  `abyssal_sire` int DEFAULT '0',
  `alchemical_hydra` int DEFAULT '0',
  `barrows_chests` int DEFAULT '0',
  `bryophyta` int DEFAULT '0',
  `callisto` int DEFAULT '0',
  `cerberus` int DEFAULT '0',
  `chambers_of_xeric` int DEFAULT '0',
  `chambers_of_xeric_challenge_mode` int DEFAULT '0',
  `chaos_elemental` int DEFAULT '0',
  `chaos_fanatic` int DEFAULT '0',
  `commander_zilyana` int DEFAULT '0',
  `corporeal_beast` int DEFAULT '0',
  `crazy_archaeologist` int DEFAULT '0',
  `dagannoth_prime` int DEFAULT '0',
  `dagannoth_rex` int DEFAULT '0',
  `dagannoth_supreme` int DEFAULT '0',
  `deranged_archaeologist` int DEFAULT '0',
  `general_graardor` int DEFAULT '0',
  `giant_mole` int DEFAULT '0',
  `grotesque_guardians` int DEFAULT '0',
  `hespori` int DEFAULT '0',
  `kalphite_queen` int DEFAULT '0',
  `king_black_dragon` int DEFAULT '0',
  `kraken` int DEFAULT '0',
  `kreearra` int DEFAULT '0',
  `kril_tsutsaroth` int DEFAULT '0',
  `mimic` int DEFAULT '0',
  `nex` int DEFAULT '0',
  `nightmare` int DEFAULT '0',
  `phosanis_nightmare` int DEFAULT '0',
  `obor` int DEFAULT '0',
  `phantom_muspah` int DEFAULT '0',
  `sarachnis` int DEFAULT '0',
  `scorpia` int DEFAULT '0',
  `skotizo` int DEFAULT '0',
  `tempoross` int DEFAULT '0',
  `the_gauntlet` int DEFAULT '0',
  `the_corrupted_gauntlet` int DEFAULT '0',
  `theatre_of_blood` int DEFAULT '0',
  `theatre_of_blood_hard` int DEFAULT '0',
  `thermonuclear_smoke_devil` int DEFAULT '0',
  `tombs_of_amascut` int DEFAULT '0',
  `tombs_of_amascut_expert` int DEFAULT '0',
  `tzkal_zuk` int DEFAULT '0',
  `tztok_jad` int DEFAULT '0',
  `venenatis` int DEFAULT '0',
  `vetion` int DEFAULT '0',
  `vorkath` int DEFAULT '0',
  `wintertodt` int DEFAULT '0',
  `zalcano` int DEFAULT '0',
  `zulrah` int DEFAULT '0',
  `rifts_closed` int DEFAULT '0',
  `artio` int DEFAULT '0',
  `calvarion` int DEFAULT '0',
  `duke_sucellus` int DEFAULT '0',
  `spindel` int DEFAULT '0',
  `the_leviathan` int DEFAULT '0',
  `the_whisperer` int DEFAULT '0',
  `vardorvis` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_playerHiscoreData_Player_id_timestamp` (`Player_id`,`timestamp`),
  UNIQUE KEY `Unique_player_date` (`Player_id`,`ts_date`),
  CONSTRAINT `FK_Players_id` FOREIGN KEY (`Player_id`) REFERENCES `Players` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
);
CREATE TRIGGER `hiscore_date_OnInsert` BEFORE INSERT ON `playerHiscoreData` FOR EACH ROW SET new.ts_date = DATE(new.timestamp);

CREATE TABLE scraper_data (
  scraper_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  record_date DATE AS (DATE(created_at)) STORED,
  player_id INT UNSIGNED NOT NULL,
  UNIQUE KEY unique_player_per_day (player_id, record_date)
);

CREATE TABLE skills (
  skill_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, # < 255
  skill_name VARCHAR(50) NOT NULL,
  UNIQUE KEY unique_skill_name (skill_name)
);
CREATE TABLE activities (
  activity_id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, # < 255
  activity_name VARCHAR(50) NOT NULL,
  UNIQUE KEY unique_activity_name (activity_name)
);


CREATE TABLE player_skills (
  scraper_id BIGINT UNSIGNED NOT NULL,
  skill_id TINYINT UNSIGNED NOT NULL,
  skill_value INT UNSIGNED NOT NULL DEFAULT 0, # < 200 000 000
  FOREIGN KEY (scraper_id) REFERENCES scraper_data(scraper_id) ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
  PRIMARY KEY (scraper_id, skill_id)
);

CREATE TABLE player_activities (
  scraper_id BIGINT UNSIGNED NOT NULL,
  activity_id TINYINT UNSIGNED NOT NULL,
  activity_value INT UNSIGNED NOT NULL DEFAULT 0, # some guy could get over 65k kc
  FOREIGN KEY (scraper_id) REFERENCES scraper_data(scraper_id) ON DELETE CASCADE,
  FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE,
  PRIMARY KEY (scraper_id, activity_id)
);