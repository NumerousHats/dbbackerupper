"""Console script for dbbackerupper."""

import sys
import os
import configparser
import json
from pathlib import Path

from appdirs import AppDirs
import click
import boto3
from dotenv import load_dotenv

from .dumper import DbDumper


@click.group()
@click.option('-v', '--verbose', 'verbose', is_flag=True, help="Run in verbose mode")
@click.option('--prefix', help="tar.gz filename prefix")
@click.option('--tempdir', help="Temp directory for dump storage")
@click.option('-s', '--simulate', 'simulate', help="Run in simulation mode: do not execute dump", is_flag=True)
@click.pass_context
def main(ctx, verbose, prefix, tempdir, bucket, simulate):
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
        aws_key = [config_vals["aws_access_key_id"], config_vals["aws_secret_access_key"]]
    else:
        raise ValueError("both access key id and secret access key must be provided in config file")

    ctx.obj = DbDumper(verbose=verbose, simulate=simulate, base_directory=tempdir,
                       prefix=prefix, dbs=databases, aws_key = aws_key, bucket=bucket)


@main.command()
@click.pass_obj
def dump(dumper):
    """Dump databases."""

    filenames = dumper.dump()

    bucket_name = 'UHEC-website-backups'  # name of the bucket

    s3_client = boto3.client('s3', dumper.aws_access_key_id, dumper.aws_secret_access_key)

    for file_name in filenames:
        response = s3_client.upload_file(file_name, bucket_name, file_name)


@main.command()
@click.pass_obj
def cleanup(dumper):
    """Delete old DB dumps."""
    dumper.cleanup()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
