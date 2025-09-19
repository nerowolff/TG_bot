import telebot
from telebot import types
from user import user_,password_,TOKEN
from sqlalchemy.orm import  sessionmaker
from rebut_tables import engine,translate_words,all_eng_words,rebut_table
from createDB import Word,User,UserStats
import random

Session=sessionmaker(bind=engine)
session=Session()

bot=telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    this_chat_id=message.chat.id
    markup=types.ReplyKeyboardMarkup(row_width=2)
    target_word_btn=types.KeyboardButton('/next')
    markup.add(target_word_btn)
    exist=session.query(User).filter(User.chat_id == this_chat_id).first()
    if not exist:
        user=User(chat_id=this_chat_id)
        session.add(user)
        session.commit()
        session.refresh(user)
        user_stats=UserStats(user_id=user.id)
        session.add(user_stats)
        for eng,ru in translate_words.items():
            words=Word(eng_word = eng,rus_word = ru,user_id=user.id)
            session.add(words)
        session.commit()
        session.refresh(words)
        session.refresh(user_stats)
    subq=session.query(User).filter(User.chat_id == this_chat_id).first()  #Тут пользователь ТЕКУЩЕЙ сессии
    words_list=session.query(Word).filter(Word.user_id==subq.id).all() #Список!!!!! слов для каждого польозвателя
    if len(words_list) < 1:
        for eng,ru in translate_words.items():
            words=Word(eng_word = eng,rus_word = ru,user_id=subq.id)
            session.add(words)
        session.commit()
    bot.send_message(this_chat_id,"Привет 👋 Давай попрактикуемся в английском языке. Тренировки можешь проходить в удобном для себя темпе.",reply_markup=markup)


@bot.message_handler(commands=['next','Дальше'])
def send_message(message):
    try:
        this_chat_id=message.chat.id
        subq=session.query(User).filter(User.chat_id == this_chat_id).first() #Тут пользователь ТЕКУЩЕЙ сессии
        words_list=session.query(Word).filter(Word.user_id==subq.id).all() #Список!!!!! слов для каждого польозвателя
        if len(words_list)==0:
            bot.send_message(this_chat_id,f'Поздравляем,вы угадали все слова по 5 раз.введите /start чтобы начать сначала')
            return
        else:
            subq.now_wordlist_index=random.randint(0, len(words_list) - 1) #Рандомный индекс для словаря
            markup=types.ReplyKeyboardMarkup(row_width=2)
            target_word=words_list[subq.now_wordlist_index].eng_word
            other_eng_words=[w for w in all_eng_words if w != target_word]
            other_three_words=random.sample(other_eng_words, 3)
            buttons=[target_word]+other_three_words
            random.shuffle(buttons)
            add_opc_but=['/Удалить🔙','/Дальше','/Добавить_слово➕']
            markup.add(*buttons)
            markup.add(*add_opc_but)
            bot.send_message(this_chat_id,f'Угадай слово "{words_list[subq.now_wordlist_index].rus_word}"',reply_markup=markup)
    except Exception as err:
        bot.send_message(this_chat_id,err)

@bot.message_handler(commands=['Добавить_слово➕'])
def add_word(message):
    msg=bot.send_message(message.chat.id,'Введите слово и перевод')
    bot.register_next_step_handler(msg,add_words)
    
@bot.message_handler(commands=['Удалить🔙'])
def delete_from_BD(message):
    try:
        this_chat_id=message.chat.id
        subq=session.query(User).filter(User.chat_id == this_chat_id).first()   #Тут пользователь ТЕКУЩЕЙ сессии
        words_list=session.query(Word).filter(Word.user_id==subq.id).all() #Список!!!!! слов для каждого польозвателя.ссылки на объекты
        if words_list:
            del_word(words_list,subq,this_chat_id)
        else:
            bot.send_message(this_chat_id, "Нет слов для удаления")
    except Exception as err:
        bot.send_message(this_chat_id,err)


@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def chek_word(message):
    try:
        this_chat_id=message.chat.id
        subq=session.query(User).filter(User.chat_id == this_chat_id).first()   #Тут пользователь ТЕКУЩЕЙ сессии
        words_list=session.query(Word).filter(Word.user_id==subq.id).all() #Список!!!!! слов для каждого польозвателя.ссылки на объекты
        stats=subq.stats[0] #Статусы для текущего пользователя
        if words_list[subq.now_wordlist_index].eng_word==message.text:
            words_list[subq.now_wordlist_index].count+=1
            stats.correct_attempts +=1
            bot.send_message(this_chat_id,f'Правильно!!!угадано {stats.correct_attempts} слов')
            
            if  words_list[subq.now_wordlist_index].count == 5:
                bot.send_message(this_chat_id,f' вы угадали слово "{words_list[subq.now_wordlist_index].rus_word}" 5 раз.')
                stats.words_learned += 1
                del_word(words_list,subq,this_chat_id)
            bot.send_message(this_chat_id, "Нажмите /Дальше для следующего слова")
            session.commit()
        else:
            bot.send_message(this_chat_id,f'Неверно =(. попробуйте еще раз.')
            bot.send_message(this_chat_id,f'для перехода к следующему слову нажмите /Дальше')
            # bot.send_message(this_chat_id, "Нажмите /Дальше для следующего слова")
    except Exception as err:
        print(err)


def del_word(words_list,subq,this_chat_id):
    try:
        delete_word=words_list[subq.now_wordlist_index]
        ru_del_wrd=delete_word.rus_word
        session.delete(delete_word)
        session.commit()
        bot.send_message(this_chat_id,f'слово "{ru_del_wrd}" удаляется из выборки')
    except Exception as err:
         session.rollback()
         bot.send_message(this_chat_id,err)


def add_words(msg):
    text=msg.text
    if not text:
        bot.send_message(msg.chat.id, "Нет данных")
        return
    list_text=text.split(' ', 1)
    user=session.query(User).filter(User.chat_id == msg.chat.id).first()#Тут пользователь ТЕКУЩЕЙ сессии
    try:
        words=Word(eng_word = list_text[0],rus_word = list_text[1],user_id=user.id)
        session.add(words)
        session.commit()
    except Exception as err:
        session.rollback()
        bot.send_message(msg.chat.id,f'"слова не добавлены, ошибка {err}"')
    #ДОБАВЛЕНИЕ ЛОГИКи УДАЛЕНИЯ! 
    
    
if __name__=="__main__":
    print('Бот запущен')
    bot.polling()