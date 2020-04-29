import click
from nadle_util import *
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests


@click.group()
@click.option('--output', '-o', type=click.Path(), default='.',
              help='Output path for downloaded files')
@click.pass_context
def cli(ctx, output):
    ''' Downloads book'''

    OPATH = Path(output)
    ctx.obj = {'OPATH': OPATH}


@cli.command()
@click.pass_context
def scrape(ctx):
    '''
    Download all the book from NADLE.
    '''
    OPATH = ctx.obj['OPATH']
    click.secho('SCRAPINNG THE SITE.', bg='red', fg='white')

    id = '0'

    url = f'http://ndl.ethernet.edu.et/handle/123456789/{id}/browse'
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, "html.parser")

    page_number = soup.find('div', class_='panel-heading text-center').text
    last_item = [x for x in page_number.split() if x.isdigit()][-1]

    click.secho(f'~{last_item} BOOKS', bg='red', fg='white')

    offset = 500
    for iv in range(0, int(last_item), offset):
        cat_url = f'http://ndl.ethernet.edu.et/handle/123456789/{id}/browse?type=title&sort_by=1&order=ASC&rpp={offset}&etal=-1&null=&offset={iv}'
        req = requests.get(cat_url)
        soup = BeautifulSoup(req.text, "html.parser")

        tbody = soup.find('table', class_='table').select('tr')[1:]

        for tr in tbody:
            single_book(OPATH, urljoin(
                base_url, tr.find('a')['href']).split('/')[-1])


@cli.command()
@click.argument('id')
@click.pass_context
def download(ctx, id):

    click.secho(f'Downloading wegpage : {get_orginal_url(id)}', bg='green')
    OPATH = ctx.obj['OPATH']
    # Identify whether the url is for a Book or a Collection
    #
    soup = get_soup(id)

    if soup.find('div', class_='browse_range'):
        # Collection URL
        collection_title = soup.title.text.split(":")[-1].strip()

        number_of_books, soup = get_soup_for_collection(id)
        tbody = soup.find('table', class_='table').select('tr')[1:]

        click.secho(
            f'Downloading "{collection_title}" collection [{number_of_books} books]...', fg='green')

        # Book ID List for the collection
        li_book = []
        for tr in tbody:
            li_book.append(
                urljoin(base_url, tr.find('a')['href']).split('/')[-1])

        for book in li_book:
            single_book(OPATH, book)

    elif soup.title.text == 'NADLE: Invalid Identifier':
        # invalid URL : Raise an Error
        # pass
        click.secho(
            f'Invalid {id}, please check and try again!', fg='red', err=True)
    else:
        # Book URL
        single_book(OPATH, id)

        # except InvalidId:
        #     click.secho(
        #         f'Invalid {id}, please check and try again!', fg='red', err=True)


if __name__ == "__main__":
    cli()
