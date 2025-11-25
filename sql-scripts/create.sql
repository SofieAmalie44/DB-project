USE rpgdb;

-- ======================
-- USERS (auth_user)
-- ======================
INSERT INTO auth_user (
    password,
    last_login,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined
)
VALUES
('!', NULL, 0, 'Viktor', '', '', 'viktor@example.com', 0, 1, NOW()),
('!', NULL, 0, 'Luna', '', '', 'moonlight@example.com', 0, 1, NOW()),
('!', NULL, 0, 'Thorin', '', '', 'thorin@example.com', 0, 1, NOW());


-- ======================
-- GUILDS
-- ======================
INSERT INTO rpg_guild (guild_name, members)
VALUES
('Knights of Dawn', 10),
('Shadow Blades', 8),
('Mages Circle', 12);


-- ======================
-- INVENTORIES
-- ======================
INSERT INTO rpg_inventory (id) VALUES (1), (2), (3);


-- ======================
-- CHARACTERS
-- ======================
INSERT INTO rpg_character (character_name, level, hp, mana, user_id, inventory_id, guild_id)
VALUES
('Aelric', 10, 200, 100, 1, 1, 1),
('Lyra', 8, 150, 180, 2, 2, 3),
('Grimnar', 12, 300, 50, 3, 3, 2);


-- ======================
-- ITEMS
-- ======================
INSERT INTO rpg_item (name, type, rarity, value, stats)
VALUES
('Iron Sword', 'Weapon', 'Common', 50, '+10 ATK'),
('Healing Potion', 'Consumable', 'Common', 10, '+50 HP'),
('Mana Crystal', 'Consumable', 'Uncommon', 25, '+40 Mana'),
('Steel Shield', 'Armor', 'Rare', 100, '+15 DEF'),
('Ring of Power', 'Accessory', 'Epic', 250, '+25 ATK +25 Mana');


-- ======================
-- INVENTORY ITEMS (M2M)
-- ======================
INSERT INTO rpg_inventory_items (inventory_id, item_id)
VALUES
(1, 1),
(1, 2),
(2, 3),
(3, 4),
(3, 5);


-- ======================
-- NPCs
-- ======================
INSERT INTO rpg_npc (name, role, location)
VALUES
('Elder Rowan', 'Quest Giver', 'Oakvale'),
('Merchant Tilda', 'Vendor', 'Ironforge'),
('Captain Duran', 'Quest Giver', 'Stormkeep');


-- ======================
-- QUESTS
-- ======================
INSERT INTO rpg_quest (title, reward_money, reward_xp, description, npc_id)
VALUES
('Defeat the Goblins', 100, 300, 'Clear the forest of goblins', 1),
('Deliver the Package', 50, 150, 'Take supplies to Ironforge', 3),
('Find the Lost Tome', 200, 400, 'Recover the ancient tome from ruins', 1);


-- ======================
-- SKILLS
-- ======================
INSERT INTO rpg_skill (name, description, damage, healing)
VALUES
('Fireball', 'Launch a ball of fire', 40, 0),
('Heal', 'Restore health', 0, 50),
('Shield Bash', 'Stun enemy briefly', 25, 0);


-- ======================
-- CHARACTER_SKILLS (M2M)
-- ======================
INSERT INTO rpg_character_skills (character_id, skill_id)
VALUES
(1, 1),
(2, 2),
(3, 3);


-- ======================
-- BATTLES
-- ======================
INSERT INTO rpg_battle (outcome, xp, money)
VALUES
('Victory', 200, 50),
('Defeat', 50, 0);


-- ======================
-- CHARACTER_BATTLES (M2M)
-- ======================
INSERT INTO rpg_character_battles (character_id, battle_id)
VALUES
(1, 1),
(2, 1),
(3, 2);


-- ======================
-- CHARACTER_QUESTS (M2M)
-- ======================
INSERT INTO rpg_character_quests (character_id, quest_id)
VALUES
(1, 1),
(2, 2),
(3, 3);

SELECT id, username FROM auth_user;

-- ======================
-- TRANSACTIONS
-- ======================
INSERT INTO rpg_transaction (quantity, cost, user_id)
VALUES
(2, 100, 1),
(1, 250, 2),
(5, 50, 3);
