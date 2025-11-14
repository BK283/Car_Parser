from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import  BeautifulSoup
import csv
import requests
import time


def fill_input_price(driver,price_from,price_to):
    input_price_from = driver.find_element("xpath", "//input[@id='price[from]']")
    input_price_from.click()
    input_price_from.send_keys(price_from)
    input_price_to = driver.find_element("xpath", "//input[@id='price[to]']")
    input_price_to.click()
    input_price_to.send_keys(price_to)

    show_button2 = driver.find_element("xpath", "//button[@data-test]")
    show_button2.click()


def select_city(driver,town,cities):
    if town in cities:
        city_element = driver.find_element("xpath", f"//span[text()='{town}']")
        city_element.click()
    else:
        wait = WebDriverWait(driver,10)
        label = wait.until(EC.element_to_be_clickable(("xpath", "//label[@class='group-label']")))
        label.click()

        wait.until(EC.visibility_of_element_located(("xpath", "//div[@data-name='region-other']")))

        city_element = wait.until(
            EC.element_to_be_clickable(("xpath", f"//span[@class='action-link' and @data-value='{town}']"))
        )
        city_element.click()


def parse_cars(html_content):
    soup = BeautifulSoup(html_content, "lxml")

    list_of_new_cars = soup.find("ul", class_="models-list").find_all("li", class_="models-list__item")
    amount_el = soup.select_one("div.container div#results div.result-block__controls p")
    amount_cars = amount_el.get_text(strip=True) if amount_el else "Количество неизвестно"
    new_cars = []

    for car in list_of_new_cars:
        try:
            mark = car.find("h5").text
        except:
            mark = "Марка не найдена"
        try:
            model = car.find("p", class_="model-card__trims").text
        except:
            model = "Модель не найдена"
        try:
            price = car.find("p", class_="model-card__price").text
            clean_price = " ".join(price.split())
        except Exception:
            clean_price = "Цена не найдена"

        try:

            features_car = car.find("ul", class_="model-card__features").find_all("li")
        except:
            features_car = "Особенности не найдены"
        try:
            img_tag = car.select_one("div.thumb-gallery.js__thumb-gallery img")
            if img_tag and img_tag.has_attr('src'):
                img_car = img_tag['src']
            else:
                img_car = "Фотка не найдена"
        except Exception:
            img_car = "Фотка не найдена"

        try:
            link = car.find("a", class_="model-card__link").get("href")
        except:
            link = "Ссылка не найдена"


        final = {
            "Марка": mark.strip(),
            "Цена": clean_price.strip(),
            "Особенности Машины": " ".join([i.text for i in features_car]) if isinstance(features_car, list) else "",
            "Подробнее": "https://kolesa.kz" + link
            }


        
        new_cars.append(final)
    return new_cars


def start1(price1,price2,town):
    
    try:
        cities = ["Астана", "Павлодар", "Шымкент", "Костанай", "Караганда"]

        driver = webdriver.Chrome()
        driver.get("https://kolesa.kz/cars/new/")
        select_city(driver, town, cities)
        fill_input_price(driver, price1, price2)
        time.sleep(3)

        wait = WebDriverWait(driver, 10)
        try:
            pages = driver.find_element("xpath", "//div[@class='pager']")
            ul = pages.find_element("xpath", ".//ul")
            list_page = ul.find_elements("xpath", "./li")
            page_final = int(list_page[-1].text)

        except:
            page_final = 1
            list_page = []
            print("Обрабатывается одна страница")

        with open("cars.csv","w",encoding="utf-8") as file:
            fieldsnames = ["Марка","Цена","Особенности Машины","Подробнее"]
            writer = csv.DictWriter(file,fieldnames=fieldsnames)
            writer.writeheader()
        
            for i in range(1,page_final+1):
                if i == 1:
                    new_url = driver.current_url
                else:
                    new_url = f"{driver.current_url}?page={i}"


                driver.get(new_url)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "models-list")))

                html_content = driver.page_source
                result = parse_cars(html_content)

                with open("cars.csv","a",encoding="utf-8") as file:
                    
                    for row in result:
                        writer.writerow(row)
                    

                

    except Exception as e:
        print(f"Ошибка при работе с URL {e}")

    finally:
        driver.quit()





cities = [
    "Актау","Актобе","Алматы","Астана","Атырау","Жанаозен","Жезказган",
    "Караганда","Кокшетау","Костанай","Кызылорда","Павлодар","Петропавловск",
    "Сарыагаш","Семей","Талдыкорган","Тараз","Туркестан","Уральск","Усть-Каменогорск","Шымкент"
]

for i, city in enumerate(cities, 1):
    print(f"{i} - {city}")


while True:
    try:
        town = int(input("Выберите город по номеру для поиска новой машины: "))
        if not 1 <= town <= len(cities):
            raise ValueError("Неверный номер города")
            continue
    except ValueError:
        print("Пожалуйста выберите корректный номер города от 1 до", len(cities))
        continue

    try:
        p1 = int(input("Введите цену от (минимум 5 000 000): "))
        p2 = int(input("Введите цену до (максимум 167 000 000): "))
        if p1 > p2:
            print("Минимальная цена не может быть больше максимальной.")
            continue
    except ValueError:
        print("Пожалуйста введите корректные числовые значения")
        continue

    start1(p1, p2, cities[town-1])
    print("Данные успешно загружены!")
    break

























