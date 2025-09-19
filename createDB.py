from sqlalchemy.orm import declarative_base,relationship
import sqlalchemy as sa
import psycopg2
from user import user_,password_

Base=declarative_base()
conn=psycopg2.connect(database="postgres",
                      user=user_,
                      password=password_)
conn.autocommit = True
def create_DB():
    with conn.cursor() as cur:
        try:        
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'db_for_bot'")
            exists = cur.fetchone()
            if not exists:
                cur.execute("CREATE DATABASE DB_for_bot")
                print('Создана база данных с именем DB_for_bot')
            else:
                print('База данных с таким именем уже существует')
        except Exception as err:
            print(err)   
if __name__=="__main__":
    create_DB()

class User(Base):
    __tablename__='users'
    id = sa.Column(sa.Integer, primary_key=True)
    chat_id= sa.Column(sa.BigInteger,unique=True)
    words = relationship("Word", back_populates="user")
    stats = relationship("UserStats", back_populates="user")
    now_wordlist_index=sa.Column(sa.Integer)
    def __str__(self):
        return f'{self.id} : {self.chat_id}'

class Word(Base):
    __tablename__='words'
    id = sa.Column(sa.Integer, primary_key=True)
    eng_word=sa.Column(sa.String)
    rus_word=sa.Column(sa.String)
    count=sa.Column(sa.Integer, default=0)
    user_id=sa.Column(sa.Integer,sa.ForeignKey('users.id'))
    user=relationship(User,back_populates="words")
    def __str__(self):
        return f'{self.eng_word} : {self.rus_word}'

class UserStats(Base):
    __tablename__ = 'user_stats'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    words_learned = sa.Column(sa.Integer, default=0)
    correct_attempts = sa.Column(sa.Integer, default=0)
    user = relationship("User", back_populates="stats")
    
    def __str__(self):
        return f'Stats for user {self.user_id}'
    

conn.close()

    

