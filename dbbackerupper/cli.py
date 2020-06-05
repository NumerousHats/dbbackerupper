"""Console script for dbbackerupper."""

import sys
import click
from .dumper import DbDumper


@click.command()
@click.option('-v', '--verbose', 'verbose', is_flag=True, help="Run in verbose mode")
@click.option('-d', '--debug', 'debug', is_flag=True, help="Run in debug mode")
@click.option('--mailto', help="Email address to mail the DB dump.")
@click.option('--prefix', help="tar.gz filename prefix")
@click.option('--tempdir', help="Temp directory for dump storage")
@click.option('-s', '--simulate', 'simulate', help="Run in simulation mode: do not execute dump", is_flag=True)
def main(verbose, debug, mailto, prefix, tempdir, simulate):
    """DB BackerUpper: a CLI tool to create MySQL database backups and email the results to a Gmail account."""
    dumper = DbDumper(debug=debug, verbose=verbose, nowarn=False, simulate=simulate,
                      base_directory=tempdir, prefix=prefix)
    dumper.run_shell("ls -l")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
