from os import path, remove
import aiosqlite
from faker import Faker
from hashlib import md5


DB_FILENAME = 'vfapi'

fake = Faker()

async def get_sql_db():
    db = await aiosqlite.connect(database=f'{DB_FILENAME}.sql.db')
    return db

async def init_sql_db():
    if path.isfile(f'{DB_FILENAME}.sql.db'):
        remove(f'{DB_FILENAME}.sql.db')
    db = await get_sql_db()
    await db.execute('''
CREATE TABLE users ( id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     username TEXT NOT NULL,
                     password TEXT NOT NULL,
                     address TEXT NOT NULL,
                     email TEXT NOT NULL,
                     contact TEXT NOT NULL
                     );'''[1:])
    await db.commit()
    for _ in range(10):
        query = f'''
INSERT INTO users ( name,
                    username,
                    password,
                    address,
                    email,
                    contact
                    )
       VALUES (
                "{fake.name()}",
                "{fake.user_name()}",
                "{md5(fake.password().encode()).hexdigest()}",
                "{fake.address()}",
                "{fake.email()}",
                "{fake.phone_number()}"
            ) ;
'''[1:-1]
        await db.execute(query)
        await db.commit()
    await db.close()
    return True

async def init_db():
    await init_sql_db()

async def reset_db():
    remove(f'{DB_FILENAME}.sql.db')
    await init_sql_db()

async def run_sql_query(query, commit=False):
    print(query)
    db = await get_sql_db()
    cursor = await db.execute(query)
    _data, data = await cursor.fetchall(), {}
    if commit: await db.commit()
    await cursor.close()
    await db.close()
    if len(_data) == 1:
        if len(_data[0]) == 1 and type(_data[0][0]) == int:
            return _data[0][0]
        _data = _data[0]
        data['id'] = _data[0]
        data['name'] = _data[1]
        data['username'] = _data[2]
        data['address'] = _data[4]
        data['email'] = _data[5]
        data['contact'] = _data[6]
        return data
    return {'users': _data}

async def run_sql_query_secure(query_with_params, commit=False):
    print(query_with_params)
    db = await get_sql_db()

    cursor = await db.execute(*query_with_params)
    _data, data = await cursor.fetchall(), {}
    if commit: await db.commit()
    await cursor.close()
    await db.close()
    if len(_data) == 1:
        if len(_data[0]) == 1 and type(_data[0][0]) == int:
            return _data[0][0]
        _data = _data[0]
        data['id'] = _data[0]
        data['name'] = _data[1]
        data['username'] = _data[2]
        data['address'] = _data[4]
        data['email'] = _data[5]
        data['contact'] = _data[6]
        return data
    return {'users': _data}