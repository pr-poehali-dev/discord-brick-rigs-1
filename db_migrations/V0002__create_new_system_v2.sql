-- Добавляем новые поля к users
ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS discord_link VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS status_text VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_owner BOOLEAN DEFAULT FALSE;

-- Создаём уникальный индекс на username
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_unique ON users(username);

-- Таблица фракций
CREATE TABLE IF NOT EXISTS factions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#999999',
    icon VARCHAR(50),
    is_open BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица участников фракций
CREATE TABLE IF NOT EXISTS faction_members (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    faction_id INTEGER NOT NULL,
    rank VARCHAR(100),
    is_general BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавляем поля к custom_roles
ALTER TABLE custom_roles ADD COLUMN IF NOT EXISTS is_admin_role BOOLEAN DEFAULT FALSE;

-- Добавляем поля к admins
ALTER TABLE admins ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE admins ADD COLUMN IF NOT EXISTS admin_rank VARCHAR(100);

-- Таблица админ-кодов
CREATE TABLE IF NOT EXISTS admin_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Добавляем поля к bans
ALTER TABLE bans ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE bans ADD COLUMN IF NOT EXISTS banned_by_id INTEGER;

-- Добавляем поля к mutes
ALTER TABLE mutes ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE mutes ADD COLUMN IF NOT EXISTS muted_by_id INTEGER;

-- Таблица форума
CREATE TABLE IF NOT EXISTS forum_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица комментариев к постам
CREATE TABLE IF NOT EXISTS forum_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавляем поля к admin_logs
ALTER TABLE admin_logs ADD COLUMN IF NOT EXISTS admin_id INTEGER;
ALTER TABLE admin_logs ADD COLUMN IF NOT EXISTS target_user_id INTEGER;

-- Индексы
CREATE INDEX IF NOT EXISTS idx_faction_members_user ON faction_members(user_id);
CREATE INDEX IF NOT EXISTS idx_faction_members_faction ON faction_members(faction_id);
CREATE INDEX IF NOT EXISTS idx_forum_posts_user ON forum_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_forum_comments_post ON forum_comments(post_id);
