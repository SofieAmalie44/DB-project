

CREATE INDEX idx_character_user_id
ON `character` (user_id);

CREATE INDEX idx_inventory_items
ON inventory_has_item (inventory_id);

CREATE INDEX idx_character_quests
ON character_has_quest (character_id);
