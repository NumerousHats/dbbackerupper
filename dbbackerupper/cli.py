"""Console script for dbbackerupper."""

import sys
import click
import configparser
import json
from pathlib import Path
from appdirs import AppDirs
from .dumper import DbDumper

from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os


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


@main.command()
@click.pass_obj
def cleanup(dumper):
    """Delete old DB dumps."""
    dumper.cleanup()


@main.command()
@click.pass_obj
def gdrive(dumper):
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = "{}/client_secrets.json".format(dumper.base_directory)
    # Below code does the authentication
    # part of the code
    gauth = GoogleAuth()

    # Creates local webserver and auto
    # handles authentication.
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # replace the value of this variable
    # with the absolute path of the directory
    path = dumper.base_directory

    # iterating thought all the files/folder
    # of the desired directory
    for x in os.listdir(path):
        file = drive.CreateFile({'title': x})
        file.SetContentFile(os.path.join(path, x))
        file.Upload()

        # Due to a known bug in pydrive if we
        # don't empty the variable used to
        # upload the files to Google Drive the
        # file stays open in memory and causes a
        # memory leak, therefore preventing its
        # deletion
        file = None


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
