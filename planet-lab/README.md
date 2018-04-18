# Overview

## [`nodes.txt`](nodes.txt)

This is the list of the nodes from `planet-lab.eu`. It is copy-pasted
from a table in a browser window, listing all the nodes in a given
slice. Since it is copy-pasted tabular data, the fields are separated
by tabs.

The only interesting column is the first one, the domain name of each
node. We can separate out this column as follows:

```bash
$ cat nodes.txt | cut -f1
```

## [`login-and-ping.py`](login-and-ping.py)

This Python 3 script goes through the list of nodes passed in via
stdin, and for each checks whether we can log in on the machine via
SSH, and ping out of it.

For each successful login, print GOOD, followed by the node URL. For
each failed login, print BAD, followed by node URL.  All error
messages (in particular, in cases of failure, are prefixed by "  !! "
on each line, to keep it easy to use grep and cut to work with the
output from this utility.

Sample output:

    BAD planetlab2.diku.dk
      !! ssh: Could not resolve hostname planetlab2.diku.dk: Name or service not known
    BAD pl2.uni-rostock.de
      !! Timeout; skipping to next machine.
    GOOD cse-yellow.cse.chalmers.se
    GOOD ple2.planet-lab.eu

The script assumes that an SSH agent is installed, and that the
desired SSH key has already been registered with the SSH agent. You
can specify the path to your desired identity file with the `-i`
option, as with regular `ssh`. See `./login-and-ping.py --help` for
more.

You should also have the Python-modules listed in
[`requirements.txt`](requirements.txt) installed:

```
$ pip3 install requirements.txt
```

## [`status.txt`](status.txt)

This is the output from the above script, from my point of view. It is
generated as follows:

```
$ cat nodes.txt | cut -f1 | ./login-and-ping.py > status.txt
```

Modulo the possible need to specify an SSH identity file.

## [`good-nodes.txt`](good-nodes.txt)

This is the list of actually good nodes, as identified above. This
list is generated as follows:

```
$ cat status.txt | grep GOOD | cut -d' ' -f2 > good-nodes.txt
```

## [`geolocate.sh`](geolocate.sh)

This script will give a guess of the location of the URL given in each
line over stdin. This guess is based on the [legacy GeoIP Country
dataset](https://dev.maxmind.com/geoip/legacy/geolite/), which is
provided here as the file `GeoIP.dat`.

## [`good-locations.txt`](good-locations.txt)

This is the list of good nodes, coupled with their locations, as
guessed by the script above. This list is generated as follows:

```
$ cat good-nodes.txt | ./geolocate.sh > good-locations.txt
```
