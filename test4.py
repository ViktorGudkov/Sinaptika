import streamlit as st
from streamlit_modal import Modal
from datetime import datetime, date, timezone, timedelta, time

if 'keyword' not in st.session_state:
    st.session_state['keyword'] = ''
if 'start_date' not in st.session_state:
    st.session_state['start_date'] = ''
if 'end_date' not in st.session_state:
    st.session_state['end_date'] = ''

# Создаем модальное окно
modal = Modal("Исторический поиск", key="history_search")

if st.sidebar.button("Исторический поиск"):
    modal.open()

if modal.is_open():
    with modal.container():
        keyword = st.text_input("Введите ключевое слово")
        if st.checkbox('Поиск всех постов', key='keyword_search') == True:
            keyword = 'all_posts'
        
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
            st.session_state['keyword']=keyword
            st.session_state['start_date']=start_date
            st.session_state['end_date']=end_date
            modal.close()

if st.session_state['keyword']:
    st.write(f"You entered: {st.session_state['keyword']}")
    st.write(f"You entered: {st.session_state['start_date']}")
    st.write(f"You entered: {st.session_state['end_date']}")
