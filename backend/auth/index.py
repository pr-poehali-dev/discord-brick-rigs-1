"""Discord OAuth авторизация и управление пользователями"""
import json
import os
import jwt
import psycopg2
from datetime import datetime, timedelta
from urllib.parse import urlencode
import urllib.request

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
            'body': ''
        }
    
    path = event.get('params', {}).get('path', '')
    
    if path == '/login':
        return discord_login()
    elif path == '/callback':
        return discord_callback(event)
    elif path == '/me':
        return get_current_user(event)
    elif path == '/logout':
        return logout()
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'})
    }


def discord_login() -> dict:
    client_id = os.environ.get('DISCORD_CLIENT_ID')
    redirect_uri = os.environ.get('DISCORD_REDIRECT_URI')
    
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'identify email'
    }
    
    auth_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'url': auth_url})
    }


def discord_callback(event: dict) -> dict:
    code = event.get('queryStringParameters', {}).get('code')
    
    if not code:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No code provided'})
        }
    
    client_id = os.environ.get('DISCORD_CLIENT_ID')
    client_secret = os.environ.get('DISCORD_CLIENT_SECRET')
    redirect_uri = os.environ.get('DISCORD_REDIRECT_URI')
    
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }
    
    req = urllib.request.Request(
        'https://discord.com/api/oauth2/token',
        data=urlencode(token_data).encode(),
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            token_response = json.loads(response.read().decode())
            access_token = token_response['access_token']
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Failed to get token: {str(e)}'})
        }
    
    user_req = urllib.request.Request(
        'https://discord.com/api/users/@me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    
    try:
        with urllib.request.urlopen(user_req) as response:
            discord_user = json.loads(response.read().decode())
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Failed to get user: {str(e)}'})
        }
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO users (discord_id, discord_username, discord_discriminator, discord_avatar, last_login)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (discord_id) 
            DO UPDATE SET 
                discord_username = EXCLUDED.discord_username,
                discord_discriminator = EXCLUDED.discord_discriminator,
                discord_avatar = EXCLUDED.discord_avatar,
                last_login = EXCLUDED.last_login,
                updated_at = CURRENT_TIMESTAMP
        """, (
            discord_user['id'],
            discord_user['username'],
            discord_user.get('discriminator'),
            discord_user.get('avatar'),
            datetime.utcnow()
        ))
        conn.commit()
        
        cur.execute("""
            SELECT u.*, a.admin_code, a.role_id, a.is_active as is_admin
            FROM users u
            LEFT JOIN admins a ON u.discord_id = a.discord_id
            WHERE u.discord_id = %s
        """, (discord_user['id'],))
        
        user_data = cur.fetchone()
        
        owner_id = os.environ.get('OWNER_DISCORD_ID')
        is_owner = discord_user['id'] == owner_id
        
        jwt_token = jwt.encode({
            'discord_id': discord_user['id'],
            'is_owner': is_owner,
            'is_admin': bool(user_data[10]) if user_data else False,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, os.environ['JWT_SECRET'], algorithm='HS256')
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-Set-Cookie': f'auth_token={jwt_token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=604800'
            },
            'body': json.dumps({
                'token': jwt_token,
                'user': {
                    'discord_id': discord_user['id'],
                    'username': discord_user['username'],
                    'avatar': discord_user.get('avatar'),
                    'is_owner': is_owner,
                    'is_admin': bool(user_data[10]) if user_data else False
                }
            })
        }
    
    except Exception as e:
        conn.rollback()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Database error: {str(e)}'})
        }
    finally:
        cur.close()
        conn.close()


def get_current_user(event: dict) -> dict:
    auth_header = event.get('headers', {}).get('X-Authorization', '')
    token = auth_header.replace('Bearer ', '')
    
    if not token:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'No token provided'})
        }
    
    try:
        payload = jwt.decode(token, os.environ['JWT_SECRET'], algorithms=['HS256'])
        discord_id = payload['discord_id']
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            SELECT u.*, a.admin_code, a.role_id, a.is_active as is_admin, cr.name as role_name, cr.color as role_color
            FROM users u
            LEFT JOIN admins a ON u.discord_id = a.discord_id
            LEFT JOIN custom_roles cr ON a.role_id = cr.id
            WHERE u.discord_id = %s
        """, (discord_id,))
        
        user = cur.fetchone()
        
        if not user:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'User not found'})
            }
        
        owner_id = os.environ.get('OWNER_DISCORD_ID')
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'discord_id': user[1],
                'username': user[2],
                'discriminator': user[3],
                'avatar': user[4],
                'nickname': user[5],
                'bio': user[6],
                'is_owner': user[1] == owner_id,
                'is_admin': bool(user[12]),
                'role': {
                    'name': user[13],
                    'color': user[14]
                } if user[13] else None
            })
        }
    
    except jwt.ExpiredSignatureError:
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Token expired'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


def logout() -> dict:
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'X-Set-Cookie': 'auth_token=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0'
        },
        'body': json.dumps({'message': 'Logged out'})
    }
