import glob
import gzip
import os

class RotatingLogfile:
        """
        Keeps track of and rotates log files when they've reached a certain size.
        """

        def __init__(self, filename, maxsize, history=50):
                """
                Specify the filename for the log file.
                The max size to rotate at (in bytes).
                History is how many previous files to keep. Setting it to -1 keeps all files.
                """

                self.name = filename
                self.logfile = open(filename, 'a')
                self.logfile.seek(0, 2) # Move to the end of the file

                self.max = maxsize
                self.history = history
                self.archive = 'archive' # Directory to store the old log files. Creates in the running dir of the main script.

                self._check_for_rotate()

        ### Private Functions ###
        def _check_for_rotate(self):
                """
                Checks the active log file to see if it's larger than the maximum tracked size.
                If it is, we rotate the log files.
                """

                if self.logfile.tell() >= self.max:
                        self._rotate_logs()

        def _rotate_logs(self):
                """
                If a log file is too big,  it rotates the file into the archive along with the logs in the archive already.
                gzips the archived files for saving space.
                Numbers the files from 1-X, where X is the oldest and 1 is the newest archived files.
                """

                base_archive_log = os.path.join(self.archive, self.name + '.%s.gz')

                if not os.path.exists(self.archive):
                        os.mkdir(self.archive)

                number_of_old_archives = len(glob.glob(base_archive_log % '*'))

                if self.history >= 0 and number_of_old_archives >= self.history:
                        os.remove(base_archive_log % number_of_old_archives)
                        number_of_old_archives -= 1

                for i in range(number_of_old_archives, 0, -1):
                        os.rename(base_archive_log % i, base_archive_log % (i + 1))

                self.close() # Close the old logfile

                # Write the log file into a gzip'd file in the archive.
                f_in = open(self.name, 'rb')
                f_out = gzip.open(base_archive_log % 1, 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()

                open(self.name, 'w').close() # Clear out the file

                self.logfile = open(self.name, 'a') # Re-open the file as append

        ### Public Functions ###
        def write(self, string):
                """
                Writes the given string to the log file.
                Rotates the logs if necessary.
                """

                if not os.path.exists(self.name):
                        self.logfile.close()
                        self.logfile = open(self.name, 'a')

                self.logfile.write(string)

                self._check_for_rotate()

        def writeline(self, string):
                """
                Writes the given string to the log file.
                Appends a newline and rotates if necessary.
                """

                self.write(string + '\n')

        def close(self):
                """
                Closes the file.
                """

                self.logfile.close()