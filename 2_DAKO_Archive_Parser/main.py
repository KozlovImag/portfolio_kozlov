## Автор: Алексей Козлов
## GitHub https://github.com/KozlovImag/

## Двигайся в вправо ---->                                                                                                                                   вместо номера слайда пиши {}                                                          
base_url = 'https://opisi.dako.gov.ua/opisi/list-files/index?folder=Fond_F-384&subfolder=opys_9&delofolder=F384_9_417&fond=384&sectablename=secondpage&countdela=630#lg=1&slide={}'


Nmin=1  # первая страница
Nmax=173 # последняя страница

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Настройки Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск браузера в фоновом режиме
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Укажите путь к драйверу Chrome
chrome_driver_path = 'chromedriver.exe'  # Замените на путь к вашему ChromeDriver

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Создаем директорию для сохранения файлов, если ее не существует
if not os.path.exists('arch_files'):
    os.makedirs('arch_files')


for num in range(Nmin-1, Nmax-1):
    url = base_url.format(num)
    driver.get(url)
    
    try:
        # Ждем, пока элемент с id 'lg-download' станет доступен
        download_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'lg-download'))
        )
        
        file_url = download_link.get_attribute('href')
        if file_url:
            file_response = requests.get(file_url)
            
            if file_response.status_code == 200:
                file_name = f'arch_files/{num}_arch.jpg'
                with open(file_name, 'wb') as file:
                    file.write(file_response.content)
                print(f'Successfully downloaded {file_name}')
            else:
                print(f'Failed to download file from {file_url}')
        else:
            print(f'Download link not found on page {url}')
    except Exception as e:
        print(f'Error on page {url}: {e}')

driver.quit()
