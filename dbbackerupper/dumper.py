"""DB Dumper.

Dump MySQL database(s).
"""

from datetime import datetime
from datetime import timedelta
import subprocess


class DbDumper:
    def __init__(self, debug=False, verbose=False, nowarn=False, simulate=False,
                 base_directory="", prefix=""):
        self.debug = debug
        self.verbose = verbose
        self.nowarn = nowarn
        self.simulate = simulate
        self.base_directory = base_directory
        self.prefix = prefix

    def run_shell(self, command):
        if self.simulate:
            print(command)
        else:
            subprocess.call(command, shell=True)

    def dump_db(self, destination):
        """Generates (or simulates the generation of) a database dump.

        Dump .tar.gz file is placed in the directory base_directory/destination, where base_directory
        is a global variable. If simulate_dump is False, then mysqldump is run (via run_shell() to
        allow for testing). If simulate_dump is True, then the file with the oldest timestamp in its
        filename is copied from base_directory/stash to base_directory/destination.

        Returns:
            datetime object of the date and time of the backup.
        """

        dbs = ["ukrhec_drupal", "ukrhec_newcivicrm"]

        for db in dbs:
            self.run_shell(
                "mysqldump -u ukrhec -p {0} > {1}/{2}/{0}.sql".format(db, self.base_directory, destination))

        dt = datetime.today()
        dt_string = dt.strftime("%Y-%m-%dT%H-%M-%S")
        filename = "{0}{1}.tar.gz".format(self.prefix, dt_string)
        self.run_shell("cd {0}/{2}; tar czf {1} *.sql".format(self.base_directory, filename, destination))
        self.run_shell("rm -f {0}/{1}/*.sql".format(self.base_directory, destination))
        return dt

    def time_to_filename(self, date_time, location):
        """
        Generate a time-stamped fully-qualified path and filename given an ISO date string.

        Args:
            date_time: The ISO date string.
            location: The directory that will be appended to the base_directory global variable to form the
                path.

        Returns:
            The path and filename corresponding to the ISO date string.
        """

        timestring = date_time.strftime("%Y-%m-%dT%H-%M-%S")
        filename = "{0}/{1}/{2}{3}.tar.gz".format(self.base_directory, location, self.prefix, timestring)
        return filename
