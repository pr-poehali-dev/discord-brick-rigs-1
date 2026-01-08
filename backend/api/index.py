"""Универсальный API для Owner Panel, профилей и фракций"""
import json
import os
import jwt
import psycopg2
from datetime import datetime, timedelta

def handler(event: dict, context) -> dict:
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Authorization',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    path = event.get('params', {}).get('path', '')
    
    if path.startswith('/owner/'):
        return handle_owner(event, method, path)
    elif path.startswith('/profile/'):
        return handle_profile(event, method, path)
    elif path.startswith('/factions/'):
        return handle_factions(event, method, path)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'}),
        'isBase64Encoded': False
    }


def verify_owner(event: dict) -> tuple:
    auth_header = event.get('headers', {}).get('X-Authorization', '')
    token = auth_header.replace('Bearer ', '')
    
    if not token:
        return None, None
    
    try:
        payload = jwt.decode(token, os.environ.get('JWT_SECRET', 'default_secret'), algorithms=['HS256'])
        if not payload.get('is_owner'):
            return None, None
        return payload, payload['user_id']
    except:
        return None, None


def handle_owner(event: dict, method: str, path: str) -> dict:
    payload, user_id = verify_owner(event)
    
    if not payload:
        return {
            'statusCode': 403,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Owner access only'}),
            'isBase64Encoded': False
        }
    
    if '/owner/admins' in path:
        if method == 'GET':
            return get_admins()
        elif method == 'POST':
            return add_admin(event, user_id)
        elif method == 'DELETE':
            return remove_admin(event)
    elif '/owner/admin-code' in path:
        if method == 'GET':
            return get_admin_code()
        elif method == 'PUT':
            return update_admin_code(event)
    elif '/owner/roles' in path:
        if method == 'GET':
            return get_roles()
        elif method == 'POST':
            return create_role(event, user_id)
        elif method == 'PUT':
            return update_role(event)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'}),
        'isBase64Encoded': False
    }


def handle_profile(event: dict, method: str, path: str) -> dict:
    parts = path.split('/')
    
    if len(parts) >= 3 and parts[2] == 'update':
        return update_profile(event)
    elif len(parts) >= 3:
        username = parts[2]
        return get_profile(username)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'}),
        'isBase64Encoded': False
    }


def handle_factions(event: dict, method: str, path: str) -> dict:
    if '/factions/list' in path:
        return get_factions()
    else:
        parts = path.split('/')
        if len(parts) >= 3:
            faction_id = parts[2]
            return get_faction(faction_id)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'}),
        'isBase64Encoded': False
    }


def get_admins() -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT u.id, u.username, u.nickname, u.avatar_url, 
                   a.id as admin_id, a.admin_rank, a.appointed_at, a.is_active,
                   cr.name as role_name, cr.color as role_color
            FROM admins a
            JOIN users u ON a.user_id = u.id
            LEFT JOIN custom_roles cr ON a.role_id = cr.id
            ORDER BY a.appointed_at DESC
        """)
        
        admins = []
        for row in cur.fetchall():
            admins.append({
                'id': row[0],
                'username': row[1],
                'nickname': row[2],
                'avatar_url': row[3],
                'admin_id': row[4],
                'admin_rank': row[5],
                'appointed_at': row[6].isoformat() if row[6] else None,
                'is_active': row[7],
                'role': {'name': row[8], 'color': row[9]} if row[8] else None
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'admins': admins}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def add_admin(event: dict, appointed_by: int) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        admin_rank = body.get('admin_rank')
        role_id = body.get('role_id')
        
        if not username or not admin_rank:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Username and admin_rank required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if not user:
            cur.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'User not found'}),
                'isBase64Encoded': False
            }
        
        user_id = user[0]
        
        cur.execute("""
            INSERT INTO admins (user_id, admin_rank, role_id, appointed_by, appointed_at, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (user_id) DO UPDATE SET
                admin_rank = EXCLUDED.admin_rank,
                role_id = EXCLUDED.role_id,
                is_active = TRUE
            RETURNING id
        """, (user_id, admin_rank, role_id, appointed_by, datetime.utcnow()))
        
        admin_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO admin_logs (admin_id, action_type, target_user_id, details, created_at)
            VALUES (%s, 'ADMIN_APPOINTED', %s, %s, %s)
        """, (appointed_by, user_id, f'Appointed as {admin_rank}', datetime.utcnow()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Admin added', 'admin_id': admin_id}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def remove_admin(event: dict) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        admin_id = body.get('admin_id')
        
        if not admin_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'admin_id required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("UPDATE admins SET is_active = FALSE WHERE id = %s", (admin_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Admin removed'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_admin_code() -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("SELECT code FROM admin_codes WHERE is_active = TRUE ORDER BY created_at DESC LIMIT 1")
        code = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'code': code[0] if code else None}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def update_admin_code(event: dict) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        new_code = body.get('code')
        
        if not new_code:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'code required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("UPDATE admin_codes SET is_active = FALSE WHERE is_active = TRUE")
        cur.execute("""
            INSERT INTO admin_codes (code, is_active, created_at)
            VALUES (%s, TRUE, %s)
        """, (new_code, datetime.utcnow()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Admin code updated', 'code': new_code}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_roles() -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, color, permissions, icon, is_admin_role, created_at
            FROM custom_roles
            ORDER BY created_at DESC
        """)
        
        roles = []
        for row in cur.fetchall():
            roles.append({
                'id': row[0],
                'name': row[1],
                'color': row[2],
                'permissions': row[3],
                'icon': row[4],
                'is_admin_role': row[5],
                'created_at': row[6].isoformat() if row[6] else None
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'roles': roles}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def create_role(event: dict, created_by: int) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        name = body.get('name')
        color = body.get('color', '#999999')
        permissions = body.get('permissions', [])
        icon = body.get('icon')
        is_admin_role = body.get('is_admin_role', False)
        
        if not name:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'name required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO custom_roles (name, color, permissions, icon, is_admin_role, created_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (name, color, permissions, icon, is_admin_role, str(created_by), datetime.utcnow()))
        
        role_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Role created', 'role_id': role_id}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def update_role(event: dict) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        role_id = body.get('role_id')
        name = body.get('name')
        color = body.get('color')
        
        if not role_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'role_id required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        updates = []
        params = []
        
        if name:
            updates.append("name = %s")
            params.append(name)
        if color:
            updates.append("color = %s")
            params.append(color)
        
        if updates:
            updates.append("updated_at = %s")
            params.append(datetime.utcnow())
            params.append(role_id)
            
            query = f"UPDATE custom_roles SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, params)
            conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Role updated'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_profile(username: str) -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT u.id, u.username, u.nickname, u.avatar_url, u.bio, u.status_text, 
                   u.discord_link, u.created_at, u.is_owner,
                   a.admin_rank, cr.name as role_name, cr.color as role_color
            FROM users u
            LEFT JOIN admins a ON u.id = a.user_id AND a.is_active = TRUE
            LEFT JOIN custom_roles cr ON a.role_id = cr.id
            WHERE u.username = %s
        """, (username,))
        
        user = cur.fetchone()
        
        if not user:
            cur.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'User not found'}),
                'isBase64Encoded': False
            }
        
        user_id = user[0]
        
        cur.execute("""
            SELECT f.id, f.name, f.color, f.type, fm.rank, fm.is_general
            FROM faction_members fm
            JOIN factions f ON fm.faction_id = f.id
            WHERE fm.user_id = %s
        """, (user_id,))
        
        factions = []
        for row in cur.fetchall():
            factions.append({
                'id': row[0],
                'name': row[1],
                'color': row[2],
                'type': row[3],
                'rank': row[4],
                'is_general': row[5]
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'id': user[0],
                'username': user[1],
                'nickname': user[2],
                'avatar_url': user[3],
                'bio': user[4],
                'status_text': user[5],
                'discord_link': user[6],
                'created_at': user[7].isoformat() if user[7] else None,
                'is_owner': user[8],
                'admin_rank': user[9],
                'role': {'name': user[10], 'color': user[11]} if user[10] else None,
                'factions': factions
            }),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def update_profile(event: dict) -> dict:
    try:
        auth_header = event.get('headers', {}).get('X-Authorization', '')
        token = auth_header.replace('Bearer ', '')
        
        if not token:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'No token provided'}),
                'isBase64Encoded': False
            }
        
        payload = jwt.decode(token, os.environ.get('JWT_SECRET', 'default_secret'), algorithms=['HS256'])
        user_id = payload['user_id']
        
        body = json.loads(event.get('body', '{}'))
        nickname = body.get('nickname')
        bio = body.get('bio')
        avatar_url = body.get('avatar_url')
        status_text = body.get('status_text')
        discord_link = body.get('discord_link')
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        updates = []
        params = []
        
        if nickname:
            updates.append("nickname = %s")
            params.append(nickname)
        if bio is not None:
            updates.append("bio = %s")
            params.append(bio)
        if avatar_url is not None:
            updates.append("avatar_url = %s")
            params.append(avatar_url)
        if status_text is not None:
            updates.append("status_text = %s")
            params.append(status_text)
        if discord_link is not None:
            updates.append("discord_link = %s")
            params.append(discord_link)
        
        if updates:
            updates.append("updated_at = %s")
            params.append(datetime.utcnow())
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, params)
            conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Profile updated'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_factions() -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, type, description, color, icon, is_open
            FROM factions
            ORDER BY 
                CASE type 
                    WHEN 'open' THEN 1
                    WHEN 'closed' THEN 2
                    WHEN 'criminal' THEN 3
                END,
                name
        """)
        
        factions = []
        for row in cur.fetchall():
            faction_id = row[0]
            
            cur.execute("SELECT COUNT(*) FROM faction_members WHERE faction_id = %s", (faction_id,))
            members_count = cur.fetchone()[0]
            
            cur.execute("""
                SELECT u.username, u.nickname, u.avatar_url, fm.rank
                FROM faction_members fm
                JOIN users u ON fm.user_id = u.id
                WHERE fm.faction_id = %s AND fm.is_general = TRUE
            """, (faction_id,))
            
            generals = []
            for g in cur.fetchall():
                generals.append({
                    'username': g[0],
                    'nickname': g[1],
                    'avatar_url': g[2],
                    'rank': g[3]
                })
            
            factions.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'description': row[3],
                'color': row[4],
                'icon': row[5],
                'is_open': row[6],
                'members_count': members_count,
                'generals': generals
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'factions': factions}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_faction(faction_id: str) -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, name, type, description, color, icon, is_open, created_at
            FROM factions
            WHERE id = %s
        """, (faction_id,))
        
        faction = cur.fetchone()
        
        if not faction:
            cur.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Faction not found'}),
                'isBase64Encoded': False
            }
        
        cur.execute("""
            SELECT u.id, u.username, u.nickname, u.avatar_url, fm.rank, fm.is_general, fm.joined_at
            FROM faction_members fm
            JOIN users u ON fm.user_id = u.id
            WHERE fm.faction_id = %s
            ORDER BY fm.is_general DESC, fm.joined_at ASC
        """, (faction_id,))
        
        members = []
        for row in cur.fetchall():
            members.append({
                'id': row[0],
                'username': row[1],
                'nickname': row[2],
                'avatar_url': row[3],
                'rank': row[4],
                'is_general': row[5],
                'joined_at': row[6].isoformat() if row[6] else None
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'id': faction[0],
                'name': faction[1],
                'type': faction[2],
                'description': faction[3],
                'color': faction[4],
                'icon': faction[5],
                'is_open': faction[6],
                'created_at': faction[7].isoformat() if faction[7] else None,
                'members': members
            }),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
