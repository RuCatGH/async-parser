import time
from bs4 import BeautifulSoup
import csv
import asyncio
import aiohttp


books_data = []

async def get_page_data(session, page):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36 OPR/88.0.4412.65"
    }
   
    
    url = f"https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table&page={page}"

    async with session.get(url=url,headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')

        books_items = soup.find("tbody", class_="products-table__body").find_all("tr")

        for bi in books_items:
            book_data = bi.find_all("td")

            try:
                book_title = book_data[0].find("a").text.strip()
            except:
                book_title = "Нет названия книги"

            try:
                book_author = book_data[1].text.strip()
            except:
                book_author = "Нет автора"

            try:
                # book_publishing = book_data[2].text
                book_publishing = book_data[2].find_all("a")
                book_publishing = ":".join([bp.text for bp in book_publishing])
            except:
                book_publishing = "Нет издательства"

            try:
                book_new_price = int(book_data[3].find("div", class_="price").find("span").find("span").text.strip().replace(" ", ""))
            except:
                book_new_price = "Нет нового прайса"

            try:
                book_old_price = int(book_data[3].find("span", class_="price-gray").text.strip().replace(" ", ""))
            except:
                book_old_price = "Нет старого прайса"

            try:
                book_sale = round(((book_old_price - book_new_price) / book_old_price) * 100)
            except:
                book_sale = "Нет скидки"

            try:
                book_status = book_data[-1].text.strip()
            except:
                book_status = "Нет статуса"
            books_data.append(
                    {
                        "book_title": book_title,
                        "book_author": book_author,
                        "book_publishing": book_publishing,
                        "book_new_price": book_new_price,
                        "book_old_price": book_old_price,
                        "book_sale": book_sale,
                        "book_status": book_status
                    }
                )
    print(f"Обработана {page}")

            

async def gather_data():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }
    url = "https://www.labirint.ru/genres/2308/?available=1&paperbooks=1&display=table"

    async  with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), "lxml")

        pages_count = int(soup.find("div", class_="pagination-numbers").find_all("a")[-1].text)
        tasks = []

        for page in range(1, pages_count +1):
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)

def main():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start_time = time.time()
    asyncio.run(gather_data())
    with open(f"labirint.csv", "w", encoding='utf-8', newline='') as file:
        writer = csv.writer(file, delimiter=';')

        writer.writerow(
            (
                "Название книги",
                "Автор",
                "Издательство",
                "Цена со скидкой",
                "Цена без скидки",
                "Процент скидки",
                "Наличие на складе"
            )
        )
        for book in books_data:

            with open(f"labirint.csv", "a", encoding='utf-8', newline='') as file:
                writer = csv.writer(file, delimiter=';')

                writer.writerow(
                    (
                        book["book_title"],
                        book["book_author"],
                        book["book_publishing"],
                        book["book_new_price"],
                        book["book_old_price"],
                        book["book_sale"],
                        book["book_status"]
                    )
                )
    finish_time = time.time() - start_time

    print(f"Затраченное на работу скрипта время: {finish_time}")
if __name__ == '__main__':
    main()

