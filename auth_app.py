#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа авторизации на сайте РБД 2026
Использует Selenium для эмуляции реального браузера
Функциональный стиль без использования классов
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import random


# Глобальные переменные
base_url = "https://rbd.education"  # Замените на актуальный домен
driver = None
remember_var = None
keep_browser_var = None
login_entry = None
password_entry = None
login_button = None
status_label = None
root_window = None
links_file_entry = None
save_folder_entry = None


def create_driver():
    """Создание и настройка браузера Chrome для эмуляции реального пользователя"""
    chrome_options = Options()
    
    # Основные настройки для скрытия автоматизации
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Рандомизация User-Agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    ]
    chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    # Дополнительные настройки для большей реалистичности
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--lang=ru-RU,ru;q=0.9,en;q=0.8')
    
    # Отключение автоматических уведомлений
    chrome_options.add_argument('--disable-notifications')
    
    # Настройка разрешений
    prefs = {
        'profile.default_content_setting_values.notifications': 2,
        'credentials_enable_service': False,
        'profile.password_manager_enabled': False,
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    # Инициализация драйвера
    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=chrome_options)
    
    # Скрытие признаков автоматизации через JavaScript
    drv.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en']
            });
        '''
    })
    
    return drv


def human_typing(element, text, delay_range=(0.05, 0.2)):
    """Эмуляция человеческого ввода текста с задержками"""
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))
    # Небольшая пауза после ввода
    time.sleep(random.uniform(0.1, 0.3))


def update_status(message):
    """Обновление статуса в главном потоке"""
    def set_text():
        status_label.config(text=message)
    root_window.after(0, set_text)


def perform_login():
    """Выполнение авторизации через браузер с последующим скачиванием файлов"""
    global driver
    
    login = login_entry.get().strip()
    password = password_entry.get()
    links_file = links_file_entry.get().strip()
    save_folder = save_folder_entry.get().strip()
    
    if not login:
        update_status("Ошибка: Введите логин")
        messagebox.showerror("Ошибка", "Введите логин или имя пользователя")
        return
    
    if not password:
        update_status("Ошибка: Введите пароль")
        messagebox.showerror("Ошибка", "Введите пароль")
        return
    
    # Загрузка списка ссылок
    links = []
    if links_file and os.path.exists(links_file):
        try:
            with open(links_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('http'):
                        links.append(line)
            update_status(f"Загружено {len(links)} ссылок из файла")
        except Exception as e:
            messagebox.showerror("Ошибка чтения файла", f"Не удалось прочитать файл ссылок:\n{str(e)}")
            return
    elif links_file:
        messagebox.showwarning("Предупреждение", f"Файл с ссылками не найден:\n{links_file}")
        return
    
    # Проверка папки для сохранения
    if save_folder and not os.path.exists(save_folder):
        try:
            os.makedirs(save_folder)
            update_status(f"Создана папка для сохранения: {save_folder}")
        except Exception as e:
            messagebox.showerror("Ошибка создания папки", f"Не удалось создать папку:\n{str(e)}")
            return
    elif not save_folder and links:
        messagebox.showwarning("Предупреждение", "Указаны ссылки для скачивания, но не выбрана папка для сохранения")
        return
    
    update_status("Запуск браузера...")
    login_button.config(state=tk.DISABLED)
    
    try:
        # Создаем браузер
        driver = create_driver()
        wait = WebDriverWait(driver, 30)
        
        # Переход на страницу авторизации
        update_status("Переход на страницу авторизации...")
        driver.get(f"{base_url}/users/sign_in")
        
        # Ждем загрузки страницы
        wait.until(EC.presence_of_element_located((By.ID, "user_first_name")))
        
        # Небольшая случайная задержка перед вводом (как будто пользователь осматривает страницу)
        time.sleep(random.uniform(0.5, 1.5))
        
        # Поиск полей ввода
        update_status("Ввод данных...")
        login_field = wait.until(EC.element_to_be_clickable((By.ID, "user_first_name")))
        password_field = driver.find_element(By.ID, "user_password")
        remember_checkbox = driver.find_element(By.ID, "user_remember_me")
        submit_button = driver.find_element(By.NAME, "commit")
        
        # Эмуляция человеческого ввода логина
        login_field.click()
        time.sleep(random.uniform(0.2, 0.5))
        human_typing(login_field, login)
        
        # Переход к полю пароля и ввод
        password_field.click()
        time.sleep(random.uniform(0.2, 0.5))
        human_typing(password_field, password)
        
        # Установка чекбокса "Запомнить меня" если нужно
        if remember_var.get():
            if not remember_checkbox.is_selected():
                remember_checkbox.click()
                time.sleep(random.uniform(0.1, 0.3))
        
        # Небольшая пауза перед отправкой формы
        time.sleep(random.uniform(0.3, 0.8))
        
        # Клик по кнопке входа
        update_status("Отправка формы...")
        submit_button.click()
        
        # Ждем результата (перенаправление или сообщение об ошибке)
        time.sleep(2)
        
        # Проверка результата
        current_url = driver.current_url
        page_source = driver.page_source.lower()
        
        # Успешный вход - редирект на другую страницу или появление элементов личного кабинета
        if '/users/sign_in' not in current_url and ('выйти' in page_source or 'logout' in page_source):
            update_status("✓ Успешная авторизация!")
            
            # Скачивание файлов по ссылкам
            if links and save_folder:
                download_files(links, save_folder, wait)
            
            if not keep_browser_var.get():
                time.sleep(3)
                driver.quit()
                driver = None
            else:
                messagebox.showinfo("Успех", "Авторизация выполнена успешно!\nБраузер открыт с вашей сессией.")
        else:
            # Проверка на ошибку авторизации
            if 'неверный' in page_source or 'ошибка' in page_source or 'логин' in page_source:
                update_status("✗ Ошибка авторизации")
                messagebox.showerror("Ошибка", "Неверный логин или пароль")
            else:
                update_status("⚠ Требуется проверка")
                messagebox.showwarning(
                    "Внимание", 
                    "Авторизация может не выполниться.\nПроверьте результат в браузере."
                )
            
            # Закрываем браузер при ошибке
            if not keep_browser_var.get():
                time.sleep(2)
                driver.quit()
                driver = None
                
    except TimeoutException:
        update_status("Ошибка: Превышено время ожидания")
        messagebox.showerror(
            "Ошибка", 
            "Превышено время ожидания ответа от сервера.\nПроверьте подключение к интернету."
        )
        if driver:
            driver.quit()
            driver = None
    except WebDriverException as e:
        update_status(f"Ошибка браузера: {str(e)}")
        messagebox.showerror(
            "Ошибка браузера", 
            f"Не удалось запустить браузер.\nУбедитесь, что Chrome установлен.\n\nДетали: {str(e)}"
        )
        if driver:
            driver.quit()
            driver = None
    except Exception as e:
        update_status(f"Ошибка: {str(e)}")
        messagebox.showerror("Ошибка", str(e))
        if driver:
            driver.quit()
            driver = None
    finally:
        login_button.config(state=tk.NORMAL)


def download_files(links, save_folder, wait):
    """Скачивание файлов по списку ссылок с эмуляцией действий пользователя"""
    update_status(f"Начало скачивания {len(links)} файлов...")
    
    for i, link in enumerate(links, 1):
        try:
            update_status(f"Скачивание файла {i}/{len(links)}...")
            
            # Переход по ссылке с случайной задержкой
            time.sleep(random.uniform(1.0, 2.5))
            driver.get(link)
            
            # Ждем загрузки страницы
            time.sleep(random.uniform(1.0, 2.0))
            
            # Попытка найти кнопку скачивания (если есть на странице)
            # Ищем различные варианты кнопок скачивания
            download_selectors = [
                "a[href*='download']",
                "button[class*='download']",
                "input[value*='Скачать']",
                "input[value*='Download']",
                ".download-btn",
                "#download-button"
            ]
            
            for selector in download_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            # Клик по кнопке скачивания с эмуляцией человека
                            driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                            time.sleep(random.uniform(0.3, 0.7))
                            elem.click()
                            update_status(f"Клик по кнопке скачивания для файла {i}")
                            break
                except:
                    continue
            
            # Если это прямая ссылка на файл, браузер начнет скачивание автоматически
            # Ждем некоторое время для начала загрузки
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as e:
            update_status(f"Ошибка при скачивании файла {i}: {str(e)}")
            continue
    
    update_status(f"✓ Скачивание завершено! Файлы сохранены в: {save_folder}")
    messagebox.showinfo("Завершено", f"Скачивание {len(links)} файлов завершено!\nПапка сохранения: {save_folder}")


def select_links_file():
    """Выбор файла со ссылками"""
    filename = filedialog.askopenfilename(
        title="Выберите файл со ссылками",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    if filename:
        links_file_entry.delete(0, tk.END)
        links_file_entry.insert(0, filename)


def select_save_folder():
    """Выбор папки для сохранения файлов"""
    folder = filedialog.askdirectory(title="Выберите папку для сохранения файлов")
    if folder:
        save_folder_entry.delete(0, tk.END)
        save_folder_entry.insert(0, folder)


def start_login(event=None):
    """Запуск авторизации в отдельном потоке"""
    thread = threading.Thread(target=perform_login, daemon=True)
    thread.start()


def create_widgets(root):
    """Создание элементов интерфейса"""
    global login_entry, password_entry, login_button, status_label
    global remember_var, keep_browser_var, root_window
    global links_file_entry, save_folder_entry
    
    root_window = root
    
    # Заголовок
    title_label = tk.Label(
        root, 
        text="РБД 2026 - Авторизация и скачивание", 
        font=("Arial", 14, "bold"),
        pady=10
    )
    title_label.pack()
    
    # Фрейм для полей ввода
    form_frame = ttk.Frame(root, padding=10)
    form_frame.pack(fill=tk.BOTH, expand=True)
    
    # Поле логина
    login_label = ttk.Label(form_frame, text="Логин или имя пользователя:")
    login_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
    
    login_entry = ttk.Entry(form_frame, width=50)
    login_entry.grid(row=1, column=0, columnspan=3, pady=5, ipady=5, sticky=tk.W)
    login_entry.focus()
    
    # Поле пароля
    password_label = ttk.Label(form_frame, text="Пароль:")
    password_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)
    
    password_entry = ttk.Entry(form_frame, width=50, show="*")
    password_entry.grid(row=3, column=0, columnspan=3, pady=5, ipady=5, sticky=tk.W)
    
    # Чекбокс "Запомнить меня"
    remember_var = tk.BooleanVar(value=False)
    remember_check = ttk.Checkbutton(
        form_frame, 
        text="Запомнить меня", 
        variable=remember_var
    )
    remember_check.grid(row=4, column=0, sticky=tk.W, pady=5)
    
    # Чекбокс "Не закрывать браузер после входа"
    keep_browser_var = tk.BooleanVar(value=False)
    keep_browser_check = ttk.Checkbutton(
        form_frame, 
        text="Не закрывать браузер после входа", 
        variable=keep_browser_var
    )
    keep_browser_check.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)
    
    # Разделитель
    separator1 = ttk.Separator(form_frame, orient='horizontal')
    separator1.grid(row=5, column=0, columnspan=3, sticky='ew', pady=15)
    
    # Файл со ссылками
    links_label = ttk.Label(form_frame, text="Файл со ссылками (.txt):")
    links_label.grid(row=6, column=0, sticky=tk.W, pady=5)
    
    links_file_entry = ttk.Entry(form_frame, width=40)
    links_file_entry.grid(row=7, column=0, columnspan=2, pady=5, ipady=5, sticky=tk.W)
    
    browse_links_btn = ttk.Button(
        form_frame, 
        text="Обзор...", 
        command=select_links_file,
        width=10
    )
    browse_links_btn.grid(row=7, column=2, pady=5, padx=(5, 0))
    
    # Папка для сохранения
    folder_label = ttk.Label(form_frame, text="Папка для сохранения:")
    folder_label.grid(row=8, column=0, sticky=tk.W, pady=5)
    
    save_folder_entry = ttk.Entry(form_frame, width=40)
    save_folder_entry.grid(row=9, column=0, columnspan=2, pady=5, ipady=5, sticky=tk.W)
    
    browse_folder_btn = ttk.Button(
        form_frame, 
        text="Обзор...", 
        command=select_save_folder,
        width=10
    )
    browse_folder_btn.grid(row=9, column=2, pady=5, padx=(5, 0))
    
    # Кнопка входа
    login_button = ttk.Button(
        form_frame, 
        text="Войти и скачать", 
        command=start_login,
        width=20
    )
    login_button.grid(row=10, column=0, columnspan=3, pady=20)
    
    # Статус бар
    status_label = ttk.Label(
        root, 
        text="Готов к работе", 
        relief=tk.SUNKEN, 
        anchor=tk.W
    )
    status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Привязка Enter для входа
    root.bind('<Return>', start_login)


def main():
    """Точка входа в приложение"""
    global root_window
    
    root = tk.Tk()
    root.title("Авторизация РБД 2026")
    root.geometry("600x500")
    root.resizable(False, False)
    
    # Установка иконки (если есть)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Создание виджетов
    create_widgets(root)
    
    # Запуск главного цикла
    root.mainloop()


if __name__ == "__main__":
    main()
