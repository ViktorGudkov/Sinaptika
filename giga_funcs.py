from langchain.prompts import PromptTemplate
from langchain import hub
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.chat_models.gigachat import GigaChat
import os
import docx
from dotenv import load_dotenv
import re
import base64
import asyncio
import math

load_dotenv()

def count_words(text):
    # Подсчет слов в тексте
    return len(text.split())

def read_posts_from_docx(document_path):
    # Загружаем документ
    doc = docx.Document(document_path)
    full_text = []
    
    # Собираем текст из всех параграфов документа
    for para in doc.paragraphs:
        full_text.append(para.text)
    
    # Объединяем все строки в одну большую строку
    full_text = "\n".join(full_text)
    
    link_pattern = re.compile(r'https?://\S+')
    # Заменяем все найденные ссылки на пустую строку
    cleaned_text = re.sub(link_pattern, '', full_text)

    # Используем регулярное выражение для разделения текста по шаблону "[Просмотры: число]"
    posts = re.split(r'----------', cleaned_text)
    
    # Удаляем пустые элементы, которые могут возникнуть при разделении
    posts = [post.strip() for post in posts if post.strip()]
    return posts

client_id = os.environ['CLIENT_ID_CM']
secret = os.environ['CLIENT_SECRET_CM']

credentials = f"{client_id}:{secret}"
auth= base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

giga_lite = GigaChat(credentials=auth,
                model= 'GigaChat-Plus',
                verify_ssl_certs=False,
                scope='GIGACHAT_API_CORP',
                profanity_check=False
                )

giga_pro = GigaChat(credentials=auth,
                model= 'GigaChat-Pro',
                verify_ssl_certs=False,
                scope='GIGACHAT_API_CORP',
                profanity_check=False)


async def giga_sum(text, prompt, sentence_num, keyword, model):
    

    chain = prompt | model


    result = await chain.ainvoke(
   
    {
       
        "text": text,
        "sentence_num":sentence_num
    }


    )
    
    return result.content
    

summary=[]

async def posts_summary(document_path, prompt_type, keyword, update_progress_callback=None):

    if prompt_type=='prompt_all_posts':
        prompt = prompt_all_posts = PromptTemplate.from_template('Проанализируй текст и '
                                      'выдели основные мысли и идеи, присутствующие в тексте.'
                                    'Представь результаты в виде структурированного списка из 1-{sentence_num} развернутых предложений. Избегай дублирование новостей. Текст: {text}'
 
    ) 
    else:
        prompt=prompt_key_word = PromptTemplate.from_template('Проанализируй текст и '
                                      f'выдели основные мысли и идеи, связанные со словом {keyword}, присутствующие в тексте.'
                                    'Представь результаты в виде структурированного списка развернутых предложений. Избегай дублирование новостей. Текст: {text}'
 
    ) 
    
    posts = read_posts_from_docx(document_path)  # Предположим, это функция для чтения постов
    total_posts = len(posts)  # Общее количество постов
    processed_posts = 0 
    t1=len(posts)/50
    if update_progress_callback:
        update_progress_callback(total_posts=total_posts, processed_posts=processed_posts)
    if t1<=11:
        sentence_num=str(20)
    elif t1<20:
        sentence_num=20-str(math.floor(t1/2))
    else:
        sentence_num=str(10)

    current_batch = []
    current_count = 0
    summary = []
    tasks = []
    task_limit = 5

    for post in posts:
        post_word_count = count_words(post)
        if current_count + post_word_count > 5000:
            # Если добавление поста превышает лимит, обработайте текущий батч и начните новый
            tasks.append(giga_sum(current_batch, prompt, sentence_num, keyword=keyword, model=giga_lite))
            processed_posts += len(current_batch)
            
            if len(tasks) == task_limit:
                # Запускаем задачи, когда их накопилось 5
                results = await asyncio.gather(*tasks)
                print(results)
                summary.extend(results)
                            # Обновляем прогресс с помощью переданной функции
                if update_progress_callback:
                    update_progress_callback(total_posts=total_posts, processed_posts=processed_posts)
                tasks = []
            current_batch = [post]
            current_count = post_word_count
        else:
            # Иначе добавьте пост в текущий батч
            current_batch.append(post)
            current_count += post_word_count

    # Не забудьте обработать последний батч, если он не пуст
   
    if current_batch:
        tasks.append(giga_sum(current_batch, prompt, sentence_num, keyword=keyword, model=giga_lite))
        processed_posts += len(current_batch)
        
    # Запуск оставшихся задач, если они есть
    if tasks:
        results = await asyncio.gather(*tasks)
        summary.extend(results)
                
                # Обновляем прогресс
        if update_progress_callback:
            update_progress_callback(total_posts=total_posts, processed_posts=processed_posts)

    # Обработка итогового списка summary
    
    #sum_summary = await giga_sum(summary, prompt, keyword=keyword, model=giga_pro)
    
    attempts = 3
    while attempts > 0:
        try:
            sentence_num=str(20)
            print('НАЧИНАЮ ИТОГОВУЮ СУММАРИЗАЦИЮ')
            sum_summary = await giga_sum(summary, prompt, sentence_num, keyword=keyword, model=giga_pro)
            print(sum_summary)
            return sum_summary
        except Exception as e:
            print(f"Error encountered: {e}. Retrying... ({attempts-1} attempts left)")
            attempts -= 1
    
    sum_summary = await giga_sum(summary, prompt, keyword=keyword, model=giga_lite)

    print(sum_summary)
    return sum_summary    

# НИЖЕ ФУНКЦИЯ ДЛЯ ОБРАБОТКИ КАЖДОГО ПОСТА ПО ОТДЕЛЬНОСТИ

def extract_date_from_post(post):
    # Предполагаем, что дата находится в первой строке поста
    lines = post.splitlines()
    if lines:
        date_line = lines[0]
        return date_line.strip()
    else:
        return ''

async def giga_sum_each_post(text, prompt, keyword, model):
    

    chain = prompt | model


    result = await chain.ainvoke(
   
    {
       
        "text": text
    }


    )
    
    return result.content

async def each_post_summary(document_path, prompt_type, keyword, update_progress_callback=None):

    if prompt_type=='prompt_all_posts':
        prompt = prompt_all_posts = PromptTemplate.from_template('Проанализируй текст и '
                                      'выдели основные мысли и идеи, присутствующие в тексте, не более чем в 2-3 предложениях.'
                                    'Текст: {text}'
 
    ) 
    else:
        prompt=prompt_key_word = PromptTemplate.from_template('Проанализируй текст и '
                                      f'выдели основные мысли и идеи, связанные со словом {keyword}, присутствующие в тексте, не более чем в 2-3 предложениях.'
                                    'Текст: {text}'
 
    ) 
    
    posts = read_posts_from_docx(document_path)  # Предположим, это функция для чтения постов
    total_posts = len(posts)  # Общее количество постов
    processed_posts = 0 

    current_batch = []
    sum_summary = []
    tasks = []
    task_limit = 5
    dates_list = []

    for post in posts:
        
        date = extract_date_from_post(post)
        dates_list.append(date)
    
        tasks.append(giga_sum_each_post(post, prompt, keyword=keyword, model=giga_lite))
        processed_posts += 1
            
        if len(tasks) == task_limit:
            # Запускаем задачи, когда их накопилось 5
            results = await asyncio.gather(*tasks)
            print(results)

            # Объединяем дату и результат
            for date, result in zip(dates_list, results):
                sum_summary.append(f"{date}\n{result}\n")
            
            sum_summary.extend(results)
                            # Обновляем прогресс с помощью переданной функции
            if update_progress_callback:
                update_progress_callback(total_posts=total_posts, processed_posts=processed_posts)
            tasks = []
            dates_list = []
       
        
    # Запуск оставшихся задач, если они есть
    if tasks:
        results = await asyncio.gather(*tasks)
        
        # Объединяем дату и результат
        for date, result in zip(dates_list, results):
            sum_summary.append(f"{date}\n{result}\n")
        

                
                # Обновляем прогресс
        if update_progress_callback:
            update_progress_callback(total_posts=total_posts, processed_posts=processed_posts)

    return ''.join(sum_summary)
    