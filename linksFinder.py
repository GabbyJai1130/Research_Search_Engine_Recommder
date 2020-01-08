import requests
from bs4 import BeautifulSoup
import json
import re


class linksFinder:

    def __init__(self):
        self.base_url = ''
        self.url = ''
        self.headers = {}
        self.restaurants_links = []
        self.restaurants_info = []

    def get_url(self, base_url, url, headers):
        self.base_url = base_url
        self.url = url
        self.headers = headers

    def get_links(self, start_num, end_num):

        for i in range(start_num, end_num):
            link = self.url + str(i)
            request = requests.get(link, headers=self.headers)
            soup = BeautifulSoup(request.text, 'lxml')

            for h2tag in soup.findAll('h2'):
                for atag in h2tag.findAll('a'):
                    link_tail = atag.get('href')
                    full_link = self.base_url + link_tail

                    self.restaurants_links.append(full_link)

        return print('Scraping done!')

    def save_links(self):
        with open('restaurants_links.txt', 'w') as output_file:
            for link in self.restaurants_links:
                output_file.write(link + '\n')

    def get_restaurants_info(self):
        for link in self.restaurants_links:
            request = requests.get(link, headers=self.headers)
            soup = BeautifulSoup(request.text, 'lxml')

            name = soup.find('div', {'class': 'poi-name'}).find('span').get_text()
            cuisine = soup.find('div', {'class': 'header-poi-categories dot-separator'}).get_text().strip().split('\n')
            rating = soup.find('div', {'class': 'header-score'}).get_text()
            rating = float(rating)

            bookmark = soup.find('div', {'class': 'header-bookmark-count js-header-bookmark-count'}).get_text()
            bookmark = int(bookmark)

            address = soup.find('div', {'class': 'content'}).find('a').get_text().strip()
            district = soup.find('div', {'class': 'header-poi-district dot-separator'}).get_text().split('\n')[1]

            price = soup.find('div', {'class': 'header-poi-price dot-separator'}).get_text().strip()

            review = soup.find('div', {'class': 'main-menu table-center'}).find_all('a', href=True)[1].get_text()
            review_count = re.search(r'\d+', review).group()
            review_count = int(review_count)

            happy = soup.find('div', {'class': 'header-smile-section'}).get_text().split('\n')[2]
            happy = int(happy)
            okay = soup.find('div', {'class': 'header-smile-section'}).get_text().split('\n')[4]
            okay = int(okay)
            sad = soup.find('div', {'class': 'header-smile-section'}).get_text().split('\n')[6]
            sad = int(sad)

            all_items = soup.find_all('div', {'class': 'condition-item'})
            condition_item_avail = []
            for item in all_items:
                check_class = item.find('span').get('class')[1]
                condition = item.find('span', {'class': 'condition-name'}).get_text()
                if check_class == 'd_sr2_lhs_tick_desktop':
                    condition_item_avail.append(condition)

            info = {
                "name": name,
                "cuisine": cuisine,
                "rating": rating,
                "bookmark": bookmark,
                "price-range": price,
                "address": address,
                "district": district,
                "review_count": review_count,
                "review_happy": happy,
                "review_okay": okay,
                "review_sad": sad,
                "available_condition": condition_item_avail
            }

            self.restaurants_info.append(info)

        return print('all restaurant info is scraped!')

    def save_json(self):

        with open('restaurants_info.json', 'w') as file:
            json.dump(self.restaurants_info, file, indent=4, separators=(',', ':'))

        return print('the json file is saved!')
