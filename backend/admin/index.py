"""Admin Panel - бан, мут, управление ролями пользователей"""
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
    
    auth_header = event.get('headers', {}).get('X-Authorization', '')
    token = auth_header.replace('Bearer ', '')
    
    if not token:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No token provided'}),
            'isBase64Encoded': False
        }
    
    try:
        payload = jwt.decode(token, os.environ.get('JWT_SECRET', 'default_secret'), algorithms=['HS256'])
        if not payload.get('is_admin') and not payload.get('is_owner'):
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Admin access only'}),
                'isBase64Encoded': False
            }
        admin_id = payload['user_id']
    except:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Invalid token'}),
            'isBase64Encoded': False
        }
    
    path = event.get('params', {}).get('path', '')
    
    if path == '/ban':
        return ban_user(event, admin_id)
    elif path == '/unban':
        return unban_user(event, admin_id)
    elif path == '/mute':
        return mute_user(event, admin_id)
    elif path == '/unmute':
        return unmute_user(event, admin_id)
    elif path == '/assign-role':
        return assign_faction_role(event, admin_id)
    elif path == '/users':
        return get_users(event)
    elif path == '/logs':
        return get_admin_logs()
    elif path == '/verify-code':
        return verify_admin_code(event)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'}),
        'isBase64Encoded': False
    }


def verify_admin_code(event: dict) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        code = body.get('code')
        
        if not code:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'code required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM admin_codes WHERE code = %s AND is_active = TRUE", (code,))
        valid = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'valid': bool(valid)}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def ban_user(event: dict, admin_id: int) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        reason = body.get('reason', 'No reason provided')
        duration = body.get('duration')
        
        if not username:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'username required'}),
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
        expires_at = (datetime.utcnow() + timedelta(hours=duration)) if duration else None
        
        cur.execute("""
            INSERT INTO bans (user_id, banned_by_id, reason, duration, banned_at, expires_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (user_id, admin_id, reason, duration, datetime.utcnow(), expires_at))
        
        cur.execute("""
            INSERT INTO admin_logs (admin_id, action_type, target_user_id, details, created_at)
            VALUES (%s, 'BAN', %s, %s, %s)
        """, (admin_id, user_id, f'Reason: {reason}', datetime.utcnow()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'User banned'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def unban_user(event: dict, admin_id: int) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        
        if not username:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'username required'}),
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
        
        cur.execute("UPDATE bans SET is_active = FALSE WHERE user_id = %s AND is_active = TRUE", (user_id,))
        
        cur.execute("""
            INSERT INTO admin_logs (admin_id, action_type, target_user_id, details, created_at)
            VALUES (%s, 'UNBAN', %s, 'User unbanned', %s)
        """, (admin_id, user_id, datetime.utcnow()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'User unbanned'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def mute_user(event: dict, admin_id: int) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        reason = body.get('reason', 'No reason provided')
        duration = body.get('duration', 60)
        
        if not username:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'username required'}),
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
        expires_at = datetime.utcnow() + timedelta(minutes=duration)
        
        cur.execute("""
            INSERT INTO mutes (user_id, muted_by_id, reason, duration, muted_at, expires_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """, (user_id, admin_id, reason, duration, datetime.utcnow(), expires_at))
        
        cur.execute("""
            INSERT INTO admin_logs (admin_id, action_type, target_user_id, details, created_at)
            VALUES (%s, 'MUTE', %s, %s, %s)
        """, (admin_id, user_id, f'Reason: {reason}, Duration: {duration}m', datetime.utcnow()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'User muted'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def unmute_user(event: dict, admin_id: int) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        
        if not username:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'username required'}),
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
        
        cur.execute("UPDATE mutes SET is_active = FALSE WHERE user_id = %s AND is_active = TRUE", (user_id,))
        
        cur.execute("""
            INSERT INTO admin_logs (admin_id, action_type, target_user_id, details, created_at)
            VALUES (%s, 'UNMUTE', %s, 'User unmuted', %s)
        """, (admin_id, user_id, datetime.utcnow()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'User unmuted'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def assign_faction_role(event: dict, admin_id: int) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        faction_id = body.get('faction_id')
        rank = body.get('rank')
        
        if not username or not faction_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'username and faction_id required'}),
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
            INSERT INTO faction_members (user_id, faction_id, rank, joined_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (user_id, faction_id, rank, datetime.utcnow()))
        
        cur.execute("""
            INSERT INTO admin_logs (admin_id, action_type, target_user_id, details, created_at)
            VALUES (%s, 'ASSIGN_FACTION', %s, %s, %s)
        """, (admin_id, user_id, f'Assigned to faction {faction_id}', datetime.utcnow()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Faction role assigned'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_users(event: dict) -> dict:
    try:
        search = event.get('queryStringParameters', {}).get('search', '')
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        if search:
            cur.execute("""
                SELECT u.id, u.username, u.nickname, u.avatar_url, u.status_text, u.is_owner,
                       a.admin_rank, b.is_active as is_banned, m.is_active as is_muted
                FROM users u
                LEFT JOIN admins a ON u.id = a.user_id AND a.is_active = TRUE
                LEFT JOIN bans b ON u.id = b.user_id AND b.is_active = TRUE
                LEFT JOIN mutes m ON u.id = m.user_id AND m.is_active = TRUE
                WHERE u.username ILIKE %s OR u.nickname ILIKE %s
                LIMIT 50
            """, (f'%{search}%', f'%{search}%'))
        else:
            cur.execute("""
                SELECT u.id, u.username, u.nickname, u.avatar_url, u.status_text, u.is_owner,
                       a.admin_rank, b.is_active as is_banned, m.is_active as is_muted
                FROM users u
                LEFT JOIN admins a ON u.id = a.user_id AND a.is_active = TRUE
                LEFT JOIN bans b ON u.id = b.user_id AND b.is_active = TRUE
                LEFT JOIN mutes m ON u.id = m.user_id AND m.is_active = TRUE
                ORDER BY u.created_at DESC
                LIMIT 50
            """)
        
        users = []
        for row in cur.fetchall():
            users.append({
                'id': row[0],
                'username': row[1],
                'nickname': row[2],
                'avatar_url': row[3],
                'status_text': row[4],
                'is_owner': row[5],
                'admin_rank': row[6],
                'is_banned': bool(row[7]),
                'is_muted': bool(row[8])
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'users': users}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def get_admin_logs() -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT l.id, l.action_type, l.details, l.created_at,
                   u1.username as admin_username, u2.username as target_username
            FROM admin_logs l
            LEFT JOIN users u1 ON l.admin_id = u1.id
            LEFT JOIN users u2 ON l.target_user_id = u2.id
            ORDER BY l.created_at DESC
            LIMIT 100
        """)
        
        logs = []
        for row in cur.fetchall():
            logs.append({
                'id': row[0],
                'action_type': row[1],
                'details': row[2],
                'created_at': row[3].isoformat() if row[3] else None,
                'admin_username': row[4],
                'target_username': row[5]
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'logs': logs}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
