# - *- coding: utf- 8 - *-

import io
import os
import codecs
import chardet
import logging
import datetime
import requests
import traceback
from time import sleep
from functools import wraps

import telebot
import SimpleQIWI
from SimpleQIWI import *
from telebot import types
from bittrex import BittrexError
from bittrex import BittrexClient
from coinbase.wallet.client import Client

import db
import menu
import text
import config


bot = telebot.TeleBot(config.token, parse_mode=None)
print("Start")
db.init_db()

banned_users = []

today = datetime.datetime.today()

NOTIFY_PAIR = "USD-BTC"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
					level=logging.INFO,
					filename='bot.log')

try:
	api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
	balance = api.balance[0]
	db.add_qiwi_later(balance)
except:
	print(traceback.format_exc())


file_1 = open("coinbase_api_key.txt", "r")
file_2 = open("coinbase_api_secret.txt", "r")
api_key = file_1.read()
api_secret = file_2.read()
client = Client(api_key, api_secret)


all_users_file = open("joined.txt", "r")
all_users = set()
for line in all_users_file:
	all_users.add(line.strip())
all_users_file.close()


not_buyers_file = open("ot_buyers.txt", "r")
not_buyers = set()
for line in not_buyers_file:
	not_buyers.add(line.strip())
not_buyers_file.close()


def send_users(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.send_users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.send_users)
				else:
					logging.info("Была отправлена рассылка (всем пользователям).")
					bot.send_message(config.admin_id, '✅ Рассылка была успешно отправлена!', reply_markup=menu.send_users)
					for user in all_users:
						bot.send_message(user, message.text, reply_markup=menu.close)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.send_users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.send_users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.send_users_eng)
				else:
					logging.info("Была отправлена рассылка (всем пользователям).")
					bot.send_message(config.admin_id, '✅ The newsletter was sent successfully!', reply_markup=menu.send_users_eng)
					for user in all_users:
						bot.send_message(user, message.text, reply_markup=menu.close_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.send_users_eng)


def send_money_3(message, account, amount):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
				else:
					comment = message.text
					api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
					api.pay(account=account, amount=amount, comment=comment)
					logging.info("Деньги были успешно отправлены. Платежная система - qiwi.")
					bot.send_message(config.admin_id, '✅ Деньги успешно отправлены!', reply_markup=menu.money_qiwi)
					bot.send_message(config.admin_id, 'Если деньги не пришли, значит вы неверно указали данные.')
			except:
				logging.info("Ошибка! Деньги не были отправлены. Платежная система - qiwi.")
				text = 'Деньги не были отправлены по одной из этих причин:'
				text_1 = "1. Пополнение ненастоящего Qiwi кошелька."
				text_2 = "2. Недостаточно средств."
				text_3 = '3. Ежемесячный лимит платежей и переводов - ограничен.'
				text_4 = '4. В примечание к платежу было добавлено что-то, кроме текста.'
				bot.send_message(config.admin_id, "❌ Ошибка!\n\n{}\n{}\n{}\n{}\n{}".format(text, text_1, text_2, text_3, text_4), reply_markup=menu.money_qiwi)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
				else:
					comment = message.text
					api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
					api.pay(account=account, amount=amount, comment=comment)
					logging.info("Деньги были успешно отправлены. Платежная система - qiwi.")
					bot.send_message(config.admin_id, '✅ The money has been successfully sent!', reply_markup=menu.money_qiwi_eng)
					bot.send_message(config.admin_id, 'If the money did not arrive, it means that you entered the data incorrectly.')
			except:
				logging.info("Ошибка! Деньги не были отправлены. Платежная система - qiwi.")
				text = 'The money was not sent for one of these reasons:'
				text_1 = "1. Replenishment of a fake Qiwi wallet."
				text_2 = "2. Insufficient funds."
				text_3 = '3. The monthly limit of payments and transfers is limited.'
				text_4 = '4. Something other than text has been added to the payment note.'
				bot.send_message(config.admin_id, "❌ Error!\n\n{}\n{}\n{}\n{}\n{}".format(text, text_1, text_2, text_3, text_4), reply_markup=menu.money_qiwi_eng)


def send_money_2(message, account):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
			else:
				amount = message.text
				msg = bot.send_message(config.admin_id, 'Введите примечание к переводу:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_money_3, account, amount)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
			else:
				amount = message.text
				msg = bot.send_message(config.admin_id, 'Enter a comment for the translation:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_money_3, account, amount)


def send_money_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
			else:
				account = message.text
				msg = bot.send_message(config.admin_id, 'Введите сумму перевода:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_money_2, account)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
			else:
				account = message.text
				msg = bot.send_message(config.admin_id, 'Enter the transfer amount:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_money_2, account)


def send_bitcoin_2(message, address):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
			else:
				try:
					amount = message.text
					client = Client(api_key, api_secret, api_version='2021-01-16')
					primary_account = client.get_primary_account()
					primary_account.send_money(to=address, amount=amount, currency='BTC')
					logging.info("Деньги были успешно отправлены. Платежная система - bitcoin.")
					bot.send_message(config.admin_id, '✅ Деньги успешно отправлены!', reply_markup=menu.money_btc)
					bot.send_message(config.admin_id, 'Если деньги не пришли, значит вы неверно указали данные.')
				except:
					logging.info("Ошибка! Деньги не были отправлены. Платежная система - bitcoin.")
					text = 'Деньги не были отправлены по одной из этих причин:'
					text_1 = "1. Недостаточно средств."
					text_2 = "2. Был введен не настоящий адрес."
					text_3 = '3. Нельзя переводить деньги на свой же адрес.'
					bot.send_message(config.admin_id, "❌ Ошибка!\n\n{}\n{}\n{}\n{}".format(text, text_1, text_2, text_3), reply_markup=menu.money_btc)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
			else:
				try:
					amount = message.text
					client = Client(api_key, api_secret, api_version='2021-01-16')
					primary_account = client.get_primary_account()
					primary_account.send_money(to=address, amount=amount, currency='BTC')
					logging.info("Деньги были успешно отправлены. Платежная система - bitcoin.")
					bot.send_message(config.admin_id, '✅ The money has been successfully sent!', reply_markup=menu.money_btc_eng)
					bot.send_message(config.admin_id, 'If the money did not arrive, it means that you entered the data incorrectly.')
				except:
					logging.info("Ошибка! Деньги не были отправлены. Платежная система - bitcoin.")
					text = 'The money was not sent for one of these reasons:'
					text_1 = "1. Insufficient funds."
					text_2 = "2. A fake address was entered."
					text_3 = '3. You can not transfer money to your own address.'
					bot.send_message(config.admin_id, "❌ Error!\n\n{}\n{}\n{}\n{}".format(text, text_1, text_2, text_3), reply_markup=menu.money_btc_eng)


def send_bitcoin(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
			else:
				address = message.text
				msg = bot.send_message(config.admin_id, 'Введите сумму перевода:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_bitcoin_2, address)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
			else:
				address = message.text
				msg = bot.send_message(config.admin_id, 'Enter the transfer amount:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_bitcoin_2, address)


def send_buyers(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.send_users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.send_users)
				else:
					buyers_file = open("yers.txt", "r")
					buyers = set()
					for line in buyers_file:
						buyers.add(line.strip())
					buyers_file.close()
					logging.info("Рассылка была отправлена (покупателям)")
					bot.send_message(config.admin_id, '✅ Рассылка была успешно отправлена!', reply_markup=menu.send_users)
					for user in buyers:
						bot.send_message(user, message.text, reply_markup=menu.close)
			except:
				print(traceback.format_exc())
				#bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.send_users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.send_users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.send_users_eng)
				else:
					buyers_file = open("yers.txt", "r")
					buyers = set()
					for line in buyers_file:
						buyers.add(line.strip())
					buyers_file.close()
					logging.info("Рассылка была отправлена (покупателям)")
					bot.send_message(config.admin_id, '✅ The newsletter was sent successfully!', reply_markup=menu.send_users_eng)
					for user in buyers:
						bot.send_message(user, message.text, reply_markup=menu.close_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.send_users_eng)


def send_not_buyers(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.send_users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.send_users)
				else:
					buyers_file = open("yers.txt", "r")
					buyers = set()
					for line in buyers_file:
						buyers.add(line.strip())
					buyers_file.close()
					logging.info("Рассылка была отправлена (не покупателям)")
					bot.send_message(config.admin_id, '✅ Рассылка была успешно отправлена!', reply_markup=menu.send_users)
					for user in all_users:
						if user not in buyers:
							bot.send_message(user, message.text, reply_markup=menu.close)
			except:
				print(traceback.format_exc())
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.send_users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.send_users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.send_users_eng)
				else:
					buyers_file = open("yers.txt", "r")
					buyers = set()
					for line in buyers_file:
						buyers.add(line.strip())
					buyers_file.close()
					logging.info("Рассылка была отправлена (не покупателям)")
					bot.send_message(config.admin_id, '✅ The newsletter was sent successfully!', reply_markup=menu.send_users_eng)
					for user in all_users:
						if user not in buyers:
							bot.send_message(user, message.text, reply_markup=menu.close_eng)
			except:
				print(traceback.format_exc())
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.send_users_eng)


def hello_edit(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				else:
					db.edit_settings_hel(message.text)
					logging.info("Изменено приветствие пользователя.")
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.new_answer)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.new_answer)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				else:
					db.edit_settings_hel(message.text)
					logging.info("Изменено приветствие пользователя.")
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.new_answer_eng)
			except:
				print(traceback.format_exc())
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.new_answer_eng)


def change_balance_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				else:
					user_id = message.text
					result = db.find_user_balance_name(user_id)
					msg = bot.send_message(config.admin_id, '<a>🌀 Пользователь: <b>{}</b>\n🙍‍♂️Имя: <b>{}</b>\n💰Баланс: <b>{}</b> ₽\n\nВведите желаемую сумму:</a>'.format(user_id, result[1], result[0]), parse_mode='HTML', reply_markup=menu.otmena)
					bot.register_next_step_handler(msg, change_balance_2, user_id)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				else:
					user_id = message.text
					result = db.find_user_balance_name(user_id)
					msg = bot.send_message(config.admin_id, '<a>🌀 User: <b>{}</b>\n🙍‍♂️Name: <b>{}</b>\n💰Balance: <b>{}</b> ₽\n\nEnter the desired amount:</a>'.format(user_id, result[1], result[0]), parse_mode='HTML', reply_markup=menu.otmena_eng)
					bot.register_next_step_handler(msg, change_balance_2, user_id)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.users_eng)


def change_purchase_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				else:
					user_id = message.text
					result = db.find_user_purchase_name(user_id)
					msg = bot.send_message(config.admin_id, '<a>🌀 Пользователь: <b>{}</b>\n🙍‍♂️Имя: <b>{}</b>\n🛍 Кол-во покупок: <b>{}</b>\n\nВведите новое значение:</a>'.format(user_id, result[1], result[0]), parse_mode='HTML', reply_markup=menu.otmena)
					bot.register_next_step_handler(msg, change_purchase_2, user_id)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				else:
					user_id = message.text
					result = db.find_user_purchase_name(user_id)
					msg = bot.send_message(config.admin_id, '<a>🌀 User: <b>{}</b>\n🙍‍♂️Name: <b>{}</b>\n🛍 Purchases: <b>{}</b>\n\nEnter a new value:</a>'.format(user_id, result[1], result[0]), parse_mode='HTML', reply_markup=menu.otmena_eng)
					bot.register_next_step_handler(msg, change_purchase_2, user_id)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.users_eng)


def change_balance_2(message, user_id):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				else:
					balance = message.text
					db.update_user_balance(balance, user_id)
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.users)
			except:
				logging.info("Ошибка! Раздел - смена баланса.")
				bot.send_message(config.admin_id, "❌ Ошибка!", reply_markup=menu.users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				else:
					balance = message.text
					db.update_user_balance(balance, user_id)
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.users_eng)
			except:
				logging.info("Ошибка! Раздел - смена баланса.")
				bot.send_message(config.admin_id, "❌ Error!", reply_markup=menu.users_eng)


def change_purchase_2(message, user_id):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				else:
					purchase = message.text
					db.update_user_purchase(purchase, user_id)
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.users)
			except:
				logging.info("Ошибка! Раздел - смена кол-во покупок.")
				bot.send_message(config.admin_id, "❌ Ошибка!", reply_markup=menu.users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				else:
					purchase = message.text
					db.update_user_purchase(purchase, user_id)
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.users_eng)
			except:
				logging.info("Ошибка! Раздел - смена кол-во покупок.")
				bot.send_message(config.admin_id, "❌ Error!", reply_markup=menu.users_eng)


def yes_2(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Нет':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'не':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'отменить':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Да':
					msg = bot.send_message(config.admin_id, 'Введите id пользователя:', reply_markup=menu.otmena)
					bot.register_next_step_handler(msg, change_balance_1)
				elif message.text == 'да':
					msg = bot.send_message(config.admin_id, 'Введите id пользователя:', reply_markup=menu.otmena)
					bot.register_next_step_handler(msg, change_balance_1)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'No':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'no':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Yes':
					msg = bot.send_message(config.admin_id, 'Enter the user ID:', reply_markup=menu.otmena_eng)
					bot.register_next_step_handler(msg, change_balance_1)
				elif message.text == 'yes':
					msg = bot.send_message(config.admin_id, 'Enter the user ID:', reply_markup=menu.otmena_eng)
					bot.register_next_step_handler(msg, change_balance_1)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.users_eng)


def yes_3(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Нет':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'не':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'отменить':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.users)
				elif message.text == 'Да':
					msg = bot.send_message(config.admin_id, 'Введите id пользователя:', reply_markup=menu.otmena)
					bot.register_next_step_handler(msg, change_purchase_1)
				elif message.text == 'да':
					msg = bot.send_message(config.admin_id, 'Введите id пользователя:', reply_markup=menu.otmena)
					bot.register_next_step_handler(msg, change_purchase_1)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.users)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'No':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'no':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.users_eng)
				elif message.text == 'Yes':
					msg = bot.send_message(config.admin_id, 'Enter the user ID:', reply_markup=menu.otmena_eng)
					bot.register_next_step_handler(msg, change_purchase_1)
				elif message.text == 'yes':
					msg = bot.send_message(config.admin_id, 'Enter the user ID:', reply_markup=menu.otmena_eng)
					bot.register_next_step_handler(msg, change_purchase_1)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.users_eng)


def kek(message, number):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
				else:
					f_number = open("edit_qiwi_money_number.txt", "w")
					f_token = open("edit_qiwi_money_token.txt", "w")
					f_number.write(number)
					f_token.write(message.text)
					logging.info("Изменены платежные данные Qiwi.")
					bot.send_message(config.admin_id, "✅ Сохранено!", reply_markup=menu.money_qiwi)
					bot.send_message(config.admin_id, "Для корректной работа платежной системы - перезапустите бота.", reply_markup=menu.money_qiwi)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.money_qiwi)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
				else:
					f_number = open("edit_qiwi_money_number.txt", "w")
					f_token = open("edit_qiwi_money_token.txt", "w")
					f_number.write(number)
					f_token.write(message.text)
					logging.info("Изменены платежные данные Qiwi.")
					bot.send_message(config.admin_id, "✅ Saved!", reply_markup=menu.money_qiwi_eng)
					bot.send_message(config.admin_id, "For the correct operation of the payment system - restart the bot.", reply_markup=menu.money_qiwi_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.money_qiwi_eng)


def no(message, key):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
				else:
					f_key = open("coinbase_api_key.txt", "w")
					f_secret = open("coinbase_api_secret.txt", "w")
					f_key.write(key)
					f_secret.write(message.text)
					logging.info("Изменены платежные данные Bitcoin.")
					bot.send_message(config.admin_id, "✅ Сохранено!", reply_markup=menu.money_btc)
					bot.send_message(config.admin_id, "Для корректной работа платежной системы - перезапустите бота.", reply_markup=menu.money_btc)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.money_btc)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
				else:
					f_key = open("coinbase_api_key.txt", "w")
					f_secret = open("coinbase_api_secret.txt", "w")
					f_key.write(key)
					f_secret.write(message.text)
					logging.info("Изменены платежные данные Bitcoin.")
					bot.send_message(config.admin_id, "✅ Saved!", reply_markup=menu.money_btc_eng)
					bot.send_message(config.admin_id, "For the correct operation of the payment system - restart the bot.", reply_markup=menu.money_btc_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.money_btc_eng)


def lol(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_qiwi)
			else:
				number = message.text
				msg = bot.send_message(config.admin_id, 'Введите токен:\n\nПолучить его можно здесь - https://qiwi.com/api', disable_web_page_preview=True, reply_markup=menu.otmena, parse_mode='HTML')
				bot.register_next_step_handler(msg, kek, number)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_qiwi_eng)
			else:
				number = message.text
				msg = bot.send_message(config.admin_id, 'Enter the token:\n\nYou can get it here - https://qiwi.com/api', disable_web_page_preview=True, reply_markup=menu.otmena_eng, parse_mode='HTML')
				bot.register_next_step_handler(msg, kek, number)


def pos_6(message, name_katalog, name, description, item, price):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				else:
					lot = message.text
					print(lot)
					db.add_position(name_katalog, name, description, price, item, lot)
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.assortment)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка!", reply_markup=menu.assortment)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				else:
					lot = message.text
					print(lot)
					db.add_position(name_katalog, name, description, price, item, lot)
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.assortment_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error!", reply_markup=menu.assortment_eng)


def pos_5(message, name_katalog, name, description, item):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			else:
				price = message.text
				msg = bot.send_message(config.admin_id, 'Введите количество товара:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, pos_6, name_katalog, name, description, item, price)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			else:
				price = message.text
				msg = bot.send_message(config.admin_id, 'Enter the product quantity:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, pos_6, name_katalog, name, description, item, price)


def pos_4(message, name_katalog, name, description):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			else:
				item = message.text
				msg = bot.send_message(config.admin_id, 'Введите цену товара:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, pos_5, name_katalog, name, description, item)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			else:
				item = message.text
				msg = bot.send_message(config.admin_id, 'Enter the product price:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, pos_5, name_katalog, name, description, item)


def pos_3(message, name_katalog, name):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			else:
				description = message.text
				text = db.return_product_2()
				msg = bot.send_message(config.admin_id, 'Выберите товар:\n\n{}\n\nНеобходимо ввести название.'.format(text), reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, pos_4, name_katalog, name, description)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			else:
				description = message.text
				text = db.return_product_2()
				msg = bot.send_message(config.admin_id, 'Select the product\n\n{}\n\nYou must enter a name.'.format(text), reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, pos_4, name_katalog, name, description)


def pos_2(message, name_katalog):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, 'Придумайте описание:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, pos_3, name_katalog, name)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, 'Come up with a description:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, pos_3, name_katalog, name)


def pos_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			else:
				name_katalog = message.text
				msg = bot.send_message(config.admin_id, 'Введите название новой позиции:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, pos_2, name_katalog)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			else:
				name_katalog = message.text
				msg = bot.send_message(config.admin_id, 'Enter the name of the new position:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, pos_2, name_katalog)


def yes(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.money_btc)
			else:
				key = message.text
				msg = bot.send_message(config.admin_id, "Введите секретный ключ API:",reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, no, key)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.money_btc_eng)
			else:
				key = message.text
				msg = bot.send_message(config.admin_id, "Enter the API secret key:",reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, no, key)


def delete_position_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				else:
					text = message.text
					db.delete_position(text)
					logging.info("Позиция была успешно удалена.")
					bot.send_message(config.admin_id, "✅ Позиция была успешно удалена!", reply_markup=menu.assortment)
					bot.send_message(config.admin_id, "Если этого не произошло, значит вы ввели неверные данные.", reply_markup=menu.assortment)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка!", reply_markup=menu.assortment)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				else:
					text = message.text
					db.delete_position(text)
					logging.info("Позиция была успешно удалена.")
					bot.send_message(config.admin_id, "✅ The position was successfully deleted!", reply_markup=menu.assortment_eng)
					bot.send_message(config.admin_id, "If this did not happen, then you entered the wrong data.", reply_markup=menu.assortment_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error!", reply_markup=menu.assortment_eng)


def edit_position_2(message, name):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				else:
					description = message.text
					db.edit_position(description, name)
					logging.info("Описание было успешно изменено.")
					bot.send_message(config.admin_id, "✅ Описание было успешно изменено!", reply_markup=menu.assortment)
					bot.send_message(config.admin_id, "Если этого не произошло, значит вы ввели неверные данные.", reply_markup=menu.assortment)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка!", reply_markup=menu.assortment)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				else:
					description = message.text
					db.edit_position(description, name)
					logging.info("Описание было успешно изменено.")
					bot.send_message(config.admin_id, "✅ The description was successfully changed!", reply_markup=menu.assortment_eng)
					bot.send_message(config.admin_id, "If this did not happen, then you entered the wrong data.", reply_markup=menu.assortment_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error!", reply_markup=menu.assortment_eng)


def edit_position_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, "Придумайте описание:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, edit_position_2, name)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, "Come up with a description:", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, edit_position_2, name)


def change_position_2(message, name):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
				else:
					price = message.text
					db.change_position(price, name)
					logging.info("Цена была успешно изменена.")
					bot.send_message(config.admin_id, "✅ Цена была успешно изменена!", reply_markup=menu.assortment)
					bot.send_message(config.admin_id, "Если этого не произошло, значит вы ввели неверные данные.", reply_markup=menu.assortment)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка!", reply_markup=menu.assortment)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
				else:
					price = message.text
					db.change_position(price, name)
					logging.info("Цена была успешно изменена.")
					bot.send_message(config.admin_id, "✅ The price was successfully changed!", reply_markup=menu.assortment_eng)
					bot.send_message(config.admin_id, "If this did not happen, then you entered the wrong data.", reply_markup=menu.assortment_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error!", reply_markup=menu.assortment_eng)


def change_position_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.assortment)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, "Введите новую цену позиции:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, change_position_2, name)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.assortment_eng)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, "Enter the new position price:", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, change_position_2, name)


def information_edit(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				else:
					db.edit_settings_inf(message.text)
					logging.info("Информация о магазине была изменена.")
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.new_answer)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.new_answer)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				else:
					db.edit_settings_inf(message.text)
					logging.info("Информация о магазине была изменена.")
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.new_answer_eng)
			except:
				logging.info("Error!")
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.new_answer_eng)


def contact_edit(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				else:
					db.edit_settings_con(message.text)
					logging.info("Контактная информация была изменена.")
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.new_answer)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.new_answer)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				else:
					db.edit_settings_con(message.text)
					logging.info("Контактная информация была изменена.")
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.new_answer_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.new_answer_eng)


def new_item_2(message, name):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.admin)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.admin)
				else:
					url = message.text
					db.add_product(url, name)
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.admin)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.admin)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.admin_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.admin_eng)
				else:
					url = message.text
					db.add_product(url, name)
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.admin_eng)
			except:
				logging.info("Error!")
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.admin_eng)


def assort_2_add(message, name):
	try:
		if message.chat.id == config.admin_id:
			language = db.return_user_lang(message.chat.id)
			if str(language) == "('Russian',)":
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.katalog_1)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.katalog_1)
				else:
					description = message.text
					db.add_katalog(name, description)
					bot.send_message(config.admin_id, "✅ Сохранено!", reply_markup=menu.katalog_1)
			else:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.katalog_1_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.katalog_1_eng)
				else:
					description = message.text
					db.add_katalog(name, description)
					bot.send_message(config.admin_id, "✅ Saved!", reply_markup=menu.katalog_1_eng)
	except:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			bot.send_message(config.admin_id, "❌ Ошибка!", reply_markup=menu.katalog_1)
		else:
			bot.send_message(config.admin_id, "❌ Error!", reply_markup=menu.katalog_1_eng)


def assort_1_add(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.katalog_1)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.katalog_1)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, "Введите текст, который будет указан сверху:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, assort_2_add, name)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.katalog_1_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.katalog_1_eng)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, "Enter the text that will be shown at the top:", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, assort_2_add, name)


def assort_1_delete(message):
	try:
		if message.chat.id == config.admin_id:
			language = db.return_user_lang(message.chat.id)
			if str(language) == "('Russian',)":
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.katalog_1)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.katalog_1)
				else:
					number = message.text
					db.delete_katalog(number)
					logging.info("Запись была удалена.")
					bot.send_message(config.admin_id, "✅ Запись была удалена!", reply_markup=menu.katalog_1)
					bot.send_message(config.admin_id, "Если она не была удалена, значит вы ввели неверное название.", reply_markup=menu.katalog_1)
			else:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.katalog_1_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.katalog_1_eng)
				else:
					number = message.text
					db.delete_katalog(number)
					logging.info("Запись была удалена.")
					bot.send_message(config.admin_id, "✅ The entry was deleted!", reply_markup=menu.katalog_1_eng)
					bot.send_message(config.admin_id, "If it was not deleted, then you entered the wrong name.", reply_markup=menu.katalog_1_eng)
	except:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			bot.send_message(config.admin_id, "❌ Ошибка! Введен неверный id.", reply_markup=menu.katalog_1)
		else:
			bot.send_message(config.admin_id, "❌ Error! Invalid id entered.", reply_markup=menu.katalog_1_eng)


def new_item_1(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			if message.text == 'Отмена':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.admin)
			elif message.text == 'Вернуться':
				bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.admin)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, 'Введите ссылку для скачивания товара (файла) или текст, который получит покупатель.\n\nПример:\n1️⃣ Ваша покупка - https://cloud.mail.ru/public/2hYB/3PhDV7XmD\n\n2️⃣ Ваша покупка -\nЛогин: autobot2021\nПароль: 12345', disable_web_page_preview = False, reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, new_item_2, name)
		else:
			if message.text == 'Cancel':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.admin_eng)
			elif message.text == 'Return':
				bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.admin_eng)
			else:
				name = message.text
				msg = bot.send_message(config.admin_id, 'Enter the link to download the product (file) or the text that the buyer will receive.\n\nExample:\n1️⃣ Your purchase - https://cloud.mail.ru/public/2hYB/3PhDV7XmD\n\n2️⃣ Your purchase -\nLogin: autobot2021\nPassword: 12345', disable_web_page_preview = False, reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, new_item_2, name)


def payment_edit(message):
	if message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			try:
				if message.text == 'Отмена':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				elif message.text == 'Вернуться':
					bot.send_message(config.admin_id, "Вы отменили действие", reply_markup=menu.new_answer)
				else:
					db.edit_settings_pay(message.text)
					logging.info("Текст после оплаты успешно изменен.")
					bot.send_message(config.admin_id, '✅ Сохранено!', reply_markup=menu.new_answer)
			except:
				bot.send_message(config.admin_id, "❌ Ошибка! Отправлять можно только текст.", reply_markup=menu.new_answer)
		else:
			try:
				if message.text == 'Cancel':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				elif message.text == 'Return':
					bot.send_message(config.admin_id, "You canceled the action", reply_markup=menu.new_answer_eng)
				else:
					db.edit_settings_pay(message.text)
					logging.info("Текст после оплаты успешно изменен.")
					bot.send_message(config.admin_id, '✅ Saved!', reply_markup=menu.new_answer_eng)
			except:
				bot.send_message(config.admin_id, "❌ Error! You can only send text.", reply_markup=menu.new_answer_eng)


@bot.message_handler(commands=["start"])
def send_welcome(message):
	language = db.return_user_lang(message.chat.id)
	if not str(message.chat.id) in all_users:
		language = db.return_user_lang(message.chat.id)
		if language == "('English',)":
			logging.info("Добавлен новый пользователь. ID: "+str(message.chat.id))
			first_name = message.from_user.first_name
			last_name = message.from_user.last_name
			user_id = message.from_user.id
			today = datetime.datetime.today()
			date = today.strftime("%Y-%m-%d")
			db.add_user(first_name, last_name, date, user_id)
			all_users_file = open("joined.txt", "a")
			all_users_file.write(str(message.chat.id) + "\n")
			all_users.add(str(message.chat.id))
			text = db.return_hello()
			text_2_2 = str(text).replace("('", "")
			text_3_2 = text_2_2.replace("',)", "")
			bot.send_message(message.chat.id, text_3_2, reply_markup=menu.start)
			bot.send_message(message.chat.id, "Select a language:", reply_markup=menu.lang)
		else:
			logging.info("Добавлен новый пользователь. ID: "+str(message.chat.id))
			first_name = message.from_user.first_name
			last_name = message.from_user.last_name
			user_id = message.from_user.id
			today = datetime.datetime.today()
			date = today.strftime("%Y-%m-%d")
			db.add_user(first_name, last_name, date, user_id)
			all_users_file = open("joined.txt", "a")
			all_users_file.write(str(message.chat.id) + "\n")
			all_users.add(str(message.chat.id))
			text = db.return_hello()
			text_2_2 = str(text).replace("('", "")
			text_3_2 = text_2_2.replace("',)", "")
			bot.send_message(message.chat.id, text_3_2, reply_markup=menu.start_eng)
			bot.send_message(message.chat.id, "Выберите язык:", reply_markup=menu.lang)
	elif message.chat.id == config.admin_id:
		language = db.return_user_lang(message.chat.id)
		if str(language) == "('Russian',)":
			logging.info("Администратор вошел в систему. ID: "+str(message.chat.id))
			text_1 = db.return_hello()
			text_2_2 = str(text_1).replace("('", "")
			text_3_2 = text_2_2.replace("',)", "")
			text_2 = "Добро пожаловать! Вы администратор этого магазина, вы можете полностью настроить бота."
			bot.send_message(config.admin_id, '{}\n\n{}'.format(text_3_2, text_2), reply_markup=menu.start_admin)
		else:
			logging.info("Администратор вошел в систему. ID: "+str(message.chat.id))
			text_1 = db.return_hello()
			text_2_2 = str(text_1).replace("('", "")
			text_3_2 = text_2_2.replace("',)", "")
			text_2 = "Welcome! You are the administrator of this store, you can fully configure the bot."
			bot.send_message(config.admin_id, '{}\n\n{}'.format(text_3_2, text_2), reply_markup=menu.start_admin_eng)
	else:
		language = db.return_user_lang(message.chat.id)
		if language == "('Russian',)":
			logging.info("Пользователь вошел в систему. ID: "+str(message.chat.id))
			text = db.return_hello()
			text_2_2 = str(text).replace("('", "")
			text_3_2 = text_2_2.replace("',)", "")
			bot.send_message(message.chat.id, text_3_2, reply_markup=menu.start)
		else:
			logging.info("Пользователь вошел в систему. ID: "+str(message.chat.id))
			text = db.return_hello()
			text_2_2 = str(text).replace("('", "")
			text_3_2 = text_2_2.replace("',)", "")
			bot.send_message(message.chat.id, text_3_2, reply_markup=menu.start_eng)


@bot.message_handler(commands=["lang"])
def change(message):
	language = db.return_user_lang(message.chat.id)
	if str(language) == "('Russian',)":
		bot.send_message(message.chat.id, "Выберите язык:", reply_markup=menu.lang)
	else:
		bot.send_message(message.chat.id, "Select a language:", reply_markup=menu.lang)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	language = db.return_user_lang(call.message.chat.id)
	if str(language) == "('Russian',)":
		api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
		try:
			balance = api.balance[0]
			db.add_qiwi_later(balance)
		except:
			logging.info(traceback.format_exc())
		client_2 = Client(api_key, api_secret, api_version='2021-01-16')
		message = []
		primary_account = client_2.get_primary_account()
		try:
			address = primary_account.create_address()
		except:
			print("Error!")
		address = str(address['deposit_uri']).replace('bitcoin:', '')
		price = 1
		comment = api.bill(price)
		client = BittrexClient()
		text_1 = db.return_katalog()
		text_2 = db.return_position_3()
		text_3 = db.return_position_price()

		for x in text_1:
			if call.data in x:
				aaa = db.return_position_5(call.data)
				lol = str(aaa[0]).replace("(", "")
				kek = lol.replace(",)", "")
				if kek == "1":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					keyboard.row(but_1)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "2":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					keyboard.row(but_1)
					keyboard.row(but_2)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "3":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "4":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "5":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "6":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "7":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "8":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "9":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					text_1_9 = db.return_position_4(call.data)
					test_9 = str(text_1_9[8])
					text_2_9 = test_9.replace("('", "")
					text_3_9 = text_2_9.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)
					keyboard.row(but_9)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "10":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					text_1_9 = db.return_position_4(call.data)
					test_9 = str(text_1_9[8])
					text_2_9 = test_9.replace("('", "")
					text_3_9 = text_2_9.replace("',)", "")

					text_1_10 = db.return_position_4(call.data)
					test_10 = str(text_1_10[9])
					text_2_10 = test_10.replace("('", "")
					text_3_10 = text_2_10.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
					but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)
					keyboard.row(but_9)
					keyboard.row(but_10)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek > "10":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					text_1_9 = db.return_position_4(call.data)
					test_9 = str(text_1_9[8])
					text_2_9 = test_9.replace("('", "")
					text_3_9 = text_2_9.replace("',)", "")

					text_1_10 = db.return_position_4(call.data)
					test_10 = str(text_1_10[9])
					text_2_10 = test_10.replace("('", "")
					text_3_10 = text_2_10.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
					but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)
					keyboard.row(but_9)
					keyboard.row(but_10)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)

		for y in text_2:
			if call.data in y:
				name = call.data
				description = db.return_tovar_description(call.data)
				test = str(description[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				lot = db.return_tovar_lot(call.data)
				test_2 = str(lot[0])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				price = db.return_tovar_price(call.data)
				test_3 = str(price[0])
				text_2_3 = test_3.replace("('", "")
				joker = text_2_3.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text="✅ Оплатить", callback_data=joker)
				keyboard.row(but_1)

				bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>🔥<b>{}</b>\n\n{}\n\n<b>Количество товара:</b> {} шт.\n<b>Цена:</b> {} ₽</a>".format(name, text_3, text_3_2, joker), parse_mode="HTML")
				bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)

		for z in text_3:
			try:
				test = int(call.data)
				if test in z:
					text = db.return_lot(test)
					q = str(text).replace("(", "")
					we = q.replace(",)", "")
					if int(we) >= 0:
						balance = db.show_user_balance(call.message.chat.id)
						q = str(balance).replace("(", "")
						w = q.replace(",)", "")
						pr = int(w)
						prs = int(test)
						if pr >= prs:
							t_1 =  db.return_position_item(prs)
							text_2_2 = str(t_1).replace("('", "")
							text_3_2 = text_2_2.replace("',)", "")

							t_2 = db.return_item(text_3_2)
							text_2_3 = str(t_2).replace("('", "")
							url = text_2_3.replace("',)", "")

							pv = db.return_payment()
							pv_2 = str(pv).replace("('", "")
							pv_3 = pv_2.replace("',)", "")

							bot.send_message(call.message.chat.id, '{}\n\nВаша покупка - {}'.format(pv_3, url))

							a_b = 1
							m = int(we)
							lot = m - a_b

							b_1 = db.show_user_balance(call.message.chat.id)
							b_1_1 = str(b_1).replace("(", "")
							b_1_2 = b_1_1.replace(",)", "")

							z = int(b_1_2)
							balance = z - test

							p_1 = db.return_purchase(call.message.chat.id)
							p_1_1 = str(p_1).replace("(", "")
							p_1_2 = p_1_1.replace(",)", "")

							v = int(p_1_2)
							purchase = v + a_b
							date = today.strftime("%Y-%m-%d")

							c_1 = db.return_cash_1()
							c_1_1 = str(c_1).replace("(", "")
							c_1_2 = c_1_1.replace(",)", "")

							j = int(c_1_2)
							cash = j + test

							db.edit_lot(lot, test)
							db.add_balance(balance, call.message.chat.id)
							db.add_purchase(purchase, call.message.chat.id)

							db.add_sale(call.message.chat.id, test, date)
							db.edit_cash(cash)

							file = open(r"yers.txt", "w")
							t = str(call.message.chat.id)
							file.write(t + '\n')

							bot.send_message(config.admin_id, "<a><b>🎉 У вас новый покупатель!\n\nПользователь:</b> {}\n<b>Сумма покупки:</b> {} ₽\n<b>Дата:</b> {}</a>".format(call.message.chat.id, test, date), parse_mode='HTML')

							l = db.return_buyers_2()
							for x in l:
								if call.message.chat.id not in x:
									db.add_buyer(call.message.chat.id, call.message.from_user.first_name, call.message.from_user.last_name)
								else:
									print(traceback.format_exc())
						else:
							bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="❗️Недостаточно средств")
					else:
						bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="К сожалению, данный товар закончился")
			except:
				logging.info(traceback.format_exc())

		if call.message:
			if call.data == '⬅️ Закрыть':
				bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'Пополнить баланс':
				bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.payment_balance)
			elif call.data == 'take_balance_qiwi':

				name = db.show_user_name(call.message.chat.id)
				register = db.show_user_register(call.message.chat.id)
				purchase = db.show_user_purchase(call.message.chat.id)
				balance = db.show_user_balance(call.message.chat.id)
				take_money = db.show_user_take_money(call.message.chat.id)

				if name[0] == None:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Имя:</b> отсутствует\n<b>👨‍💻 Мой ID:</b> {}\n<b>💰 Мой баланс:</b> {} ₽\n<b>🛒 Покупок:</b> {}\n<b>💸 Сумма пополнений:</b> {} ₽\n<b>📝 Зарегистрирован:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user)
				else:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Имя:</b> {}\n<b>👨‍💻 Мой ID:</b> {}\n<b>💰 Мой баланс:</b> {} ₽\n<b>🛒 Покупок:</b> {}\n<b>💸 Сумма пополнений:</b> {} ₽\n<b>📝 Зарегистрирован:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(name[0], call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user)

				url = "https://qiwi.com/payment/form/99?extra%5B%27account%27%5D=" + config.qiwi_number + "&amountInteger=None&amountFraction=0&extra%5B%27comment%27%5D=" + comment + "&currency=643&blocked[0]=account&blocked[2]=comment"
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text="Проверить оплату", callback_data="Проверить оплату 1")
				but_2 = types.InlineKeyboardButton(text="Оплатить в браузере", url=url)
				but_3 = types.InlineKeyboardButton(text="⬅️ Закрыть", callback_data="⬅️ Закрыть")
				keyboard.add(but_1, but_2)
				keyboard.row(but_3)
				bot.send_message(call.message.chat.id, "<a>Информация об оплате\n\n🥝 QIWI-кошелек: <pre>{}</pre>\n\n📝 Комментарий к переводу: <pre>{}</pre>\n➖➖➖➖➖➖➖➖➖➖\n\nПополните указанный киви кошелёк на любую сумму.\nПеревод должен быть совершён с киви кошелька.\nОбязательно в рублях.\n\nПри нажатии оплатить в браузере, Вам останется ввести лишь сумму платежа.</a>".format(config.qiwi_number, comment), parse_mode='HTML', reply_markup=keyboard)
				api.start()
				while True:
					if api.check(comment):
						balance = api.balance[0]
						db.add_qiwi_now(balance)
						later = db.return_qiwi_later()
						now = db.return_qiwi_now()
						money_1_1 = str(later).replace("(", "")
						money_1 = money_1_1.replace(",)", "")
						money_2_1 = str(now).replace("(", "")
						money_2 = money_2_1.replace(",)", "")
						money = float(money_2) - float(money_1)
						balance_1 = db.show_user_balance(call.message.chat.id)
						take_money_1 = db.show_user_take_money(call.message.chat.id)

						balance_1_1 = str(balance_1).replace("(", "")
						balance_1_2 = str(balance_1_1).replace(",)", "")

						take_money_1_1 = str(take_money_1).replace("(", "")
						take_money_1_2 = str(take_money_1_1).replace(",)", "")

						balance = int(balance_1_2) + money
						take_money = int(take_money_1_2) + money
						db.add_take_money(take_money, call.message.chat.id)
						db.add_balance(balance, call.message.chat.id)
						logging.info("Пользователь пополнил баланс с помощью Qiwi! ID: "+str(message.chat.id))
						bot.send_message(call.message.chat.id, "🎉 Вы успешно пополнили баланс!")
						bot.send_message(config.admin_id, "<a><b>🎉 Пополнение!\n\nПользователь:</b> {}\n\n<b>Сумма:</b> {} ₽</a>".format(call.message.chat.id, money), parse_mode='HTML')
						break
					sleep(1)
				api.stop()
			elif call.data == '🇷🇺Русский':
				if call.message.chat.id == config.admin_id:
					bot.send_message(call.message.chat.id, "Язык изменен на русский!", reply_markup=menu.start_admin)
					db.update_user_lang("Russian", config.admin_id)
				else:
					bot.send_message(call.message.chat.id, "Язык изменен на русский!", reply_markup=menu.start)
					db.update_user_lang("Russian", call.message.chat.id)
			elif call.data == '🇬🇧English':
				if call.message.chat.id == config.admin_id:
					bot.send_message(call.message.chat.id, "The language has been changed to English!", reply_markup=menu.start_admin_eng)
					db.update_user_lang("English", config.admin_id)
				else:
					bot.send_message(call.message.chat.id, "The language has been changed to English!", reply_markup=menu.start_eng)
					db.update_user_lang("English", call.message.chat.id)
			elif call.data == 'take_balance_bitcoin':
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text="Проверить оплату", callback_data="Проверить оплату 2")
				but_2 = types.InlineKeyboardButton(text="⬅️ Закрыть", callback_data="⬅️ Закрыть")
				keyboard.row(but_1)
				keyboard.row(but_2)
				price = client.get_last_price(pair=NOTIFY_PAIR)
				text = "{} = {}".format(NOTIFY_PAIR, price)
				usd = text.replace("USD-BTC = ", "")
				bot.send_message(call.message.chat.id, """<a>Информация об оплате\n\n🔄 Курс конвертации: <pre>{} $</pre>\n\n📝 BTC адрес: <pre>{}</pre>\n➖➖➖➖➖➖➖➖➖➖\n\nПереведите на указанный адрес любую сумму. После 1 подтверждения транзакции обязательно нажмите "Проверить оплату"!</a>""".format(usd, address), parse_mode='HTML', reply_markup=keyboard)
			elif call.data == 'Проверить оплату 2':
				try:
					API_link = "https://api.blockcypher.com/v1/btc/main/addrs/" + address
					updates = requests.get(API_link + "/full?limit=50").json()
					text = updates["total_received"]
					if text > 0:
						balance_1 = db.show_user_balance(call.message.chat.id)
						balance = balance[0] + text
						take_money = take_money_1[0] + text
						db.add_take_money(take_money, call.message.chat.id)
						db.add_balance(balance, call.message.chat.id)
						logging.info("Пользователь пополнил баланс с помощью Bitcoin! ID: "+str(message.chat.id))
						bot.send_message(call.message.chat.id, "🎉 Вы успешно пополнили баланс!")
						bot.send_message(config.admin_id, "🎉 Пополнение!\n\nПользователь {}, пополнил баланс в магазине на сумму: {}".format(call.message.chat.id, text))
				except:
					logging.info("Ошибка при пополнении с помощью Bitcoin!"+str(message.chat.id))
			elif call.data == 'Проверить оплату 1':
				api.check(comment)
			elif call.data == 'Назад 1':
				name = db.show_user_name(call.message.chat.id)
				register = db.show_user_register(call.message.chat.id)
				purchase = db.show_user_purchase(call.message.chat.id)
				balance = db.show_user_balance(call.message.chat.id)
				take_money = db.show_user_take_money(call.message.chat.id)
				if name[0] == None:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Имя:</b> отсутствует\n<b>👨‍💻 Мой ID:</b> {}\n<b>💰 Мой баланс:</b> {} ₽\n<b>🛒 Покупок:</b> {}\n<b>💸 Сумма пополнений:</b> {} ₽\n<b>📝 Зарегистрирован:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user)
				else:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Имя:</b> {}\n<b>👨‍💻 Мой ID:</b> {}\n<b>💰 Мой баланс:</b> {} ₽\n<b>🛒 Покупок:</b> {}\n<b>💸 Сумма пополнений:</b> {} ₽\n<b>📝 Зарегистрирован:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(name[0], call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user)

#TODO:

	else:
		api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
		try:
			balance = api.balance[0]
			db.add_qiwi_later(balance)
		except:
			print(traceback.format_exc())
		client_2 = Client(api_key, api_secret, api_version='2021-01-16')
		message = []
		primary_account = client_2.get_primary_account()
		try:
			address = primary_account.create_address()
		except:
			print("Error!")
		address = str(address['deposit_uri']).replace('bitcoin:', '')
		price = 1
		comment = api.bill(price)
		client = BittrexClient()
		text_1 = db.return_katalog()
		text_2 = db.return_position_3()
		text_3 = db.return_position_price()

		for x in text_1:
			if call.data in x:
				aaa = db.return_position_5(call.data)
				lol = str(aaa[0]).replace("(", "")
				kek = lol.replace(",)", "")
				if kek == "1":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					keyboard.row(but_1)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "2":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					keyboard.row(but_1)
					keyboard.row(but_2)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "3":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "4":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "5":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "6":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "7":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "8":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "9":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					text_1_9 = db.return_position_4(call.data)
					test_9 = str(text_1_9[8])
					text_2_9 = test_9.replace("('", "")
					text_3_9 = text_2_9.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)
					keyboard.row(but_9)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek == "10":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					text_1_9 = db.return_position_4(call.data)
					test_9 = str(text_1_9[8])
					text_2_9 = test_9.replace("('", "")
					text_3_9 = text_2_9.replace("',)", "")

					text_1_10 = db.return_position_4(call.data)
					test_10 = str(text_1_10[9])
					text_2_10 = test_10.replace("('", "")
					text_3_10 = text_2_10.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
					but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)
					keyboard.row(but_9)
					keyboard.row(but_10)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)
				elif kek > "10":
					text_1 = db.return_position_4(call.data)
					test = str(text_1[0])
					text_2 = test.replace("('", "")
					text_3 = text_2.replace("',)", "")

					text_1_2 = db.return_position_4(call.data)
					test_2 = str(text_1_2[1])
					text_2_2 = test_2.replace("('", "")
					text_3_2 = text_2_2.replace("',)", "")

					text_1_3 = db.return_position_4(call.data)
					test_3 = str(text_1_3[2])
					text_2_3 = test_3.replace("('", "")
					text_3_3 = text_2_3.replace("',)", "")

					text_1_4 = db.return_position_4(call.data)
					test_4 = str(text_1_4[3])
					text_2_4 = test_4.replace("('", "")
					text_3_4 = text_2_4.replace("',)", "")

					text_1_5 = db.return_position_4(call.data)
					test_5 = str(text_1_5[4])
					text_2_5 = test_5.replace("('", "")
					text_3_5 = text_2_5.replace("',)", "")

					text_1_6 = db.return_position_4(call.data)
					test_6 = str(text_1_6[5])
					text_2_6 = test_6.replace("('", "")
					text_3_6 = text_2_6.replace("',)", "")

					text_1_7 = db.return_position_4(call.data)
					test_7 = str(text_1_7[6])
					text_2_7 = test_7.replace("('", "")
					text_3_7 = text_2_7.replace("',)", "")

					text_1_8 = db.return_position_4(call.data)
					test_8 = str(text_1_8[7])
					text_2_8 = test_8.replace("('", "")
					text_3_8 = text_2_8.replace("',)", "")

					text_1_9 = db.return_position_4(call.data)
					test_9 = str(text_1_9[8])
					text_2_9 = test_9.replace("('", "")
					text_3_9 = text_2_9.replace("',)", "")

					text_1_10 = db.return_position_4(call.data)
					test_10 = str(text_1_10[9])
					text_2_10 = test_10.replace("('", "")
					text_3_10 = text_2_10.replace("',)", "")

					keyboard = types.InlineKeyboardMarkup()
					but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
					but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
					but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
					but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
					but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
					but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
					but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
					but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
					but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
					but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
					keyboard.row(but_1)
					keyboard.row(but_2)
					keyboard.row(but_3)
					keyboard.row(but_4)
					keyboard.row(but_5)
					keyboard.row(but_6)
					keyboard.row(but_7)
					keyboard.row(but_8)
					keyboard.row(but_9)
					keyboard.row(but_10)

					defcon = db.defcon(call.data)
					defcon_2 = str(defcon).replace("('", "")
					defcon_3 = defcon_2.replace("',)", "")

					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=defcon_3)
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)

		for y in text_2:
			if call.data in y:
				name = call.data
				description = db.return_tovar_description(call.data)
				test = str(description[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				lot = db.return_tovar_lot(call.data)
				test_2 = str(lot[0])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				price = db.return_tovar_price(call.data)
				test_3 = str(price[0])
				text_2_3 = test_3.replace("('", "")
				joker = text_2_3.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text="✅ Buy", callback_data=joker)
				keyboard.row(but_1)

				bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>🔥<b>{}</b>\n\n{}\n\n<b>Product quantity:</b> {} шт.\n<b>Price:</b> {} ₽</a>".format(name, text_3, text_3_2, joker), parse_mode="HTML")
				bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)

		for z in text_3:
			try:
				test = int(call.data)
				if test in z:
					text = db.return_lot(test)
					q = str(text).replace("(", "")
					we = q.replace(",)", "")
					if int(we) >= 0:
						balance = db.show_user_balance(call.message.chat.id)
						q = str(balance).replace("(", "")
						w = q.replace(",)", "")
						pr = int(w)
						prs = int(test)
						if pr >= prs:
							t_1 =  db.return_position_item(prs)
							text_2_2 = str(t_1).replace("('", "")
							text_3_2 = text_2_2.replace("',)", "")

							t_2 = db.return_item(text_3_2)
							text_2_3 = str(t_2).replace("('", "")
							url = text_2_3.replace("',)", "")
							pv = db.return_payment()
							pv_2 = str(pv).replace("('", "")
							pv_3 = pv_2.replace("',)", "")

							bot.send_message(call.message.chat.id, '{}\n\nYour purchase - {}'.format(pv_3, url))

							a_b = 1
							m = int(we)
							lot = m - a_b

							b_1 = db.show_user_balance(call.message.chat.id)
							b_1_1 = str(b_1).replace("(", "")
							b_1_2 = b_1_1.replace(",)", "")

							z = int(b_1_2)
							balance = z - test

							p_1 = db.return_purchase(call.message.chat.id)
							p_1_1 = str(p_1).replace("(", "")
							p_1_2 = p_1_1.replace(",)", "")

							v = int(p_1_2)
							purchase = v + a_b
							date = today.strftime("%Y-%m-%d")

							c_1 = db.return_cash_1()
							c_1_1 = str(c_1).replace("(", "")
							c_1_2 = c_1_1.replace(",)", "")

							j = int(c_1_2)
							cash = j + test

							db.edit_lot(lot, test)
							db.add_balance(balance, call.message.chat.id)
							db.add_purchase(purchase, call.message.chat.id)

							db.add_sale(call.message.chat.id, test, date)
							db.edit_cash(cash)

							file = open(r"yers.txt", "w")
							t = str(call.message.chat.id)
							file.write(t + '\n')

							bot.send_message(config.admin_id, "<a><b>🎉 У вас новый покупатель!\n\nПользователь:</b> {}\n<b>Сумма покупки:</b> {} ₽\n<b>Дата:</b> {}</a>".format(call.message.chat.id, test, date), parse_mode='HTML')

							l = db.return_buyers_2()
							for x in l:
								if call.message.chat.id not in x:
									db.add_buyer(call.message.chat.id, call.message.from_user.first_name, call.message.from_user.last_name)
								else:
									print(traceback.format_exc())
						else:
							bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="❗️Insufficient funds")
					else:
						bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Unfortunately, this product is out of stock")
			except:
				print(traceback.format_exc())

		if call.message:
			if call.data == '⬅️ Close':
				bot.delete_message(call.message.chat.id, call.message.message_id)
			elif call.data == 'Top up your balance':
				bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.payment_balance_eng)
			elif call.data == 'take_balance_qiwi':

				name = db.show_user_name(call.message.chat.id)
				register = db.show_user_register(call.message.chat.id)
				purchase = db.show_user_purchase(call.message.chat.id)
				balance = db.show_user_balance(call.message.chat.id)
				take_money = db.show_user_take_money(call.message.chat.id)

				if name[0] == None:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Name:</b> отсутствует\n<b>👨‍💻 My ID:</b> {}\n<b>💰 My balance:</b> {} ₽\n<b>🛒 Purchases:</b> {}\n<b>💸 Amount of deposits:</b> {} ₽\n<b>📝 Registered:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user_eng)
				else:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Name:</b> {}\n<b>👨‍💻 My ID:</b> {}\n<b>💰 My balance:</b> {} ₽\n<b>🛒 Purchases:</b> {}\n<b>💸 Amount of deposits:</b> {} ₽\n<b>📝 Registered:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(name[0], call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user_eng)

				url = "https://qiwi.com/payment/form/99?extra%5B%27account%27%5D=" + config.qiwi_number + "&amountInteger=None&amountFraction=0&extra%5B%27comment%27%5D=" + comment + "&currency=643&blocked[0]=account&blocked[2]=comment"
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text="Check payment", callback_data="Check payment 1")
				but_2 = types.InlineKeyboardButton(text="Pay in the browser", url=url)
				but_3 = types.InlineKeyboardButton(text="⬅️ Close", callback_data="⬅️ Close")
				keyboard.add(but_1, but_2)
				keyboard.row(but_3)
				bot.send_message(call.message.chat.id, "<a>Payment information\n\n🥝 QIWI-wallet: <pre>{}</pre>\n\n📝 Comment on the translation: <pre>{}</pre>\n➖➖➖➖➖➖➖➖➖➖\n\nTop up the specified qiwi wallet with any amount.\nThe transfer must be made from a qiwi wallet.\nAlways in rubles.\n\nWhen you click pay in the browser, you will only need to enter the payment amount.</a>".format(config.qiwi_number, comment), parse_mode='HTML', reply_markup=keyboard)
				api.start()
				while True:
					if api.check(comment):
						balance = api.balance[0]
						db.add_qiwi_now(balance)
						later = db.return_qiwi_later()
						now = db.return_qiwi_now()
						money_1_1 = str(later).replace("(", "")
						money_1 = money_1_1.replace(",)", "")
						money_2_1 = str(now).replace("(", "")
						money_2 = money_2_1.replace(",)", "")
						money = float(money_2) - float(money_1)
						balance_1 = db.show_user_balance(call.message.chat.id)
						take_money_1 = db.show_user_take_money(call.message.chat.id)

						balance_1_1 = str(balance_1).replace("(", "")
						balance_1_2 = str(balance_1_1).replace(",)", "")

						take_money_1_1 = str(take_money_1).replace("(", "")
						take_money_1_2 = str(take_money_1_1).replace(",)", "")

						balance = int(balance_1_2) + money
						take_money = int(take_money_1_2) + money
						db.add_take_money(take_money, call.message.chat.id)
						db.add_balance(balance, call.message.chat.id)
						logging.info("Пользователь пополнил баланс с помощью Qiwi! ID: "+str(message.chat.id))
						bot.send_message(call.message.chat.id, "🎉 You have successfully replenished your balance!")
						bot.send_message(config.admin_id, "<a><b>🎉 Пополнение!\n\nПользователь:</b> {}\n\n<b>Сумма:</b> {} ₽</a>".format(call.message.chat.id, money), parse_mode='HTML')
						break
					sleep(1)
				api.stop()
			elif call.data == '🇷🇺Русский':
				if call.message.chat.id == config.admin_id:
					bot.send_message(call.message.chat.id, "Язык изменен на русский!", reply_markup=menu.start_admin)
					db.update_user_lang("Russian", config.admin_id)
				else:
					bot.send_message(call.message.chat.id, "Язык изменен на русский!", reply_markup=menu.start)
					db.update_user_lang("Russian", call.message.chat.id)
			elif call.data == '🇬🇧English':
				if call.message.chat.id == config.admin_id:
					bot.send_message(call.message.chat.id, "The language has been changed to English!", reply_markup=menu.start_admin_eng)
					db.update_user_lang("English", config.admin_id)
				else:
					bot.send_message(call.message.chat.id, "The language has been changed to English!", reply_markup=menu.start_eng)
					db.update_user_lang("English", message.chat.id)
			elif call.data == 'take_balance_bitcoin':
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text="Check payment", callback_data="Check payment 2")
				but_2 = types.InlineKeyboardButton(text="⬅️ Close", callback_data="⬅️ Close")
				keyboard.row(but_1)
				keyboard.row(but_2)
				price = client.get_last_price(pair=NOTIFY_PAIR)
				text = "{} = {}".format(NOTIFY_PAIR, price)
				usd = text.replace("USD-BTC = ", "") #kiwi
				bot.send_message(call.message.chat.id, """<a>Payment information\n\n🔄 Conversion rate: <pre>{} $</pre>\n\n📝 BTC address: <pre>{}</pre>\n➖➖➖➖➖➖➖➖➖➖\n\nTransfer any amount to the specified address. After 1 confirmation of the transaction, be sure to click "Check payment"!</a>""".format(usd, address), parse_mode='HTML', reply_markup=keyboard)
			elif call.data == 'Check payment 2':
				try:
					API_link = "https://api.blockcypher.com/v1/btc/main/addrs/" + address
					updates = requests.get(API_link + "/full?limit=50").json()
					text = updates["total_received"]
					if text > 0:
						balance_1 = db.show_user_balance(call.message.chat.id)
						balance = balance[0] + text
						take_money = take_money_1[0] + text
						db.add_take_money(take_money, call.message.chat.id)
						db.add_balance(balance, call.message.chat.id)
						logging.info("Пользователь пополнил баланс с помощью Bitcoin! ID: "+str(message.chat.id))
						bot.send_message(call.message.chat.id, "🎉 You have successfully replenished your balance!")
						bot.send_message(config.admin_id, "🎉 Пополнение!\n\nПользователь {}, пополнил баланс в магазине на сумму: {}".format(call.message.chat.id, text))
				except:
					logging.info("Ошибка при пополнении с помощью Bitcoin!"+str(message.chat.id))
			elif call.data == 'Check payment 1':
				api.check(comment)
			elif call.data == 'Close 1':
				name = db.show_user_name(call.message.chat.id)
				register = db.show_user_register(call.message.chat.id)
				purchase = db.show_user_purchase(call.message.chat.id)
				balance = db.show_user_balance(call.message.chat.id)
				take_money = db.show_user_take_money(call.message.chat.id)
				if name[0] == None:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Name:</b> отсутствует\n<b>👨‍💻 My ID:</b> {}\n<b>💰 My balance:</b> {} ₽\n<b>🛒 Purchases:</b> {}\n<b>💸 Amount of deposits:</b> {} ₽\n<b>📝 Registered:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user_eng)
				else:
					bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Name:</b> {}\n<b>👨‍💻 My ID:</b> {}\n<b>💰 My balance:</b> {} ₽\n<b>🛒 Purchases:</b> {}\n<b>💸 Amount of deposits:</b> {} ₽\n<b>📝 Registered:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(name[0], call.message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML')
					bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=menu.info_user_eng)



@bot.message_handler(content_types=["text"])
def send_message(message):
	language = db.return_user_lang(message.chat.id)
	if str(language) == "('Russian',)":
		api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
		try:
			balance = api.balance[0]
			db.add_qiwi_later(balance)
		except:
			print(traceback.format_exc())
		file_1 = open("coinbase_api_key.txt", "r")
		file_2 = open("coinbase_api_secret.txt", "r")
		api_key = file_1.read()
		api_secret = file_2.read()
		client = Client(api_key, api_secret)
		buyers_file = open("yers.txt", "r")
		buyers = set()
		for line in buyers_file:
			buyers.add(line.strip())
		buyers_file.close()
		if message.text == 'Админ панель':
			if message.chat.id == config.admin_id:
				logging.info("Администратор вошел в админ-панель.")
				#file_1 = open("bot.log", "r")
				#read = file_1.read()
				#bot.send_message(config.admin_id, read, reply_markup=menu.admin)
				bot.send_message(config.admin_id, "Вы вошли в Админ панель!", reply_markup=menu.admin)
		elif message.text == 'Настройка ответов бота':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Что вы хотите изменить?', reply_markup=menu.new_answer)
		elif message.text == 'Каталог товаров':
			db.init_db()
			text = db.return_katalog_2()
			if text[0] == 0:
				print("Error!")
			elif text[0] == 1:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				keyboard.row(but_1)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 2:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				keyboard.row(but_1)
				keyboard.row(but_2)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 3:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 4:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 5:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 6:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 7:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 8:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 9:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				text_1_9 = db.name_kat()
				test_9 = str(text_1_9[8])
				text_2_9 = test_9.replace("('", "")
				text_3_9 = text_2_9.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				keyboard.row(but_9)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			elif text[0] == 10:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				text_1_9 = db.name_kat()
				test_9 = str(text_1_9[8])
				text_2_9 = test_9.replace("('", "")
				text_3_9 = text_2_9.replace("',)", "")

				text_1_10 = db.name_kat()
				test_10 = str(text_1_10[9])
				text_2_10 = test_10.replace("('", "")
				text_3_10 = text_2_10.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
				but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				keyboard.row(but_9)
				keyboard.row(but_10)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
			else:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				text_1_9 = db.name_kat()
				test_9 = str(text_1_9[8])
				text_2_9 = test_9.replace("('", "")
				text_3_9 = text_2_9.replace("',)", "")

				text_1_10 = db.name_kat()
				test_10 = str(text_1_10[9])
				text_2_10 = test_10.replace("('", "")
				text_3_10 = text_2_10.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
				but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				keyboard.row(but_9)
				keyboard.row(but_10)
				bot.send_message(message.chat.id, 'Каталог товаров:', reply_markup=keyboard)
		elif message.text == 'Информация':
			text = db.return_information()
			bot.send_message(message.chat.id, text, reply_markup=menu.close)
		elif message.text == 'Личный кабинет':
			name = db.show_user_name(message.chat.id)
			register = db.show_user_register(message.chat.id)
			purchase = db.show_user_purchase(message.chat.id)
			balance = db.show_user_balance(message.chat.id)
			take_money = db.show_user_take_money(message.chat.id)
			if name[0] == None:
				bot.send_message(message.chat.id, "<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Имя:</b> отсутствует\n<b>👨‍💻 Мой ID:</b> {}\n<b>💰 Мой баланс:</b> {} ₽\n<b>🛒 Покупок:</b> {}\n<b>💸 Сумма пополнений:</b> {} ₽\n<b>📝 Зарегистрирован:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML', reply_markup=menu.info_user)
			else:
				bot.send_message(message.chat.id, "<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Имя:</b> {}\n<b>👨‍💻 Мой ID:</b> {}\n<b>💰 Мой баланс:</b> {} ₽\n<b>🛒 Покупок:</b> {}\n<b>💸 Сумма пополнений:</b> {} ₽\n<b>📝 Зарегистрирован:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(name[0], message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML', reply_markup=menu.info_user)
		elif message.text == '🌐 Баланс CoinBase':
			if message.chat.id == config.admin_id:
				try:
					message = []
					accounts = client.get_accounts()
					for wallet in accounts.data:
						message.append(str(wallet['name']) + ' ' + str(wallet['native_balance']))
						value = str(wallet['native_balance']).replace('USD', '')
					message.append('Total Balance: ' + 'USD ' + str(value))
					text = '\n'.join(message)
					bot.send_message(config.admin_id, text, reply_markup=menu.close)
				except:
					bot.send_message(config.admin_id, "❌ Ошибка! Неверный ключ API.")
		elif message.text == 'Связаться':
			text = db.return_contact()
			bot.send_message(message.chat.id, text, reply_markup=menu.close)
		elif message.text == '🗂 Архив':
			if message.chat.id == config.admin_id:
				text_1 = '🧨 Данные платежных систем🧨'
				file_1 = open("info\edit_qiwi_money_number.txt", "r")
				file_2 = open("info\edit_qiwi_money_token.txt", "r")
				file_3 = open("info\coinbase_api_key.txt", "r")
				file_4 = open("info\coinbase_api_secret.txt", "r")
				text_2 = file_1.read()
				text_3 = file_2.read()
				text_4 = file_3.read()
				text_5 = file_4.read()
				logging.info("Администратор запросил данные платежных систем. ID: "+str(message.chat.id))
				bot.send_message(config.admin_id, '<a><b>{}\n\n🥝 QIWI:\nНомер:</b> {}\n<b>Токен:</b> {}\n\n<b>💰BITCOIN:\nКлюч API:</b> {}\n<b>Секретный ключ API:</b> {}</a>'.format(text_1, text_2, text_3, text_4, text_5), parse_mode='HTML', reply_markup=menu.close)
		elif message.text == 'Изменить приветствие пользователя':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить приветствие пользователя.")
				msg = bot.send_message(config.admin_id, "Отправьте мне сообщение, которое будет присылаться пользователю на команду start.", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, hello_edit)
		elif message.text == 'Добавить ответ на кнопку информация':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить ответ на кнопку информация.")
				msg = bot.send_message(config.admin_id, "Отправьте мне сообщение, которое будет присылаться пользователю.", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, information_edit)
		elif message.text == 'Изменить каталог товаров':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить каталог товаров.")
				msg = bot.send_message(config.admin_id, "Выберите действие.", reply_markup=menu.katalog_1)
		elif message.text == 'Добавить товар в каталог':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить товар в каталог.")
				msg = bot.send_message(config.admin_id, "Введите название:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, assort_1_add)
		elif message.text == 'Удалить товар из каталога':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка удалить товар из каталога.")
				text = db.return_katalog()
				msg = bot.send_message(config.admin_id, "Что из этого вы хотите удалить? Для удаления введите название нужной записи.\n\n{}".format(text), reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, assort_1_delete)
		elif message.text == 'Добавить ответ на кнопку связаться':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить ответ на кнопку связаться.")
				msg = bot.send_message(config.admin_id, 'Отправьте мне сообщение, которое будет присылаться пользователю.', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, contact_edit)
		elif message.text == 'Добавить текст после оплаты':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить текст после оплаты.")
				msg = bot.send_message(config.admin_id, 'Отправьте мне сообщение, которое будет присылаться пользователю после оплаты.', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, payment_edit)
		elif message.text == 'Очистить логи':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка очистки логов.")
				bot.send_message(config.admin_id, 'Вы уверены? Все данные будут удалены.', reply_markup=menu.yes_or_no)
		elif message.text == 'Да. Я уверен':
			if message.chat.id == config.admin_id:
				with open('bot.log', 'wb'):
					pass
				logging.info("Логи успешно очищены.")
				bot.send_message(config.admin_id, '✅ Логи успешно очищены!', reply_markup=menu.logi)
		elif message.text == 'Нет. Я передумал':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Вы вернулись назад.', reply_markup=menu.logi)
		elif message.text == '🌐 Ваш баланс':
			if message.chat.id == config.admin_id:
				try:
					logging.info("Администратор запросил баланс Qiwi.")
					api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
					balance = api.balance[0]
					number = config.qiwi_number
					bot.send_message(config.admin_id, "Номер: {}\n\nБаланс: {} руб".format(number, balance), reply_markup=menu.close)
				except:
					bot.send_message(config.admin_id, "❌ Ошибка! Неверный номер или токен Qiwi кошелька.")
		elif message.text == 'Настройка ассортимента':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Здесь вы можете полностью Ваш ассортимент. Чтобы воспользоваться данной функцией выберите нужное действие ниже.', reply_markup=menu.assortment)
		elif message.text == 'Пользователи':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Этот раздел может помочь Вам с настройкой и редактированием пользователей.', reply_markup=menu.users)
		elif message.text == 'Логи':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Что вас интересует? Как хотите получить логи?', reply_markup=menu.logi)
		elif message.text == 'Отправить файлом':
			if message.chat.id == config.admin_id:
					with open("bot.log","rb") as file:
						file_read = file.read()
					bot.send_document(config.admin_id, file_read, "bot.log")
		elif message.text == 'Отправить сообщением':
			if message.chat.id == config.admin_id:
				try:
					text = open("bot.log", 'r')
					text2 = text.read()
					bot.send_message(config.admin_id, '💾 ЛОГИ 💾\n{}'.format(text2), reply_markup=menu.logi)
				except:
					bot.send_message(config.admin_id, "❗️Нельзя отправить сообщением. Файл слишком большой.", reply_markup=menu.logi)
		elif message.text == 'Список пользователей':
			if message.chat.id == config.admin_id:
				logging.info("Был запрошен список пользователей.")
				text = db.return_users_2()
				bot.send_message(config.admin_id, '👤 Подробная информация о пользователях:\n\n{}'.format(text))
		elif message.text == 'Изменить баланс':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить баланс пользователя.")
				msg = bot.send_message(config.admin_id, 'Внимание❗️ Изменение баланса может привести к возможным проблемам в работе бота, а также неправильном отображении статистики. Вы хотите продолжить?', reply_markup=menu.yes)
				bot.register_next_step_handler(msg, yes_2)
		elif message.text == 'Изменить кол-во покупок':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить кол-во покупок.")
				msg = bot.send_message(config.admin_id, 'Внимание❗️ Изменение кол-во покупок может привести к возможным проблемам в работе бота, а также неправильном отображении статистики. Вы хотите продолжить?', reply_markup=menu.yes)
				bot.register_next_step_handler(msg, yes_3)
		elif message.text == '🥝 Qiwi':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Настройка кошелька', reply_markup=menu.money_qiwi)
		elif message.text == '💳 Получить QIWI':
			if message.chat.id == config.admin_id:
				text = '💳 Ваш номер Киви кошелька:'
				bot.send_message(config.admin_id, '{}\n\n{}'.format(text, config.qiwi_number), reply_markup=menu.close)
		elif message.text == '💳 Получить BTC':
			if message.chat.id == config.admin_id:
				try:
					logging.info("Была создана ссылка для получения BTC.")
					client = Client(api_key, api_secret, api_version='2021-01-16')
					message = []
					primary_account = client.get_primary_account()
					address = primary_account.create_address()
					text = str(address['deposit_uri']).replace('bitcoin:', '')
					bot.send_message(config.admin_id, '<a>🧨Адрес для получения:\n\n<pre>{}</pre></a>'.format(text), parse_mode='HTML', reply_markup=menu.close)
				except:
					bot.send_message(config.admin_id, "❌ Ошибка! Неверный ключ API.")
		elif message.text == '📤 Отправить QIWI':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка отправить деньги на Qiwi.")
				msg = bot.send_message(config.admin_id, "Введите номер, на который будут отправлены средства:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_money_1)
		elif message.text == '📤 Отправить BTC':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка отправить Bitcoin.")
				msg = bot.send_message(config.admin_id, 'Введите адрес Bitcoin кошелька, на который будут отправлены средства:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_bitcoin)
		elif message.text == 'Добавить/Изменить данные':
			if message.chat.id == config.admin_id:
				msg = bot.send_message(config.admin_id, "Введите номер кошелька:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, lol)
		elif message.text == 'Выгрузить все позиции':
			if message.chat.id == config.admin_id:
				logging.info("Администратор сделал запрос на выгрузку позиций.")
				text = db.return_position_2()
				bot.send_message(config.admin_id, "💻 Информация о позициях магазина:\n\n{}".format(text), reply_markup=menu.close)
		elif message.text == 'Выгрузить все товары позиции':
			if message.chat.id == config.admin_id:
				logging.info("Администратор сделал запрос на выгрузку товаров.")
				text = db.return_product_3()
				bot.send_message(config.admin_id, "📲 Информация о товарах:\n\n{}".format(text), reply_markup=menu.close)
		elif message.text == 'Добавить позицию':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить позицию.")
				text = db.return_katalog()
				msg = bot.send_message(config.admin_id, "Выберите из списка нужную категорию:\n\n{}\n\nНеобходимо ввести текст.".format(text), reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, pos_1)
		elif message.text == 'Удалить позицию':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка удалить позицию.")
				text = db.return_position_3()
				msg = bot.send_message(config.admin_id, "Выберите позицию, которую вы хотите удалить:\n\n{}\n\nНеобходимо ввести текст.".format(text), reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, delete_position_1)
		elif message.text == 'Изменить описание позиции':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить описание позиции.")
				text = db.return_position_3()
				msg = bot.send_message(config.admin_id, "Выберите позицию, описание которой вы хотите изменить:\n\n{}\n\nНеобходимо ввести текст.".format(text), reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, edit_position_1)
		elif message.text == 'Изменить цену позиции':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить цену позиции.")
				text = db.return_position_3()
				msg = bot.send_message(config.admin_id, "Выберите позицию, цену которой вы изменить:\n\n{}\n\nНеобходимо ввести текст.".format(text), reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, change_position_1)
		elif message.text == 'Загрузка нового товара':
			if message.chat.id == config.admin_id:
				msg = bot.send_message(config.admin_id, "Введите название товара:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, new_item_1)
		elif message.text == 'Добавить/изменить данные':
			if message.chat.id == config.admin_id:
				msg = bot.send_message(config.admin_id, "Введите ключ API:", reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, yes)
		elif message.text == '💰Bitcoin':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Настройка кошелька', reply_markup=menu.money_btc)
		elif message.text == 'Выгрузка данных':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Какие данные вас интересуют?', reply_markup=menu.assortment_data)
		elif message.text == 'Настройка платёжек':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Настройка платежных систем.', reply_markup=menu.money)
		elif message.text == 'Статистика':
			if message.chat.id == config.admin_id:
				logging.info("Был запрос на получение статистики.")
				users = db.return_users()
				buyers = db.return_buyers()
				position = db.return_position()
				product = db.return_product_4()
				sales = db.return_sales()
				cash = db.return_cash_100()
				bot.send_message(config.admin_id, '<a>📈 Статистика\n\n👨‍💻Кол-во пользователей: <b>{}</b>\n💰Заработано: <b>{}</b> ₽\n✅ Количество продаж: <b>{}</b>\n📦 Количество товаров: <b>{}</b>\n📤 Количество позиций: <b>{}</b>\n🧨Покупатели: <b>{}</b></a>'.format(users[0], cash[0], sales[0], product[0], position[0], buyers[0]), parse_mode='HTML', reply_markup=menu.close)
		elif message.text == 'Рассылка':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, "Кто получит рассылку?", reply_markup=menu.send_users)
		elif message.text == 'Все пользователи':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка сделать рассылку всем пользователям.")
				msg = bot.send_message(config.admin_id, 'Введите текст:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_users)
		elif message.text == 'Покупатели':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка сделать рассылку покупателям.")
				msg = bot.send_message(config.admin_id, 'Введите текст:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_buyers)
		elif message.text == 'Ничего не купившие':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка сделать рассылку пользователям, которые еще не совершали покупки в магазине.")
				msg = bot.send_message(config.admin_id, 'Введите текст:', reply_markup=menu.otmena)
				bot.register_next_step_handler(msg, send_not_buyers)
		elif message.text == 'Назад':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, "Вы вернулись назад", reply_markup=menu.start_admin)
		elif message.text == 'Вернуться':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, "Вы вернулись назад", reply_markup=menu.admin)
		else:
			bot.send_message(message.chat.id, "Ничего не понятно!")


#TODO:


	else:
		api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
		try:
			balance = api.balance[0]
			db.add_qiwi_later(balance)
		except:
			print(traceback.format_exc())
		file_1 = open("coinbase_api_key.txt", "r")
		file_2 = open("coinbase_api_secret.txt", "r")
		api_key = file_1.read()
		api_secret = file_2.read()
		client = Client(api_key, api_secret)
		buyers_file = open("yers.txt", "r")
		buyers = set()
		for line in buyers_file:
			buyers.add(line.strip())
		buyers_file.close()
		if message.text == 'Admin panel':
			if message.chat.id == config.admin_id:
				logging.info("Администратор вошел в админ-панель.")
				bot.send_message(config.admin_id, "You are logged in to the Admin panel!", reply_markup=menu.admin_eng)
		elif message.text == 'Configuring bot responses':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'What do you want to change?', reply_markup=menu.new_answer_eng)
		elif message.text == 'Clear logs':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка очистки логов.")
				bot.send_message(config.admin_id, 'Are you sure? All data will be deleted.', reply_markup=menu.yes_or_no_eng)
		elif message.text == "No. I'm not sure.":
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'You went back.', reply_markup=menu.logi_eng)
		elif message.text == "Yes. I'm sure.":
			if message.chat.id == config.admin_id:
				with open('bot.log', 'wb'):
					pass
				logging.info("Логи успешно очищены.")
				bot.send_message(config.admin_id, '✅ Logs have been cleared successfully!', reply_markup=menu.logi_eng)
		elif message.text == 'Catalog':
			db.init_db()
			text = db.return_katalog_2()
			if text[0] == 0:
				print("Error!")
			elif text[0] == 1:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				keyboard.row(but_1)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 2:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")
				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				keyboard.row(but_1)
				keyboard.row(but_2)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 3:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 4:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 5:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 6:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 7:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 8:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 9:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				text_1_9 = db.name_kat()
				test_9 = str(text_1_9[8])
				text_2_9 = test_9.replace("('", "")
				text_3_9 = text_2_9.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				keyboard.row(but_9)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			elif text[0] == 10:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				text_1_9 = db.name_kat()
				test_9 = str(text_1_9[8])
				text_2_9 = test_9.replace("('", "")
				text_3_9 = text_2_9.replace("',)", "")

				text_1_10 = db.name_kat()
				test_10 = str(text_1_10[9])
				text_2_10 = test_10.replace("('", "")
				text_3_10 = text_2_10.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
				but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				keyboard.row(but_9)
				keyboard.row(but_10)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
			else:
				text_1 = db.name_kat()
				test = str(text_1[0])
				text_2 = test.replace("('", "")
				text_3 = text_2.replace("',)", "")

				text_1_2 = db.name_kat()
				test_2 = str(text_1_2[1])
				text_2_2 = test_2.replace("('", "")
				text_3_2 = text_2_2.replace("',)", "")

				text_1_3 = db.name_kat()
				test_3 = str(text_1_3[2])
				text_2_3 = test_3.replace("('", "")
				text_3_3 = text_2_3.replace("',)", "")

				text_1_4 = db.name_kat()
				test_4 = str(text_1_4[3])
				text_2_4 = test_4.replace("('", "")
				text_3_4 = text_2_4.replace("',)", "")

				text_1_5 = db.name_kat()
				test_5 = str(text_1_5[4])
				text_2_5 = test_5.replace("('", "")
				text_3_5 = text_2_5.replace("',)", "")

				text_1_6 = db.name_kat()
				test_6 = str(text_1_6[5])
				text_2_6 = test_6.replace("('", "")
				text_3_6 = text_2_6.replace("',)", "")

				text_1_7 = db.name_kat()
				test_7 = str(text_1_7[6])
				text_2_7 = test_7.replace("('", "")
				text_3_7 = text_2_7.replace("',)", "")

				text_1_8 = db.name_kat()
				test_8 = str(text_1_8[7])
				text_2_8 = test_8.replace("('", "")
				text_3_8 = text_2_8.replace("',)", "")

				text_1_9 = db.name_kat()
				test_9 = str(text_1_9[8])
				text_2_9 = test_9.replace("('", "")
				text_3_9 = text_2_9.replace("',)", "")

				text_1_10 = db.name_kat()
				test_10 = str(text_1_10[9])
				text_2_10 = test_10.replace("('", "")
				text_3_10 = text_2_10.replace("',)", "")

				keyboard = types.InlineKeyboardMarkup()
				but_1 = types.InlineKeyboardButton(text=text_3, callback_data=text_3)
				but_2 = types.InlineKeyboardButton(text=text_3_2, callback_data=text_3_2)
				but_3 = types.InlineKeyboardButton(text=text_3_3, callback_data=text_3_3)
				but_4 = types.InlineKeyboardButton(text=text_3_4, callback_data=text_3_4)
				but_5 = types.InlineKeyboardButton(text=text_3_5, callback_data=text_3_5)
				but_6 = types.InlineKeyboardButton(text=text_3_6, callback_data=text_3_6)
				but_7 = types.InlineKeyboardButton(text=text_3_7, callback_data=text_3_7)
				but_8 = types.InlineKeyboardButton(text=text_3_8, callback_data=text_3_8)
				but_9 = types.InlineKeyboardButton(text=text_3_9, callback_data=text_3_9)
				but_10 = types.InlineKeyboardButton(text=text_3_10, callback_data=text_3_10)
				keyboard.row(but_1)
				keyboard.row(but_2)
				keyboard.row(but_3)
				keyboard.row(but_4)
				keyboard.row(but_5)
				keyboard.row(but_6)
				keyboard.row(but_7)
				keyboard.row(but_8)
				keyboard.row(but_9)
				keyboard.row(but_10)
				bot.send_message(message.chat.id, 'Catalog:', reply_markup=keyboard)
		elif message.text == 'Information':
			text = db.return_information()
			bot.send_message(message.chat.id, text, reply_markup=menu.close_eng)
		elif message.text == 'Account':
			name = db.show_user_name(message.chat.id)
			register = db.show_user_register(message.chat.id)
			purchase = db.show_user_purchase(message.chat.id)
			balance = db.show_user_balance(message.chat.id)
			take_money = db.show_user_take_money(message.chat.id)
			if name[0] == None:
				bot.send_message(message.chat.id, "<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Name:</b> missing\n<b>👨‍💻 My ID:</b> {}\n<b>💰 My balance:</b> {} ₽\n<b>🛒 Purchases:</b> {}\n<b>💸 Amount of deposits:</b> {} ₽\n<b>📝 Registered:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML', reply_markup=menu.info_user_eng)
			else:
				bot.send_message(message.chat.id, "<a>➖➖➖➖➖➖➖➖➖➖\n<b>📲 Name:</b> {}\n<b>👨‍💻 My ID:</b> {}\n<b>💰 My balance:</b> {} ₽\n<b>🛒 Purchases:</b> {}\n<b>💸 Amount of deposits:</b> {} ₽\n<b>📝 Registered:</b> {}\n➖➖➖➖➖➖➖➖➖➖</a>".format(name[0], message.chat.id, balance[0], purchase[0], take_money[0], register[0]), parse_mode='HTML', reply_markup=menu.info_user_eng)
		elif message.text == '🌐 Balance CoinBase':
			if message.chat.id == config.admin_id:
				try:
					message = []
					accounts = client.get_accounts()
					for wallet in accounts.data:
						message.append(str(wallet['name']) + ' ' + str(wallet['native_balance']))
						value = str(wallet['native_balance']).replace('USD', '')
					message.append('Total Balance: ' + 'USD ' + str(value))
					text = '\n'.join(message)
					bot.send_message(config.admin_id, text, reply_markup=menu.close_eng)
				except:
					bot.send_message(config.admin_id, "❌ Error! Invalid API key.")
		elif message.text == 'Contacts':
			text = db.return_contact()
			bot.send_message(message.chat.id, text, reply_markup=menu.close_eng)
		elif message.text == '🗂 Archive':
			if message.chat.id == config.admin_id:
				text_1 = '🧨 Payment system data🧨'
				file_1 = open("info\edit_qiwi_money_number.txt", "r")
				file_2 = open("info\edit_qiwi_money_token.txt", "r")
				file_3 = open("info\coinbase_api_key.txt", "r")
				file_4 = open("info\coinbase_api_secret.txt", "r")
				text_2 = file_1.read()
				text_3 = file_2.read()
				text_4 = file_3.read()
				text_5 = file_4.read()
				logging.info("Администратор запросил данные платежных систем. ID: "+str(message.chat.id))
				bot.send_message(config.admin_id, '<a><b>{}\n\n🥝 QIWI:\nNumber:</b> {}\n<b>Token:</b> {}\n\n<b>💰BITCOIN:\nAPI key:</b> {}\n<b>API Secret key:</b> {}</a>'.format(text_1, text_2, text_3, text_4, text_5), parse_mode='HTML', reply_markup=menu.close_eng)
		elif message.text == 'Change the users greeting':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить приветствие пользователя.")
				msg = bot.send_message(config.admin_id, "Send me a message that will be sent to the user on the start command.", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, hello_edit)
		elif message.text == 'Add a response to the info button':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить ответ на кнопку информация.")
				msg = bot.send_message(config.admin_id, "Send me a message that will be sent to the user.", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, information_edit)
		elif message.text == 'Change the product catalog':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить каталог товаров.")
				msg = bot.send_message(config.admin_id, "Select an action.", reply_markup=menu.katalog_1_eng)
		elif message.text == 'Add product to catalog':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить товар в каталог.")
				msg = bot.send_message(config.admin_id, "Enter a name", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, assort_1_add)
		elif message.text == 'Remove an item from the catalog':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка удалить товар из каталога.")
				text = db.return_katalog()
				msg = bot.send_message(config.admin_id, "Which of these do you want to remove? To delete it, enter the name of the desired record.\n\n{}".format(text), reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, assort_1_delete)
		elif message.text == 'Add a response to the contact button':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить ответ на кнопку связаться.")
				msg = bot.send_message(config.admin_id, 'Send me a message that will be sent to the user.', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, contact_edit)
		elif message.text == 'Add text after payment':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить текст после оплаты.")
				msg = bot.send_message(config.admin_id, 'Send me a message that will be sent to the user after the payment.', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, payment_edit)
		elif message.text == '🌐 Your balance':
			if message.chat.id == config.admin_id:
				try:
					logging.info("Администратор запросил баланс Qiwi.")
					api = QApi(token=config.token_qiwi, phone=config.qiwi_number)
					balance = api.balance[0]
					number = config.qiwi_number
					bot.send_message(config.admin_id, "Number: {}\n\nBalance: {} руб".format(number, balance), reply_markup=menu.close_eng)
				except:
					bot.send_message(config.admin_id, "❌ Error! Invalid Qiwi wallet number or token.")
		elif message.text == 'Setting up an assortment':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Here you can find your entire product range. To use this feature, select the appropriate action below.', reply_markup=menu.assortment_eng)
		elif message.text == 'Users':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'This section can help you with setting up and editing users.', reply_markup=menu.users_eng)
		elif message.text == 'Logs':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'What are you interested in? How do you want to get the logs?', reply_markup=menu.logi_eng)
		elif message.text == 'Send as a file':
			if message.chat.id == config.admin_id:
					with open("bot.log","rb") as file:
						file_read = file.read()
					bot.send_document(config.admin_id, file_read, "bot.log")
		elif message.text == 'Send a message':
			if message.chat.id == config.admin_id:
				try:
					text = open("bot.log", 'r')
					text2 = text.read()
					bot.send_message(config.admin_id, '💾 LOGS 💾\n{}'.format(text2), reply_markup=menu.logi_eng)
				except:
					bot.send_message(config.admin_id, "❗️You can't send a message. The file is too large.", reply_markup=menu.logi_eng)
		elif message.text == 'List of users':
			if message.chat.id == config.admin_id:
				logging.info("Был запрошен список пользователей.")
				text = db.return_users_2()
				bot.send_message(config.admin_id, '👤 Detailed information about users:\n\n{}'.format(text))
		elif message.text == 'Change balance':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить баланс пользователя.")
				msg = bot.send_message(config.admin_id, 'Attention❗️ Changing the balance can lead to possible problems in the operation of the bot, as well as incorrect display of statistics. Do you want to continue?', reply_markup=menu.yes_eng)
				bot.register_next_step_handler(msg, yes_2)
		elif message.text == 'Change the number of purchases':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить кол-во покупок.")
				msg = bot.send_message(config.admin_id, 'Attention❗️ Changing the number of purchases can lead to possible problems in the operation of the bot, as well as incorrect display of statistics. Do you want to continue?', reply_markup=menu.yes_eng)
				bot.register_next_step_handler(msg, yes_3)
		elif message.text == '🥝 qiwi':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Setting up a wallet', reply_markup=menu.money_qiwi_eng)
		elif message.text == '💳 Receive QIWI':
			if message.chat.id == config.admin_id:
				text = '💳 Your Qiwi Wallet number:'
				bot.send_message(config.admin_id, '{}\n\n{}'.format(text, config.qiwi_number), reply_markup=menu.close_eng)
		elif message.text == '💳 Receive BTC':
			if message.chat.id == config.admin_id:
				try:
					logging.info("Была создана ссылка для получения BTC.")
					client = Client(api_key, api_secret, api_version='2021-01-16')
					message = []
					primary_account = client.get_primary_account()
					address = primary_account.create_address()
					text = str(address['deposit_uri']).replace('bitcoin:', '')
					bot.send_message(config.admin_id, '<a>🧨Address to receive:\n\n<pre>{}</pre></a>'.format(text), parse_mode='HTML', reply_markup=menu.close_eng)
				except:
					bot.send_message(config.admin_id, "❌ Error! Invalid API key.")
		elif message.text == '📤 Send QIWI':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка отправить деньги на Qiwi.")
				msg = bot.send_message(config.admin_id, "Enter the number to which the funds will be sent:", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_money_1)
		elif message.text == '📤 Отправить BTC':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка отправить Bitcoin.")
				msg = bot.send_message(config.admin_id, 'Введите адрес Bitcoin кошелька, на который будут отправлены средства:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_bitcoin)
		elif message.text == 'Add/Edit data':
			if message.chat.id == config.admin_id:
				msg = bot.send_message(config.admin_id, "Enter your wallet number:", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, lol)
		elif message.text == 'Show all positions':
			if message.chat.id == config.admin_id:
				logging.info("Администратор сделал запрос на выгрузку позиций.")
				text = db.return_position_2()
				bot.send_message(config.admin_id, "💻 Information about the store's positions:\n\n{}".format(text), reply_markup=menu.close_eng)
		elif message.text == 'Show all products of the position':
			if message.chat.id == config.admin_id:
				logging.info("Администратор сделал запрос на выгрузку товаров.")
				text = db.return_product_3()
				bot.send_message(config.admin_id, "📲 Product Information:\n\n{}".format(text), reply_markup=menu.close_eng)
		elif message.text == 'Add a position':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка добавить позицию.")
				text = db.return_katalog()
				msg = bot.send_message(config.admin_id, "Select the desired category from the list:\n\n{}\n\nYou must enter the text.".format(text), reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, pos_1)
		elif message.text == 'Delete a position':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка удалить позицию.")
				text = db.return_position_3()
				msg = bot.send_message(config.admin_id, "Select the item you want to delete:\n\n{}\n\nYou must enter the text.".format(text), reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, delete_position_1)
		elif message.text == 'Change the item description':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить описание позиции.")
				text = db.return_position_3()
				msg = bot.send_message(config.admin_id, "Select the item whose description you want to change:\n\n{}\n\nYou must enter the text.".format(text), reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, edit_position_1)
		elif message.text == 'Change the position price':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка изменить цену позиции.")
				text = db.return_position_3()
				msg = bot.send_message(config.admin_id, "Select the position whose price you want to change:\n\n{}\n\nYou must enter the text.".format(text), reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, change_position_1)
		elif message.text == 'Loading a new product':
			if message.chat.id == config.admin_id:
				msg = bot.send_message(config.admin_id, "Enter the product name:", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, new_item_1)
		elif message.text == 'Add/edit data':
			if message.chat.id == config.admin_id:
				msg = bot.send_message(config.admin_id, "Enter the API key:", reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, yes)
		elif message.text == '💰bitcoin':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Setting up a wallet', reply_markup=menu.money_btc_eng)
		elif message.text == 'Uploading data':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'What data are you interested in?', reply_markup=menu.assortment_data_eng)
		elif message.text == 'Setting up payment cards':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, 'Setting up payment systems.', reply_markup=menu.money_eng)
		elif message.text == 'Statistics':
			if message.chat.id == config.admin_id:
				logging.info("Был запрос на получение статистики.")
				users = db.return_users()
				buyers = db.return_buyers()
				position = db.return_position()
				product = db.return_product_4()
				sales = db.return_sales()
				cash = db.return_cash_100()
				bot.send_message(config.admin_id, '<a>📈 Statistic\n\n👨‍💻Number of users: <b>{}</b>\n💰Earned: <b>{}</b> ₽\n✅ Number of sales: <b>{}</b>\n📦 Number of products: <b>{}</b>\n📤 Number of positions: <b>{}</b>\n🧨Buyers: <b>{}</b></a>'.format(users[0], cash[0], sales[0], product[0], position[0], buyers[0]), parse_mode='HTML', reply_markup=menu.close_eng)
		elif message.text == 'Mailing':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, "Who will receive the newsletter?", reply_markup=menu.send_users_eng)
		elif message.text == 'All users':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка сделать рассылку всем пользователям.")
				msg = bot.send_message(config.admin_id, 'Enter the text:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_users)
		elif message.text == 'Only buyers':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка сделать рассылку покупателям.")
				msg = bot.send_message(config.admin_id, 'Enter the text:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_buyers)
		elif message.text == 'Those who didnt buy anything':
			if message.chat.id == config.admin_id:
				logging.info("Произведена попытка сделать рассылку пользователям, которые еще не совершали покупки в магазине.")
				msg = bot.send_message(config.admin_id, 'Enter the text:', reply_markup=menu.otmena_eng)
				bot.register_next_step_handler(msg, send_not_buyers)
		elif message.text == 'Back':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, "You went back", reply_markup=menu.start_admin_eng)
		elif message.text == 'Return':
			if message.chat.id == config.admin_id:
				bot.send_message(config.admin_id, "You went back", reply_markup=menu.admin_eng)
		else:
			bot.send_message(message.chat.id, "Nothing is clear!")



if __name__ == '__main__':
	bot.polling(none_stop=True)