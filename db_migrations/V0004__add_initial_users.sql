-- Добавляем Owner аккаунт
INSERT INTO users (discord_id, discord_username, username, password_hash, nickname, is_owner, created_at) 
VALUES ('owner_1', 'TOURIST_WAGNERA', 'TOURIST_WAGNERA', 'e37fc63e60d09dca9b37f9b8f9be85c0b0b64ef24e9d87cf6c046ba2c907f4e3', 'Турист-Вагнера', TRUE, CURRENT_TIMESTAMP)
ON CONFLICT (discord_id) DO NOTHING;

-- Добавляем админов
INSERT INTO users (discord_id, discord_username, username, password_hash, nickname, created_at) VALUES
('pancake_1', 'Pancake', 'Pancake', 'temp_hash', 'Pancake', CURRENT_TIMESTAMP),
('cailon_1', 'Cailon86', 'Cailon86', 'temp_hash', 'Cailon86', CURRENT_TIMESTAMP),
('cj_1', 'Cj', 'Cj', 'temp_hash', 'Cj', CURRENT_TIMESTAMP),
('gotnevl_1', 'gotnevl', 'gotnevl', 'temp_hash', 'gotnevl', CURRENT_TIMESTAMP)
ON CONFLICT (discord_id) DO NOTHING;
