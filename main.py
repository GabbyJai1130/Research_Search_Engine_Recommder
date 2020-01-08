from linksFinder import linksFinder
from serachEngine import searchEngine

if __name__ == "__main__":
    headers = {
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'cache-control': 'max-age=0',
    }

    url = 'https://www.openrice.com/en/hongkong/restaurants?page='
    base_url = 'https://www.openrice.com'

    Finder = linksFinder()

    Finder.get_url(base_url, url, headers)
    Finder.get_links(start_num=1, end_num=5)

    Finder.save_links()
    Finder.get_restaurants_info()
    Finder.save_json()

    engine = searchEngine()
    engine.get_json('restaurants_info.json')

    # Demo
    results = engine.search({'country': 'Japanese',
                             'avail_cond': ['Online Reservation', 'Alcoholic Drinks', 'Phone Reservation']})

    df_sim_results = engine.top_N_similar('FireBird', None, 3)