
-- USERS
INSERT INTO user (username, email, password)
VALUES
('Viktor', 'viktor@example.com', 'pass123'),
('Luna', 'luna@example.com', 'moonlight'),
('Thorin', 'thorin@example.com', 'oakenshield');

-- GUILDS
INSERT INTO guild (guild_name, members)
VALUES
('Knights of Dawn', '10'),
('Shadow Blades', '8'),
('Mages Circle', '12');

-- INVENTORIES
INSERT INTO inventory VALUES (), (), ();

-- CHARACTERS
INSERT INTO `character` (character_name, level, hp, mana, user_id, inventory_id, guild_id)
VALUES
('Aelric', 10, 200, 100, 1, 1, 1),
('Lyra', 8, 150, 180, 2, 2, 3),
('Grimnar', 12, 300, 50, 3, 3, 2);

-- ITEMS
INSERT INTO item (name, type, rarity, value, stats)
VALUES
('Iron Sword', 'Weapon', 'Common', '50', '+10 ATK'),
('Healing Potion', 'Consumable', 'Common', '10', '+50 HP'),
('Mana Crystal', 'Consumable', 'Uncommon', '25', '+40 Mana'),
('Steel Shield', 'Armor', 'Rare', '100', '+15 DEF'),
('Ring of Power', 'Accessory', 'Epic', '250', '+25 ATK +25 Mana');

-- INVENTORY_HAS_ITEM
INSERT INTO inventory_has_item (inventory_id, item_id)
VALUES
(1, 1),
(1, 2),
(2, 3),
(3, 4),
(3, 5);

-- NPCs
INSERT INTO npc (name, role, location)
VALUES
('Elder Rowan', 'Quest Giver', 'Oakvale'),
('Merchant Tilda', 'Vendor', 'Ironforge'),
('Captain Duran', 'Quest Giver', 'Stormkeep');

-- QUESTS
INSERT INTO quest (title, reward_money, reward_xp, description, npc_id)
VALUES
('Defeat the Goblins', '100', 300, 'Clear the forest of goblins', 1),
('Deliver the Package', '50', 150, 'Take supplies to Ironforge', 3),
('Find the Lost Tome', '200', 400, 'Recover the ancient tome from ruins', 1);

-- SKILLS
INSERT INTO skills (name, description, damage, healing)
VALUES
('Fireball', 'Launch a ball of fire', 40, 0),
('Heal', 'Restore health to an ally', 0, 50),
('Shield Bash', 'Stun enemy briefly', 25, 0);

-- CHARACTER_HAS_SKILLS
INSERT INTO character_has_skills (character_id, character_inventory_id, skills_id)
VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 3);

-- BATTLES
INSERT INTO battle (outcome, xp, money)
VALUES
('Victory', 200, '50'),
('Defeat', 50, '0');

-- CHARACTER_HAS_BATTLE
INSERT INTO character_has_battle (character_id, character_inventory_id, battle_id)
VALUES
(1, 1, 1),
(2, 2, 1),
(3, 3, 2);

-- CHARACTER_HAS_QUEST
INSERT INTO character_has_quest (character_id, character_inventory_id, quest_id)
VALUES
(1, 1, 1),
(2, 2, 2),
(3, 3, 3);

-- TRANSACTIONS
INSERT INTO transaction (quantity, cost, user_id)
VALUES
('2', 100, 1),
('1', 250, 2),
('5', 50, 3);