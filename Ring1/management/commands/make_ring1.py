# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Pieces2x2.models import TwoSide, TwoSideOptions, Piece2x2
from Pieces2x2.helpers import calc_segment
from Ring1.models import Ring1
import time


class Command(BaseCommand):

    help = "Make all possible combinations of ring1, the outer 2x2 ring"

    """
        +----+----+----+----+----+----+----+----+
        | 1  | 2  | 3  | 4  | 5  | 6  | 7  | 8  |
        +----+----+----+----+----+----+----+----+
        | 9  | 10 |                   | 15 | 16 |
        +----+----+                   +----+----+
        | 17 |                             | 24 |
        +----+                             +----+
        | 25 |                             | 32 |
        +----+                             +----+
        | 33 |                             | 40 |
        +----+                             +----+
        | 41 |                             | 48 |
        +----+----+                   +----+----+
        | 49 | 50 |                   | 55 | 56 |
        +----+----+----+----+----+----+----+----+
        | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |
        +----+----+----+----+----+----+----+----+
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.twoside_border = TwoSide.objects.get(two_sides='XX').nr

        two2nr = dict()
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
        # for
        self.twoside2reverse = dict()
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.twoside2reverse[nr] = rev_nr
        # for

        self.processor = 0
        self.locs = (1, 2, 3, 4, 5, 6, 7, 8,
                     9, 16,
                     17, 24,
                     25, 32,
                     33, 40,
                     41, 48,
                     49, 56,
                     57, 58, 59, 60, 61, 62, 63, 64,
                     10, 15, 50, 55,
                     11, 18, 42, 51, 47, 54, 14, 23)

        self.solve_order = (
                            # 1, 2, 9, 10,
                            # 8, 7, 16, 15,
                            # 58, 49, 50, 41, 59,
                            # 64, 63, 56, 55
                            32, 61, 33, 4,
                            40, 60, 25, 5,
                            )

        # [loc] = [loc on side1..4 or -1 if border or -2 if neighbour is a gap]
        self.neighbours = self._calc_neighbours()

        # [loc] = [4 side nr]
        self.segment_nrs: dict[int, tuple] = dict()
        for loc in self.locs:
            self.segment_nrs[loc] = (calc_segment(loc, 1),
                                     calc_segment(loc, 2),
                                     calc_segment(loc, 3),
                                     calc_segment(loc, 4))
        # for

        self.unused0 = list(range(1, 256+1))

        # remove the hints not in Ring1
        self.unused0.remove(139)      # needed for loc 36
        # self.unused0.remove(208)      # needed for loc 10
        # self.unused0.remove(255)      # needed for loc 15
        # self.unused0.remove(181)      # needed for loc 50
        # self.unused0.remove(249)      # needed for loc 55

        # [1..64] = None or Piece2x2 with side1/2/3/4
        self.board: dict[int, Piece2x2 | None] = {}
        for loc in self.locs:
            self.board[loc] = None

        self.board_order = list()   # solved order (for popping)
        self.board_progress = list()
        self.board_unused = self.unused0[:]
        self.requested_order = list()

        self.prev_tick = time.monotonic()

        self.segment_options = dict()
        self.segment_options_rev = dict()

    def add_arguments(self, parser):
        parser.add_argument('processor', type=int, help='Processor number to use')

    def _calc_neighbours(self):
        neighbours = dict()

        # order of the entries: side 1, 2, 3, 4
        for nr in range(1, 64+1):
            if nr in self.locs:
                if nr == 36:
                    n = (-2, -2, -2, -2)
                else:
                    n = list()
                    col = (nr - 1) % 8
                    row = int((nr - 1) / 8)

                    # side 1
                    if row == 0:
                        n.append(-1)    # outer border
                    elif nr - 8 in self.locs:
                        n.append(nr - 8)
                    else:
                        n.append(-2)    # inner gap

                    # side 2
                    if col == 7:
                        n.append(-1)    # outer border
                    elif nr + 1 in self.locs:
                        n.append(nr + 1)
                    else:
                        n.append(-2)    # inner gap

                    # side 3
                    if row == 7:
                        n.append(-1)    # outer border
                    elif nr + 8 in self.locs:
                        n.append(nr + 8)
                    else:
                        n.append(-2)    # inner gap

                    # side 4
                    if col == 0:
                        n.append(-1)    # outer border
                    elif nr - 1 in self.locs:
                        n.append(nr - 1)
                    else:
                        n.append(-2)    # inner gap

                neighbours[nr] = tuple(n)
        # for
        return neighbours

    def _reverse_sides(self, options):
        return [self.twoside2reverse[two_side] for two_side in options]

    def _board_place(self, p_nr: int, p2x2):
        self.board_order.append(p_nr)
        self.board[p_nr] = p2x2
        self.board_unused.remove(p2x2.nr1)
        self.board_unused.remove(p2x2.nr2)
        self.board_unused.remove(p2x2.nr3)
        self.board_unused.remove(p2x2.nr4)

    def _board_pop(self):
        p_nr = self.board_order[-1]
        self.board_order = self.board_order[:-1]
        p2x2 = self.board[p_nr]
        self.board[p_nr] = None
        self.board_unused.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])

    def _save_ring1(self):
        ring = Ring1()
        for loc in self.locs:
            field = 'nr%s' % loc
            p2x2 = self.board[loc]
            if p2x2:
                nr = p2x2.nr
            else:
                nr = 0
            setattr(ring, field, nr)
        # for

        ring.processor = self.processor
        ring.nr36 = 0
        ring.save()
        self.stdout.write('[INFO] Saved Ring1 with pk=%s' % ring.pk)

    def _query_segment_options(self, segment):
        """ Return the options remaining for a specific segment """
        options = (TwoSideOptions
                   .objects
                   .filter(processor=self.processor,
                           segment=segment)
                   .values_list('two_side', flat=True))
        options = list(options)
        # self.stdout.write('[DEBUG] Segment %s has %s options' % (segment, len(options)))
        return options

    def _get_segments_options(self):
        for loc in self.locs:
            for side in range(1, 4+1):
                segment = calc_segment(loc, side)
                options = self._query_segment_options(segment)
                self.segment_options[segment] = options
                self.segment_options_rev[segment] = self._reverse_sides(options)
        # for

    @staticmethod
    def _iter(loc, unused, options_side1, options_side2, options_side3, options_side4):
        qset = (Piece2x2
                .objects
                .filter(nr1__in=unused,
                        nr2__in=unused,
                        nr3__in=unused,
                        nr4__in=unused))

        if options_side1:
            qset = qset.filter(side1__in=options_side1)
        if options_side2:
            qset = qset.filter(side2__in=options_side2)
        if options_side3:
            qset = qset.filter(side3__in=options_side3)
        if options_side4:
            qset = qset.filter(side4__in=options_side4)

        if loc == 10:
            qset = qset.filter(nr1=208)
        elif loc == 15:
            qset = qset.filter(nr2=255)
        elif loc == 36:
            qset = qset.filter(nr2=139)
        elif loc == 50:
            qset = qset.filter(nr3=181)
        elif loc == 55:
            qset = qset.filter(nr4=249)

        qset = qset.order_by('nr')

        p2x2s = list(qset)

        todo = len(p2x2s)
        # todo = qset.count()
        # print('todo: %s' % todo)

        for p in p2x2s:
            msg = '%s/%s' % (loc, todo)
            yield p, msg
            todo -= 1
        # for

    def _select_next_loc(self):
        """ decide which position on the board to work on """

        if len(self.board_order) < len(self.solve_order):
            return self.solve_order[len(self.board_order)], False, self.board_unused

        qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                       nr2__in=self.board_unused,
                                       nr3__in=self.board_unused,
                                       nr4__in=self.board_unused)

        claims = dict()     # [loc] = (nr, nr, ..)
        single_claims = list()

        for loc in self.locs:
            loc_claims = list()
            if self.board[loc] is None:
                # empty position on the board

                if loc in (10, 15, 50, 55, 11, 18, 42, 51, 47, 54, 14, 23):
                    is_lonely = True
                    for n_loc in self.neighbours[loc]:
                        if n_loc > 0 and self.board[n_loc]:
                            is_lonely = False
                            break
                    # for
                    if is_lonely:
                        claims[loc] = loc_claims
                        continue

                seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
                options_side1 = self.segment_options[seg1]
                options_side2 = self.segment_options[seg2]
                options_side3 = self.segment_options_rev[seg3]
                options_side4 = self.segment_options_rev[seg4]

                n1, n2, n3, n4 = self.neighbours[loc]
                if n1 > 0:
                    p = self.board[n1]
                    if p:
                        options_side1 = [self.twoside2reverse[p.side3]]
                if n2 > 0:
                    p = self.board[n2]
                    if p:
                        options_side2 = [self.twoside2reverse[p.side4]]
                if n3 > 0:
                    p = self.board[n3]
                    if p:
                        options_side3 = [self.twoside2reverse[p.side1]]
                if n4 > 0:
                    p = self.board[n4]
                    if p:
                        options_side4 = [self.twoside2reverse[p.side2]]

                qset2 = qset.filter(side1__in=options_side1,
                                    side2__in=options_side2,
                                    side3__in=options_side3,
                                    side4__in=options_side4)

                if loc in (10, 15, 50, 55, 36):
                    qset2 = qset2.filter(has_hint=True)

                elif loc in (11, 18, 14, 23, 47, 54, 51, 42):
                    qset2 = qset2.filter(has_hint=False,
                                         is_border=False)
                else:
                    qset2 = qset2.filter(is_border=True)

                # find the claims this location has
                # nrs1 = list(qset2.distinct('nr1').values_list('nr1', flat=True))
                # nrs2 = list(qset2.distinct('nr2').values_list('nr2', flat=True))
                # nrs3 = list(qset2.distinct('nr3').values_list('nr3', flat=True))
                # nrs4 = list(qset2.distinct('nr4').values_list('nr4', flat=True))
                nrs1 = list()
                nrs2 = list()
                nrs3 = list()
                nrs4 = list()
                for p2x2 in qset2.all():
                    if len(nrs1) < 2:
                        if p2x2.nr1 not in nrs1:
                            nrs1.append(p2x2.nr1)
                    if len(nrs2) < 2:
                        if p2x2.nr2 not in nrs2:
                            nrs2.append(p2x2.nr2)
                    if len(nrs3) < 2:
                        if p2x2.nr3 not in nrs3:
                            nrs3.append(p2x2.nr3)
                    if len(nrs4) < 2:
                        if p2x2.nr4 not in nrs4:
                            nrs4.append(p2x2.nr4)
                    if len(nrs1) > 1 and len(nrs2) > 1 and len(nrs3) > 1 and len(nrs4) > 1:
                        break
                # for
                if len(nrs1) == 1:
                    loc_claims.append(nrs1[0])
                if len(nrs2) == 1:
                    loc_claims.append(nrs2[0])
                if len(nrs3) == 1:
                    loc_claims.append(nrs3[0])
                if len(nrs4) == 1:
                    loc_claims.append(nrs4[0])

            loc_claims = list(set(loc_claims))
            claims[loc] = loc_claims
            single_claims.extend(loc_claims)
        # for

        # print('claims: %s' % repr(claims))
        # print('single_claims: %s' % repr(single_claims))
        if len(single_claims) != len(set(single_claims)):
            claims_fmt = list()
            for loc, claimed in claims.items():
                if len(claimed) > 0:
                    claims_fmt.append('%s:%s' % (loc, repr(claimed)))
            # for
            self.stdout.write('[DEBUG] Duplicate claims: %s' % ", ".join(claims_fmt))
            return -1, True, []

        tick = time.monotonic()
        if tick - self.prev_tick > 5:
            self.prev_tick = tick
            msg = '(%s) %s' % (len(self.board_order), ", ".join(self.board_progress))
            print(msg)
            claims_fmt = list()
            for loc, claimed in claims.items():
                if len(claimed) > 0:
                    claims_fmt.append('%s:%s' % (loc, repr(claimed)))
            # for
            print('%s %s' % ("     "[:2+len(str(len(self.board_order)))], ", ".join(claims_fmt)))
            # print('%s' % repr(self.board_unused))

        loc_counts = list()
        for loc in self.locs:
            if self.board[loc] is None:
                # empty position on the board

                is_lonely = True
                for n_loc in self.neighbours[loc]:
                    if n_loc > 0 and self.board[n_loc]:
                        is_lonely = False
                        break
                # for
                if is_lonely:
                    continue

                seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
                options_side1 = self.segment_options[seg1]
                options_side2 = self.segment_options[seg2]
                options_side3 = self.segment_options_rev[seg3]
                options_side4 = self.segment_options_rev[seg4]

                n1, n2, n3, n4 = self.neighbours[loc]
                if n1 > 0:
                    p = self.board[n1]
                    if p:
                        options_side1 = [self.twoside2reverse[p.side3]]
                if n2 > 0:
                    p = self.board[n2]
                    if p:
                        options_side2 = [self.twoside2reverse[p.side4]]
                if n3 > 0:
                    p = self.board[n3]
                    if p:
                        options_side3 = [self.twoside2reverse[p.side1]]
                if n4 > 0:
                    p = self.board[n4]
                    if p:
                        options_side4 = [self.twoside2reverse[p.side2]]

                # remove all single claims from the unused pieces
                unused = self.board_unused[:]
                for nr in single_claims:
                    if nr in unused:
                        unused.remove(nr)
                # for

                # add the claims for this specific location
                unused.extend(claims[loc])

                qset = Piece2x2.objects.filter(nr1__in=self.board_unused,
                                               nr2__in=self.board_unused,
                                               nr3__in=self.board_unused,
                                               nr4__in=self.board_unused,
                                               side1__in=options_side1,
                                               side2__in=options_side2,
                                               side3__in=options_side3,
                                               side4__in=options_side4)

                if loc in (10, 15, 50, 55, 36):
                    count = qset.filter(has_hint=True).count()

                elif loc in (11, 18, 14, 23, 47, 54, 51, 42):
                    # if len(self.board_order) < 14:
                    #     continue
                    count = qset.filter(has_hint=False,
                                        is_border=False).count()
                else:
                    # border
                    count = qset.filter(is_border=True).count()

                if count == 0:
                    # dead end
                    self.stdout.write('[DEBUG] No options for %s' % loc)
                    return -1, True, []

                tup = (count, loc)
                loc_counts.append(tup)
        # for

        # take the lowest
        if len(loc_counts) > 0:
            loc_counts.sort()       # lowest first
            loc = loc_counts[0][-1]

            # remove all single claims from the unused pieces
            unused = self.board_unused[:]
            for nr in single_claims:
                if nr in unused:
                    unused.remove(nr)
            # for

            # add the claims needed for the selectie location
            unused.extend(claims[loc])

            # self.stdout.write('[INFO] Added %s' % p_nr)
            return loc, False, unused

        # niets kunnen kiezen
        self.stdout.write('[ERROR] select_next_loc failed')
        self.stdout.write('[DEBUG] solve_order = %s' % repr(self.board_order))
        return -1, True, []

    def _find_recurse(self):
        if len(self.board_order) == len(self.locs):
            self._save_ring1()
            return

        # decide which loc to continue with
        loc, has_zero, unused = self._select_next_loc()
        if has_zero:
            return
        # self.stdout.write('next loc: %s' % loc)

        seg1, seg2, seg3, seg4 = self.segment_nrs[loc]
        options_side1 = self.segment_options[seg1]
        options_side2 = self.segment_options[seg2]
        options_side3 = self.segment_options_rev[seg3]
        options_side4 = self.segment_options_rev[seg4]

        n1, n2, n3, n4 = self.neighbours[loc]
        if n1 >= 0:
            p = self.board[n1]
            if p:
                options_side1 = [self.twoside2reverse[p.side3]]
        if n2 >= 0:
            p = self.board[n2]
            if p:
                options_side2 = [self.twoside2reverse[p.side4]]
        if n3 >= 0:
            p = self.board[n3]
            if p:
                options_side3 = [self.twoside2reverse[p.side1]]
        if n4 >= 0:
            p = self.board[n4]
            if p:
                options_side4 = [self.twoside2reverse[p.side2]]

        for p, msg in self._iter(loc, unused, options_side1, options_side2, options_side3, options_side4):
            self._board_place(loc, p)
            self.board_progress.append(msg)

            self._find_recurse()

            self._board_pop()
            self.board_progress = self.board_progress[:-1]
        # for

    def handle(self, *args, **options):
        self.processor = options['processor']
        self.stdout.write('[INFO] Processor: %s' % self.processor)

        self._get_segments_options()

        try:
            self._find_recurse()
        except KeyboardInterrupt:
            pass

# end of file
