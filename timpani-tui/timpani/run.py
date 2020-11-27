import click
from .gui.timpani import TimpaniGui


@click.command()
@click.argument('command')
def main(command):
    if command == 'run':
        run = TimpaniGui()
        run.main()