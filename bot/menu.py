#Production by Berlin
#Telegram - @por0vos1k


import telebot
from telebot import types


start = telebot.types.ReplyKeyboardMarkup(True, False)
start.add('Каталог товаров', 'Личный кабинет')
start.add('Информация', 'Связаться')

start_admin = telebot.types.ReplyKeyboardMarkup(True, False)
start_admin.add('Каталог товаров', 'Личный кабинет')
start_admin.row('Админ панель')
start_admin.add('Информация', 'Связаться')


admin = telebot.types.ReplyKeyboardMarkup(True, False)
admin.row('Настройка ответов бота')
admin.add('Настройка ассортимента', 'Загрузка нового товара')
admin.row('Настройка платёжек')
admin.add('Статистика', 'Рассылка')
admin.add('Пользователи', 'Логи')
admin.row('Назад')


users = telebot.types.ReplyKeyboardMarkup(True, False)
users.row('Изменить баланс')
users.row('Изменить кол-во покупок')
users.row('Список пользователей')
users.row('Назад')


send_users = telebot.types.ReplyKeyboardMarkup(True, False)
send_users.row('Все пользователи')
send_users.row('Покупатели')
send_users.row('Ничего не купившие')
send_users.row('Вернуться')


logi = telebot.types.ReplyKeyboardMarkup(True, False)
logi.row('Отправить файлом')
logi.row('Отправить сообщением')
logi.row('Очистить логи')
logi.row('Вернуться')


otmena = telebot.types.ReplyKeyboardMarkup(True, False)
otmena.row('Отмена')
otmena.row('Вернуться')


yes = telebot.types.ReplyKeyboardMarkup(True, False)
yes.row('Да')
yes.row('Нет')


money = telebot.types.ReplyKeyboardMarkup(True, False)
money.row('🥝 Qiwi', '💰Bitcoin')
money.row('🗂 Архив', 'Вернуться')


money_qiwi = telebot.types.ReplyKeyboardMarkup(True, False)
money_qiwi.row('🌐 Ваш баланс')
money_qiwi.add('💳 Получить QIWI', '📤 Отправить QIWI')
money_qiwi.row('Добавить/Изменить данные')
money_qiwi.row('Вернуться')


money_btc = telebot.types.ReplyKeyboardMarkup(True, False)
money_btc.row('🌐 Баланс CoinBase')
money_btc.add('💳 Получить BTC', '📤 Отправить BTC')
money_btc.row('Добавить/изменить данные')
money_btc.row('Вернуться')


assortment = telebot.types.ReplyKeyboardMarkup(True, False)
assortment.add('Добавить позицию', 'Удалить позицию')
assortment.row('Изменить каталог товаров')
assortment.add('Изменить описание позиции', 'Изменить цену позиции')
assortment.row('Выгрузка данных', 'Вернуться')


katalog_1 = telebot.types.ReplyKeyboardMarkup(True, False)
katalog_1.add('Добавить товар в каталог')
katalog_1.add('Удалить товар из каталога')
katalog_1.row('Вернуться')


assortment_data = telebot.types.ReplyKeyboardMarkup(True, False)
assortment_data.row('Выгрузить все позиции')
assortment_data.row('Выгрузить все товары позиции')
assortment_data.row('Вернуться')


yes_or_no = telebot.types.ReplyKeyboardMarkup(True, False)
yes_or_no.row("Да. Я уверен")
yes_or_no.row("Нет. Я передумал")
yes_or_no.row("Вернуться")


new_answer = telebot.types.ReplyKeyboardMarkup(True, False)
new_answer.row('Изменить приветствие пользователя')
new_answer.row('Добавить ответ на кнопку информация')
new_answer.row('Добавить ответ на кнопку связаться')
new_answer.row('Добавить текст после оплаты')
new_answer.row('Вернуться')


info_user = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="Пополнить баланс", callback_data="Пополнить баланс")
but_3 = types.InlineKeyboardButton(text="⬅️ Закрыть", callback_data="⬅️ Закрыть")
info_user.row(but_1)
info_user.row(but_3)


lang = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="🇷🇺Русский", callback_data="🇷🇺Русский")
but_2 = types.InlineKeyboardButton(text="🇬🇧English", callback_data="🇬🇧English")
lang.row(but_1)
lang.row(but_2)


payment_balance = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="🥝 QIWI", callback_data="take_balance_qiwi")
but_2 = types.InlineKeyboardButton(text="💰 BITCOIN", callback_data="take_balance_bitcoin")
but_3 = types.InlineKeyboardButton(text="⬅️ Закрыть", callback_data="⬅️ Закрыть")
payment_balance.add(but_1, but_2)
payment_balance.row(but_3)


close = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="⬅️ Закрыть", callback_data="⬅️ Закрыть")
close.row(but_1)


back_1 = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="⬅️ Назад", callback_data="Назад 1")
back_1.row(but_1)











start_eng = telebot.types.ReplyKeyboardMarkup(True, False)
start_eng.add('Catalog', 'Account')
start_eng.add('Information', 'Contacts')


yes_or_no_eng = telebot.types.ReplyKeyboardMarkup(True, False)
yes_or_no_eng.row("Yes. I'm sure.")
yes_or_no_eng.row("No. I'm not sure.")
yes_or_no_eng.row("Return")

start_admin_eng = telebot.types.ReplyKeyboardMarkup(True, False)
start_admin_eng.add('Catalog', 'Account')
start_admin_eng.row('Admin panel')
start_admin_eng.add('Information', 'Contacts')


admin_eng = telebot.types.ReplyKeyboardMarkup(True, False)
admin_eng.row('Configuring bot responses')
admin_eng.add('Setting up an assortment', 'Loading a new product')
admin_eng.row('Setting up payment cards')
admin_eng.add('Statistics', 'Mailing')
admin_eng.add('Users', 'Logs')
admin_eng.row('Back')


users_eng = telebot.types.ReplyKeyboardMarkup(True, False)
users_eng.row('Change balance')
users_eng.row('Change the number of purchases')
users_eng.row('List of users')
users_eng.row('Back')


send_users_eng = telebot.types.ReplyKeyboardMarkup(True, False)
send_users_eng.row('All users')
send_users_eng.row('Only buyers')
send_users_eng.row('Those who didnt buy anything')
send_users_eng.row('Return')


logi_eng = telebot.types.ReplyKeyboardMarkup(True, False)
logi_eng.row('Send as a file')
logi_eng.row('Send a message')
logi_eng.row('Clear logs')
logi_eng.row('Return')


otmena_eng = telebot.types.ReplyKeyboardMarkup(True, False)
otmena_eng.row('Cancel')
otmena_eng.row('Return')


yes_eng = telebot.types.ReplyKeyboardMarkup(True, False)
yes_eng.row('Yes')
yes_eng.row('No')


money_eng = telebot.types.ReplyKeyboardMarkup(True, False)
money_eng.row('🥝 qiwi', '💰bitcoin')
money_eng.row('🗂 Archive', 'Return')


money_qiwi_eng = telebot.types.ReplyKeyboardMarkup(True, False)
money_qiwi_eng.row('🌐 Your balance')
money_qiwi_eng.add('💳 Receive QIWI', '📤 Send QIWI')
money_qiwi_eng.row('Add/Edit data')
money_qiwi_eng.row('Return')


money_btc_eng = telebot.types.ReplyKeyboardMarkup(True, False)
money_btc_eng.row('🌐 Balance CoinBase')
money_btc_eng.add('💳 Receive BTC', '📤 Send BTC')
money_btc_eng.row('Add/edit data')
money_btc_eng.row('Return')


assortment_eng = telebot.types.ReplyKeyboardMarkup(True, False)
assortment_eng.add('Add a position', 'Delete a position')
assortment_eng.row('Change the product catalog')
assortment_eng.add('Change the item description', 'Change the position price')
assortment_eng.row('Uploading data', 'Return')


katalog_1_eng = telebot.types.ReplyKeyboardMarkup(True, False)
katalog_1_eng.add('Add product to catalog')
katalog_1_eng.add('Remove an item from the catalog')
katalog_1_eng.row('Return')


assortment_data_eng = telebot.types.ReplyKeyboardMarkup(True, False)
assortment_data_eng.row('Show all positions')
assortment_data_eng.row('Show all products of the position')
assortment_data_eng.row('Return')


new_answer_eng = telebot.types.ReplyKeyboardMarkup(True, False)
new_answer_eng.row('Change the users greeting')
new_answer_eng.row('Add a response to the info button')
new_answer_eng.row('Add a response to the contact button')
new_answer_eng.row('Add text after payment')
new_answer_eng.row('Return')


info_user_eng = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="Top up your balance", callback_data="Top up your balance")
but_3 = types.InlineKeyboardButton(text="⬅️ Close", callback_data="⬅️ Close")
info_user_eng.row(but_1)
info_user_eng.row(but_3)


lang = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="🇷🇺Русский", callback_data="🇷🇺Русский")
but_2 = types.InlineKeyboardButton(text="🇬🇧English", callback_data="🇬🇧English")
lang.row(but_1)
lang.row(but_2)


payment_balance_eng = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="🥝 QIWI", callback_data="take_balance_qiwi")
but_2 = types.InlineKeyboardButton(text="💰 BITCOIN", callback_data="take_balance_bitcoin")
but_3 = types.InlineKeyboardButton(text="⬅️ Close", callback_data="⬅️ Close")
payment_balance_eng.add(but_1, but_2)
payment_balance_eng.row(but_3)


close_eng = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="⬅️ Close", callback_data="⬅️ Close")
close_eng.row(but_1)


back_1_eng = types.InlineKeyboardMarkup()
but_1 = types.InlineKeyboardButton(text="⬅️ Back", callback_data="Back 1")
back_1_eng.row(but_1)