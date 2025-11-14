import asyncio
import csv
import random
import time
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


# Список возможных User-Agent для рандомизации
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0"
]

# Список языков для Accept-Language
ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
]

SENTIMENT_MAPPING = {
    'positiv': 'positive',
    'negativ': 'negative',
    'neutral': 'neutral'
}

async def scrape_reviews():

    proxy = None

    user_agent = random.choice(USER_AGENTS)
    accept_language = random.choice(ACCEPT_LANGUAGES)

    all_reviews = []

    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=False,
            proxy=proxy
        )
        context = await browser.new_context(
            user_agent=user_agent,
            extra_http_headers={
                "Accept-Language": accept_language
            }
        )

        page = await context.new_page()

        base_url = "https://www.airlines-inform.ru/about_airline/s7_airlines/"

        try:
            print(f"Открываю первую страницу: {base_url}")
            await page.goto(base_url, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(5, 10))

            print("Получаю список всех страниц навигации...")
            await page.wait_for_selector('.navpages a[onclick*="loadPage20"]', timeout=10000)
            page_links = await page.locator('.navpages a[onclick*="loadPage20"]').all()
            urls_to_visit = []
            for link in page_links:
                href = await link.get_attribute('href')
                if href:
                    full_url = f"https://www.airlines-inform.ru{href}"
                    if full_url not in urls_to_visit:
                        urls_to_visit.append(full_url)

            print(f"Найдено {len(urls_to_visit)} страниц для посещения.")

            # --- Цикл по всем найденным URL ---
            for i, url in enumerate(urls_to_visit):
                print(f"Обрабатываю страницу {i+1}/{len(urls_to_visit)}: {url}")

                await page.wait_for_selector('.message_forum', timeout=10000)
                
                forum_containers = await page.locator('.message_forum').all()

                if not forum_containers:
                    print(f"  Предупреждение: Контейнеры отзывов (.message_forum) не найдены на странице {url}")
                    continue

                page_reviews = []
                for container in forum_containers:
                    try:

                        text_element = container.locator('[id*="message_text_"]')
                        text_content = await text_element.text_content()
                        text_content = text_content.strip() if text_content else ''

                        data_element = container.locator('.forum_data')
                        class_attr = await data_element.get_attribute('class')
                        if not class_attr:
                            print(f"    Предупреждение: Элемент .forum_data не имеет атрибута class, пропуск.")
                            continue

                        classes = class_attr.split()
                        sentiment = 'unknown'
                        for cls in classes:
                            if cls in SENTIMENT_MAPPING:
                                sentiment = SENTIMENT_MAPPING[cls]
                                break
                        
                        if sentiment == 'unknown':
                             print(f"    Предупреждение: Сентимент не найден в классах '{class_attr}', пропуск.")
                             continue

                        if text_content:
                            page_reviews.append({'text': text_content, 'sentiment': sentiment})
                        else:
                            print(f"    Предупреждение: Текст отзыва пуст, пропуск. Сентимент: {sentiment}")

                    except Exception as e:
                        print(f"  Ошибка при извлечении данных из контейнера на {url}: {e}")
                        continue

                print(f"  Найдено {len(page_reviews)} отзывов с сентиментом на этой странице.")
                all_reviews.extend(page_reviews)

        except Exception as e:
            print(f"Произошла ошибка при работе с браузером: {e}")

        finally:
            await browser.close()

    if all_reviews:
        filename = 's7_airlines_reviews_with_sentiment.csv'
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Review', 'Sentiment'])
                for review_data in all_reviews:
                    writer.writerow([review_data['text'], review_data['sentiment']])
            print(f"\n---\nВсе отзывы ({len(all_reviews)} шт.) успешно сохранены в файл {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении CSV: {e}")
    else:
        print("\n---\nНе удалось извлечь ни одного отзыва.")


if __name__ == "__main__":
    asyncio.run(scrape_reviews())