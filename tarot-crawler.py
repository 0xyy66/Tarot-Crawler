import httpx
from bs4 import BeautifulSoup
import json


'''
{
    majorarcana:
        [
            {
                card:
                short_info:
                    upright:
                    reversed:
                    description:
                info:
                    upright:
                    reversed:
            }
        ]
    minorarcana:
        {
            Wands:
                [
                    {
                        card:
                        short_info:
                            {
                                upright:
                                reversed:
                                description:
                            }
                        info:
                            {
                                upright:
                                reversed:
                            }
                    }

                ]
            ...
        }
}
'''

def get_major_arcana_urls(client):
    base_url = 'https://www.biddytarot.com'
    res = client.get(base_url + '/tarot-card-meanings/major-arcana/')
    print('[x] Major Arcana scraping')
    soup = BeautifulSoup(res.text, 'html.parser')
    a_tags = soup.find_all('a')
    urls = []
    for a in a_tags:
        if 'major-arcana' in a['href']:
            urls.append(base_url + a['href'])
    return urls

def get_minor_arcana_urls(client, seed):
    base_url = 'https://www.biddytarot.com'
    res = client.get(base_url + f'/tarot-card-meanings/minor-arcana/suit-of-{seed}/')
    print('[x] Minor Arcana scraping')
    soup = BeautifulSoup(res.text, 'html.parser')
    a_tags = soup.find_all('a')
    urls = []
    for a in a_tags:
        if 'minor-arcana' in a['href']:
            if base_url not in a['href']:
                urls.append(base_url + a['href'])
            else:
                urls.append(a['href'])
    del urls[0]
    return urls

def get_major_arcana_info(client, urls):
    MajorArcana = []
    for url in urls:
        res = client.get(url)
        print(f'[x] MA - {url.split("/")[-2]} scraping')
        soup = BeautifulSoup(res.text, 'html.parser')
        mobhide = soup.find_all('div', {'class': 'mobilehide'})
        card_name = mobhide[0].find('h3').contents[0].replace('Keywords', '')
        short_info = mobhide[0].find_all('p')
        card = {
            'card': card_name,
            'short_info':
                {
                    'upright': '',
                    'reversed': '',
                    'description': ''
                },
            'info':
                {
                    'upright': '',
                    'reversed': ''
                }
        }
        for p in short_info:
            if 'UPRIGHT:' in str(p):
                card['short_info']['upright'] = ((str(p)).split('</span>')[1].split('</p>')[0]).strip()
            elif 'REVERSED:' in str(p):
                card['short_info']['reversed'] = ((str(p)).split('</span>')[1].split('</p>')[0]).strip()
            elif 'NOTE:' not in p:
                card['short_info']['description'] += p.contents[0].strip() + ' '
        post_area = soup.find_all('div', {'class': 'row'})
        for p in post_area[4].find_all('p'):
            card['info']['upright'] += p.contents[0].strip() + ' '
        for p in post_area[5].find_all('p'):
            card['info']['reversed'] += p.contents[0].strip() + ' '
        # remove space at the end
        card['short_info']['description'] = card['short_info']['description'].strip()
        card['info']['upright'] = card['info']['upright'].strip()
        card['info']['reversed'] = card['info']['reversed'].strip()
        MajorArcana.append(card)
    return MajorArcana

def get_minor_arcana_info(client, urls, seed):
    suit_of_seed = []
    for url in urls:
        res = client.get(url)
        print(f'[x] ma - {seed} - {url.split("/")[-2]} scraping')
        soup = BeautifulSoup(res.text, 'html.parser')
        mobhide = soup.find_all('div', {'class': 'mobilehide'})
        card_name = mobhide[0].find('h3').contents[0].replace('Keywords', '')
        short_info = mobhide[0].find_all('p')
        card = {
            'card': card_name,
            'short_info':
                {
                    'upright': '',
                    'reversed': '',
                    'description': ''
                },
            'info':
                {
                    'upright': '',
                    'reversed': ''
                }
        }
        for p in short_info:
            if 'UPRIGHT:' in str(p):
                card['short_info']['upright'] = ((str(p)).split('</span>')[1].split('</p>')[0]).strip()
            elif 'REVERSED:' in str(p):
                card['short_info']['reversed'] = ((str(p)).split('</span>')[1].split('</p>')[0]).strip()
            elif 'NOTE:' not in p:
                card['short_info']['description'] += p.contents[0].strip() + ' '
        post_area = soup.find_all('div', {'class': 'row'})
        for p in post_area[4].find_all('p'):
            card['info']['upright'] += p.contents[0].strip() + ' '
        for p in post_area[5].find_all('p'):
            card['info']['reversed'] += p.contents[0].strip() + ' '
        # remove space at the end
        card['short_info']['description'] = card['short_info']['description'].strip()
        card['info']['upright'] = card['info']['upright'].strip()
        card['info']['reversed'] = card['info']['reversed'].strip()
        suit_of_seed.append(card)
    return suit_of_seed

if __name__ == '__main__':
    client = httpx.Client()
    client.headers = {
        "User-Agent": "Tarot Crawler. Source code on GitHub soon!"
    }
    MA_urls = get_major_arcana_urls(client)
    MajorArcana = get_major_arcana_info(client, MA_urls)
    minorArcana = {}
    ma_urls = get_minor_arcana_urls(client, seed='cups')
    minorArcana['cups'] = get_minor_arcana_info(client, ma_urls, seed='cups')
    ma_urls = get_minor_arcana_urls(client, seed='swords')
    minorArcana['swords'] = get_minor_arcana_info(client, ma_urls, seed='swords')
    ma_urls = get_minor_arcana_urls(client, seed='pentacles')
    minorArcana['pentacles'] = get_minor_arcana_info(client, ma_urls, seed='pentacles')
    ma_urls = get_minor_arcana_urls(client, seed='wands')
    minorArcana['wands'] = get_minor_arcana_info(client, ma_urls, seed='wands')
    deck = {
        "major_arcana": MajorArcana,
        "minor_arcana": minorArcana 
    }
    with open('tarot_deck.json', 'w') as f:
        json.dump(deck, f)


