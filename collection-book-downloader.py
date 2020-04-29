import click
from nadle_util import get_soup_for_collection, InvalidId
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

base_url = 'http://ndl.ethernet.edu.et/handle/123456789/'


@click.command()
@click.argument('id')
@click.option('--output', '-o', type=click.Path(), default='.',
              help='Output path for  downloaded files')
def cli(id, output):

    OPATH = Path(output)
    # scrape the links for the  urls
    # get a soup object
    # validate the given url as valid
    # Verify that it is a valid Collection URL
    # do the samething as single_book
    try:
        soup = get_soup_for_collection(id)
        tbody = soup.find('table', class_='table').select('tr')[1:]

        li_book = []
        for tr in tbody:
            li_book.append(
                urljoin(base_url, tr.find('a')['href']).split('/')[-1])
    
    except InvalidId:
        click.secho(
            f'{id} is an invalid id, please check and try again!', fg='red', err=True)

# soup = get_soup(id)
# extract metadata
# save path_location
# download_book()
# save_metadata_as_json


cli()
