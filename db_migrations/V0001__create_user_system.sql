-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(255) UNIQUE NOT NULL,
    discord_username VARCHAR(255) NOT NULL,
    discord_discriminator VARCHAR(10),
    discord_avatar VARCHAR(255),
    nickname VARCHAR(255),
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Таблица кастомных ролей
CREATE TABLE IF NOT EXISTS custom_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    color VARCHAR(7) DEFAULT '#999999',
    permissions TEXT[] DEFAULT '{}',
    icon VARCHAR(50),
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица администраторов
CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(255) UNIQUE NOT NULL,
    role_id INTEGER,
    admin_code VARCHAR(255),
    appointed_by VARCHAR(255) NOT NULL,
    appointed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица банов
CREATE TABLE IF NOT EXISTS bans (
    id SERIAL PRIMARY KEY,
    user_discord_id VARCHAR(255) NOT NULL,
    banned_by VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    duration INTEGER,
    banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица мутов
CREATE TABLE IF NOT EXISTS mutes (
    id SERIAL PRIMARY KEY,
    user_discord_id VARCHAR(255) NOT NULL,
    muted_by VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    duration INTEGER NOT NULL,
    muted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица логов действий админов
CREATE TABLE IF NOT EXISTS admin_logs (
    id SERIAL PRIMARY KEY,
    admin_discord_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    target_discord_id VARCHAR(255),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users(discord_id);
CREATE INDEX IF NOT EXISTS idx_admins_discord_id ON admins(discord_id);
CREATE INDEX IF NOT EXISTS idx_bans_user_discord_id ON bans(user_discord_id);
CREATE INDEX IF NOT EXISTS idx_mutes_user_discord_id ON mutes(user_discord_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_logs(admin_discord_id);
