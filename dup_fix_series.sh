#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Missing arguments: first and last board numbers"
    exit 1
fi

first_board=$1
last_board=$2

echo "[INFO] Running dup_fix_lowest on all boards in the range $first_board to $last_board"

x=$first_board
while [ $x -le $last_board ]
do
    new_boards=$(./manage.py dup_fix_lowest $x)
    echo "[INFO] Adding scans for boards $new_boards"
    for board in $new_boards
    do
        ./manage.py add_work $board scan1 2 2
        ./manage.py add_work $board scan9 9 9
    done

    x=$((x+1))
done

# end of file
