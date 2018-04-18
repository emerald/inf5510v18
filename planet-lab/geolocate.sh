#!/usr/bin/env bash

set -euo pipefail

while read line
do
  location=$(geoiplookup -f GeoIP.dat "$line" | cut -d ' ' -f5-);
  printf "%s, %s\n" "$line" "$location"
done
