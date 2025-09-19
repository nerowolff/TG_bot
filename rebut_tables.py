from sqlalchemy.orm import  sessionmaker
from sqlalchemy import create_engine
from user import user_,password_
from createDB import Base
engine=create_engine(f'postgresql+psycopg2://{user_}:{password_}@localhost/db_for_bot',connect_args={'options': '-c client_encoding=utf8'})

Session=sessionmaker(bind=engine)
session=Session()
translate_words={
    "food":"еда",
    "breakfast":"завтрак",
    "dinner":"обед или ужин",
    "lunch":"ланч",
    "snack":"закуска",
    "meal":"блюдо",
    "beverage":"напиток",
    "sour":"кислый",
    "bitter":"горький",
    "spicy":"острый",
    "salty":"соленый",
    "sweet":"сладкий"
    }
all_eng_words=["food","breakfast","dinner","lunch","snack","meal","sour","bitter","spicy","salty","sweet","beverage"]

def drop_create_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print('Таблицы обновлены')

def rebut_table(engine,translate_words):
    drop_create_table(engine)
    session.commit()
    session.close()    

if __name__=="__main__":
    rebut_table(engine,translate_words)


