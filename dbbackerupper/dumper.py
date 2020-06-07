"""DB Dumper.

Dump MySQL database(s).
"""

from datetime import datetime
from datetime import timedelta
import subprocess


class DbDumper:
    keep_days = 7

    def __init__(self, debug=False, verbose=False, nowarn=False, simulate=False,
                 base_directory="", prefix="", dbs=None):
        self.debug = debug
        self.verbose = verbose
        self.nowarn = nowarn
        self.simulate = simulate
        self.base_directory = base_directory
        self.prefix = prefix
        self.dbs = dbs if type(dbs) is list else []

    def run_shell(self, command):
        """Run (or simulate the running) of a command via subprocess.call."""
        if self.simulate:
            print(command)
        else:
            subprocess.call(command, shell=True)

    def dump(self):
        """Generates a database dump.

        Dump .tar.gz file is placed in the directory self.base_directory/destination by executing
        mysqldump via run_shell() to allow for simulation.

        Returns:
            datetime object of the date and time of the backup.
        """

        for db in self.dbs:
            self.run_shell("mysqldump --login-path=backups {0} > {1}/{0}.sql".format(db, self.base_directory))

        dt = datetime.today()
        dt_string = dt.strftime("%Y-%m-%dT%H-%M-%S")
        filename = "{0}{1}.tar.gz".format(self.prefix, dt_string)
        self.run_shell("cd {}; tar czf {} *.sql".format(self.base_directory, filename))
        self.run_shell("rm -f {}/*.sql".format(self.base_directory))
        return dt

    def cleanup(self):
        """Delete dump files older than DbDumper.keep_days."""
        pass
