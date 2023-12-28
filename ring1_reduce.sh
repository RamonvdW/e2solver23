#!/bin/bash

processor=$1

[ -z "$processor" ] && exit 1

./manage.* eval_loc_1 $processor 10
./manage.* eval_loc_1 $processor 15
./manage.* eval_loc_1 $processor 50
./manage.* eval_loc_1 $processor 55

./manage.* eval_loc_1 $processor 11
./manage.* eval_loc_1 $processor 12
./manage.* eval_loc_1 $processor 13
./manage.* eval_loc_1 $processor 14

./manage.* eval_loc_1 $processor 23
./manage.* eval_loc_1 $processor 31
./manage.* eval_loc_1 $processor 39
./manage.* eval_loc_1 $processor 47

./manage.* eval_loc_1 $processor 51
./manage.* eval_loc_1 $processor 52
./manage.* eval_loc_1 $processor 53
./manage.* eval_loc_1 $processor 54

./manage.* eval_loc_1 $processor 18
./manage.* eval_loc_1 $processor 26
./manage.* eval_loc_1 $processor 34
./manage.* eval_loc_1 $processor 42


./manage.* eval_loc_4 $processor 10
./manage.* eval_loc_1 $processor 11
./manage.* eval_loc_1 $processor 18
./manage.* eval_loc_1 $processor 19

./manage.* eval_loc_4 $processor 14
./manage.* eval_loc_1 $processor 14
./manage.* eval_loc_1 $processor 23
./manage.* eval_loc_1 $processor 22

./manage.* eval_loc_4 $processor 42
./manage.* eval_loc_1 $processor 42
./manage.* eval_loc_1 $processor 51
./manage.* eval_loc_1 $processor 43

./manage.* eval_loc_4 $processor 46
./manage.* eval_loc_1 $processor 47
./manage.* eval_loc_1 $processor 54
./manage.* eval_loc_1 $processor 46

exit

./manage.* eval_loc_9 $processor 10
./manage.* eval_loc_9 $processor 13
./manage.* eval_loc_9 $processor 34
./manage.* eval_loc_9 $processor 37

# end of file
