#!/usr/bin/env python

### Python Modules ###
import re
import time

### Globals ###
PATTERNS = {'msg': re.compile(r'%(.*?):'),
            'user': re.compile(r'(?:user:|by) (\w+)'),
            'time': re.compile(r'^(.{15})'),
            'source': re.compile(r'(?:Source:|from) (.*?)(?: |\])'),
            'destination': re.compile(r' ((?:\d+\.\d+\.\d+\.\d+)|b.*?)(?: |.eglin.af.mil)')}

class LogParser:
        """
        Parses the syslog file for entries we're interested in.
        """

        def __init__(self, filename):
                """
                Filename is the name of the file we want.
                """

                self.loglines = self._follow(open(filename, 'r'))

        ### Private Functions ###
        def _follow(self, the_file):
                """
                Follows a file and yields a line everytime the file updates.
                """

                the_file.seek(0, 2)
                while True:
                        line = the_file.readline()
                        if not line:
                                time.sleep(0.1)
                                continue
                        yield line

        def _get_results(self, string):
                """
                Runs a dictionary of patterns against a string to build
                a dictionary of results. Done this way because python 2.4
                doesn't support dictionary comprehensions.
                """

                results = {}
                for k, v in PATTERNS.items():
                        tmp = re.findall(v, string)
                        if tmp:
                                results[k] = tmp[0]
                        else:
                                results[k] = ''

                return results

        ### Public Functions ###
        def get_lines(self, pattern):
                """
                Creates a generator looking for lines that match the given pattern.
                """

                p = re.compile(pattern)

                for line in self.loglines:
                        if re.search(p, line): # We have an interesting line
                                yield self._get_results(line)