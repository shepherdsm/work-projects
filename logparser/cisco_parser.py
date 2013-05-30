#!/usr/bin/env python

### Python Modules ###
import socket

### User Modules ###
import logparser
import rotatinglog

LOG_DIR = r'/var/log/cisco_syslog.log'
OUT_FILE = r'/srv/projects/cisco_reader/syslog.log'

def make_color(string):
    """
    Takes a string and returns a colored version of it.
    """

    RED = '31'
    GREEN = '32'
    YELLOW = '33'

    front = '\033[0;%sm'
    end = '\033[0m'

    color = YELLOW

    if 'FAILED' in string:
        color = RED
    elif 'SUCCESS' in string:
        color = GREEN

    return front % color + string + end

def get_host(ip):
    """
    Finds the best hostname for the given IP address. It removes
    the domain because I don't think it's neccessary.

    Returns the hostname if it finds it.
    Console if the login was from a console port.
    And the IP address if neither of the above are true.
    """

    try:
        return socket.gethostbyaddr(ip)[0][:-13]
    except socket.gaierror:
        return ip
    except socket.herror:
        return ip
    except socket.error:
        return 'local'

def ip_to_hostname(res):
    """
    Takes the results dictionary and 'prettifies' the IP addresses.
    """

    tmp = res.copy()

    for k in 'source destination'.split():
        tmp[k] = get_host(tmp[k])

    return tmp

if __name__ == '__main__':
    two_MB = 2097152
    lp = logparser.LogParser(LOG_DIR)
    rl = rotatinglog.RotatingLogfile(OUT_FILE, two_MB)

    for result in lp.get_lines('CONFIG|LOGIN'):
        output = '%(time)s - %(user)s - Source: %(source)s - Destination: %(destination)s - %(msg)s' % ip_to_hostname(result)
        rl.writeline(make_color(output))