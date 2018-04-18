#!/usr/bin/env python3

import click
import fileinput
import os
import os.path
import pexpect
import re
import sys


LOGIN = 'diku_inf5510'
N_SECS_TIMEOUT = 3

PROMPT=r"[#$]"


class KeyNotInSSHAgent(Exception):
    def __init__(self):
        self.message = "This script relies on an SSH agent being installed;\n" + \
         "and on your SSH key being registered with the SSH agent."

class CouldNotLogin(Exception):
    def __init__(self, message):
        self.message = message

class SSH(pexpect.spawn):
    def __init__(self, server, options=[]):
        pexpect.spawn.__init__(self,
            'ssh', ['-l', LOGIN] + options + [server])

    def expect(self, p):
        return super(SSH, self).expect(p,
            timeout=N_SECS_TIMEOUT)


    def text(self):
        return self.before.decode('utf-8')

    def login(self):
        i = self.expect([PROMPT,
            "(?i)are you sure you want to continue connecting",
            "Enter passphrase for key"])
        if i == 1:
            self.sendline("yes")
            i = s.expect([PROMPT])
        elif i == 2:
            raise KeyNotInSSHAgent()

        if i != 0:
            raise CouldNotLogin(self.text())


def printGOOD(server):
    print("GOOD", server)


def printErrorMessage(message):
    prefix = '  !! '
    print(prefix + message.strip().replace('\n', '\n' + prefix))


def printBAD(server, message):
    print("BAD", server)
    printErrorMessage(message)


def checkServer(server, ssh_options=[]):
    s = SSH(server, ssh_options)

    try:
        s.login()

        s.sendline("sudo ping -c 1 google.com")
        i = s.expect(["Name or service not known", "google.com ping statistics"])
        if i == 0:
            printBAD(server, "Can't ping out :-(")
        else:
            printGOOD(server)

        s.sendline('exit')
        s.expect(pexpect.EOF)
    except CouldNotLogin as e:
        printBAD(server, e.message)
    except KeyNotInSSHAgent as e:
        printBAD(server, e.message)
        sys.exit(1)
    except pexpect.exceptions.TIMEOUT:
        printBAD(server, 'Timeout; skipping to next machine.')
    except pexpect.exceptions.EOF:
        printBAD(server, s.text())

    s.close()

    sys.stdout.flush()


@click.command()
@click.option('-i', '--identity', type=str, default='',
    help='The SSH identity file to use')
def main(identity):
    """Try and login on each node listed over stdin, and ping out of it.

For each successful login, print GOOD, followed by the inode URL. For
each failed login, print BAD, followed by node URL.  All error
messages (in particular, in cases of failure, are prefixed by "  !! "
on each line, to keep it easy to use grep and cut to work with the
output from this utility.

Sample output:

\b
    BAD planetlab2.diku.dk
      !! ssh: Could not resolve hostname planetlab2.diku.dk: Name or service not known
    BAD pl2.uni-rostock.de
      !! Timeout; skipping to next machine.
    GOOD cse-yellow.cse.chalmers.se
    GOOD ple2.planet-lab.eu

For this utility to work, you should have the requirements in
requirements.txt installed. Also, you will need an SSH agent, and have
your desired SSH key already registered with the SSH agent."""

    ssh_options = []
    if identity != '':
        ssh_options = ['-i', identity]

    for line in sys.stdin:
        server = line.strip()
        checkServer(server, ssh_options)

if __name__ == "__main__":
    main()
