#!/bin/bash

processor=$1
if [ -z "$processor" ]
then
    echo "Missing argument: processor number"
    exit 1
fi


scan1()
{
    echo "[SCAN PROGRESS] Ring1 scan1 (loc_1) $processor"
    
    ./manage.* eval_loc_1 $processor 10
    ./manage.* eval_loc_1 $processor 11
    ./manage.* eval_loc_1 $processor 12
    ./manage.* eval_loc_1 $processor 13
    ./manage.* eval_loc_1 $processor 14
    ./manage.* eval_loc_1 $processor 15
    ./manage.* eval_loc_1 $processor 23
    ./manage.* eval_loc_1 $processor 31
    ./manage.* eval_loc_1 $processor 39
    ./manage.* eval_loc_1 $processor 47
    ./manage.* eval_loc_1 $processor 55
    ./manage.* eval_loc_1 $processor 54
    ./manage.* eval_loc_1 $processor 53
    ./manage.* eval_loc_1 $processor 52
    ./manage.* eval_loc_1 $processor 51
    ./manage.* eval_loc_1 $processor 50
    ./manage.* eval_loc_1 $processor 42
    ./manage.* eval_loc_1 $processor 34
    ./manage.* eval_loc_1 $processor 26
    ./manage.* eval_loc_1 $processor 18
}

scan2()
{    
    echo "[SCAN PROGRESS] Ring1 scan2 (loc_4) $processor"

    ./manage.* eval_loc_4 $processor 1
    ./manage.* eval_loc_4 $processor 2
    ./manage.* eval_loc_4 $processor 3
    ./manage.* eval_loc_4 $processor 4
    ./manage.* eval_loc_4 $processor 5
    ./manage.* eval_loc_4 $processor 6
    ./manage.* eval_loc_4 $processor 7
    ./manage.* eval_loc_4 $processor 15
    ./manage.* eval_loc_4 $processor 23
    ./manage.* eval_loc_4 $processor 31
    ./manage.* eval_loc_4 $processor 39
    ./manage.* eval_loc_4 $processor 47
    ./manage.* eval_loc_4 $processor 55
    ./manage.* eval_loc_4 $processor 54
    ./manage.* eval_loc_4 $processor 53
    ./manage.* eval_loc_4 $processor 52
    ./manage.* eval_loc_4 $processor 51
    ./manage.* eval_loc_4 $processor 50
    ./manage.* eval_loc_4 $processor 49
    ./manage.* eval_loc_4 $processor 41
    ./manage.* eval_loc_4 $processor 33
    ./manage.* eval_loc_4 $processor 25
    ./manage.* eval_loc_4 $processor 17
    ./manage.* eval_loc_4 $processor 9
}

scan3()
{
    echo "[SCAN PROGRESS] Ring1 scan3 (loc_1) $processor"

    ./manage.* eval_loc_1 $processor 19
    ./manage.* eval_loc_1 $processor 20
    ./manage.* eval_loc_1 $processor 21
    ./manage.* eval_loc_1 $processor 22
    ./manage.* eval_loc_1 $processor 30
    ./manage.* eval_loc_1 $processor 38
    ./manage.* eval_loc_1 $processor 46
    ./manage.* eval_loc_1 $processor 45
    ./manage.* eval_loc_1 $processor 44
    ./manage.* eval_loc_1 $processor 43
    ./manage.* eval_loc_1 $processor 35
    ./manage.* eval_loc_1 $processor 27

    ./manage.* eval_loc_1 $processor 28
    ./manage.* eval_loc_1 $processor 29
    ./manage.* eval_loc_1 $processor 36
    ./manage.* eval_loc_1 $processor 37
}

scan4()
{
    echo "[SCAN PROGRESS] Ring1 scan4 (loc_4) $processor"

    ./manage.* eval_loc_4 $processor 10
    ./manage.* eval_loc_4 $processor 11
    ./manage.* eval_loc_4 $processor 12
    ./manage.* eval_loc_4 $processor 13

    ./manage.* eval_loc_4 $processor 14   
    ./manage.* eval_loc_4 $processor 22
    ./manage.* eval_loc_4 $processor 30
    ./manage.* eval_loc_4 $processor 38
    
    ./manage.* eval_loc_4 $processor 46
    ./manage.* eval_loc_4 $processor 45
    ./manage.* eval_loc_4 $processor 44
    ./manage.* eval_loc_4 $processor 43
    
    ./manage.* eval_loc_4 $processor 42
    ./manage.* eval_loc_4 $processor 34
    ./manage.* eval_loc_4 $processor 26
    ./manage.* eval_loc_4 $processor 18
}

scan5()
{
    echo "[SCAN PROGRESS] Ring1 scan5 (loc_4) $processor"

    ./manage.* eval_loc_4 $processor 19
    ./manage.* eval_loc_4 $processor 20

    ./manage.* eval_loc_4 $processor 21
    ./manage.* eval_loc_4 $processor 29

    ./manage.* eval_loc_4 $processor 37
    ./manage.* eval_loc_4 $processor 36

    ./manage.* eval_loc_4 $processor 35
    ./manage.* eval_loc_4 $processor 27
}

scan6()
{
    echo "[SCAN PROGRESS] Ring1 scan6 (loc_9) $processor"

    ./manage.* eval_loc_9 $processor 1
    ./manage.* eval_loc_9 $processor 9
    ./manage.* eval_loc_9 $processor 2

    ./manage.* eval_loc_9 $processor 6
    ./manage.* eval_loc_9 $processor 5
    ./manage.* eval_loc_9 $processor 14

    ./manage.* eval_loc_9 $processor 46
    ./manage.* eval_loc_9 $processor 38
    ./manage.* eval_loc_9 $processor 45

    ./manage.* eval_loc_9 $processor 41
    ./manage.* eval_loc_9 $processor 33
    ./manage.* eval_loc_9 $processor 42
}

scan7 ()
{
    echo "[SCAN PROGRESS] Ring1 scan7 (loc_9) $processor"

    ./manage.* eval_loc_9 $processor 3
    ./manage.* eval_loc_9 $processor 4

    ./manage.* eval_loc_9 $processor 17
    ./manage.* eval_loc_9 $processor 25

    ./manage.* eval_loc_9 $processor 22
    ./manage.* eval_loc_9 $processor 30

    ./manage.* eval_loc_9 $processor 43
    ./manage.* eval_loc_9 $processor 44
}

scan8 ()
{
    echo "[SCAN PROGRESS] Ring1 scan8 (loc_9) $processor"

    ./manage.* eval_loc_9 $processor 10
    ./manage.* eval_loc_9 $processor 11
    ./manage.* eval_loc_9 $processor 12

    ./manage.* eval_loc_9 $processor 13
    ./manage.* eval_loc_9 $processor 21
    ./manage.* eval_loc_9 $processor 29

    ./manage.* eval_loc_9 $processor 18
    ./manage.* eval_loc_9 $processor 26
    ./manage.* eval_loc_9 $processor 34

    ./manage.* eval_loc_9 $processor 35
    ./manage.* eval_loc_9 $processor 36
    ./manage.* eval_loc_9 $processor 37
}

scan9()
{
    echo "[SCAN PROGRESS] Ring1 scan9 (loc_16) $processor"

    ./manage.* eval_loc_16 $processor 1
    ./manage.* eval_loc_16 $processor 5
    ./manage.* eval_loc_16 $processor 33
    ./manage.* eval_loc_16 $processor 37
}

scan10()
{
    echo "[SCAN PROGRESS] Ring1 scan9 (loc_16) $processor"

    ./manage.* eval_loc_16 $processor 2
    ./manage.* eval_loc_16 $processor 9
    ./manage.* eval_loc_16 $processor 4
    ./manage.* eval_loc_16 $processor 13
    ./manage.* eval_loc_16 $processor 25
    ./manage.* eval_loc_16 $processor 34
    ./manage.* eval_loc_16 $processor 29
    ./manage.* eval_loc_16 $processor 36
}

scan11()
{
    echo "[SCAN PROGRESS] Ring1 scan9 (loc_16) $processor"

    ./manage.* eval_loc_16 $processor 10
    ./manage.* eval_loc_16 $processor 12
    ./manage.* eval_loc_16 $processor 26
    ./manage.* eval_loc_16 $processor 28
}

prev_count=0
count=$(./manage.* count_segments $processor)

while [ $prev_count -ne $count ];
do
    prev_count=$count
    
    scan1
    
    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan2

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan3

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan4

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan5
        
    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan6

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan7

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan8

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan9

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan10

    count=$(./manage.* count_segments $processor)
    [ $count -eq $prev_count ] && scan11

    count=$(./manage.* count_segments $processor)
done

# end of file
