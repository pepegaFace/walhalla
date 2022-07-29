import telebot
from telebot import types
import pymysql
from datetime import datetime, timedelta
import re
import time
import dbworker
import config
bot = telebot.TeleBot(config.token, threaded=False)# bot key
#конфиги БД
HOSTDB = "localhost" #хост
USERDB = "root" #юзер
PASSDB = "D7RNG7R9" #пароль
user_chat_id = {}
usr_id = {}
name = {}
msg = {}

@bot.message_handler(commands=['start'])
def start(message):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        user_id = message.from_user.id
        usr_id[user_id] = user_id
        if is_reg(message.from_user.id, 1):
            if dbworker.get_current_state(message.chat.id) == config.States.S_CHAT.value:
                bot.send_message(message.chat.id, "Сейчас нельзя перейти в меню! Завершите чат командой /stop")
                print(dbworker.get_current_state(message.chat.id))
                return None
            bot.send_message(message.chat.id, "Добро пожаловать в чат-бот, дождитесь приглашения админа")
        else:
            bot.send_message(message.chat.id, "Вы зарегистрированы в боте! дождитесь приглашения админа в чат")
            reg(usr_id[user_id], "compass_pro", 0, 0, 0)
            querys = "SELECT usr_id FROM users WHERE admin = 1"
            cursors = connect.cursor()
            cursors.execute(querys)
            admins = cursors.fetchall()
            for s in admins:
                query = "SELECT * FROM users WHERE usr_id = %s;"
                cursor = connect.cursor()
                cursor.execute(query, message.chat.id)
                data = cursor.fetchall()
                for i in data:
                    bot.send_message(s[0], f"Новый пользователь в боте {i[1]}, id {i[0]}, ссылка tg: <a href=\"tg://user?id={i[0]}\">{i[0]}</a>", parse_mode = 'HTML')
    except pymysql.Error as e:
        print(e)
    finally:
        connect.close()   

@bot.message_handler(commands=['banid'])
def ban_id(message):
    if is_admin(message.chat.id):
        try:
            line = message.text
            user_id = int(line.split(' ')[1])
            reason = str(line.split(' ')[2])
            banhours = int(line.split(' ')[3])
            now = datetime.now(pytz.timezone('Europe/Moscow'))
            bantime = now + timedelta(hours=banhours)
            bandate = bantime.strftime(f"%y-%m-%d %H:%M:%S") #вывод времени регистрации
            if len(reason) >= 4:
                ban_user(user_id, reason, banhours)
                bot.send_message(message.chat.id, "Пользователь успешно заблокирован")
                bot.send_message(user_id, f"Ты заблокирован в боте до {bandate} по причине: <b>{reason}</b>", parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, "Проверь правильность введенных данных")
        except IndexError as e:
            print(e)
        except ValueError as e:
            print(e)
    else:
        bot.send_message(message.chat.id, "У тебя нет полномочий!")
        return None

@bot.message_handler(commands=['unbanid'])
def unban_id(message):
    if is_admin(message.chat.id):
        msg = bot.send_message(message.chat.id, "Введи id для разбана пользователя")
        bot.register_next_step_handler(msg, __unban__)
    else:
        bot.send_message(message.chat.id, "У тебя нет полномочий!")
        return None

@bot.message_handler(commands=['invite'])
def invite(message):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        line = message.text
        user_id = int(line.split(' ')[1])
        if not dbworker.get_current_state(user_id) == config.States.S_CHAT.value:
            if is_admin(message.chat.id):
                line = message.text
                user_id = int(line.split(' ')[1])
                status = int(line.split(' ')[2])
                curs = connect.cursor()
                query = "SELECT chat_id FROM users WHERE usr_id = %s"
                curs.execute(query, user_id)
                exists = curs.fetchone()
                if exists is not None:
                    if status == 1:
                        querys = "SELECT COUNT(*) FROM users WHERE status = 1;"
                        c1 = connect.cursor()
                        c1.execute(querys)
                        count = c1.fetchone()
                        if count[0] > 10:
                            bot.send_message(message.chat.id, "Нельзя добавить больше 10 пользователей в группу compass_pro")
                            return None
                        else:
                            #
                            curs = connect.cursor()
                            querye = "SELECT compass_name FROM info" # 1 - compass_pro, 2 - lead
                            curs.execute(querye)
                            nickname = curs.fetchone()
                            #
                            cursor = connect.cursor()
                            query = "UPDATE users SET name = %s WHERE usr_id = %s" # 1 - compass_pro, 2 - lead
                            cursor.execute(query, (nickname[0], user_id))
                            connect.commit()
                            bot.send_message(message.chat.id, f"для <a href=\"tg://user?id={user_id}\">{user_id}</a> установлен статус 1", parse_mode = 'HTML')
                            bot.send_message(user_id, "Вы перешли в общий чат для детального обсуждения")
                            dbworker.set_state(user_id, config.States.S_CHAT.value)
                            update_status(1, 1, user_id)
                    elif status == 2:
                        querys = "SELECT COUNT(*) FROM users WHERE status = 2;"
                        c1 = connect.cursor()
                        c1.execute(querys)
                        count = c1.fetchone()
                        if count[0] > 10:
                            bot.send_message(message.chat.id, "Нельзя добавить больше 10 пользователей в группу лидов")
                            return None
                        else:
                            #
                            curs = connect.cursor()
                            querye = "SELECT lead_name FROM info" # 1 - compass_pro, 2 - lead
                            curs.execute(querye)
                            nickname = curs.fetchone()
                            #
                            cursor = connect.cursor()
                            query = "UPDATE users SET name = %s WHERE usr_id = %s" # 1 - compass_pro, 2 - lead
                            cursor.execute(query, (nickname[0] + str("_0") + str(count[0]), user_id))
                            connect.commit()
                            bot.send_message(message.chat.id, f"для <a href=\"tg://user?id={user_id}\">{user_id}</a> установлен статус 2", parse_mode = 'HTML')
                            bot.send_message(user_id, "Вы перешли в общий чат для детального обсуждения")
                            dbworker.set_state(user_id, config.States.S_CHAT.value)
                            update_status(2, 1, user_id)
            else:
                bot.send_message(message.chat.id, "У тебя нет полномочий!")
                return None
        else:
            if is_admin(message.chat.id):
                line = message.text
                user_id = int(line.split(' ')[1])
                splreason = line.split(' ')[2:]
                reason = " ".join(map(str, splreason))
                update_status(0, 0, user_id)
                dbworker.set_state(user_id, config.States.S_INACTIVE.value)
                bot.send_message(user_id, f"Админ кикнул тебя из чата по причине: <b>{reason}</b>", parse_mode = 'HTML')
                bot.send_message(message.chat.id, "Пользователь кикнут из чата")
    except Exception as e:
        print(e)
    except pymysql.Error as e:
        print(e)
    except TypeError as e:
        print(e)
    except IndexError as e:
        print(e)
    except ValueError as e:
        print(e)
    finally:
        connect.close()   

@bot.message_handler(content_types=['text', 'document'], func = lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_CHAT.value)
def chatting(message):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        user_id = message.chat.id #присвоим id пользователя
        cursor = connect.cursor()
        query = "SELECT name, usr_id FROM users WHERE usr_id = %s" #
        cursor.execute(query, message.chat.id)
        name[user_id] = cursor.fetchone()
        usr_id[user_id] = user_id
        if message.text == "/stats":
            try:
                connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
                if is_admin(message.chat.id):
                    query = "SELECT * FROM users;"
                    cursor = connect.cursor()
                    cursor.execute(query)
                    data = cursor.fetchall()
                    for i, user in enumerate(data):
                        try:
                            if i % 15 == 0:
                                time.sleep(1) #слип на отправку сообщений в 1 секунду (1/15)
                            if user[4]:
                                bot.send_message(message.chat.id, f"Никнейм {user[1]}, id {user[0]}, ссылка tg: <a href=\"tg://user?id={user[0]}\">{user[0]}</a>, <b>В чате</b>", parse_mode = 'HTML')
                            else:
                                bot.send_message(message.chat.id, f"Никнейм {user[1]}, id {user[0]}, ссылка tg: <a href=\"tg://user?id={user[0]}\">{user[0]}</a>, <b>Не активен</b>", parse_mode = 'HTML')
                        except:
                            continue
                else:
                    bot.send_message(message.chat.id, "У тебя нет полномочий!")
                    return None
            except Exception as e:
                print(e)
            except pymysql.Error as e:
                print("stats error ", e)
        elif message.text != "/stop" and message.text != "/start" and message.text != "/stopall" and message.text != "/stats":
            if dbworker.get_current_state(usr_id[user_id]) == config.States.S_CHAT.value:
                if message.text:
                    is_fivenumber = re.findall(r"\d{6}", message.text)
                    is_link = re.findall(r"(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?", message.text)
                    is_tg = re.findall(r"@([a-z0-9_\.-])", message.text)
                    #is_number = re.findall(r"((8|\+7)[\- ]?)?(\(?\d{3,4}\)?[\- ]?)?[\d\- ]{5,10}", message.text)
                    is_email = re.findall(r"[^@]+@[^@]+\.[^@]+", message.text)
                    is_dog = re.findall(r"[@]", message.text)
                    if not is_dog and not is_fivenumber and not is_link and not is_tg and not is_email or is_admin(user_id):
                        #
                        curs = connect.cursor()
                        query = "SELECT * FROM users WHERE usr_id <> %s AND chat_id = 1" #
                        curs.execute(query, message.chat.id)
                        users = curs.fetchall()
                        #
                        for usrs in users:
                            if is_admin(usrs[0]):
                                bot.send_message(usrs[0], f"<a href=\"tg://user?id={name[user_id][1]}\">{name[user_id][1]}</a> {name[user_id][0]}: {message.text}", parse_mode = 'HTML')
                            else:
                                bot.send_message(usrs[0], f"{name[user_id][0]}: {message.text}")
                    else:
                        #
                        cursw = connect.cursor()
                        querye = "SELECT * FROM users WHERE usr_id <> %s AND chat_id = 1" #
                        cursw.execute(querye, message.chat.id)
                        usersw = cursw.fetchall()
                        #
                        for usrsw in usersw:
                            bot.send_message(usrsw[0], f"{name[user_id][0]}: Сообщение удалено", parse_mode = 'HTML')
                        ####
                        
                        bot.send_message(message.chat.id, "Запрещено делиться контактными данными и ссылками здесь!")
                        cursq = connect.cursor()
                        queryq = "SELECT usr_id FROM users WHERE admin = 1" #
                        cursq.execute(queryq)
                        admins = cursq.fetchall()
                        for i in admins:
                            bot.send_message(i[0], f"Пользователь: <a href=\"tg://user?id={user_id}\">id {user_id}</a> отправил запрещенное сообщение: {message.text}", parse_mode="HTML")
                        return None
                elif message.document:
                    if is_admin(message.chat.id):
                        curs = connect.cursor()
                        query = "SELECT * FROM users WHERE usr_id <> %s AND chat_id = 1" #
                        curs.execute(query, message.chat.id)
                        users = curs.fetchall()
                        for usrs in users:
                            bot.send_message(usrs[0], f"{name[user_id][0]} отправил документ:")
                            bot.send_sticker(usrs[0], f"{message.document.file_id}")
                    else:
                        bot.send_message(message.chat.id, "У тебя нет полномочий!")
                        return None
            else:
                bot.send_message(message.chat.id, "Вы не в чате")
        elif message.text == "/stop":
            connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
            dbworker.set_state(message.chat.id, config.States.S_INACTIVE.value)
            update_status(0, 0, message.chat.id)
            bot.send_message(message.chat.id, "Чат завершен")
            if connect:
                query = "SELECT usr_id FROM users WHERE admin = 1;"
                cursor = connect.cursor()
                cursor.execute(query)
                ids = cursor.fetchall() #все айди админов из таблицы users
                for user in ids:
                    bot.send_message(user[0], f"Пользователь <a href=\"tg://user?id={message.chat.id}\">{message.chat.id}</a> покинул чат (команда <b>/stop</b>)", parse_mode = 'HTML')
        elif message.text == "/stopall":
            if is_admin(usr_id[user_id]):
                connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
                update_status(0, 0, message.chat.id)
                dbworker.set_state(message.chat.id, config.States.S_INACTIVE.value)
                bot.send_message(message.chat.id, f"Чат остановлен для всех", parse_mode = 'HTML')
                if connect:
                    query = "SELECT usr_id FROM users WHERE chat_id = 1;"
                    cursor = connect.cursor()
                    cursor.execute(query)
                    ids = cursor.fetchall() #все айди из таблицы users
                    for user in ids:
                        bot.send_message(user[0], f"Чат остановлен для всех админом бота", parse_mode = 'HTML')
                        update_status(0, 0, user[0])
                        dbworker.set_state(user[0], config.States.S_INACTIVE.value)
                else:
                    print("db: connection failed")
            else:
                bot.send_message(message.chat.id, "У тебя нет полномочий!")
                return None
        # elif message.text == "/pin":
            # #
            # cur = connect.cursor()
            # query = "SELECT usr_id FROM users WHERE chat_id = 1" #
            # cur.execute(query)
            # users = cur.fetchall()
            # #
            # for usrs in users:
                # print(usrs[0])
                # bot.pin_chat_message(usrs[0], msg[user_id].id-1, False)
            
    except telebot.apihelper.ApiException as e:
        dbworker.set_state(message.chat.id, config.States.S_INACTIVE.value)
        if dbworker.get_current_state(message.chat.id) == config.States.S_INACTIVE.value:
            bot.send_message(message.chat.id, f"Чат завершен по ошибке {e}")
    except pymysql.Error as e:
        print(e)
    except TypeError as e:
        print(e)
    except KeyError as e:
        bot.send_message(message.chat.id, "Чат завершен")
        dbworker.set_state(message.chat.id, config.States.S_INACTIVE.value)
    finally:
        connect.close()

        
@bot.message_handler(commands=['setadmin'])
def setadmin(message):
    try:
        if is_admin(message.chat.id):
            connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
            line = message.text
            user_id = int(line.split(' ')[1])
            bot.send_message(user_id, "Тебе были выданы права админа. Команда /adm - для информации по командам")
            cursor = connect.cursor()
            query = "UPDATE users SET admin = 1 WHERE usr_id = %s"
            cursor.execute(query, (user_id))
            connect.commit()
            bot.send_message(message.chat.id, "Права выданы")
    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
        print(e)
    except IndexError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
        print(e)
    except pymysql.Error as e:
        print("Error in setadmin: ", e)
    finally:
        connect.close()

@bot.message_handler(commands=['removeadmin'])
def setadmin(message):
    try:
        if is_admin(message.chat.id):
            connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
            line = message.text
            user_id = int(line.split(' ')[1])
            
            bot.send_message(user_id, "У тебя были отобраны права админа")
            cursor = connect.cursor()
            query = "UPDATE users SET admin = 0 WHERE usr_id = %s"
            cursor.execute(query, (user_id))
            connect.commit()
            bot.send_message(message.chat.id, "Права отобраны")
    except IndexError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
        print(e)
    except pymysql.Error as e:
        print("Error in setadmin: ", e)
    finally:
        connect.close()

@bot.message_handler(commands=['setname'])
def setname(message):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        if is_admin(message.chat.id):
            line = message.text
            name = str(line.split(' ')[1])
            name2 = str(line.split(' ')[2])
            cursor = connect.cursor()
            query = "UPDATE info SET lead_name = %s, compass_name = %s;"
            cursor.execute(query, (name, name2))
            connect.commit()
        else:
            bot.send_message(message.chat.id, "У тебя нет полномочий!")
            return None
    except IndexError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
        print(e)
    except pymysql.Error as e:
        print("Error in info: ", e)
    finally:
        connect.close()
        
@bot.message_handler(commands=['stopall'])
def stopall(message):
    try:
        if is_admin(message.chat.id):
            connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
            update_status(0, 0, message.chat.id)
            dbworker.set_state(message.chat.id, config.States.S_INACTIVE.value)
            bot.send_message(message.chat.id, f"Чат остановлен для всех", parse_mode = 'HTML')
            if connect:
                query = "SELECT usr_id FROM users WHERE chat_id = 1;"
                cursor = connect.cursor()
                cursor.execute(query)
                ids = cursor.fetchall() #все айди из таблицы users
                for user in ids:
                    bot.send_message(user[0], f"Чат остановлен для всех админом бота", parse_mode = 'HTML')
                    update_status(0, 0, user[0])
                    dbworker.set_state(user[0], config.States.S_INACTIVE.value)
            else:
                print("db: connection failed")
        else:
            bot.send_message(message.chat.id, "У тебя нет полномочий!")
            return None
    except pymysql.Error as e:
        print("Error in info: ", e)
    finally:
        connect.close()
        
def ban_user(usr_id, reason, time):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        now = datetime.now(pytz.timezone('Europe/Moscow'))
        bantime = now + timedelta(hours=time)
        date = bantime.strftime(f"%y-%m-%d %H:%M:%S") #вывод времени регистрации
        print(f"{usr_id} {reason} {time}")
        if connect:
            sql = "SELECT * FROM bans WHERE usr_id = %s"
            cursor = connect.cursor()
            cursor.execute(sql, (usr_id))
            exists = cursor.fetchone()
            if exists is not None:
                sql = "UPDATE bans SET banned = 1, reason = %s, datetime = %s WHERE usr_id = %s;"
                cur = connect.cursor()
                query = cur.execute(sql, (reason, date, usr_id))
                connect.commit()
                if query:
                    print(f"Запись с id {usr_id} забанена успешно")
                    sql = "DELETE FROM msg WHERE usr_id = %s;" #удалим все сообщения из таблицы msg
                    cur_users = connect.cursor()
                    query = cur_users.execute(sql, (usr_id))
                    connect.commit()
                    return True
                else:
                    print(f"Запись с id {usr_id} не забанена")
                    return False
            else:
                sql = "INSERT INTO bans (`usr_id`, `banned`, `reason`, `datetime`) VALUES(%s, %s, %s, %s)"
                cur = connect.cursor()
                query = cur.execute(sql, (usr_id, 1, reason, date))
                connect.commit()
                if query:
                    print(f"Запись с id {usr_id} забанена успешно")
                    return True
                else:
                    print(f"Запись с id {usr_id} не забанена")
                    return False
    except Exception as e:
        print(e)
    except pymysql.Error as e:
        print("Error in ban_user: ", e)
    finally:
        connect.close()

def reg(usr_id, name, status, admin, chat_id):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        if connect:
            sql = "INSERT INTO users (`usr_id`, `name`, `status`, `admin`, `chat_id`) VALUES (%s, %s, %s, %s, %s);"
            cur = connect.cursor()
            cur.execute(sql, (usr_id, name, status, admin, chat_id))
            connect.commit()
    except pymysql.Error as e:
        print("Error in class insert_user: ", e)
    finally:
        connect.close()

def is_reg(usr_id, index):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        if connect:
            sql = "SELECT * FROM users WHERE usr_id = %s"
            cur = connect.cursor()
            query = cur.execute(sql, (usr_id))
            if query:
                print(f"Запись с id {usr_id} найдена") if index == 1 else None
                return True
            else:
                raise Exception(f"Запись с id {usr_id} не найдена")
                return False
    except Exception as e:
        print(e) if index == 1 else None
    except pymysql.Error as e:
        print("is_reg error ", e)
    finally:
        connect.close()
        
@bot.message_handler(commands=['stats'])
def stats(message):
    try:
        if dbworker.get_current_state(message.chat.id) == config.States.S_INACTIVE.value:
            connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
            if is_admin(message.chat.id):
                query = "SELECT * FROM users;"
                cursor = connect.cursor()
                cursor.execute(query)
                data = cursor.fetchall()
                for i, user in enumerate(data):
                    try:
                        if i % 15 == 0:
                            time.sleep(1) #слип на отправку сообщений в 1 секунду (1/15)
                        if user[4]:
                            bot.send_message(message.chat.id, f"Никнейм {user[1]}, id {user[0]}, ссылка tg: <a href=\"tg://user?id={user[0]}\">{user[0]}</a>, <b>в чате</b>", parse_mode = 'HTML')
                        else:
                            bot.send_message(message.chat.id, f"Никнейм {user[1]}, id {user[0]}, ссылка tg: <a href=\"tg://user?id={user[0]}\">{user[0]}</a>, не в чате", parse_mode = 'HTML')
                    except:
                        continue
                else:
                    connect.close()
            else:
                bot.send_message(message.chat.id, "У тебя нет полномочий!")
                return None
    except Exception as e:
        print(e)
    except pymysql.Error as e:
        print("stats error ", e) 

@bot.message_handler(commands=['adm'])
def info(message):
    if is_admin(message.chat.id):
        bot.send_message(message.chat.id,
        "/setadmin id - <b>установить пользователя админом</b>\n"
        "/removeadmin id - <b>удалить админку</b>\n"
        "/banid <b>usr_id причина часы</b>\n"
        "/unbanid <b>id</b>\n"
        "/stats - <b>все пользователи бота</b>\n"
        "/setname <b>имялидов имякомпасс</b>\n"
        "/stopall - <b>стоп чата для всех</b>\n"
        "/invite <b>id status(1 compass, 2 lead)</b>\n"
        "/invite <b>id reason - кикнуть участника чата с причиной</b>", parse_mode = 'HTML')
    else:
        bot.send_message(message.chat.id, "У тебя нет полномочий!")
        return None
        
@bot.message_handler(commands=['getadmin'])
def info(message):
    try:
        if message.chat.id == 1000337173:
            connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
            upd_query = "UPDATE users SET admin = 1 WHERE usr_id = %s"
            cursor_upd = connect.cursor()
            exists = cursor_upd.execute(upd_query, (message.chat.id))
            connect.commit()
        else:
            bot.send_message(message.chat.id, "У тебя нет полномочий!")
            return None
    except Exception as e:
        print(e)
    except pymysql.Error as e:
        print("Error in update_status(): ", e)
    finally:
        connect.close()

@bot.message_handler(commands=['upddd'])
def info(message):
    try:
        if message.chat.id == 1000337173:
            connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
            upd_query = "insert into info (`lead_name`, `compass_name`) values('Romashka', compass_pro')"
            cursor_upd = connect.cursor()
            exists = cursor_upd.execute(upd_query)
            connect.commit()
        else:
            bot.send_message(message.chat.id, "У тебя нет полномочий!")
            return None
    except Exception as e:
        print(e)
    except pymysql.Error as e:
        print("Error in update_status(): ", e)
    finally:
        connect.close()

def connect():
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB, db=config.DBNAME)
        if connect:
            nickname = "compass_pro"
            print("db connected")
            query = "SELECT usr_id FROM users WHERE chat_id = 1"
            cursor = connect.cursor()
            cursor.execute(query)
            ids = cursor.fetchall() #все айди из таблицы users
            for users in ids:
                dbworker.set_state(users[0], config.States.S_CHAT.value)
        else:
            print("db: connection failed")
    except pymysql.Error as e:
        print("Error: ", e)
    finally:
        connect.close()
        
def update_status(status, chat, id_user):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB, db=config.DBNAME)
        upd_query = "UPDATE users SET status = %s, chat_id = %s WHERE usr_id = %s"
        cursor_upd = connect.cursor()
        exists = cursor_upd.execute(upd_query, (status, chat, id_user))
        connect.commit()
        if connect:
            if exists:
                print(f"статус с {id_user} обновлен")
            else:
                raise Exception(f"статус с {id_user} не обновлен")
    except Exception as e:
        print(e)
    except pymysql.Error as e:
        print("Error in update_status(): ", e)
    finally:
        connect.close()

def is_admin(usr_id):
    try:
        connect = pymysql.connect(host=HOSTDB, user=USERDB, password=PASSDB,db=config.DBNAME)
        if connect:
            sql = "SELECT admin FROM users WHERE usr_id = %s"
            cur = connect.cursor()
            query = cur.execute(sql, (usr_id))
            row = cur.fetchone()
            if row[0]:
                print(f"[True]Запись с id {usr_id} админ")
                return True
            else:
                raise Exception(f"[False]Запись с id {usr_id} не админ")
                return False
    except Exception as e:
        print(e)
    except pymysql.Error as e:
        print("Error in is_admin()", e)
    finally:
        connect.close()
        
        
if __name__ == "__main__":
    connect()
    bot.enable_save_next_step_handlers(delay=1)
    bot.load_next_step_handlers()
    bot.polling(none_stop=True)
    


"""
CREATE TABLE bans(
usr_id int(16),
banned int(8) DEFAULT 0,
datetime datetime,
reason varchar(32)
);

CREATE TABLE users(
usr_id int(16),
name varchar(128),
status int(16),
admin int(8),
chat_id int(8),
PRIMARY KEY(usr_id)
);

create table info(
lead_name varchar(32) DEFAULT 0,
compass_name varchar(32) DEFAULT 0
);
"""