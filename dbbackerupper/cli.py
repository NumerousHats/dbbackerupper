"""Console script for dbbackerupper."""
import os.path
import sys
import configparser
import json
from pathlib import Path

from appdirs import AppDirs
import click
import boto3

from .dumper import DbDumper

import os


@click.group()
@click.option('-v', '--verbose', 'verbose', is_flag=True, help="Run in verbose mode")
@click.option('--prefix', help="tar.gz filename prefix")
@click.option('--tempdir', help="Temp directory for dump storage")
@click.option('-s', '--simulate', 'simulate', help="Run in simulation mode: do not execute dump", is_flag=True)
@click.option('--bucket', help="AWS S3 bucket name")
@click.pass_context
def main(ctx, verbose, prefix, tempdir, simulate, bucket):
    """DBBackerUpper: a CLI tool to create MySQL database backups and upload to S3."""
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

    if "bucket" in config_vals and bucket is None:
        bucket = config_vals["bucket"]

    if "aws_access_key_id" in config_vals and "aws_secret_access_key" in config_vals:
        aws_key = {"id": config_vals["aws_access_key_id"], "secret": config_vals["aws_secret_access_key"]}
    else:
        raise ValueError("both access key id and secret access key must be provided in config file")

    ctx.obj = DbDumper(verbose=verbose, simulate=simulate, base_directory=tempdir,
                       prefix=prefix, dbs=databases, aws_key=aws_key, bucket=bucket)


@main.command()
@click.pass_obj
def dump(dumper):
    """Dump databases."""

    filenames = dumper.dump()

    s3_client = boto3.client('s3', aws_access_key_id=dumper.aws_key["id"],
                             aws_secret_access_key=dumper.aws_key["secret"])

    for file_name in filenames:
        response = s3_client.upload_file(file_name, dumper.bucket, os.path.basename(file_name))


@main.command()
@click.pass_obj
def cleanup(dumper):
    """Delete old DB dumps."""
    dumper.cleanup()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
