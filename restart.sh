#!/bin/sh

if [ "$1" == "--clean" ]
then
    echo "[INFO] Creating empty database"
    sudo -u postgres dropdb --if-exists e2
    sudo -u postgres dropdb --if-exists test_e2 || exit 1   # avoid problems with next test run
    sudo -u postgres createdb -E UTF8 e2 || exit 1
    sudo -u postgres psql -d e2 -q -c 'GRANT CREATE ON SCHEMA public TO e2app'

    ./manage.* migrate

    echo "[INFO] Creating all ThreeSide"
    ./manage.* make_3sides

    echo "[INFO] Creating all Piece2x2"
    ./manage.* make2x2_borders
fi

exit

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
#./manage.* eval_loc_4 2 1     # effect: 0
#./manage.* eval_loc_4 2 7     # effect: 0
./manage.* eval_loc_4 2 49     # effect: -1
./manage.* eval_loc_4 2 55     # effect: -1

#./manage.* dup_segments 3
#./manage.* eval_loc_4 3 2      # effect: 0
#./manage.* eval_loc_4 3 9      # effect: 0

#./manage.* eval_loc_4 3 6      # effect: 0
#./manage.* eval_loc_4 3 15     # effect: 0

#./manage.* eval_loc_4 3 50     # effect: 0
#./manage.* eval_loc_4 3 41     # effect: 0

#./manage.* eval_loc_4 3 54     # effect: 0
#./manage.* eval_loc_4 3 47     # effect: 0

#echo "[INFO] Reduce center"
#./manage.* dup_segments 4
#./manage.* eval_loc_4 4 28     # effect: 0
#./manage.* eval_loc_4 4 36     # effect: 0

#echo "[INFO] Reduction 4 attempts"
#./manage.* dup_segments 4
#./manage.* eval_loc_4 4 10     # effect: 0
#./manage.* eval_loc_4 4 14     # effect: 0
#./manage.* eval_loc_4 4 42     # effect: 0
#./manage.* eval_loc_4 4 46     # effect: 0

#echo "[INFO] Reduction 9 attempts"
#./manage.* dup_segments 9
#./manage.* eval_loc_9 9 1      # effect: 0
#./manage.* eval_loc_9 9 6      # effect: 0
#./manage.* eval_loc_9 9 41     # effect: 0
#./manage.* eval_loc_9 9 46     # effect: 0
./manage.* eval_loc_9 9 34

echo "[INFO] Reduction 16 attempts"
./manage.* dup_segments 16
#screen -S 16a -dn ./manage,* eval_loc_16 16 1      # effect: 0
screen -S 16a -dn ./manage,* eval_loc_16 16 5
screen -S 16a -dn ./manage,* eval_loc_16 16 9
screen -S 16a -dn ./manage,* eval_loc_16 16 12
screen -S 16a -dn ./manage,* eval_loc_16 16 19
#screen -S 16a -dn ./manage,* eval_loc_16 16 33     # effect: 0
screen -S 16a -dn ./manage,* eval_loc_16 16 36
#screen -S 16a -dn ./manage,* eval_loc_16 16 37     # effect: 0

echo "[INFO] Reduction 25 attempts"
./manage.* dup_segments 25
#screen -S 25a -dn ./manage.* eval_loc_25 25 1 18
#screen -S 25a -dn ./manage.* eval_loc_25 25 1 139
#screen -S 25c -dn ./manage.* eval_loc_25 25 19 37
#screen -S 25d -dn ./manage.* eval_loc_25 25 19 157

echo "[INFO] Reduction corners 9 attempts"
./manage.* dup_segments 36
#screen -S c1a -dn ./manage.* eval_corners_9 36 9
#screen -S c1b -dn ./manage.* eval_corners_9 36 130
#screen -S c2a -dn ./manage.* eval_corners_9 36 136
#screen -S c2b -dn ./manage.* eval_corners_9 36 16
#screen -S c3a -dn ./manage.* eval_corners_9 36 64
#screen -S c3b -dn ./manage.* eval_corners_9 36 192
#screen -S c4a -dn ./manage.* eval_corners_9 36 186
#screen -S c4b -dn ./manage.* eval_corners_9 36 57

echo "[INFO] Reduction ring1 attempts"
./manage.* dup_segments 28      # 4x7 = 28
#screen -S r1a -dn ./manage.* eval_ring1 28 11
#screen -S r1a -dn ./manage.* eval_ring1 28 14
#screen -S r1a -dn ./manage.* eval_ring1 28 152
#screen -S r1a -dn ./manage.* eval_ring1 28 176
#screen -S r1a -dn ./manage.* eval_ring1 28 62
#screen -S r1a -dn ./manage.* eval_ring1 28 59
#screen -S r1a -dn ./manage.* eval_ring1 28 170
#screen -S r1a -dn ./manage.* eval_ring1 28 146

# end of file

