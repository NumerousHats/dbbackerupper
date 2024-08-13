"""DB Dumper.

Dump MySQL database(s).

It assumes that you have used "mysql_config_editor set" to securely store the appropriate
database username and password into the login-path "backups". Note that you must enclose
the password in quotes if it contains a "#" character (https://unix.stackexchange.com/a/352072/416720)

"""

import os
import re
from datetime import datetime
from datetime import timedelta
import subprocess


class DbDumper:
    keep_days = 14

    def __init__(self, verbose=False, simulate=False, base_directory="", prefix="", dbs=None,
                 aws_key=None, azure_key=None, bucket=None, loginpath=None):
        self.verbose = verbose
        self.simulate = simulate
        self.base_directory = base_directory
        self.prefix = prefix
        self.dbs = dbs if type(dbs) is list else []
        self.bucket = bucket
        self.aws_key = aws_key
        self.azure_key = azure_key
        self.loginpath = loginpath

    def run_shell(self, command):
        """Run (or simulate the running) of a command via subprocess.call."""
        if self.simulate:
            return f"{command} at {datetime.now()}"
        else:
            subprocess.call(command, shell=True)

    def override_db(self, new_databases):
        self.dbs = new_databases

    def dump(self):
        """Generates a database dump.

        Dump .tar.gz files (one per database) is placed in the directory self.base_directory/destination by executing
        mysqldump via run_shell() to allow for simulation.

        Returns:
            Filenames that the dumps were saved to.
        """

        files = []
        dt = datetime.today()
        dt_string = dt.strftime("%Y-%m-%dT%H-%M-%S")

        for db in self.dbs:
            dump_out = self.run_shell(
                (f"mysqldump --login-path={self.loginpath} {db} --no-tablespaces --single-transaction "
                 f"--routines --set-gtid-purged=OFF --column-statistics=0 > {self.base_directory}/{db}.sql"))
            if self.simulate:
                subprocess.call(f"echo '{dump_out}' > {self.base_directory}/{db}.sql", shell=True)

        filename = f"{self.prefix}_{dt_string}.tar.gz"
        subprocess.call(f"cd {self.base_directory}; tar czf {filename} *.sql", shell=True)
        subprocess.call(f"rm -f {self.base_directory}/*.sql", shell=True)
        files.append(f"{self.base_directory}/{filename}")

        return files

    def cleanup(self):
        """Delete dump files older than DbDumper.keep_days."""

        now = datetime.now()
        filename_pattern = re.escape(self.prefix) + r"_(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}).tar.gz"
        keep_days = timedelta(days=DbDumper.keep_days)

        for file in [f for f in os.listdir(self.base_directory)
                     if os.path.isfile(os.path.join(self.base_directory, f))]:
            date_match = re.match(filename_pattern, file)
            if date_match:
                if now - datetime.strptime(date_match.group(1), "%Y-%m-%dT%H-%M-%S") > keep_days:
                    os.remove(file)
