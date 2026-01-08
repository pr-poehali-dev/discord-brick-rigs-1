-- Добавляем админов с required полями
INSERT INTO admins (discord_id, user_id, admin_rank, role_id, appointed_by, appointed_at, is_active)
VALUES 
('admin_pancake', 3, 'Старший администратор', 4, '2', CURRENT_TIMESTAMP, TRUE),
('admin_gotnevl', 6, 'Администратор', 3, '2', CURRENT_TIMESTAMP, TRUE),
('admin_cj', 5, 'Младший администратор', 2, '2', CURRENT_TIMESTAMP, TRUE);

-- Добавляем генералов фракций
INSERT INTO faction_members (user_id, faction_id, rank, is_general, joined_at)
SELECT 2, f.id, 'Генерал', TRUE, CURRENT_TIMESTAMP
FROM factions f WHERE f.name = 'ЦОДД';

INSERT INTO faction_members (user_id, faction_id, rank, is_general, joined_at)
SELECT 4, f.id, 'Генерал', TRUE, CURRENT_TIMESTAMP
FROM factions f WHERE f.name = 'МВД';

INSERT INTO faction_members (user_id, faction_id, rank, is_general, joined_at)
SELECT 3, f.id, 'Генерал', TRUE, CURRENT_TIMESTAMP
FROM factions f WHERE f.name = 'Армия';
