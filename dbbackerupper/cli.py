"""Console script for dbbackerupper."""

import sys
import click
import configparser
import json
from pathlib import Path
from appdirs import AppDirs
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

    dirs = AppDirs("dbbackerupper", "UHEC")
    config_file = Path(dirs.user_data_dir) / "dbbackerupper.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    config_vals = config["dbbackerupper"]

    if "mailto" in config_vals and mailto is None:
        mailto = config_vals["mailto"]

    if "prefix" in config_vals and prefix is None:
        prefix = config_vals["prefix"]

    if "tempdir" in config_vals and tempdir is None:
        tempdir = config_vals["tempdir"]

    if "databases" in config_vals:
        databases = json.loads(config_vals["databases"])
    else:
        databases = []

    dumper = DbDumper(debug=debug, verbose=verbose, nowarn=False, simulate=simulate,
                      base_directory=tempdir, prefix=prefix, dbs=databases)
    filename = dumper.dump()
    dumper.cleanup()

    # TODO send the email


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
