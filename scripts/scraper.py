```python
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import warnings
import os

# Игнорируем предупреждения
warnings.filterwarnings('ignore')

# Создаем директорию для сохранения графиков, если она не существует
os.makedirs("plots", exist_ok=True)

def get_driver():
    """Функция для настройки и запуска веб-драйвера."""
    options = ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")  # Запуск в фоновом режиме; уберите это для отладки
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return Chrome(options=options)

def parse_local_matches(context_element):
    """Функция для парсинга локальных матчей из элемента контекста."""
    match_data = []  # Список для хранения данных матчей
    local_teams = context_element.find_elements(By.CSS_SELECTOR, '.eOSe1-7e2ea15e')
    local_odds = context_element.find_elements(By.CSS_SELECTOR, '.do7iP-7e2ea15e')

    teams = [el.text.strip() for el in local_teams if el.text.strip()]
    odds = []

    # Извлечение коэффициентов и их преобразование
    for el in local_odds:
        text = el.text.strip().replace(',', '.').replace('+', '').strip()
        if text.replace('.', '', 1).isdigit() and len(text) <= 6:
            odds.append(text)

    # Формирование данных для каждого матча
    for j in range(0, len(teams) - 1, 2):
        if (j // 2) * 3 + 2 >= len(odds):  # Проверка на количество коэффициентов
            continue
        p1, draw, p2 = odds[(j // 2) * 3: (j // 2) * 3 + 3]
        if all([p1, draw, p2]):  # Проверка наличия всех коэффициентов
            match_data.append({
                'team1': teams[j],
                'team2': teams[j + 1],
                'coeff_win1': float(p1),
                'coeff_draw': float(draw),
                'coeff_win2': float(p2),
                'sport': 'football',
                'timestamp': pd.Timestamp.now()  # Текущая дата и время
            })
    return match_data

def scrape_betboom():
    """Основная функция для сканирования сайта BetBoom и извлечения данных."""
    driver = get_driver()  # Получаем драйвер
    url = "https://betboom.ru/sport/football"  # URL для парсинга
    driver.get(url)
    time.sleep(5)  # Ждем загрузки страницы

    # Прокручиваем страницу вниз
    for _ in range(4):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)

    match_data = []  # Список для хранения данных всех матчей
    match_data.extend(parse_local_matches(driver))  # Парсим локальные матчи

    match_buttons = driver.find_elements(By.CSS_SELECTOR, '.nFgMI-7e2ea15e')
    print(f"\nНайдено блоков для раскрытия: {len(match_buttons)}")

    for i, btn in enumerate(match_buttons[1:], start=2):
        try:
            print(f"Обработка блока #{i}")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.2)
            btn.click()  # Кликаем по блоку для раскрытия коэффициентов
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.eOSe1-7e2ea15e'))
            )
            container = btn.find_element(By.XPATH, './..')  # Находим контейнер для данных
            block_data = parse_local_matches(container)  # Парсим данные блока
            match_data.extend(block_data)  # Добавляем данные в общий список
        except Exception as e:
            print(f"Проблема с блоком #{i}: {e}")
            continue

    try:
        driver.quit()  # Закрываем драйвер
    except:
        pass

    # Сохраняем данные в DataFrame и в CSV файл
    df = pd.DataFrame(match_data)
    df.drop_duplicates(inplace=True)  # Удаляем дубликаты
    df.to_csv("winline_data_clean.csv", index=False)
    return df

# Запускаем функцию для сбора данных
df = scrape_betboom()
