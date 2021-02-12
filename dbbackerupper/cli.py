"""Console script for dbbackerupper."""

import sys
import click
import configparser
import json
from pathlib import Path
from appdirs import AppDirs
from .dumper import DbDumper


@click.group()
@click.option('-v', '--verbose', 'verbose', is_flag=True, help="Run in verbose mode")
@click.option('--prefix', help="tar.gz filename prefix")
@click.option('--tempdir', help="Temp directory for dump storage")
@click.option('-s', '--simulate', 'simulate', help="Run in simulation mode: do not execute dump", is_flag=True)
@click.option('--mailto', help="Email address where to mail the DB dump ('None' to prevent mailing).")
@click.pass_context
def main(ctx, verbose, prefix, tempdir, simulate, mailto):
    """DBBackerUpper: a CLI tool to create MySQL database backups and email the results using Gmail."""
    dirs = AppDirs("dbbackerupper", "UHEC")
    config_file = Path(dirs.user_data_dir) / "dbbackerupper.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
    config_vals = config["dbbackerupper"]

    if "prefix" in config_vals and prefix is None:
        prefix = config_vals["prefix"]

    if "tempdir" in config_vals and tempdir is None:
        tempdir = config_vals["tempdir"]

    if "databases" in config_vals:
        databases = json.loads(config_vals["databases"])
    else:
        databases = []

    if "mailto" in config_vals and mailto is None:
        mailto = config_vals["mailto"]

    ctx.obj = DbDumper(verbose=verbose, simulate=simulate, base_directory=tempdir,
                       prefix=prefix, dbs=databases, mailto=mailto)


@main.command()
@click.pass_obj
def dump(dumper):
    """Dump databases."""

    filename = dumper.dump()

    if dumper.mailto != "None" and not dumper.simulate:
        dirs = AppDirs("dbbackerupper", "UHEC")
        creds_file = Path(dirs.user_data_dir) / "oauth2_creds.json"
        yag = SMTP(dumper.mailto, oauth2_file=creds_file)
        yag.send(subject="Database backup", contents=filename)


@main.command()
@click.pass_obj
def cleanup(dumper):
    """Delete old DB dumps."""
    dumper.cleanup()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
