
-- Stored Procedures

-- Procedure 1 - Quest Completion
DELIMITER $$

CREATE PROCEDURE sp_complete_quest(
    IN p_character_id BIGINT,
    IN p_quest_id BIGINT
)
BEGIN
    DECLARE v_reward_xp INT;
    DECLARE v_reward_money INT;

    -- Get rewards from quest
    SELECT reward_xp, reward_money
    INTO v_reward_xp, v_reward_money
    FROM rpg_quest
    WHERE id = p_quest_id;

    -- Add XP and gold to character
    UPDATE rpg_character
    SET xp = xp + IFNULL(v_reward_xp, 0),
        gold = gold + IFNULL(v_reward_money, 0)
    WHERE id = p_character_id;

END$$

DELIMITER ;


-- Procedure 2 - Character Creation
DELIMITER $$

CREATE PROCEDURE sp_create_character(
    IN p_user_id INT,
    IN p_name VARCHAR(100),
    IN p_starting_gold INT,
    IN p_starting_xp INT
)
BEGIN
    -- Insert new character
    INSERT INTO rpg_character (user_id, name, gold, xp)
    VALUES (p_user_id, p_name, p_starting_gold, p_starting_xp);

    -- Return the generated character ID
    SELECT LAST_INSERT_ID() AS new_character_id;
END$$

DELIMITER ;


-- Procedure 3 - Safe Purchase Transaction
DELIMITER $$

CREATE PROCEDURE sp_purchase_item(
    IN p_user_id INT,
    IN p_item_id BIGINT,
    IN p_quantity INT,
    IN p_cost_per_item INT
)
BEGIN
    DECLARE total_cost INT;
    DECLARE user_gold INT;

    SET total_cost = p_quantity * p_cost_per_item;

    -- 1. Get user gold
    SELECT gold INTO user_gold
    FROM rpg_character
    WHERE user_id = p_user_id
    LIMIT 1;

    -- 2. Check if enough gold
    IF user_gold < total_cost THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Not enough gold to complete purchase.';
    END IF;

    -- 3. Deduct gold
    UPDATE rpg_character
    SET gold = gold - total_cost
    WHERE user_id = p_user_id;

    -- 4. Insert into transaction log
    INSERT INTO rpg_transaction (user_id, quantity, cost)
    VALUES (p_user_id, p_quantity, total_cost);

    -- 5. Add to inventory (character_id = user_id)
    INSERT INTO rpg_inventory (character_id, item_id, quantity)
    VALUES (p_user_id, p_item_id, p_quantity)
    ON DUPLICATE KEY UPDATE quantity = quantity + p_quantity;

    -- 6. Return success message
    SELECT 'Purchase completed successfully.' AS message;

END$$

DELIMITER ;


-- Procedure 4 - Automatic XP Gain & Level Up Logic
DELIMITER $$

CREATE PROCEDURE sp_level_up_character(
    IN p_character_id BIGINT,
    IN p_xp_gained INT
)
BEGIN
    DECLARE new_xp INT;
    DECLARE new_level INT;
    DECLARE current_level INT;

    -- Get current level
    SELECT level INTO current_level
    FROM rpg_character
    WHERE id = p_character_id;

    -- Add XP
    UPDATE rpg_character
    SET xp = xp + p_xp_gained
    WHERE id = p_character_id;

    -- Check if enough xp to level up
    SELECT xp INTO new_xp
    FROM rpg_character
    WHERE id = p_character_id;

    -- Simple leveling system: each level requires 100 xp
    SET new_level = FLOOR(new_xp / 100) + 1;

    UPDATE rpg_character
    SET level = new_level
    WHERE id = p_character_id;

    SELECT CONCAT('Character leveled up to ', new_level) AS message;
END $$

DELIMITER ;

-- Test calls
CALL sp_level_up_character(1, 120);


