from playwright.sync_api import sync_playwright

# Укажите ваши данные
LOGIN_URL = "http://school65.ru/login"
TARGET_URL = "https://example.com/download/file.pdf"  # Ссылка, по которой начинается скачивание
USERNAME = "seggiy@mail.ru"
PASSWORD = "School6565"
DOWNLOAD_PATH = r"C:\Downloads"  # Папка для сохранения

with sync_playwright() as p:
    # 1. Запускаем браузер (headless=False, чтобы видеть процесс)
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True,  # Разрешаем скачивание
                                  downloads_path=DOWNLOAD_PATH)
    page = context.new_page()

    # 2. АВТОРИЗАЦИЯ
    page.goto(LOGIN_URL)
    page.fill("#login", USERNAME)      # Замените #username на ваш селектор
    page.fill("#pwd", PASSWORD)      # Замените #password на ваш селектор
    page.click("#loginButton")   # Нажимаем на кнопку входа

    # Важно: Явно ждем перехода на страницу после успешного входа
    # Убедитесь, что URL изменился или появился какой-то уникальный элемент
    page.wait_for_url("**/dashboard**", timeout=10000)  # Ждем URL с панелью управления
    print("✅ Авторизация успешна!")

    # 3. ПЕРЕХОД ПО ССЫЛКЕ И СОХРАНЕНИЕ ФАЙЛА
    # Начинаем "слушать" событие скачивания ДО того, как мы кликнем по ссылке
    with page.expect_download() as download_info:
        page.goto(TARGET_URL)  # Или page.click("a.download-link")

    # После завершения загрузки получаем объект файла
    download = download_info.value
    # Сохраняем файл в нужную папку с оригинальным или новым именем
    download.save_as(f"{DOWNLOAD_PATH}/{download.suggested_filename}")
    print(f"✅ Файл сохранен: {download.suggested_filename}")

    # Закрываем браузер
    browser.close()