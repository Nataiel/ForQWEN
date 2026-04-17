import requests
import time
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import Dict, Any, List, Optional, Callable
from functools import reduce

# --- Конфигурация (Данные) ---
CONFIG = {
    "login_url": "http://school65.ru/Auth.aspx?refererurl=http%3a%2f%2fschool65.ru%2fdefault.aspx",
    "data_url": "http://school65.ru/tables",
    "username": "seggiy@mail.ru",
    "password": "School6565",
    "delay_range": (2, 5),  # Случайная задержка между действиями
}

# --- Утилиты (Чистые функции) ---

def random_delay(min_sec: int, max_sec: int) -> float:
    """Генерирует случайную задержку для имитации человека."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay

def generate_headers() -> Dict[str, str]:
    """Создает заголовки, имитирующие реальный браузер."""
    ua = UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

def build_login_payload(username: str, password: str) -> Dict[str, str]:
    """Формирует полезную нагрузку для входа."""
    # Примечание: имена полей 'username' и 'password' нужно заменить на реальные из формы сайта
    return {
        "login": username,
        "passwordHash": password,
        "submit": "Login"
    }

# --- Логика работы с сетью (Функции высшего порядка и трансформеры) ---

def create_session() -> requests.Session:
    """Создает новую сессию."""
    return requests.Session()

def perform_login(session: requests.Session, url: str, payload: Dict[str, str], headers: Dict[str, str]) -> requests.Session:
    """Выполняет вход и возвращает обновленную сессию (с куками)."""
    print(f"[INFO] Попытка входа на {url}...")
    response = session.post(url, data=payload, headers=headers)
    
    # Простая проверка успеха (можно усложнить проверкой наличия конкретного элемента в ответе)
    if response.status_code == 200 and "logout" in response.text.lower():
        print("[SUCCESS] Авторизация успешна.")
    else:
        print(f"[WARNING] Статус ответа: {response.status_code}. Возможно, вход не удался или сайт требует JS.")
    
    return session

def fetch_data(session: requests.Session, url: str, headers: Dict[str, str]) -> str:
    """Загружает содержимое страницы с данными."""
    print(f"[INFO] Загрузка данных с {url}...")
    response = session.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_tables(html_content: str) -> List[List[str]]:
    """Парсит HTML и извлекает таблицы в виде списка списков."""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = []
    
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cols:
                rows.append(cols)
        if rows:
            tables.append(rows)
            
    return tables

# --- Композиция (Основной поток) ---

def run_pipeline(config: Dict[str, Any]) -> List[List[str]]:
    """
    Основная функция-конвейер.
    Связывает все этапы вместе в функциональном стиле.
    """
    # Этап 1: Подготовка окружения
    headers = generate_headers()
    session = create_session()
    
    # Этап 2: Авторизация
    # Имитируем задержку перед действием
    random_delay(*config["delay_range"])
    
    payload = build_login_payload(config["username"], config["password"])
    authenticated_session = perform_login(session, config["login_url"], payload, headers)
    
    # Этап 3: Получение данных
    random_delay(*config["delay_range"])
    html_content = fetch_data(authenticated_session, config["data_url"], headers)
    
    # Этап 4: Парсинг
    tables = parse_tables(html_content)
    
    return tables

if __name__ == "__main__":
    try:
        # Запуск конвейера
        result_tables = run_pipeline(CONFIG)
        
        # Вывод результата
        print(f"\n[RESULT] Найдено таблиц: {len(result_tables)}")
        for i, table in enumerate(result_tables):
            print(f"--- Таблица {i+1} (первые 3 строки) ---")
            for row in table[:3]:
                print(row)
                
    except Exception as e:
        print(f"[ERROR] Произошла ошибка: {e}")