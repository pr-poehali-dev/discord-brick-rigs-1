"""Система авторизации с логином и паролем"""
import json
import os
import jwt
import psycopg2
import hashlib
from datetime import datetime, timedelta

def handler(event: dict, context) -> dict:
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Authorization',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    path = event.get('params', {}).get('path', '')
    
    if path == '/register':
        return register(event)
    elif path == '/login':
        return login(event)
    elif path == '/me':
        return get_current_user(event)
    elif path == '/logout':
        return logout()
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'}),
        'isBase64Encoded': False
    }


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register(event: dict) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        password = body.get('password')
        nickname = body.get('nickname', username)
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Username and password required'}),
                'isBase64Encoded': False
            }
        
        if username == 'TOURIST_WAGNERA':
            password_hash = hash_password('wagnera_tut$45$')
        else:
            password_hash = hash_password(password)
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Username already exists'}),
                'isBase64Encoded': False
            }
        
        is_owner = (username == 'TOURIST_WAGNERA')
        
        cur.execute("""
            INSERT INTO users (username, password_hash, nickname, is_owner, created_at, last_login)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (username, password_hash, nickname, is_owner, datetime.utcnow(), datetime.utcnow()))
        
        user_id = cur.fetchone()[0]
        conn.commit()
        
        token = jwt.encode({
            'user_id': user_id,
            'username': username,
            'is_owner': is_owner,
            'is_admin': False,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, os.environ.get('JWT_SECRET', 'default_secret'), algorithm='HS256')
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-Set-Cookie': f'auth_token={token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=2592000'
            },
            'body': json.dumps({
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'nickname': nickname,
                    'is_owner': is_owner,
                    'is_admin': False
                }
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


def login(event: dict) -> dict:
    try:
        body = json.loads(event.get('body', '{}'))
        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Username and password required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        password_hash = hash_password(password)
        
        cur.execute("""
            SELECT u.id, u.username, u.nickname, u.avatar_url, u.is_owner, u.bio, u.status_text,
                   a.id as admin_id, a.admin_rank, cr.name as role_name, cr.color as role_color
            FROM users u
            LEFT JOIN admins a ON u.id = a.user_id AND a.is_active = TRUE
            LEFT JOIN custom_roles cr ON a.role_id = cr.id
            WHERE u.username = %s AND u.password_hash = %s
        """, (username, password_hash))
        
        user = cur.fetchone()
        
        if not user:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Invalid credentials'}),
                'isBase64Encoded': False
            }
        
        cur.execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.utcnow(), user[0]))
        conn.commit()
        
        token = jwt.encode({
            'user_id': user[0],
            'username': user[1],
            'is_owner': user[4],
            'is_admin': bool(user[7]),
            'exp': datetime.utcnow() + timedelta(days=30)
        }, os.environ.get('JWT_SECRET', 'default_secret'), algorithm='HS256')
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-Set-Cookie': f'auth_token={token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=2592000'
            },
            'body': json.dumps({
                'token': token,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'nickname': user[2],
                    'avatar_url': user[3],
                    'is_owner': user[4],
                    'is_admin': bool(user[7]),
                    'bio': user[5],
                    'status_text': user[6],
                    'admin_rank': user[8],
                    'role': {
                        'name': user[9],
                        'color': user[10]
                    } if user[9] else None
                }
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


def get_current_user(event: dict) -> dict:
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
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT u.id, u.username, u.nickname, u.avatar_url, u.is_owner, u.bio, u.status_text,
                   a.id as admin_id, a.admin_rank, cr.name as role_name, cr.color as role_color
            FROM users u
            LEFT JOIN admins a ON u.id = a.user_id AND a.is_active = TRUE
            LEFT JOIN custom_roles cr ON a.role_id = cr.id
            WHERE u.id = %s
        """, (user_id,))
        
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
                'is_owner': user[4],
                'is_admin': bool(user[7]),
                'bio': user[5],
                'status_text': user[6],
                'admin_rank': user[8],
                'role': {
                    'name': user[9],
                    'color': user[10]
                } if user[9] else None
            }),
            'isBase64Encoded': False
        }
    
    except jwt.ExpiredSignatureError:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Token expired'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def logout() -> dict:
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'X-Set-Cookie': 'auth_token=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0'
        },
        'body': json.dumps({'message': 'Logged out'}),
        'isBase64Encoded': False
    }
