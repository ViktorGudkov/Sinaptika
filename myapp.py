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
from streamlit_modal import Modal
from telethon.tl.functions.contacts import ImportContactsRequest
from datetime import datetime, date, timezone, timedelta, time

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

api_id = os.environ["API_ID"]
api_hash = os.environ["API_HASH"]
phone = '+79067220866'


nest_asyncio.apply()


initial_channels = ['bcs_express', 'tinkoff_invest_official', 'markettwits', 'cbrstocks', 'finpizdec', 'headlines_for_traders', 
                    'selfinvestor', 'if_market_news', 'forbesrussia', 'bitkogan_hotline', 'thewallstreetpro', 'roflpuls', 
                    'vedomosti', 'profinansy_news','marketpowercomics','sinara_finance','pro_bonds','fm_invest','test030424']


keyword = st.sidebar.text_input("Введите ключевое слово для мониторинга")
user_phone_number = st.sidebar.text_input("Введите номер телефона для отправки сообщений")

if 'monitoring' not in st.session_state:
    st.session_state['monitoring'] = False

if 'main_running' not in st.session_state:
    st.session_state['main_running'] = False

if 'client' not in st.session_state:
    st.session_state['client'] = TelegramClient('anon', api_id, api_hash)

client = st.session_state['client']

if 'keyword_h' not in st.session_state:
    st.session_state['keyword_h'] = ''
if 'start_date' not in st.session_state:
    st.session_state['start_date'] = ''
if 'end_date' not in st.session_state:
    st.session_state['end_date'] = ''

# def check_event_loop():
#     try:
#         loop = asyncio.get_running_loop()
#         if loop.is_running():
#             print("Event loop is running")
#         else:
#             print("Event loop exists but is not running")
#     except RuntimeError:
#         print("No event loop exists")

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

async def stop_monitoring():
    await client.disconnect()
    client.remove_event_handler(start_monitoring, events.NewMessage())
    del st.session_state['client']
    st.session_state['monitoring'] = False

async def start_monitoring(event):
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

async def main():
    st.session_state['main_running'] = True
    async with client:
        client.add_event_handler(start_monitoring, events.NewMessage())
        await client.start(phone=phone)
        st.session_state['monitoring'] = True
        await client.run_until_disconnected()

# Текущий текст кнопки в зависимости от состояния
button_text = "Остановить мониторинг" if st.session_state['monitoring'] else "Начать мониторинг"

if st.sidebar.button(button_text, key='telegram_monitor_button'):
    if st.session_state['monitoring']:
        asyncio.run(stop_monitoring())

        
    else:
        st.session_state['monitoring'] = True
           
    st.rerun()

modal = Modal("Исторический поиск", key="history_search")

if st.sidebar.button("Исторический поиск", key='history_search_button'):
    modal.open()
    

if modal.is_open():
    with modal.container():
        keyword_h = st.text_input("Введите ключевое слово")
        if st.checkbox('Поиск всех постов', key='keyword_search') == True:
            keyword_h = 'all_posts'
        
        period = st.selectbox("Период поиска", ["Один день", "Неделя", "Месяц", "Произвольная дата"], key="period_selectbox")
        
        if period=='Произвольная дата':
            start_date= st.date_input('Введите дату начала поиска', key='start_date_input')

        end_date = st.date_input('Введите дату завершения поиска', key='end_date_input')
        
        if period == 'Один день':
             start_date = end_date - timedelta(days=1)
        elif period == 'Неделя':
            start_date = end_date - timedelta(days=7)
        elif period == 'Месяц':
             start_date = end_date - timedelta(days=30)

        if st.button("Начать поиск"):
            st.session_state['keyword_h']=keyword_h
            st.session_state['start_date']=start_date
            st.session_state['end_date']=end_date
            modal.close()

if st.session_state['keyword_h']:
    st.write(f"You entered: {st.session_state['keyword_h']}")
    st.write(f"You entered: {st.session_state['start_date']}")
    st.write(f"You entered: {st.session_state['end_date']}")

if st.session_state['monitoring'] and not st.session_state['main_running']:
#if st.session_state['monitoring'] == True:
    asyncio.run(main())
        




