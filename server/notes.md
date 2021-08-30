
How to find the pid for a running process 
https://unix.stackexchange.com/a/237911
ps ax | awk '! /awk/ && /myprocessname/ { print $1}'

