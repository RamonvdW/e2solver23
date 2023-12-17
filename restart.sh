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
./manage.* eval_loc_1 1 2 
./manage.* eval_loc_1 1 9 
./manage.* eval_loc_1 1 7 
./manage.* eval_loc_1 1 16
./manage.* eval_loc_1 1 49
./manage.* eval_loc_1 1 58
./manage.* eval_loc_1 1 56
./manage.* eval_loc_1 1 63

echo "[INFO] Reduction 4 in the corners"
./manage.* dup_segments 2
./manage.* eval_loc_4 --commit 2 1
./manage.* eval_loc_4 --commit 2 7
./manage.* eval_loc_4 --commit 2 49
./manage.* eval_loc_4 --commit 2 55

./manage.* dup_segments 3
./manage.* eval_loc_4 --commit 3 2
./manage.* eval_loc_4 --commit 3 9

./manage.* eval_loc_4 --commit 3 6
./manage.* eval_loc_4 --commit 3 15

./manage.* eval_loc_4 --commit 3 50
./manage.* eval_loc_4 --commit 3 41

./manage.* eval_loc_4 --commit 3 54
./manage.* eval_loc_4 --commit 3 47

echo "[INFO] Reduction 4 attempts"
./manage.* dup_segments 4
./manage.* eval_loc_4 --commit 4 10
./manage.* eval_loc_4 --commit 4 14
./manage.* eval_loc_4 --commit 4 42
./manage.* eval_loc_4 --commit 4 46

# end of file

