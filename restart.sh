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
./manage.* eval_loc_1 2
./manage.* eval_loc_1 9
./manage.* eval_loc_1 7
./manage.* eval_loc_1 16
./manage.* eval_loc_1 49
./manage.* eval_loc_1 58
./manage.* eval_loc_1 56
./manage.* eval_loc_1 63

echo "[INFO] Reduction 4 in the corners"
./manage.* eval_loc_4 --commit 1
./manage.* eval_loc_4 --commit 2 
./manage.* eval_loc_4 --commit 9

./manage.* eval_loc_4 --commit 7
./manage.* eval_loc_4 --commit 6
./manage.* eval_loc_4 --commit 15

./manage.* eval_loc_4 --commit 49
./manage.* eval_loc_4 --commit 50
./manage.* eval_loc_4 --commit 41

./manage.* eval_loc_4 --commit 55
./manage.* eval_loc_4 --commit 54
./manage.* eval_loc_4 --commit 47

echo "[INFO] Reduction 4 attempts"
./manage.* eval_loc_4 --commit 10
./manage.* eval_loc_4 --commit 14
./manage.* eval_loc_4 --commit 42
./manage.* eval_loc_4 --commit 46

# end of file

