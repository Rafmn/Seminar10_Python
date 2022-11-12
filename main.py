# Доработать бота об игре в конфеты или создать любого игрового бота.

import logging
import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

reply_keyboard = [['/info', '/play', '/close']]
bot_keyboard = [['/simple_bot', '/clever_bot']]
stop_keyboard = [['/stop']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
bot_markup = ReplyKeyboardMarkup(bot_keyboard, one_time_keyboard=False)
stop_markup = ReplyKeyboardMarkup(stop_keyboard, one_time_keyboard=False)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

with open('file_with_token.txt') as f:
    token = f.readline()
TOKEN = token

sweety = 0
flag = False # simple_bot

def start(update, context):
    update.message.reply_text("Привет! Это бот с игрой в конфеты! Нажмите info чтоб прочитать правила или play чтоб начать играть", reply_markup=markup)

def play(update, context):
    update.message.reply_text("С каким ботом будете играть, с обычным (simple) или умным (clerer)?", reply_markup=bot_markup)
    # return 1

def simple_bot(update, context):
    update.message.reply_text("Вы выбрали обычного бота. Введите количество конфет с которыми будете играть", reply_markup=stop_markup)
    global flag
    flag = True
    return 1

def clever_bot(update, context):
    global flag
    flag = False
    update.message.reply_text("Вы выбрали умного бота. Введите количество конфет с которыми будете играть", reply_markup=stop_markup)
    return 1

def play_get_sweety(update, context):
    global sweety
    sweety = int(update.message.text) 
    update.message.reply_text("Сколько конфет вы возьмете? Можно взять от 1 до 28 конфет")
    if flag == True:
        return 2
    else:
        return 3

def play_simple_bot(update, context):
    global sweety
    try:
        ent_num = int(update.message.text)
        if not 1 <= ent_num <= 28:
            update.message.reply_text("Введите число от 1 до 28")
            return 3
        sweety = sweety - ent_num        
        update.message.reply_text(f"Конфет было: {sweety}")
        if sweety > 28:
            temp = random.randint(1, 28)
            sweety -= temp
            update.message.reply_text(f"Бот взял {temp} конфет. Конфет осталось: {sweety}")
            if sweety > 28:
                update.message.reply_text("Сколько конфет вы возьмете?")
            else:
                update.message.reply_text("Вы победили!", reply_markup=markup)
                file_gif = open('photo_win.gif', 'rb')
                context.bot.send_document(chat_id=update.effective_chat.id, document=file_gif)
                return ConversationHandler.END
            return 2
        else:
            update.message.reply_text("Бот выиграл", reply_markup=markup)
            file_gif = open('bot_win.gif', 'rb')
            context.bot.send_document(chat_id=update.effective_chat.id, document=file_gif)
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Введите число от 1 до 28")
        return 2

def sweets_bot(sweety):   # Calculate how many sweets clever_bot must take
    a = sweety // 28
    if a % 2 == 0 or sweety % 28 == 0:      
        sweets = 28                  
    else:                                   
        if sweety % 28 == 1:                
            sweets = 1               
        else:                               
            sweets = sweety % 28 - 1
    return sweets

def play_clever_bot(update, context):
    global sweety
    try:
        ent_num = int(update.message.text)
        if not 1 <= ent_num <= 28:
            update.message.reply_text("Введите число от 1 до 28")
            return 3
        sweety = sweety - ent_num
        update.message.reply_text(f"Было {sweety} конфет")
        if sweety > 28:
            sweet_bots = sweets_bot(sweety)
            sweety -= sweet_bots
            update.message.reply_text(f"Бот взял {sweet_bots} конфет. Конфет осталось: {sweety}")
            if sweety > 28:
                update.message.reply_text("Сколько конфет вы возьмете?")
            else:
                update.message.reply_text("Вы победили!", reply_markup=markup)
                file_gif = open('photo_win.gif', 'rb')
                context.bot.send_document(chat_id=update.effective_chat.id, document=file_gif)
                return ConversationHandler.END
            return 3
        else:
            update.message.reply_text("Бот победил", reply_markup=markup)
            file_gif = open('bot_win.gif', 'rb')
            context.bot.send_document(chat_id=update.effective_chat.id, document=file_gif)
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Введите число от 1 до 28")
        return 3

def stop(update, context):
    update.message.reply_text("Удачи!", reply_markup=markup)
    return ConversationHandler.END

def info(update, context):
    update.message.reply_text("Правила игры с конфетами: Для начала необходимо ввести общее количество конфет. Далее по очереди из общей кучи забираете от 1 до 28 конфет. Побеждает тот, кто сможет забрать все последние конфеты.")

def close(update, context):
    update.message.reply_text("Спасибо за игру!", reply_makup=markup)

play_handler = ConversationHandler(
    entry_points=[CommandHandler('simple_bot', simple_bot), CommandHandler('clever_bot', clever_bot)],
    
    # Condition into the chat
    states = {
        1: [MessageHandler(Filters.text & ~Filters.command, play_get_sweety)],
        2: [MessageHandler(Filters.text & ~Filters.command, play_simple_bot)],
        3: [MessageHandler(Filters.text & ~Filters.command, play_clever_bot)],
    },
    
    # Point of command '/stop'
    fallbacks=[CommandHandler("stop", stop)]
)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(play_handler)
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("close", close))
    dp.add_handler(CommandHandler("play", play))
    dp.add_handler(CommandHandler("clever_bot", clever_bot))
    dp.add_handler(CommandHandler("simple_bot", simple_bot))
    


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()