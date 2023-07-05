import requests,random,telebot,time
from config import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from json import JSONDecodeError
from database import create_db_and_tables,engine
from sqlmodel import Session,select
from database import Offer
from bs4 import BeautifulSoup
from loguru import logger

logger.add("mostaql_bot.log",format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {function} | {message}",colorize=False,enqueue=True,mode="w")

create_db_and_tables()

bot = telebot.TeleBot(bot_token)

project_page_url  = "https://mostaql.com/project/"
projects_page_url = 'https://mostaql.com/projects?category=business,development,engineering-architecture,design,marketing,writing-translation,support&budget_max=10000&sort=latest&_=1688336827002'

requests_session = requests.Session()
requests_session.headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
                            'x-requested-with': 'XMLHttpRequest',}

def set_new_proxy() : 
    creds = str(random.randint(10000,0x7fffffff)) + ":" + "foobar"
    requests_session.proxies = {'http': 'socks5h://{}@localhost:9050'.format(creds), 'https': 'socks5h://{}@localhost:9050'.format(creds)}


def get_offer_description(offer_id) : 
    logger.info(f'set new proxy to fetch offer_id : {str(offer["id"])} ')
    set_new_proxy()
    response = requests_session.get(project_page_url+str(offer['id']))
    soup = BeautifulSoup(response.text,'lxml')
    category        = (soup.find_all('li',{'class':'breadcrumb-item'}))[-1].text.strip()
    title           = (soup.find_all('span',{'data-type':'page-header-title'}))[0].text.strip()
    price           = (soup.find_all('td',{'data-type':'project-budget_range'}))[0].text.strip()
    project_owner   = (soup.find_all('h5',{'class':'postcard__title profile__name mrg--an'}))[0].text.strip()
    logger.info(f'offer_id : {offer_id}')
    logger.info(f'category : {category}')
    logger.info(f'title : {title}')
    logger.info(f'price : {price}')
    logger.info(f'project_owner : {project_owner}')
    return {
        "offer_id" : offer_id,
        "category" :  category,
        "title" : title,
        "price" :price,
        "project_owner" :project_owner
        }

def build_message(offer : Offer) : 
    return f'''📣📣 New Job Alert 📣📣

🔹 Job Field: {offer.category}
------------------------------------------------------------------------
🔹 Job Title: {offer.title}
------------------------------------------------------------------------
🔹 Job Budget: {offer.price}
------------------------------------------------------------------------
🔹 Employer: {offer.project_owner}
------------------------------------------------------------------------
'''
def send_alert(chat_id,offer : Offer) : 
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ Click here to visit the project's page ➡️", url=project_page_url+str(offer.offer_id)))
    bot.send_message(chat_id=chat_id,
                     text=build_message(offer),
                     reply_markup=markup)

while True : 
    set_new_proxy()
    database_session = Session(engine)
    response = requests_session.get(projects_page_url)
    try : 
        offers = response.json()['collection']
        logger.info(f'fetch {len(offers)} offers')
        for offer in offers : 

            fetched_offer = database_session.exec(select(Offer).where(Offer.offer_id==offer['id'])).first()
            if fetched_offer :
                continue
            response = requests_session.get(project_page_url+str(offer['id']))
            offer_description = get_offer_description(offer['id'])
            offer_to_send = Offer(
                offer_id        = offer_description['offer_id'],
                category        = offer_description['category'],
                title           = offer_description['title'],
                project_owner   = offer_description['project_owner'],
                price           = offer_description['price']
            )
            database_session.add(offer_to_send)
            database_session.commit()
            for chat_id in chat_ids : 
                send_alert(chat_id,offer_to_send)
    except Exception as e :
        logger.error(f'error occured : {str(e)}')
    logger.info('sleep for 1 minute to release the resources')
    time.sleep(60)
    database_session.close()







