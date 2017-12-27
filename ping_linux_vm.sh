#!/bin/bash

# first we ping the management IP address
# Then we add double loop to ping all of the
# devices in the test subnet works.
# all of this to be clear please read the docs
# First start pinging the odd IPs . please read the doc
var="ping -c 3 172.16.11.1"
$var

for i in {2..32}
do
        var="ping -c 3 172.16.10.$i";
        $var
done

