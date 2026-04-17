#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа авторизации на сайте РБД 2026
Использует Selenium для эмуляции реального браузера
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import random


class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация РБД 2026")
        self.root.geometry("450x400")
        self.root.resizable(False, False)
        
        # Базовый URL сайта
        self.base_url = "https://rbd.education"  # Замените на актуальный домен
        
        # Браузер (инициализируется при входе)
        self.driver = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self.root, 
            text="РБД 2026 - Авторизация", 
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Фрейм для полей ввода
        form_frame = ttk.Frame(self.root, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле логина
        login_label = ttk.Label(form_frame, text="Логин или имя пользователя:")
        login_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.login_entry = ttk.Entry(form_frame, width=40)
        self.login_entry.grid(row=1, column=0, pady=5, ipady=5)
        self.login_entry.focus()
        
        # Поле пароля
        password_label = ttk.Label(form_frame, text="Пароль:")
        password_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.password_entry = ttk.Entry(form_frame, width=40, show="*")
        self.password_entry.grid(row=3, column=0, pady=5, ipady=5)
        
        # Чекбокс "Запомнить меня"
        self.remember_var = tk.BooleanVar(value=False)
        remember_check = ttk.Checkbutton(
            form_frame, 
            text="Запомнить меня", 
            variable=self.remember_var
        )
        remember_check.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Чекбокс "Не закрывать браузер после входа"
        self.keep_browser_var = tk.BooleanVar(value=False)
        keep_browser_check = ttk.Checkbutton(
            form_frame, 
            text="Не закрывать браузер после входа", 
            variable=self.keep_browser_var
        )
        keep_browser_check.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        # Кнопка входа
        self.login_button = ttk.Button(
            form_frame, 
            text="Войти", 
            command=self.start_login,
            width=20
        )
        self.login_button.grid(row=6, column=0, pady=20)
        
        # Статус бар
        self.status_label = ttk.Label(
            self.root, 
            text="Готов к работе", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Привязка Enter для входа
        self.root.bind('<Return>', lambda e: self.start_login())
    
    def create_driver(self):
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
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Скрытие признаков автоматизации через JavaScript
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
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
        
        return driver
    
    def human_typing(self, element, text, delay_range=(0.05, 0.2)):
        """Эмуляция человеческого ввода текста с задержками"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
        # Небольшая пауза после ввода
        time.sleep(random.uniform(0.1, 0.3))
    
    def perform_login(self):
        """Выполнение авторизации через браузер"""
        login = self.login_entry.get().strip()
        password = self.password_entry.get()
        
        if not login:
            self.update_status("Ошибка: Введите логин")
            messagebox.showerror("Ошибка", "Введите логин или имя пользователя")
            return
        
        if not password:
            self.update_status("Ошибка: Введите пароль")
            messagebox.showerror("Ошибка", "Введите пароль")
            return
        
        self.update_status("Запуск браузера...")
        self.login_button.config(state=tk.DISABLED)
        
        try:
            # Создаем браузер
            self.driver = self.create_driver()
            wait = WebDriverWait(self.driver, 30)
            
            # Переход на страницу авторизации
            self.update_status("Переход на страницу авторизации...")
            self.driver.get(f"{self.base_url}/users/sign_in")
            
            # Ждем загрузки страницы
            wait.until(EC.presence_of_element_located((By.ID, "user_first_name")))
            
            # Небольшая случайная задержка перед вводом (как будто пользователь осматривает страницу)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Поиск полей ввода
            self.update_status("Ввод данных...")
            login_field = wait.until(EC.element_to_be_clickable((By.ID, "user_first_name")))
            password_field = self.driver.find_element(By.ID, "user_password")
            remember_checkbox = self.driver.find_element(By.ID, "user_remember_me")
            submit_button = self.driver.find_element(By.NAME, "commit")
            
            # Эмуляция человеческого ввода логина
            login_field.click()
            time.sleep(random.uniform(0.2, 0.5))
            self.human_typing(login_field, login)
            
            # Переход к полю пароля и ввод
            password_field.click()
            time.sleep(random.uniform(0.2, 0.5))
            self.human_typing(password_field, password)
            
            # Установка чекбокса "Запомнить меня" если нужно
            if self.remember_var.get():
                if not remember_checkbox.is_selected():
                    remember_checkbox.click()
                    time.sleep(random.uniform(0.1, 0.3))
            
            # Небольшая пауза перед отправкой формы
            time.sleep(random.uniform(0.3, 0.8))
            
            # Клик по кнопке входа
            self.update_status("Отправка формы...")
            submit_button.click()
            
            # Ждем результата (перенаправление или сообщение об ошибке)
            time.sleep(2)
            
            # Проверка результата
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Успешный вход - редирект на другую страницу или появление элементов личного кабинета
            if '/users/sign_in' not in current_url and 'выйти' in page_source or 'logout' in page_source:
                self.update_status("✓ Успешная авторизация!")
                messagebox.showinfo("Успех", "Авторизация выполнена успешно!\nБраузер открыт с вашей сессией.")
                
                # Если не нужно закрывать браузер, оставляем его открытым
                if not self.keep_browser_var.get():
                    time.sleep(3)
                    self.driver.quit()
                    self.driver = None
            else:
                # Проверка на ошибку авторизации
                if 'неверный' in page_source or 'ошибка' in page_source or 'логин' in page_source:
                    self.update_status("✗ Ошибка авторизации")
                    messagebox.showerror("Ошибка", "Неверный логин или пароль")
                else:
                    self.update_status("⚠ Требуется проверка")
                    messagebox.showwarning(
                        "Внимание", 
                        "Авторизация может не выполниться.\nПроверьте результат в браузере."
                    )
                
                # Закрываем браузер при ошибке
                if not self.keep_browser_var.get():
                    time.sleep(2)
                    self.driver.quit()
                    self.driver = None
                    
        except TimeoutException:
            self.update_status("Ошибка: Превышено время ожидания")
            messagebox.showerror(
                "Ошибка", 
                "Превышено время ожидания ответа от сервера.\nПроверьте подключение к интернету."
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
        except WebDriverException as e:
            self.update_status(f"Ошибка браузера: {str(e)}")
            messagebox.showerror(
                "Ошибка браузера", 
                f"Не удалось запустить браузер.\nУбедитесь, что Chrome установлен.\n\nДетали: {str(e)}"
            )
            if self.driver:
                self.driver.quit()
                self.driver = None
        except Exception as e:
            self.update_status(f"Ошибка: {str(e)}")
            messagebox.showerror("Ошибка", str(e))
            if self.driver:
                self.driver.quit()
                self.driver = None
        finally:
            self.login_button.config(state=tk.NORMAL)
    
    def start_login(self):
        """Запуск авторизации в отдельном потоке"""
        thread = threading.Thread(target=self.perform_login, daemon=True)
        thread.start()
    
    def update_status(self, message):
        """Обновление статуса в главном потоке"""
        self.root.after(0, lambda: self.status_label.config(text=message))


def main():
    root = tk.Tk()
    
    # Установка иконки (если есть)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = AuthApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
