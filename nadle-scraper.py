'''
National Academic Digital Library of Ethiopia Scraper
Downloads all the books and organizes them
    - Field
    - Author

    This is the best organization I could come up,
let me know if there is a better one.

VERSION = 0.1
- TODO list
    Get arguments from the command line
    Read links from file
    Remove scrapinng capabilities
'''

import re
import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlopen
from tqdm import tqdm


base_url = 'http://ndl.ethernet.edu.et/handle/123456789/'

header = {'User-Agent':
          'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB6.5; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; TheWorld)'}

OPATH = Path('.')


def removeReservedChars(value):
    """ Remove reserved characters because of Windows OS compatibility
    """
    return "".join(i for i in value if i not in r'\/:*?"<>|')


def get_metadata(soup):
    mdata = dict()

    t = soup.select('table', class_='table itemDisplayTable')

    if t[0].find(class_='metadataFieldValue dc_title'):
        mdata['BOOK TITLE'] = removeReservedChars(t[0].find(
            class_='metadataFieldValue dc_title').text)
    else:
        mdata['BOOK TITLE'] = ''

    if t[0].find(class_='author'):
        mdata['AUTHOR'] = removeReservedChars(t[0].find(class_='author').text)
    else:
        mdata['AUTHOR'] = ''

    if t[0].find(
            class_='metadataFieldValue dc_identifier_isbn'):
        mdata['ISBN'] = t[0].find(
            class_='metadataFieldValue dc_identifier_isbn').text
    else:
        mdata['ISBN'] = ''

    if t[0].find(
            class_='metadataFieldValue dc_date_issued'):
        mdata['ISSUE DATE'] = t[0].find(
            class_='metadataFieldValue dc_date_issued').text
    else:
        mdata['ISSUE DATE'] = ''

    if t[0].find(
            class_='metadataFieldValue dc_publisher'):
        mdata['PUBLISHER'] = t[0].find(
            class_='metadataFieldValue dc_publisher').text
    else:
        mdata['PUBLISHER'] = ''

    if t[0].find_all('td')[-1]:
        mdata['COLLECTION'] = removeReservedChars(t[0].find_all('td')[-1].text)
    else:
        mdata['COLLECTION'] = ''

    if t[0].find(class_='metadataFieldValue dc_subject'):
        mdata['TAGS'] = t[0].find(class_='metadataFieldValue dc_subject').text
    else:
        mdata['TAGS'] = ''

    if t[0].find(
            class_='metadataFieldValue dc_identifier_uri'):
        mdata['URL'] = t[0].find(
            class_='metadataFieldValue dc_identifier_uri').text
    else:
        mdata['URL'] = ''

    mdata['DL LINK'] = urljoin(base_url, t[1].find('a')['href'])

    return mdata


def download_book(file, url):

    # Get the file size of the episode from the url
    file_size = int(urlopen(url).info().get('Content-Length', -1))

    # Check if the file is half downloaded.
    if file.exists():
        print(f'Resuming {file.stem} ...')
        first_byte = file.stat().st_size
    else:
        first_byte = 0

    if file.exists() and first_byte >= file_size:
        print(f'Skipping {file.stem}, already downloaded.')
        return

    # If previously interrupted .
    # Only get the part that is not downloaded
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}

    req = requests.get(url, headers=header, stream=True)

    pbar = tqdm(total=file_size,  initial=first_byte,
                unit='B', unit_scale=True, desc=file.stem)

    # Write out
    with file.open('wb')as book:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                book.write(chunk)
                pbar.update(1024)

    pbar.close()


def save_metadata(file, data):

    with file.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


for i in range(72, 78189):

    # url = f'{base_url}{i}'
    # For readabilty
    url = "{}{}".format(base_url, i)

    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, "html.parser")

    try:

        d = get_metadata(soup)

        if d['COLLECTION']:
            pcollection = OPATH / d['COLLECTION'] / d['AUTHOR']
        else:
            collection = OPATH / 'Unkown' / d['AUTHOR']
        pcollection.mkdir(parents=True, exist_ok=True)

        fpdf = pcollection / f"{d['BOOK TITLE']}.pdf"
        fjson = pcollection / f"{d['BOOK TITLE']}.json"

        download_book(fpdf, d['DL LINK'])
        save_metadata(fjson, d)

    except (AttributeError, IndexError):
        print('Oweee we got a problem, but continuing')
        with open('error.log', 'a') as log:
            log.write(f'{str(datetime.now())} :> {d["URL"]}\n')
    except:
        print('Owee, we requested a page that doesnt exist')
        with open('error.log', 'a') as log:
            log.write(
                f'{str(datetime.now())} Owweee this is a huge one\n\t:> {d["URL"]}\n')
