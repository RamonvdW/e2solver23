# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from BasePieces.pieces_1x1 import PIECES
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

        # the allowed inner side for the border piece just before/after a corner
        self.inner_b_requirements = {
            # c,b: corner, base nr
            (1, 1): ('BB', 'BD', 'BF', 'BJ', 'BL', 'BR', 'BT', 'GD', 'GL', 'GO', 'GR', 'GT', 'GU', 'HB', 'HF', 'HJ',
                     'HL', 'HP', 'JD', 'JJ', 'JL', 'JO', 'JP', 'JT', 'OB', 'OJ', 'OL', 'OO', 'OT', 'PB', 'PF', 'PJ',
                     'PL', 'PR', 'PT', 'PU', 'RB', 'RD', 'RF', 'RR', 'RT', 'TF', 'TJ', 'TL', 'TO', 'TP', 'VF', 'VJ',
                     'VO', 'VP', 'VT', 'VU'),
            (1, 2): ('CB', 'CJ', 'CO', 'CP', 'CR', 'DB', 'DF', 'DJ', 'DL', 'DP', 'DR', 'HF', 'HJ', 'HL', 'HP', 'KF',
                     'KJ', 'OB', 'OD', 'OF', 'OJ', 'OL', 'OO', 'OT', 'PB', 'PD', 'PF', 'PJ', 'PL', 'PR', 'PT', 'PU',
                     'RB', 'RD', 'RF', 'RP', 'RT', 'SB', 'SD', 'SF', 'SJ', 'SL', 'SO', 'SU', 'TF', 'TJ', 'TL', 'TP',
                     'TT'),
            (1, 3): ('BB', 'BG', 'BH', 'BJ', 'BO', 'GO', 'GS', 'GU', 'HB', 'HH', 'HJ', 'HS', 'HU', 'JG', 'JH', 'JJ',
                     'JO', 'OB', 'OJ', 'OO', 'OS', 'PB', 'PG', 'PJ', 'PS', 'PU', 'RB', 'TB', 'TG', 'TH', 'TJ', 'TO',
                     'TS', 'TU', 'VB', 'VH', 'VJ', 'VO', 'VU'),
            (1, 4): ('DB', 'DH', 'DK', 'DR', 'DS', 'DV', 'GK', 'GO', 'GR', 'GS', 'GV', 'JB', 'JT', 'JV', 'LB', 'LH',
                     'LK', 'LR', 'LS', 'LV', 'NB', 'NK', 'NO', 'NT', 'NV', 'OJ', 'OS', 'OT', 'OV', 'RB', 'RR', 'RT',
                     'RV', 'SB', 'SH', 'SJ', 'SK', 'SO', 'SS', 'TK', 'TO', 'TR', 'TS', 'TT', 'UB', 'UK', 'UR', 'US',
                     'UV'),
            (2, 1): ('BD', 'BJ', 'BL', 'BR', 'BT', 'BU', 'GB', 'GD', 'GL', 'GO', 'GP', 'GR', 'GT', 'HB', 'HD', 'HF',
                     'HJ', 'HL', 'HO', 'HP', 'HU', 'JB', 'JF', 'JL', 'JP', 'JR', 'JT', 'JU', 'OB', 'OD', 'OF', 'OJ',
                     'OL', 'OO', 'PB', 'PF', 'PJ', 'PO', 'PT', 'PU', 'RB', 'RD', 'RF', 'RP', 'RT', 'TF', 'TJ', 'TL',
                     'TO', 'TP', 'TR', 'TT', 'TU', 'VD', 'VJ', 'VP', 'VR', 'VT', 'VU'),
            (2, 2): ('CB', 'CF', 'CP', 'CR', 'CT', 'CU', 'DL', 'DO', 'DP', 'HB', 'HF', 'HJ', 'HL', 'HO', 'HU', 'KJ',
                     'KO', 'KR', 'OB', 'OD', 'OF', 'OJ', 'OL', 'OO', 'PB', 'PO', 'PT', 'RD', 'RF', 'RP', 'SD', 'SJ',
                     'SL', 'SO', 'SR', 'ST', 'SU', 'TB', 'TD', 'TF', 'TO', 'TP', 'TT', 'TU'),
            (2, 3): ('BG', 'BH', 'BS', 'GO', 'GS', 'GU', 'HG', 'HH', 'HJ', 'HO', 'HS', 'JG', 'JH', 'JU', 'OB', 'OJ',
                     'OO', 'OS', 'PB', 'PG', 'PH', 'PJ', 'PO', 'PS', 'PU', 'RB', 'RS', 'TJ', 'TO', 'TS', 'VG', 'VJ',
                     'VO', 'VS', 'VU'),
            (2, 4): ('DB', 'DH', 'DK', 'DR', 'DS', 'DV', 'GK', 'GO', 'GS', 'GT', 'JV', 'LH', 'LJ', 'LK', 'LO', 'LR',
                     'LT', 'LV', 'NH', 'NJ', 'NK', 'NO', 'NR', 'NS', 'NT', 'OB', 'OJ', 'OK', 'OO', 'OS', 'RB', 'RS',
                     'RT', 'RV', 'SH', 'SK', 'SO', 'SR', 'SS', 'ST', 'TH', 'TK', 'TT', 'UB', 'UH', 'UK', 'UO', 'US',
                     'UV'),
            (3, 1): ('BB', 'BD', 'BJ', 'BR', 'BT', 'BU', 'GB', 'GL', 'GO', 'GP', 'HF', 'HJ', 'HL', 'HU', 'JF', 'JJ',
                     'JL', 'JP', 'JT', 'JU', 'OB', 'OJ', 'OL', 'OO', 'PD', 'PJ', 'PL', 'PO', 'PR', 'PT', 'PU', 'RB',
                     'RD', 'RF', 'RR', 'TB', 'TF', 'TJ', 'TP', 'TT', 'TU', 'VD', 'VF', 'VJ', 'VU'),
            (3, 2): ('CB', 'CD', 'CF', 'CJ', 'CL', 'CO', 'CP', 'CU', 'DB', 'DJ', 'DL', 'DO', 'DU', 'HJ', 'HL', 'HU',
                     'KD', 'KJ', 'KL', 'KO', 'KP', 'OB', 'OD', 'OJ', 'OL', 'OO', 'PD', 'PJ', 'PL', 'PO', 'PR', 'PT',
                     'PU', 'RB', 'RF', 'SD', 'SF', 'SJ', 'SL', 'SO', 'SR', 'ST', 'SU', 'TF', 'TP', 'TT', 'TU'),
            (3, 3): ('BG', 'BH', 'BJ', 'BU', 'GB', 'GO', 'GS', 'GU', 'HB', 'HG', 'HH', 'HJ', 'HO', 'HS', 'JH', 'JJ',
                     'JS', 'OB', 'OH', 'OJ', 'OO', 'PJ', 'PO', 'PS', 'PU', 'RB', 'RG', 'RS', 'TB', 'TG', 'TH', 'TJ',
                     'VB', 'VH', 'VJ', 'VO', 'VS', 'VU'),
            (3, 4): ('DB', 'DH', 'DJ', 'DK', 'DO', 'DS', 'DV', 'GB', 'GK', 'GO', 'GR', 'GS', 'GT', 'GV', 'JJ', 'JK',
                     'JR', 'JS', 'JT', 'JV', 'LB', 'LH', 'LJ', 'LO', 'LR', 'LT', 'LV', 'NK', 'NO', 'NR', 'NT', 'NV',
                     'OB', 'OH', 'OJ', 'OK', 'OO', 'RB', 'RK', 'RR', 'RS', 'RV', 'SB', 'SH', 'SJ', 'SO', 'SS', 'ST',
                     'TB', 'TH', 'TJ', 'TT', 'UB', 'UH', 'UK', 'UO', 'UR', 'UV'),
            (4, 1): ('BB', 'BD', 'BJ', 'BL', 'BR', 'BT', 'GL', 'GO', 'GP', 'GU', 'HB', 'HF', 'HJ', 'HL', 'HP', 'JD',
                     'JF', 'JJ', 'JL', 'JO', 'JP', 'JT', 'JU', 'OB', 'OF', 'OJ', 'OL', 'OO', 'PB', 'PD', 'PF', 'PJ',
                     'PL', 'PR', 'PT', 'PU', 'RB', 'RD', 'RF', 'RR', 'RT', 'TF', 'TP', 'TT', 'VJ', 'VO', 'VP', 'VT',
                     'VU'),
            (4, 2): ('CB', 'CD', 'CF', 'CJ', 'CL', 'CP', 'CU', 'DB', 'DF', 'DJ', 'DL', 'DP', 'HB', 'HF', 'HJ', 'KF',
                     'KJ', 'KO', 'KP', 'KT', 'OB', 'OD', 'OF', 'OJ', 'OL', 'OO', 'OT', 'PB', 'PD', 'PF', 'PJ', 'PL',
                     'PR', 'PT', 'PU', 'RB', 'RF', 'RT', 'SB', 'SD', 'SF', 'SJ', 'SL', 'SO', 'SU', 'TF', 'TP', 'TT'),
            (4, 3): ('BG', 'BH', 'BJ', 'BS', 'GG', 'GO', 'GS', 'GU', 'HB', 'HJ', 'HS', 'HU', 'JG', 'JH', 'JJ', 'JO',
                     'JU', 'OB', 'OJ', 'OO', 'PB', 'PJ', 'PS', 'PU', 'RB', 'TG', 'TH', 'TO', 'TS', 'TU', 'VG', 'VH',
                     'VJ', 'VO', 'VS', 'VU'),
            (4, 4): ('DB', 'DH', 'DJ', 'DK', 'DR', 'DV', 'GK', 'GO', 'GR', 'GS', 'GV', 'JH', 'JJ', 'JK', 'JR', 'JV',
                     'LB', 'LH', 'LJ', 'LK', 'LR', 'LS', 'LT', 'LV', 'NB', 'NH', 'NK', 'NS', 'NT', 'NV', 'OB', 'OH',
                     'OJ', 'OK', 'OO', 'OV', 'RB', 'RV', 'SH', 'SJ', 'SO', 'SS', 'ST', 'TB', 'TH', 'TK', 'TR', 'TS',
                     'UB', 'UH', 'UO', 'US', 'UV'),
        }

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

    def _iter_recurse(self):
        # print("(%s) %s" % (len(self.solve_order), self.solve_order))
        if len(self.solve_order) == 60:
            if self.side_order[0] == self.side_order[-1]:
                # final inner check
                corner = 1
                c = self.solve_order[0]
                req = self.inner_b_requirements[(corner, c)]
                ok = True
                if len(req) > 0:
                    pre_b = self.solve_order[-1]
                    post_b = self.solve_order[1]
                    bb = self.b_inner[pre_b] + self.b_inner[post_b]
                    ok = bb in req
                    # print('bb %s is %s' % (bb, ok))

                if ok:
                    # print('solution: %s' % repr(self.solve_order))
                    sol = self.solve_order[-7:] + self.solve_order[:-7]
                    yield sol

        else:
            if len(self.solve_order) in (0, 15, 30, 45):
                # add a corner
                prev_side = self.side_order[-1]
                for c in self.c_nrs:
                    if c not in self.solve_order:
                        side_in, side_out = self.c_in_out[c]
                        if side_in == prev_side:
                            self.solve_order.append(c)
                            self.side_order.append(side_out)

                            yield from  self._iter_recurse()

                            self.solve_order = self.solve_order[:-1]
                            self.side_order = self.side_order[:-1]
                # for
            else:
                # add a border
                prev_side = self.side_order[-1]
                nrs = self.in2b_nrs[prev_side]
                for b in nrs:
                    if b not in self.solve_order:
                        side_in, side_out = self.b_in_out[b]
                        if side_in == prev_side:
                            ok = True
                            if len(self.solve_order) in (16, 31, 46):
                                corner = 1 + int((len(self.solve_order) - 1) / 15)
                                c = self.solve_order[-1]
                                req = self.inner_b_requirements[(corner, c)]
                                if len(req) > 0:
                                    prev_b = self.solve_order[-2]
                                    bb = self.b_inner[prev_b] + self.b_inner[b]
                                    ok = bb in req
                                    # print('bb %s is %s' % (bb, ok))

                            if ok:
                                self.solve_order.append(b)
                                self.side_order.append(side_out)

                                yield from self._iter_recurse()

                                self.solve_order = self.solve_order[:-1]
                                self.side_order = self.side_order[:-1]
                # for

    def iter_solutions(self):
        self.solve_order = list()
        self.side_order = list()

        c = self.c_nrs[0]
        side_in, side_out = self.c_in_out[c]
        self.side_order.append(side_in)

        yield from self._iter_recurse()

    def get_first_solution(self):
        for sol in self.iter_solutions():
            # put the last 7 pieces first
            return sol
        return []


# end of file
