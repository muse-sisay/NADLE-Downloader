import click
from nadle_util import download_book, save_metadata_as_json, extract_metadata, get_soup, get_orginal_url, InvalidId, construct_file_paths
from pathlib import Path


@click.command()
@click.argument('id')
@click.option('--output', '-o', type=click.Path(), default='.',
              help='Output path for  downloaded files')
def cli(id, output):
    ''' Downloads book'''

    OPATH = Path(output)
    #foobar(OPATH, id )
    try:
        #foobar(OPATH, id )
        soup = get_soup(id)

        d = extract_metadata(soup)

        fpdf, fjson = construct_file_paths(OPATH, d)

        download_book(fpdf, d['DL LINK'])
        save_metadata_as_json(fjson, d)

    except InvalidId:
        click.secho(
            f'Invalid {id}, please check and try again!', fg='red', err=True)


if __name__ == "__main__":
    cli()
