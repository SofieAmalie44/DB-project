

CREATE INDEX idx_character_user_id
ON rpg_character (user_id);

CREATE INDEX idx_inventoryitem
ON rpg_inventoryitem (inventory_id);

CREATE INDEX idx_character_quests
ON rpg_character_quests (character_id);
