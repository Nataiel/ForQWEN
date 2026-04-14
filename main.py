"""
Скрипт для парсинга таблиц с сайта с авторизацией.
Маскируется под обычного пользователя браузера.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from fake_useragent import UserAgent

# Генерируем реалистичный User-Agent
ua = UserAgent()
HEADERS = {
    'User-Agent': ua.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}


class WebsiteScraper:
    """Класс для сбора данных с сайта с маскировкой под браузер."""
    
    def __init__(self, login_url, data_url):
        """
        Инициализация скрепера.
        
        Args:
            login_url: URL страницы авторизации
            data_url: URL страницы с таблицами
        """
        self.login_url = login_url
        self.data_url = data_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Добавляет случайную задержку как у реального пользователя."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def login(self, username, password, additional_data=None):
        """
        Выполняет авторизацию на сайте.
        
        Args:
            username: Логин пользователя
            password: Пароль
            additional_data: Дополнительные данные для формы входа
        
        Returns:
            bool: True если авторизация успешна
        """
        # Данные для отправки (нужно адаптировать под конкретный сайт)
        login_data = {
            'username': username,
            'password': password,
        }
        
        if additional_data:
            login_data.update(additional_data)
        
        print(f"[*] Выполняем вход на {self.login_url}...")
        print(f"[*] Используем User-Agent: {self.session.headers['User-Agent']}")
        
        # Имитируем задержку перед отправкой формы
        self.human_delay(2, 4)
        
        response = self.session.post(
            self.login_url,
            data=login_data,
            allow_redirects=True
        )
        
        # Проверяем успешность входа (нужно адаптировать под сайт)
        if response.status_code == 200:
            print("[+] Авторизация прошла успешно!")
            return True
        else:
            print(f"[-] Ошибка авторизации. Код ответа: {response.status_code}")
            return False
    
    def get_tables(self):
        """
        Получает таблицы с защищенной страницы.
        
        Returns:
            list: Список найденных таблиц
        """
        print(f"[*] Загружаем страницу с таблицами: {self.data_url}")
        
        # Имитируем задержку как у человека
        self.human_delay(1, 3)
        
        response = self.session.get(self.data_url)
        
        if response.status_code != 200:
            print(f"[-] Ошибка загрузки страницы. Код: {response.status_code}")
            return []
        
        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        print(f"[+] Найдено таблиц: {len(tables)}")
        
        return tables
    
    def save_table_to_csv(self, table, filename='table.csv'):
        """Сохраняет таблицу в CSV файл."""
        import csv
        
        rows = []
        for tr in table.find_all('tr'):
            row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            if row:
                rows.append(row)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"[+] Таблица сохранена в {filename}")


# ============================================================================
# АльтЕРНАТИВА: Использование Selenium для полной эмуляции браузера
# (если сайт использует много JavaScript)
# ============================================================================

def scrape_with_selenium(login_url, username, password, data_url):
    """
    Парсинг с использованием Selenium - полная эмуляция браузера.
    Требует установки: pip install selenium webdriver-manager
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    
    # Настройки Chrome для маскировки
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(f"user-agent={ua.random}")
    
    # Создаем драйвер
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # Скрываем признак автоматизации
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"[*] Открываем страницу входа: {login_url}")
        driver.get(login_url)
        
        # Имитируем задержку человека
        time.sleep(random.uniform(2, 4))
        
        # Заполняем форму (селекторы нужно адаптировать под сайт)
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        # Печатаем с задержкой как человек
        for char in username:
            username_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(0.5, 1))
        
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        time.sleep(random.uniform(1, 2))
        
        # Отправляем форму
        password_field.submit()
        
        print("[+] Форма отправлена, ждем загрузки...")
        time.sleep(random.uniform(3, 5))
        
        # Переходим к данным
        driver.get(data_url)
        time.sleep(random.uniform(2, 4))
        
        # Получаем HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        
        print(f"[+] Найдено таблиц: {len(tables)}")
        
        return tables
        
    finally:
        driver.quit()


# ============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == '__main__':
    # ЗАМЕНИТЕ НА ДАННЫЕ ВАШЕГО САЙТА
    LOGIN_URL = 'https://example.com/login'
    DATA_URL = 'https://example.com/tables'
    USERNAME = 'your_username'
    PASSWORD = 'your_password'
    
    print("=" * 60)
    print("СКРЕПЕР ТАБЛИЦ С АВТОРИЗАЦИЕЙ")
    print("=" * 60)
    
    # Вариант 1: Использование requests (быстрее, но не работает с JS)
    scraper = WebsiteScraper(LOGIN_URL, DATA_URL)
    
    # Вход на сайт
    if scraper.login(USERNAME, PASSWORD):
        # Получение таблиц
        tables = scraper.get_tables()
        
        # Сохранение первой таблицы
        if tables:
            scraper.save_table_to_csv(tables[0], 'result.csv')
    
    print("\n" + "=" * 60)
    print("ПРИМЕЧАНИЯ ПО МАСКИРОВКЕ:")
    print("=" * 60)
    print("""
1. User-Agent - меняется на случайный браузер
2. Заголовки - как у настоящего браузера
3. Задержки - случайные паузы между действиями
4. Сессия - cookies сохраняются как в браузере
5. Для сайтов с JS используйте Selenium вариант

ВАЖНО: 
- Изучите robots.txt сайта перед парсингом
- Соблюдайте правила использования сайта
- Не делайте слишком частые запросы
- Уважайте нагрузку на сервер
    """)
