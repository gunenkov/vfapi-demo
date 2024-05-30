from hashlib import md5
from typing import Optional
import asyncio
from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from db import init_db, reset_db, run_sql_query, run_sql_query_secure
from schemas import User, UserAuthSchema

app = FastAPI(
        title="vFastAPI",
        version="0.0.1",
        )

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
def root():
    return {'goto': '/docs'}

@app.get('/select')
async def sql_return_users_from_username(username: str):
    resp = await run_sql_query(f'SELECT * FROM users WHERE username = "{username}";')
    return resp

@app.post('/auth')
async def auth(auth_schema: UserAuthSchema, response: Response):
    resp = await run_sql_query(f'SELECT * FROM users WHERE username = "{auth_schema.username}" AND password = "{auth_schema.password}";')
    print(resp)
    if type(resp) is dict and 'users' in resp.keys():
        raise HTTPException(status_code=401, detail='Not authorized!')
    response.set_cookie(key='username', value=resp['username'], samesite='none', secure=True)
    return resp['username']

@app.get('/whoami')
async def whoami(request: Request):
    if 'username' not in request.cookies.keys():
        raise HTTPException(status_code=401, detail='Not authorized!')
    return request.cookies['username']

@app.post('/user')
async def add_user(user: User):
    user.password = md5(user.password.encode()).hexdigest()
    query = f'''
INSERT INTO users (
                    name,
                    username,
                    password,
                    address,
                    email,
                    contact
                ) VALUES ( 
                            "{user.name}",
                            "{user.username}",
                            "{user.password}",
                            "{user.address}",
                            "{user.email}",
                            "{user.contact}"
                            );
'''[1:-1]
    await run_sql_query(query, commit=True)
    await run_sql_query('SELECT id from users ORDER BY ROWID DESC limit 1;')
    return {'resp': 'done'}

@app.delete('/user')
async def delete_user(username: Optional[str] = '', user: Optional[User] = None):
    if username:
        await run_sql_query(f'DELETE FROM users WHERE username = "{username}";', commit=True)
        return {'resp': 'done'}
    elif user:
        await run_sql_query(f'DELETE FROM users WHERE address = {user.address};', commit=True)
    return {'resp': '!done'}

@app.put('/put')
async def put():
    return {'resp': 'done'}

@app.post('/reset')
async def reset_database():
    await reset_db()
    return {'resp': 'done'}

if __name__ == '__main__':
    asyncio.run(init_db()); __import__('uvicorn').run('main:app', host='0.0.0.0', port=8888, reload=False)
