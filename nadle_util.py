import click
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.request import urlopen
from tqdm import tqdm

base_url = 'http://ndl.ethernet.edu.et/handle/123456789/'
header = {'User-Agent':
          'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB6.5; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; TheWorld)'}


class InvalidId(Exception):
    pass


def download_book(file, url):
    '''Download PDF file '''
    # Get the file size of the episode from the url
    file_size = int(urlopen(url).info().get('Content-Length', -1))

    # Check if the file is half downloaded.
    if file.exists():
        #print(f'Resuming {file.stem} ...')
        click.secho(f'Resuming {file.stem} ...', fg='yellow')
        first_byte = file.stat().st_size
    else:
        first_byte = 0

    if file.exists() and first_byte >= file_size:
        #print(f'Skipping {file.stem}, already downloaded.')
        click.secho(f'Skipping {file.stem}, already downloaded.', fg='green')
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


def save_metadata_as_json(file, data):

    with file.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def extract_metadata(soup):

    mdata = dict()

    #t = soup.select('table', class_='itemDisplayTable')
    t = soup.select('table')

    if t[0].find(class_='metadataFieldValue dc_title'):
        mdata['BOOK TITLE'] = remove_reserved_chars(t[0].find(
            class_='metadataFieldValue dc_title').text)
    else:
        mdata['BOOK TITLE'] = ''

    if t[0].find(class_='author'):
        mdata['AUTHOR'] = remove_reserved_chars(
            t[0].find(class_='author').text)
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
        mdata['COLLECTION'] = remove_reserved_chars(
            t[0].find_all('td')[-1].text)
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


def remove_reserved_chars(word):
    """ Remove reserved characters because of Windows OS compatibility
    """
    return "".join(i for i in word if i not in r'\/:*?"<>|')


def get_soup(id):
    req = requests.get(get_orginal_url(id), headers=header)
    soup = BeautifulSoup(req.text, "html.parser")

    if soup.title.text == 'NADLE: Invalid Identifier' or soup.find('div', class_='browse_range'):
        raise InvalidId
    else:
        return soup


def get_soup_for_collection(id):

    response = requests.get(get_orginal_url(id), headers=header)
    soup = BeautifulSoup(response.text, "html.parser")

    page_number = soup.find('div', class_='browse_range')

    if page_number:
        ''' This little, tiny part checks if this is a valid Category URL, neat right?? '''
        page_number = page_number.text
        last_item = [x for x in page_number.split() if x.isdigit()][-1]
    else:
        raise InvalidId

    cat_url = f'http://ndl.ethernet.edu.et/handle/123456789/{id}/browse?type=title&sort_by=1&order=ASC&rpp={last_item}&etal=-1&null=&offset=0'
    req = requests.get(cat_url)
    soup = BeautifulSoup(req.text, "html.parser")
    return soup


def get_orginal_url(id):
    return f'{base_url}{id}'


def construct_file_paths(OPATH, data):

    if data['COLLECTION']:
        pcollection = OPATH / data['COLLECTION'] / data['AUTHOR']
    else:
        pcollection = OPATH / 'Unkown' / data['AUTHOR']

    pcollection.mkdir(parents=True, exist_ok=True)

    fpdf = pcollection / f"{data['BOOK TITLE']}.pdf"
    fjson = pcollection / f"{data['BOOK TITLE']}.json"

    return fpdf, fjson
