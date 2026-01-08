"""Форум - создание постов и комментариев"""
import json
import os
import jwt
import psycopg2
from datetime import datetime

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
    
    if path == '/posts':
        if method == 'GET':
            return get_posts(event)
        elif method == 'POST':
            return create_post(event)
    elif path.startswith('/posts/'):
        post_id = path.split('/')[-1]
        if method == 'GET':
            return get_post(post_id)
        elif method == 'PUT':
            return update_post(event, post_id)
    elif path == '/comments':
        if method == 'POST':
            return add_comment(event)
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'error': 'Not found'}),
        'isBase64Encoded': False
    }


def get_posts(event: dict) -> dict:
    try:
        category = event.get('queryStringParameters', {}).get('category')
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        if category:
            cur.execute("""
                SELECT p.id, p.title, p.content, p.category, p.views, p.likes, p.created_at,
                       u.username, u.nickname, u.avatar_url
                FROM forum_posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.category = %s
                ORDER BY p.created_at DESC
                LIMIT 50
            """, (category,))
        else:
            cur.execute("""
                SELECT p.id, p.title, p.content, p.category, p.views, p.likes, p.created_at,
                       u.username, u.nickname, u.avatar_url
                FROM forum_posts p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
                LIMIT 50
            """)
        
        posts = []
        for row in cur.fetchall():
            post_id = row[0]
            
            cur.execute("SELECT COUNT(*) FROM forum_comments WHERE post_id = %s", (post_id,))
            comments_count = cur.fetchone()[0]
            
            posts.append({
                'id': row[0],
                'title': row[1],
                'content': row[2][:200] + '...' if len(row[2]) > 200 else row[2],
                'category': row[3],
                'views': row[4],
                'likes': row[5],
                'created_at': row[6].isoformat() if row[6] else None,
                'author': {
                    'username': row[7],
                    'nickname': row[8],
                    'avatar_url': row[9]
                },
                'comments_count': comments_count
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'posts': posts}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def create_post(event: dict) -> dict:
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
        title = body.get('title')
        content = body.get('content')
        category = body.get('category', 'general')
        
        if not title or not content:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'title and content required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO forum_posts (user_id, title, content, category, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, title, content, category, datetime.utcnow()))
        
        post_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Post created', 'post_id': post_id}),
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


def get_post(post_id: str) -> dict:
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("UPDATE forum_posts SET views = views + 1 WHERE id = %s", (post_id,))
        conn.commit()
        
        cur.execute("""
            SELECT p.id, p.title, p.content, p.category, p.views, p.likes, p.created_at,
                   u.username, u.nickname, u.avatar_url
            FROM forum_posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """, (post_id,))
        
        post = cur.fetchone()
        
        if not post:
            cur.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Post not found'}),
                'isBase64Encoded': False
            }
        
        cur.execute("""
            SELECT c.id, c.content, c.created_at,
                   u.username, u.nickname, u.avatar_url
            FROM forum_comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        """, (post_id,))
        
        comments = []
        for row in cur.fetchall():
            comments.append({
                'id': row[0],
                'content': row[1],
                'created_at': row[2].isoformat() if row[2] else None,
                'author': {
                    'username': row[3],
                    'nickname': row[4],
                    'avatar_url': row[5]
                }
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'id': post[0],
                'title': post[1],
                'content': post[2],
                'category': post[3],
                'views': post[4],
                'likes': post[5],
                'created_at': post[6].isoformat() if post[6] else None,
                'author': {
                    'username': post[7],
                    'nickname': post[8],
                    'avatar_url': post[9]
                },
                'comments': comments
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


def add_comment(event: dict) -> dict:
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
        post_id = body.get('post_id')
        content = body.get('content')
        
        if not post_id or not content:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'post_id and content required'}),
                'isBase64Encoded': False
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO forum_comments (post_id, user_id, content, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (post_id, user_id, content, datetime.utcnow()))
        
        comment_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Comment added', 'comment_id': comment_id}),
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


def update_post(event: dict, post_id: str) -> dict:
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
        action = body.get('action')
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        
        cur.execute("SELECT user_id FROM forum_posts WHERE id = %s", (post_id,))
        post = cur.fetchone()
        
        if not post:
            cur.close()
            conn.close()
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Post not found'}),
                'isBase64Encoded': False
            }
        
        if action == 'like':
            cur.execute("UPDATE forum_posts SET likes = likes + 1 WHERE id = %s", (post_id,))
            conn.commit()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Post updated'}),
            'isBase64Encoded': False
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
