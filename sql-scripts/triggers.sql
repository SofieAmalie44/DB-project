
-- Triggers


-- TRIGGER 1 — Prevent negative inventory quantity

DELIMITER $$

CREATE TRIGGER trg_inventory_prevent_negative
BEFORE UPDATE ON rpg_inventory
FOR EACH ROW
BEGIN
    IF NEW.quantity < 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Inventory quantity cannot be negative.';
    END IF;
END$$

DELIMITER ;



-- TRIGGER 2 — Update inventory after a transaction

DELIMITER $$

CREATE TRIGGER trg_transaction_adjust_inventory
AFTER INSERT ON rpg_transaction
FOR EACH ROW
BEGIN
    INSERT INTO rpg_inventory (character_id, item_id, quantity)
    VALUES (
        (SELECT id FROM rpg_character WHERE user_id = NEW.user_id LIMIT 1),
        NEW.item_id,
        NEW.quantity
    )
    ON DUPLICATE KEY UPDATE quantity = quantity + NEW.quantity;
END$$

DELIMITER ;


-- TRIGGER 3 — Auto-update character gold

DELIMITER $$

CREATE TRIGGER trg_transaction_adjust_gold
AFTER INSERT ON rpg_transaction
FOR EACH ROW
BEGIN
    UPDATE rpg_character
    SET gold = gold - NEW.cost
    WHERE user_id = NEW.user_id;
END$$

DELIMITER ;


-- TRIGGER 4 — Auto set quest completion timestamp

DELIMITER $$

CREATE TRIGGER trg_quest_completion_timestamp
BEFORE UPDATE ON rpg_quest
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' AND OLD.status <> 'completed' THEN
        SET NEW.completed_at = NOW();
    END IF;
END$$

DELIMITER ;



