import streamlit as st
from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
import asyncio
import nest_asyncio
import logging
from docx import Document
from telethon.tl.types import InputPhoneContact
import streamlit as st
from telethon.tl.functions.contacts import ImportContactsRequest

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

api_id = os.environ["API_ID"]
api_hash = os.environ["API_HASH"]
phone = '+79067220866'


nest_asyncio.apply()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

client = TelegramClient('anon', api_id, api_hash)

initial_channels = ['bcs_express', 'tinkoff_invest_official', 'markettwits', 'cbrstocks', 'finpizdec', 'headlines_for_traders', 
                    'selfinvestor', 'if_market_news', 'forbesrussia', 'bitkogan_hotline', 'thewallstreetpro', 'roflpuls', 
                    'vedomosti', 'profinansy_news','marketpowercomics','sinara_finance','pro_bonds','fm_invest','test030424']


keyword = st.sidebar.text_input("Введите ключевое слово для мониторинга")
user_phone_number = st.sidebar.text_input("Введите номер телефона для отправки сообщений")

async def get_user_id_by_phone(user_phone_number):
    try:
        # Создаем объект контакта
        contact = InputPhoneContact(client_id=0, phone=user_phone_number, first_name="Temp", last_name="Contact")
        
        # Импортируем контакт
        result = await client(ImportContactsRequest([contact]))
        
        # Получаем идентификатор пользователя
        user_id = result.users[0].id
        print(f"User ID для {user_phone_number}: {user_id}")
        return user_id
    
    except Exception as e:
        print(f"Не удалось получить идентификатор пользователя: {e}")

async def get_id():

    user_id = await get_user_id_by_phone(user_phone_number)
    print(f"User ID: {user_id}")
    return user_id

async def monitoring(event):
    message_text = event.message.text.lower()  # Получаем текст сообщения и приводим к нижнему регистру
    channel_entity = await event.get_chat()  # Получаем информацию о канале
    channel_name = channel_entity.username  # Название канала
    if keyword.lower() in message_text:
        message_to_show = f"Канал: {channel_name}\n{event.message.text}"  # Формируем сообщение для пересылки
        st.write(message_to_show)
      
    
    # Получаем ID пользователя по номеру телефона
        user_id = await get_id()
    # Отправляем сообщение
        await client.send_message(user_id, message_to_show)


if st.sidebar.button("Начать мониторинг"):

    
    async def main():
        client.add_event_handler(monitoring, events.NewMessage())

        await client.start(phone=phone)
        await client.run_until_disconnected()
    
    loop.run_until_complete(main())

if st.sidebar.button("Исторический поиск"):
    st.write('Test')





