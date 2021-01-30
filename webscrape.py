import os
import re
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup

def get_title():
    # Return Title and episode number as tup

    full_title = soup.find('a', {'class': "journal-entry-navigation-current"}).contents[0]
    start_ind = full_title.find('-')

    has_num = False
    for char in full_title:
        if char.isdigit():
            has_num = True
            break
    if not has_num:
        return -1, -1

    if start_ind == -1:
        start_ind = full_title.find(':')
    elif full_title.find(':') != -1 and full_title.find(':') < start_ind:
        start_ind = full_title.find(':')
        
    start_ind += 2

    ep_num = re.findall(r'\d+', full_title)[0]

    return "Episode " + ep_num + ' - ' + full_title[start_ind:], int(ep_num)

def get_mp3():
    links = soup.find_all('a', href=True)
    mp3_link = ''
    for link in links:
        if ".mp3" in link.get('href'):
            mp3_link = link.get('href')

    if not mp3_link:
        print("Could not find mp3 for ", get_title())

    return urlopen(mp3_link).read()
    
def get_ep_list():
    host = "http://rationallyspeakingpodcast.org"

    # Find and compile all episode links
    eps = [host + link.get('href') for link in soup.find_all('a') if link.get('href')[:6] == '/show/']
    return eps

def last_downloaded():
    dir = os.listdir()

    # Find the largest number in all the filenames
    ep_nums = [int(re.findall(r'\d+', f)[0]) for f in dir if len(re.findall(r'\d+', f)) > 0]
    last_downloaded = max(ep_nums)
    
    return last_downloaded

def clean_title(title):
    # Clean title of any restricted chars for filenames

    title = title.replace(u'\xa0', u' ')

    restricted_chars = '<>:"/\\|?*'
    for char in restricted_chars:
        title = title.replace(char, '')
        
    return title

def download_episode(title):
    # Downloads the current episode soup is linked to 

    audio = get_mp3()
    cleaned_title = clean_title(title)
    f = open(cleaned_title + '.mp3', 'wb')
    f.write(audio)
    f.close()
    print("Finished downloading", title)

if __name__ == '__main__':

    url = "http://rationallyspeakingpodcast.org/archive/"
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    last_downloaded = last_downloaded()
    ep_list = get_ep_list()

    for idx, episode in enumerate(ep_list):
        page = urlopen(episode)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        title, ep_num = get_title()

        # Sleep every 14 episodes to avoid HTTP Error 429
        if len(ep_list) != idx + 1 and not (len(ep_list) - idx + 1) % 14:
            time.sleep(30)

        if title == -1:
            print("Skipping non-episode...")
            continue
        elif ep_num <= last_downloaded:
            print("Directory is up to date!")
            break

        download_episode(title)
