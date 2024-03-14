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
            # c,b: c=first to fourth corner placed, b=corner base nr
            (1, 1): ('BB', 'BD', 'BF', 'BJ', 'BL', 'BO', 'BR', 'BT', 'BU', 'GB', 'GD', 'GL', 'GO', 'GP', 'GT', 'GU',
                     'HB', 'HD', 'HF', 'HJ', 'HL', 'HO', 'HP', 'HU', 'JD', 'JF', 'JJ', 'JO', 'JP', 'JR', 'JT', 'JU',
                     'OB', 'OD', 'OF', 'OJ', 'OL', 'OO', 'OT', 'OU', 'PB', 'PD', 'PF', 'PJ', 'PL', 'PO', 'PR', 'PT',
                     'PU', 'RB', 'RF', 'RL', 'RP', 'RR', 'RT', 'TB', 'TD', 'TF', 'TJ', 'TL', 'TO', 'TP', 'TR', 'TT',
                     'TU', 'VD', 'VJ', 'VO', 'VP', 'VR', 'VT', 'VU'),
            (1, 2): ('CB', 'CD', 'CF', 'CJ', 'CL', 'CO', 'CP', 'CR', 'CT', 'CU', 'DB', 'DF', 'DJ', 'DL', 'DO', 'DP',
                     'DR', 'HB', 'HD', 'HF', 'HJ', 'HL', 'HU', 'KD', 'KF', 'KJ', 'KL', 'KP', 'KR', 'KT', 'OB', 'OD',
                     'OF', 'OJ', 'OL', 'OO', 'OT', 'OU', 'PD', 'PF', 'PJ', 'PL', 'PO', 'PR', 'PT', 'PU', 'RB', 'RD',
                     'RF', 'RL', 'RP', 'RT', 'SB', 'SD', 'SF', 'SJ', 'SL', 'SO', 'SR', 'ST', 'SU', 'TB', 'TF', 'TJ',
                     'TL', 'TO', 'TP', 'TU'),
            (1, 3): ('BB', 'BG', 'BH', 'BJ', 'BO', 'BS', 'BU', 'GB', 'GG', 'GO', 'GU', 'HB', 'HG', 'HH', 'HJ', 'HO',
                     'HS', 'HU', 'JB', 'JH', 'JJ', 'JO', 'JS', 'OB', 'OJ', 'OO', 'OS', 'PB', 'PG', 'PH', 'PJ', 'PO',
                     'PS', 'PU', 'RB', 'RG', 'RH', 'RS', 'TB', 'TG', 'TH', 'TJ', 'TO', 'TS', 'TU', 'VB', 'VG', 'VH',
                     'VJ', 'VO', 'VU'),
            (1, 4): ('DB', 'DJ', 'DK', 'DO', 'DR', 'DS', 'DV', 'GB', 'GK', 'GO', 'GR', 'GT', 'GV', 'JB', 'JH', 'JJ',
                     'JK', 'JO', 'JR', 'JS', 'JT', 'JV', 'LB', 'LH', 'LJ', 'LK', 'LO', 'LR', 'LS', 'LT', 'LV', 'NB',
                     'NJ', 'NK', 'NO', 'NR', 'NS', 'NT', 'NV', 'OB', 'OJ', 'OK', 'OO', 'OS', 'OT', 'RB', 'RH', 'RK',
                     'RR', 'RS', 'RT', 'RV', 'SH', 'SJ', 'SK', 'SO', 'SR', 'SS', 'ST', 'TB', 'TH', 'TJ', 'TK', 'TO',
                     'TR', 'TS', 'TT', 'UB', 'UH', 'UJ', 'UK', 'UO', 'UR', 'US', 'UV'),

            (2, 1): ('BB', 'BD', 'BF', 'BJ', 'BL', 'BO', 'BR', 'BT', 'BU', 'GB', 'GD', 'GL', 'GO', 'GP', 'GR', 'GT',
                     'GU', 'HB', 'HF', 'HJ', 'HL', 'HO', 'HP', 'HU', 'JB', 'JD', 'JF', 'JJ', 'JL', 'JO', 'JP', 'JR',
                     'OB', 'OD', 'OF', 'OJ', 'OL', 'OO', 'OT', 'PB', 'PD', 'PF', 'PJ', 'PO', 'PR', 'PT', 'PU', 'RB',
                     'RD', 'RF', 'RR', 'RT', 'TB', 'TD', 'TF', 'TO', 'TP', 'TT', 'VB', 'VD', 'VF', 'VJ', 'VO', 'VP',
                     'VR', 'VT', 'VU'),
            (2, 2): ('CB', 'CD', 'CF', 'CJ', 'CO', 'CP', 'CR', 'CT', 'CU', 'DB', 'DF', 'DL', 'DO', 'DP', 'DR', 'DU',
                     'HB', 'HF', 'HJ', 'HL', 'HO', 'HP', 'HU', 'KD', 'KF', 'KJ', 'KL', 'KO', 'KP', 'KR', 'KT', 'OB',
                     'OD', 'OF', 'OJ', 'OL', 'OO', 'OT', 'PB', 'PD', 'PF', 'PJ', 'PL', 'PO', 'PT', 'PU', 'RB', 'RD',
                     'RF', 'RT', 'SD', 'SF', 'SJ', 'SL', 'SO', 'SR', 'ST', 'SU', 'TB', 'TD', 'TF', 'TP', 'TR', 'TT'),
            (2, 3): ('BB', 'BG', 'BH', 'BJ', 'BO', 'BS', 'GB', 'GO', 'GS', 'GU', 'HH', 'HJ', 'HO', 'HS', 'HU', 'JG',
                     'JH', 'JJ', 'JO', 'OB', 'OJ', 'OO', 'OS', 'PB', 'PJ', 'PO', 'PS', 'PU', 'RB', 'RG', 'RH', 'RS',
                     'TB', 'TG', 'TH', 'TO', 'TS', 'VG', 'VJ', 'VO', 'VU'),
            (2, 4): ('DB', 'DH', 'DJ', 'DK', 'DO', 'DR', 'DS', 'DV', 'GK', 'GO', 'GS', 'GT', 'GV', 'JH', 'JJ', 'JK',
                     'JO', 'JT', 'JV', 'LB', 'LH', 'LJ', 'LK', 'LO', 'LR', 'LS', 'LT', 'LV', 'NB', 'NH', 'NJ', 'NK',
                     'NO', 'NR', 'NS', 'NT', 'OB', 'OJ', 'OO', 'OS', 'OT', 'RB', 'RK', 'RR', 'RS', 'RT', 'RV', 'SB',
                     'SH', 'SJ', 'SO', 'SR', 'SS', 'ST', 'TB', 'TH', 'TK', 'TO', 'TS', 'TT', 'UB', 'UH', 'UJ', 'UK',
                     'UO', 'UR', 'US', 'UV'),

            (3, 1): ('BB', 'BD', 'BJ', 'BL', 'BR', 'BT', 'BU', 'GB', 'GD', 'GL', 'GO', 'GP', 'GU', 'HD', 'HF', 'HJ',
                     'HL', 'HP', 'HU', 'JF', 'JJ', 'JL', 'JP', 'JT', 'JU', 'OB', 'OF', 'OJ', 'OL', 'OO', 'PB', 'PD',
                     'PJ', 'PL', 'PO', 'PR', 'PT', 'PU', 'RB', 'RD', 'RF', 'RR', 'RT', 'TB', 'TF', 'TJ', 'TP', 'TT',
                     'TU', 'VB', 'VD', 'VF', 'VJ', 'VO', 'VP', 'VR', 'VU'),
            (3, 2): ('CB', 'CD', 'CF', 'CJ', 'CL', 'CO', 'CP', 'CT', 'CU', 'DB', 'DF', 'DJ', 'DL', 'DO', 'DP', 'DU',
                     'HD', 'HJ', 'HL', 'HU', 'KD', 'KJ', 'KL', 'KO', 'KP', 'OB', 'OD', 'OF', 'OJ', 'OL', 'OO', 'PB',
                     'PD', 'PJ', 'PL', 'PO', 'PR', 'PT', 'PU', 'RB', 'RF', 'SD', 'SF', 'SJ', 'SL', 'SO', 'SR', 'ST',
                     'SU', 'TF', 'TO', 'TP', 'TT', 'TU'),
            (3, 3): ('BG', 'BH', 'BJ', 'BS', 'BU', 'GB', 'GO', 'GS', 'GU', 'HB', 'HG', 'HH', 'HJ', 'HO', 'HS', 'HU',
                     'JH', 'JJ', 'JS', 'JU', 'OB', 'OH', 'OJ', 'OO', 'PJ', 'PO', 'PS', 'PU', 'RB', 'RG', 'RH', 'RS',
                     'TB', 'TG', 'TH', 'TJ', 'TS', 'TU', 'VB', 'VH', 'VJ', 'VO', 'VS', 'VU'),
            (3, 4): ('DB', 'DH', 'DJ', 'DK', 'DO', 'DS', 'DV', 'GB', 'GK', 'GO', 'GR', 'GS', 'GT', 'GV', 'JH', 'JJ',
                     'JK', 'JR', 'JS', 'JT', 'JV', 'LB', 'LH', 'LJ', 'LO', 'LR', 'LT', 'LV', 'NB', 'NH', 'NJ', 'NK',
                     'NO', 'NR', 'NS', 'NT', 'NV', 'OB', 'OH', 'OJ', 'OK', 'OO', 'OT', 'OV', 'RB', 'RK', 'RR', 'RS',
                     'RT', 'RV', 'SB', 'SH', 'SJ', 'SO', 'SS', 'ST', 'TB', 'TH', 'TJ', 'TS', 'TT', 'UB', 'UH', 'UK',
                     'UO', 'UR', 'US', 'UV'),

            (4, 1): ('BB', 'BD', 'BF', 'BJ', 'BL', 'BR', 'BT', 'GL', 'GO', 'GP', 'GU', 'HB', 'HF', 'HJ', 'HL', 'HO',
                     'HP', 'JD', 'JF', 'JJ', 'JL', 'JO', 'JP', 'JT', 'JU', 'OB', 'OF', 'OJ', 'OL', 'OO', 'OT', 'PB',
                     'PD', 'PF', 'PJ', 'PL', 'PR', 'PT', 'PU', 'RB', 'RD', 'RF', 'RR', 'RT', 'TF', 'TJ', 'TL', 'TO',
                     'TP', 'TT', 'VB', 'VF', 'VJ', 'VO', 'VP', 'VT', 'VU'),
            (4, 2): ('CB', 'CD', 'CF', 'CJ', 'CL', 'CP', 'CU', 'DB', 'DF', 'DJ', 'DL', 'DP', 'HB', 'HF', 'HJ', 'HL',
                     'HO', 'KF', 'KJ', 'KO', 'KP', 'KT', 'OB', 'OD', 'OF', 'OJ', 'OL', 'OO', 'OT', 'PB', 'PD', 'PF',
                     'PJ', 'PL', 'PR', 'PT', 'PU', 'RB', 'RD', 'RF', 'RT', 'SB', 'SD', 'SF', 'SJ', 'SL', 'SO', 'SU',
                     'TF', 'TO', 'TP', 'TT'),
            (4, 3): ('BB', 'BG', 'BH', 'BJ', 'BS', 'GG', 'GO', 'GS', 'GU', 'HB', 'HJ', 'HO', 'HS', 'HU', 'JG', 'JH',
                     'JJ', 'JO', 'JU', 'OB', 'OJ', 'OO', 'OS', 'PB', 'PJ', 'PS', 'PU', 'RB', 'TB', 'TG', 'TH', 'TJ',
                     'TO', 'TS', 'TU', 'VB', 'VG', 'VH', 'VJ', 'VO', 'VS', 'VU'),
            (4, 4): ('DB', 'DH', 'DJ', 'DK', 'DR', 'DV', 'GK', 'GO', 'GR', 'GS', 'GT', 'GV', 'JH', 'JJ', 'JK', 'JO',
                     'JR', 'JT', 'JV', 'LB', 'LH', 'LJ', 'LK', 'LR', 'LS', 'LT', 'LV', 'NB', 'NH', 'NK', 'NS', 'NT',
                     'NV', 'OB', 'OH', 'OJ', 'OK', 'OO', 'OS', 'OT', 'OV', 'RB', 'RK', 'RR', 'RT', 'RV', 'SH', 'SJ',
                     'SO', 'SS', 'ST', 'TB', 'TH', 'TK', 'TO', 'TR', 'TS', 'TT', 'UB', 'UH', 'UJ', 'UK', 'UO', 'UR',
                     'US', 'UV'),
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
            # solution is complete, but is it correct?
            if self.side_order[0] == self.side_order[-1]:
                # the sides match
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
                    # reorganize cbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbb
                    #       into bbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbbbbbbbbbcbbbbbbb
                    sol = self.solve_order[-7:] + self.solve_order[:-7]
                    yield sol

        elif len(self.solve_order) in (0, 15, 30, 45):
            # add a corner
            prev_side = self.side_order[-1]
            for c in self.c_nrs:
                if c not in self.solve_order:
                    # corner is unused
                    side_in, side_out = self.c_in_out[c]
                    if side_in == prev_side:
                        # corner fits
                        self.solve_order.append(c)
                        self.side_order.append(side_out)

                        yield from self._iter_recurse()

                        self.solve_order = self.solve_order[:-1]
                        self.side_order = self.side_order[:-1]
            # for
        else:
            # add a border
            prev_side = self.side_order[-1]
            nrs = self.in2b_nrs[prev_side]      # all possible pieces with that specific side
            for b in nrs:
                if b not in self.solve_order:
                    # base piece is unused
                    side_in, side_out = self.b_in_out[b]
                    if side_in == prev_side:
                        # piece fits
                        ok = True
                        if len(self.solve_order) in (16, 31, 46):
                            # just beyond a corner
                            corner = 1 + int((len(self.solve_order) - 1) / 15)
                            # corner: 2, 3 or 4
                            c = self.solve_order[-1]        # corner base nr
                            req = self.inner_b_requirements[(corner, c)]
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
