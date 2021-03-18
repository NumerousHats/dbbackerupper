"""DB Dumper.

Dump MySQL database(s).

It assumes that you have used "mysql_config_editor set" to securely store the appropriate
database username and password into the login-path "backups". Note that you must enclose
the password in quotes if it contains a "#" character (https://unix.stackexchange.com/a/352072/416720)

"""

from datetime import datetime
from datetime import timedelta
import subprocess


class DbDumper:
    keep_days = 7

    def __init__(self, verbose=False, simulate=False, base_directory="", prefix="", dbs=None, mailto=None):
        self.verbose = verbose
        self.simulate = simulate
        self.base_directory = base_directory
        self.prefix = prefix
        self.mailto = mailto
        self.dbs = dbs if type(dbs) is list else []

    def run_shell(self, command):
        """Run (or simulate the running) of a command via subprocess.call."""
        if self.simulate:
            print(command)
        else:
            subprocess.call(command, shell=True)

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
            self.run_shell("mysqldump --login-path=backups {0} > {1}/{0}.sql".format(db, self.base_directory))
            filename = "{0}_{1}_{2}.tar.gz".format(self.prefix, db, dt_string)
            self.run_shell("cd {}; tar czf {} *.sql".format(self.base_directory, filename))
            self.run_shell("rm -f {}/*.sql".format(self.base_directory))
            files.append("{}/{}".format(self.base_directory, filename))

        return files

    def cleanup(self):
        """Delete dump files older than DbDumper.keep_days."""
        print("Would be running cleanup now...")
