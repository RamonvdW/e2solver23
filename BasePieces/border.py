# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from BasePieces.pieces_1x1 import PIECES
from BasePieces.border_pre_corners import bbcbb1, bbcbb2, bbcbb3, bbcbb4
import random


class GenerateBorder(object):

    """ create solutions for the outer border
        based on a seed for repeatable randomization

        returns a list of 60 base piece numbers, ordered as follows:
        c, 14b, c, 14b, c, 14b, c, 14b

        (c = corner, b = outer border)
    """

    def __init__(self, seed: int):
        self.c_in_out = dict()        # [base nr] = (in, out)
        self.b_in_out = dict()        # [base nr] = (in, out)
        self.b_inner = dict()         # [base nr] = inner side
        self.in2b_nrs = dict()        # [side] = [nr, nr, ..]
        self.in2bbcbb = dict()        # [side] = [bbcbb, ..]

        self.c_nrs = [1, 2, 3, 4]
        for nr in self.c_nrs:
            piece = PIECES[nr - 1]

            # side1=out, side2=in (side3, 4 = outer border)
            side_in = piece[2-1]
            side_out = piece[1-1]

            self.c_in_out[nr] = (side_in, side_out)
        # for

        for nr in range(5, 60+1):
            piece = PIECES[nr - 1]

            # side2=in, side4=out (side3 = outer border, 1 = inner border)
            side_in = piece[2-1]
            side_out = piece[4-1]
            side_inner = piece[1-1]

            self.b_in_out[nr] = (side_in, side_out)
            self.b_inner[nr] = side_inner

            try:
                self.in2b_nrs[side_in].append(nr)
            except KeyError:
                self.in2b_nrs[side_in] = [nr]
        # for

        self.solve_order = list()
        self.side_order = list()

        self._randomize(seed)

        self.c2bbcbb = {
            1: bbcbb1,
            2: bbcbb2,
            3: bbcbb3,
            4: bbcbb4
        }

        for bbcbb_list in (bbcbb1, bbcbb2, bbcbb3, bbcbb4):
            for bbcbb in bbcbb_list:
                b = bbcbb[0]
                side_in, _ = self.b_in_out[b]
                try:
                    self.in2bbcbb[side_in].append(bbcbb)
                except KeyError:
                    self.in2bbcbb[side_in] = [bbcbb]
        # for

    @staticmethod
    def _randomize_list(r: random.Random, iterations: int, lst: list):
        upper = len(lst)
        for lp in range(iterations):
            idx = int(r.uniform(0, upper))
            nr = lst.pop(idx)
            lst.append(nr)
        # for

    def _randomize(self, seed: int):
        r = random.Random(seed)
        self._randomize_list(r, 10, self.c_nrs)

        for lst in self.in2b_nrs.values():
            self._randomize_list(r, 1000, lst)
        # for

        self._randomize_list(r, 10000, bbcbb1)
        self._randomize_list(r, 10000, bbcbb2)
        self._randomize_list(r, 10000, bbcbb3)
        self._randomize_list(r, 10000, bbcbb4)

    def _iter_recurse(self):
        """
            len of solve_order:
            0 = add bbcbb
            5..14 = add 10 borders
            15 = add bbcbb
            20..29 = add 10 borders
            30 = add bbcbb
            35..44 = add 10 borders
            45 = add bbcbb
            50..59 = add 10 borders
            60 = check head/tail match
        """
        #print("(%s) %s" % (len(self.solve_order), self.solve_order))

        prev_side = self.side_order[-1]

        if len(self.solve_order) in (15, 30, 45):
            # add a bbcbb
            for bbcbb in self.in2bbcbb[prev_side]:
                ok = True
                for p in bbcbb:
                    if p in self.solve_order:
                        ok = False
                        break
                # for

                if ok:
                    self.solve_order.extend(bbcbb)

                    for p in bbcbb:
                        if p in (1, 2, 3, 4):
                            _, side_out = self.c_in_out[p]
                        else:
                            _, side_out = self.b_in_out[p]
                        self.side_order.append(side_out)
                    # for

                    yield from self._iter_recurse()

                    self.side_order = self.side_order[:-5]
                    self.solve_order = self.solve_order[:-5]
            # for

        elif len(self.solve_order) == 60:
            # solution is complete
            # check that the tail fits the head
            if self.side_order[0] == self.side_order[-1]:
                # match
                # reorganize bbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbb
                #       into bbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbb
                sol = self.solve_order[-5:] + self.solve_order[:-5]
                yield sol

        else:
            # add a border
            nrs = self.in2b_nrs[prev_side]  # all possible pieces with that specific side
            for b in nrs:
                if b not in self.solve_order:
                    # base piece is unused
                    side_in, side_out = self.b_in_out[b]
                    if side_in == prev_side:
                        # piece fits
                        self.solve_order.append(b)
                        self.side_order.append(side_out)

                        yield from self._iter_recurse()

                        self.solve_order = self.solve_order[:-1]
                        self.side_order = self.side_order[:-1]
            # for

    def iter_solutions(self):
        self.solve_order = list()
        self.side_order = list()

        # pick the first corner
        c = self.c_nrs[0]

        # pick the first available bbcbb with that corner
        for bbcbb in self.c2bbcbb[1]:
            if bbcbb[2] == c:
                self.solve_order.extend(bbcbb)

                side_in, _ = self.b_in_out[bbcbb[0]]        # head/tail of the entire border
                self.side_order.append(side_in)
                for p in bbcbb:
                    if p in (1, 2, 3, 4):
                        _, side_out = self.c_in_out[p]
                    else:
                        _, side_out = self.b_in_out[p]
                    self.side_order.append(side_out)
                # for

                yield from self._iter_recurse()

                self.side_order = self.side_order[:-6]
                self.solve_order = self.solve_order[:-5]
        # for

        #side_in, side_out = self.c_in_out[c]
        #self.side_order.append(side_in)

        #yield from self._iter_recurse()
        yield bbcbb

    def get_first_solution(self):
        for sol in self.iter_solutions():
            # put the last 7 pieces first
            return sol
        return []


# end of file
