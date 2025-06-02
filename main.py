import requests
import feedparser
from datetime import datetime, timedelta
import time
import os
import json


OUTPUT_DIR = './arxiv_metadata'  # Директория для сохранения файлов
CATEGORY = 'cs.AI'  # Категория статей
MAX_RESULTS_PER_REQUEST = 1000  # Максимум статей на запрос (до 300000)
DELAY_BETWEEN_REQUESTS = 4  # Задержка между запросами (сек)
LOOKBACK_DAYS = 90  # Количество дней для выгрузки (3 месяца)


os.makedirs(OUTPUT_DIR, exist_ok=True)


end_date = datetime.today()


for day_offset in range(LOOKBACK_DAYS):
    current_date = end_date - timedelta(days=day_offset)
    date_str = current_date.strftime('%Y%m%d')


    time_start = f"{date_str}000000"
    time_end = f"{date_str}235959"


    search_query = (
        f'submittedDate:[{time_start} TO {time_end}] '
        f'AND cat:{CATEGORY}'
    ).replace(' ', '+')

    start_index = 0
    all_entries = []


    while True:

        url = (
            f'http://export.arxiv.org/api/query?'
            f'search_query={search_query}'
            f'&start={start_index}'
            f'&max_results={MAX_RESULTS_PER_REQUEST}'
        )


        response = requests.get(url)


        if response.status_code != 200:
            print(f'Ошибка {response.status_code} для {current_date.date()}')
            break


        feed = feedparser.parse(response.content)


        if not feed.entries:
            break


        all_entries.extend(feed.entries)


        total_results = int(feed.feed.get('opensearch_totalresults', 0))
        start_index += len(feed.entries)

        if start_index >= total_results:
            break

        time.sleep(DELAY_BETWEEN_REQUESTS)


    processed_entries = []
    for entry in all_entries:

        authors = [author.name for author in entry.get('authors', [])]


        published = entry.get('published', '')


        pdf_link = next(
            (link.href for link in entry.get('links', [])
             if link.type == 'application/pdf'),
            None
        )

        processed_entries.append({
            'title': entry.get('title', ''),
            'authors': authors,
            'published': published,
            'pdf_link': pdf_link
        })


    if processed_entries:
        filename = f"{current_date.strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_entries, f, indent=2, ensure_ascii=False)

        print(f'Saved {len(processed_entries)} entries for {filename}')
    else:
        print(f'No entries for {current_date.strftime("%Y-%m-%d")}')

    time.sleep(DELAY_BETWEEN_REQUESTS)
