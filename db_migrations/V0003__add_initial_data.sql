-- Добавляем фракции открытые
INSERT INTO factions (name, type, description, color, is_open) VALUES
('МВД', 'open', 'Министерство внутренних дел', '#0066CC', TRUE),
('СОБР', 'open', 'Специальный отряд быстрого реагирования', '#003366', TRUE),
('ДПС', 'open', 'Дорожно-патрульная служба', '#0099FF', TRUE),
('Росгвардия', 'open', 'Федеральная служба войск национальной гвардии', '#CC0000', TRUE),
('ЦОДД', 'open', 'Центр организации дорожного движения', '#FF9900', TRUE),
('Армия', 'open', 'Вооружённые силы', '#006600', TRUE);

-- Добавляем закрытые фракции
INSERT INTO factions (name, type, description, color, is_open) VALUES
('ССО', 'closed', 'Силы специальных операций', '#000033', FALSE),
('СБП', 'closed', 'Служба безопасности президента', '#660000', FALSE),
('ФСБ', 'closed', 'Федеральная служба безопасности', '#330033', FALSE),
('ФСО', 'closed', 'Федеральная служба охраны', '#333333', FALSE);

-- Добавляем криминальные структуры
INSERT INTO factions (name, type, description, color, is_open) VALUES
('ОПГ Тёмного', 'criminal', 'Организованная преступная группировка', '#1a1a1a', TRUE),
('ОПГ Красное', 'criminal', 'Организованная преступная группировка', '#8B0000', TRUE),
('Тамбовское ОПГ', 'criminal', 'Организованная преступная группировка', '#4B0082', TRUE);

-- Добавляем ранги администраторов
INSERT INTO custom_roles (name, color, is_admin_role, created_by) VALUES
('Младший администратор', '#3498db', TRUE, 'system'),
('Администратор', '#e74c3c', TRUE, 'system'),
('Старший администратор', '#9b59b6', TRUE, 'system');

-- Добавляем первый админ-код
INSERT INTO admin_codes (code, is_active, created_at) 
VALUES ('99797', TRUE, CURRENT_TIMESTAMP);
