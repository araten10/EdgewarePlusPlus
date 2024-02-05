#!/bin/sh

for pid in $(ps -u $USER -ef | grep -E "python.* *+.pyw" | awk '{print $2}'); do
    echo $pid
    kill -9 $pid
done
