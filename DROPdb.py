from sqlalchemy.orm import declarative_base
import psycopg2
from user import user_,password_

Base=declarative_base()
conn=psycopg2.connect(database="postgres",user=user_,password=password_)
conn.autocommit = True
with conn.cursor() as cur:
    try:
        cur.execute("DROP DATABASE IF EXISTS DB_for_bot")
        print('База данных DB_for_bot удалена')
        conn.commit()
    except Exception as err:
        print(err)
    conn.close