#!/bin/sh

if [ "$1" == "--clean" ]
then
    echo "[INFO] Creating empty database"
    sudo -u postgres dropdb --if-exists e2
    sudo -u postgres dropdb --if-exists test_e2 || exit 1   # avoid problems with next test run
    sudo -u postgres createdb -E UTF8 e2 || exit 1
    sudo -u postgres psql -d e2 -q -c 'GRANT CREATE ON SCHEMA public TO e2app'

    ./manage.* migrate

    echo "[INFO] Creating all Piece2x2"
    ./manage.* make2x2
fi

echo "[INFO] Creating all TwoSideOptions"
./manage.* init_segments --confirm

echo "[INFO] Reduction 1"
./manage.* dup_segments 1
./manage.* eval_loc_1 1 2       # effect: -21
./manage.* eval_loc_1 1 9       # effect: -12
./manage.* eval_loc_1 1 7       # effect: -22
./manage.* eval_loc_1 1 16      # effect: -17
./manage.* eval_loc_1 1 49      # effect: -28
./manage.* eval_loc_1 1 58      # effect: -23
./manage.* eval_loc_1 1 56      # effect: -23
./manage.* eval_loc_1 1 63      # effect: -29

echo "[INFO] Reduction 4 in the corners"
./manage.* dup_segments 2
#./manage.* eval_loc_4 --commit 2 1     # effect: 0
#./manage.* eval_loc_4 --commit 2 7     # effect: 0
./manage.* eval_loc_4 --commit 2 49     # effect: -1
./manage.* eval_loc_4 --commit 2 55     # effect: -1

#./manage.* dup_segments 3
#./manage.* eval_loc_4 --commit 3 2      # effect: 0
#./manage.* eval_loc_4 --commit 3 9      # effect: 0

#./manage.* eval_loc_4 --commit 3 6      # effect: 0
#./manage.* eval_loc_4 --commit 3 15     # effect: 0

#./manage.* eval_loc_4 --commit 3 50     # effect: 0
#./manage.* eval_loc_4 --commit 3 41     # effect: 0

#./manage.* eval_loc_4 --commit 3 54     # effect: 0
#./manage.* eval_loc_4 --commit 3 47     # effect: 0

echo "[INFO] Reduce center"
#./manage.* dup_segments 4
#./manage.* eval_loc_4 --commit 4 28     # effect: 0

echo "[INFO] Reduction 4 attempts"
./manage.* dup_segments 4
./manage.* eval_loc_4 --commit 4 10
./manage.* eval_loc_4 --commit 4 14
./manage.* eval_loc_4 --commit 4 42
./manage.* eval_loc_4 --commit 4 46

echo "[INFO] Reduction 9 attempts"
./manage.* dup_segments 9
./manage.* eval_loc_9 --commit 9 1
./manage.* eval_loc_9 --commit 9 6
./manage.* eval_loc_9 --commit 9 41
./manage.* eval_loc_9 --commit 9 46

echo "[INFO] Reduction 16 attempts"
./manage.* dup_segments 16
./manage,* eval_loc_16 --commmit 16 1
./manage,* eval_loc_16 --commmit 16 5
./manage,* eval_loc_16 --commmit 16 33
./manage,* eval_loc_16 --commmit 16 37
./manage,* eval_loc_16 --commmit 16 19


# end of file

