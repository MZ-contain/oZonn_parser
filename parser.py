from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import os
import csv
import traceback
from pyfiglet import Figlet
preview_text = Figlet(font='jazmine')
print(preview_text.renderText('Serkilo')) 
keywords = input("Введите ключевые слова: ").split()

# в переменную SELLER вписать название продавца в кавычках, оно будет выделено зеленым!
SELLER = "GLS Pharmaceuticals"

# Время загрузки страницы. Можно увеличить, если будут ошибки, уменьшать НЕ РЕКОМЕНДУЕТСЯ!
SLEEP_TIME = 7

# Страница, с которой начинать поиск
START_PAGE = 1

# Максимально число предметов
MAX_ITEMS = 10

class Parse:

	def __init__(self, URL, SELLER, SLEEP_TIME, START_PAGE):
		
		path_dir = os.path.dirname(os.path.abspath(__file__))

		if 'ozon.ru' in URL or 'wildberries.ru' in URL:
			self.URL = URL
			if SELLER:
				self.SELLER = SELLER.lower()
				self.SLEEP_TIME = SLEEP_TIME
				self.START_PAGE = START_PAGE
				if not type(SLEEP_TIME) == int:
					raise "В переменную SLEEP_TIME Нужно вставить целое число без кавычек!"

				if 'wildberries.ru' in URL:
					self.platform = 'wb'
				elif 'ozon.ru' in URL:
					self.platform = 'ozon'

				driver_url = path_dir + "/chromedriver.exe"
				self.driver = webdriver.Chrome(executable_path=driver_url)
			else:
				self.SELLER = ""
		else:
			raise "Парсер предназначен только для ozon.ru и wildberries.ru"
		self.result = []
		

	def open_page(self, page=1):
		if not 'page' in self.URL:
			if self.platform == 'ozon':
				URL = self.URL.replace("&text", f"&page={page}&text")
			else:
				URL = self.URL.replace("&search", f"&page={page}&search")
			sleep(3)
			self.driver.get(URL)
			for i in range(self.SLEEP_TIME):
				os.system('cls')
				print(f"Open Page {page}", '.' * i)
				sleep(1)
			return {"source": self.driver.page_source, 'url': URL, 'page': page}
		else:
			raise "Вставьте ссылку с первой страницы"

	def open_tab(self, tab, page):
		self.driver.execute_script(f"window.open('https://www.wildberries.ru{tab}','_blank');")
		main_tab = self.driver.window_handles[0]
		new_tab = self.driver.window_handles[1]
		self.driver.switch_to.window(new_tab)
		class_ = "seller__content"
		page_soup = BeautifulSoup(self.driver.page_source)
		block = page_soup.find('p', class_=class_)
		if block is not None:
			text = block.get_text(strip=True)
			if self.SELLER in text.lower():
				self.result.append(
					{'url': f'https://www.wildberries.ru{tab}', 'page': page}
					)
				print(f"Найдено совпадение на странице {page}\nСсылка: https://www.wildberries.ru{tab}")
			status = True
		else:
			status = False
			print("BLOCK NONE")
		self.driver.close()
		self.driver.switch_to.window(main_tab)
		sleep(self.SLEEP_TIME-SLEEP_TIME/2)
		return status
		

	def parse(self,):
		page = START_PAGE - 1
		need_find = True
		have_error = False
		while need_find:
			page += 1
			html = self.open_page(page)
			soup = BeautifulSoup(html['source'], 'lxml')
			if self.platform == 'ozon':
				
				items = soup.findAll('div', class_='n4i ni5')
				if items == []:
					items = soup.findAll('div', class_='n4i i5n')
				
				if items != []:
					for item in items:
						try:
							try:
								price = item.find('span', class_="ui-t0 ui-s7")
								price = price.get_text(strip=True)
							except:
								continue
       
							name = item.find('span', class_="c9z z9c dd0 d3d tsBodyL li9")
							name = name.get_text(strip=True)
       
							block = item.find('span', class_="c9z z9c dd d5d tsBodyM ni")
							if block is not None:
								text = block.get_text(strip=True)
								text = text.split(", продавец ")
								if len(text) < 2:
									continue
								self.result.append(
									{'Цена': price, 'Название': name, "Бренд": text[1]}
									)
								if len(self.result) > MAX_ITEMS:
									need_find = False
									break
							else:
								print("block NONE:", block)
						except Exception as e:
							os.system('cls')
							need_find = False
							have_error = True
							print(traceback.format_exc())

				else:
					need_find = False

			elif self.platform == 'wb':
				items = soup.findAll('div', class_='product-card j-card-item')
				if items != []:
					tabs = []
					for item in items:
						try:
							tab = item.find('a').get('href')
							tabs.append(tab)
						except:
							os.system('cls')
							need_find = False
							have_error = True
							print(traceback.format_exc())
					for tab in tabs:
						while not self.open_tab(tab, page):
							pass
				else:
					need_find = False
		if self.result:
			return self.result
		else:
			print("*" * 50)
			print("Совпадений не найдено. Попробуйте увеличить значение SLEEP_TIME через несколько минут.")
			print("!" * 50)
			print(traceback.format_exc())
		if have_error:
			print("*" * 50)
			print(f"Возникла ошибка. Обработано {page - 1} Страниц\n\nЗапустите скрипт с этой страницы через несколько минут")
			print("!" * 50)
		else:
			print("Ошибок не возникло, пройдены все страницы :)")

if __name__ == '__main__':
    
	parser = Parse("https://www.ozon.ru/search/?text={keywords[0]}&from_global=true", SELLER, SLEEP_TIME, START_PAGE)
	
	results = {}
	for keyword in keywords:
		url = f"https://www.ozon.ru/search/?text={keyword}&from_global=true"
		parser.URL = url
		results[keyword]=parser.parse()

	parser.driver.close()
	row_names = ["Запрос","Бренд","Название","Цена"]
	with open("file.csv", "w", encoding="utf-8") as file:
		writer = csv.DictWriter(file, fieldnames=row_names)
		wr = csv.writer(file, delimiter=',', dialect='excel')
		writer.writeheader()

		for result in results:
			for res in results[result]:
				res["Запрос"] = result
				writer.writerow(res)
			wr.writerow("\n")
