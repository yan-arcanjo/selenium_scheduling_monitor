from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import os
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()

# Configurar o navegador no modo headless
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Roda sem abrir janela
chrome_options.add_argument("--log-level=3")  # Desabilitar logs de informações
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--disable-logging")  # Desabilitar logs
chrome_options.add_argument("--disable-gpu")  # Opcional, melhora a performance
chrome_options.add_argument("--no-sandbox")  # Opcional, necessário para alguns ambientes

# Desabilita o warning de verificação de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

driver = webdriver.Chrome(chrome_options)

URL = os.getenv('URL_TO_MONITOR')
driver.get(URL)

driver.maximize_window()


def get_xpath_text(xpath:str):
    next_reservation = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    text_to_monitor = next_reservation.text
    return text_to_monitor


def send_alert_telegram(text:str):
    # Substitua pelo seu Token do bot
    TOKEN = os.getenv('TELEGRAM_API_TOKEN')

    # Substitua pelo seu ID de usuário que vai receber o alerta
    user_id = os.getenv('TELEGRAM_USER_ID')

    # Mensagem que você quer enviar
    message_to_telegram = f"Olá! O mês foi encontrado, corra para agendar! - {text}"

    # URL da requisição para enviar a mensagem
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    # Parâmetros da requisição
    params = {
        'chat_id': user_id,  # ID de usuário para quem a mensagem será enviada
        'text': message_to_telegram,  # Texto da mensagem
    }

    # Enviar a mensagem
    response = requests.get(url, params=params, verify=False)
    print('Alerta enviado!')

xpath = '//*[@id="__next"]/div/main/section[1]/div/div/div[2]/div/div[1]/div/div[1]/span/span'

while True:
    try:
        text_to_monitor = get_xpath_text(xpath)

        if('Março' in text_to_monitor):
            print(f'MÊS ENCONTRADO: {text_to_monitor}')
            # Enviar a mensagem
            send_alert_telegram(text_to_monitor)       
        
        else: 
            print(f'MÊS NÃO ENCONTRADO: {text_to_monitor}')
        
        time.sleep(30)

    except TimeoutException:
        print("Erro, pulando pra próxima verificação")

    except StaleElementReferenceException:
        print("Erro, pulando pra próxima verificação")

    driver.refresh()


