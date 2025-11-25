USE rpgdb;

-- Reset daily quests
SET GLOBAL event_scheduler = ON;

CREATE EVENT ev_reset_daily_quests
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
    UPDATE rpg_quest
    SET status = 'available';
    
-- Daily login bonus
CREATE EVENT ev_daily_login_bonus
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 1 MINUTE
DO 
    UPDATE rpg_character
    SET gold = gold + 10,
        xp = xp + 5;

