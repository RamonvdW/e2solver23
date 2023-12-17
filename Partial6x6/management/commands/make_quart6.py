# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from BasePieces.hints import ALL_HINT_NRS
from Pieces2x2.models import TwoSide, Piece2x2
from Pieces2x2.helpers import LOC_CORNERS, LOC_BORDERS, LOC_HINTS, LOC_NEIGHBOURS
from Partial6x6.models import Quart6


class Command(BaseCommand):

    help = "Quart6 generator"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.verbose = 0
        self.board = dict()   # [nr] = Piece2x2
        for nr in range(1, 64+1):
            self.board[nr] = None
        # for
        self.board_unused_nrs = [nr
                                 for nr in range(1, 256+1)
                                 if nr not in ALL_HINT_NRS]

        self.two_border = TwoSide.objects.get(two_sides='XX').nr
        self.side_nr2reverse = dict()
        two2nr = dict()
        for two in TwoSide.objects.all():
            two2nr[two.two_sides] = two.nr
        # for
        for two_sides, nr in two2nr.items():
            two_rev = two_sides[1] + two_sides[0]
            rev_nr = two2nr[two_rev]
            self.side_nr2reverse[nr] = rev_nr
        # for

    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--reset', action='store_true')

    def _count_2x2(self, nr):
        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        p1 = p2 = p3 = p4 = None
        x1 = x2 = x3 = x4 = None

        if nr in LOC_CORNERS:
            if nr == 1:
                s1 = s4 = self.two_border
            elif nr == 8:
                s1 = s2 = self.two_border
            elif nr == 57:
                s3 = s4 = self.two_border
            else:
                s2 = s3 = self.two_border

        elif nr in LOC_BORDERS:
            if nr < 9:
                s1 = self.two_border
                x2 = self.two_border
                x4 = self.two_border

            elif nr > 57:
                x2 = self.two_border
                s3 = self.two_border
                x4 = self.two_border

            elif nr & 1 == 1:
                x1 = self.two_border
                x3 = self.two_border
                s4 = self.two_border

            else:
                x1 = self.two_border
                s2 = self.two_border
                x3 = self.two_border

        else:
            x1 = x2 = x3 = x4 = self.two_border

            if nr in LOC_HINTS:
                # has_hint = True
                if nr == 10:
                    p1 = 208
                elif nr == 15:
                    p2 = 255
                elif nr == 36:
                    p2 = 139
                elif nr == 50:
                    p3 = 181
                elif nr == 55:
                    p4 = 249

        unused_nrs = self.board_unused_nrs
        must_have_nrs = list()

        qset = Piece2x2.objects.all()

        if s1:
            qset = qset.filter(side1=s1)
        elif x1:
            qset = qset.exclude(side1=x1)

        if s2:
            qset = qset.filter(side2=s2)
        elif x2:
            qset = qset.exclude(side2=x2)

        if s3:
            qset = qset.filter(side3=s3)
        elif x3:
            qset = qset.exclude(side3=x3)

        if s4:
            qset = qset.filter(side4=s4)
        elif x4:
            qset = qset.exclude(side4=x4)

        if p1:
            qset = qset.filter(nr1=p1)
        else:
            qset = qset.filter(nr1__in=unused_nrs)

        if p2:
            qset = qset.filter(nr2=p2)
        else:
            qset = qset.filter(nr2__in=unused_nrs)

        if p3:
            qset = qset.filter(nr3=p3)
        else:
            qset = qset.filter(nr3__in=unused_nrs)

        if p4:
            qset = qset.filter(nr4=p4)
        else:
            qset = qset.filter(nr4__in=unused_nrs)

        count = qset.count()

        if count > 0:
            avail_nr1 = list(qset.distinct('nr1').values_list('nr1', flat=True))
            avail_nr2 = list(qset.distinct('nr2').values_list('nr2', flat=True))
            avail_nr3 = list(qset.distinct('nr3').values_list('nr3', flat=True))
            avail_nr4 = list(qset.distinct('nr4').values_list('nr4', flat=True))

            avail_nrs = set(avail_nr1 + avail_nr2 + avail_nr3 + avail_nr4)
            avail_len = len(avail_nrs)

            if avail_len == 0 or avail_len > 5:
                freedom = str(avail_len)
            else:
                avail_nrs = list(avail_nrs)
                avail_nrs.sort()
                avail_nrs = [str(nr) for nr in avail_nrs]
                freedom = ",".join(avail_nrs)

            for avail in (avail_nr1, avail_nr2, avail_nr3, avail_nr4):
                if len(avail) == 1:
                    must_have_nrs.append(avail[0])
            # for
        else:
            freedom = '0'

        return count, freedom, must_have_nrs

    def _board_free_nr(self, nr):
        p = self.board[nr]
        if p:
            self.board[nr] = None
            free_nrs = [nr for nr in (p.nr1, p.nr2, p.nr3, p.nr4) if nr not in ALL_HINT_NRS]
            self.board_unused_nrs.extend(free_nrs)

    def _board_fill_nr(self, nr, p: Piece2x2):
        if self.verbose:
            self.stdout.write('+[%s] = %s with base nrs %s' % (nr, p.nr, repr([p.nr1, p.nr2, p.nr3, p.nr4])))

        p.exp_s1 = self.side_nr2reverse[p.side3]
        p.exp_s2 = self.side_nr2reverse[p.side4]
        p.exp_s3 = self.side_nr2reverse[p.side1]
        p.exp_s4 = self.side_nr2reverse[p.side2]

        self.board[nr] = p
        for nr in (p.nr1, p.nr2, p.nr3, p.nr4):
            try:
                self.board_unused_nrs.remove(nr)
            except ValueError:
                # happens with the hints
                pass
        # for

    def _get_sides(self, nr):
        nr1, nr2, nr3, nr4 = LOC_NEIGHBOURS[nr]

        s1 = s2 = s3 = s4 = None

        if nr1 > 0:
            p = self.board[nr1]
            if p:
                s1 = p.exp_s1

        if nr2 > 0:
            p = self.board[nr2]
            if p:
                s2 = p.exp_s2

        if nr3 > 0:
            p = self.board[nr3]
            if p:
                s3 = p.exp_s3

        if nr4 > 0:
            p = self.board[nr4]
            if p:
                s4 = p.exp_s4

        return s1, s2, s3, s4

    def _iter_for_nr_no_borders(self, nr):

        # get the sides
        s1, s2, s3, s4 = self._get_sides(nr)
        x1 = x2 = x3 = x4 = self.two_border
        p1 = p2 = p3 = p4 = None

        if nr in LOC_HINTS:
            if nr == 10:
                p1 = 208
            elif nr == 15:
                p2 = 255
            elif nr == 36:
                p2 = 139
            elif nr == 50:
                p3 = 181
            elif nr == 55:
                p4 = 249

        qset = Piece2x2.objects.order_by('nr')

        # skip outer borders
        unused_nrs = [nr for nr in self.board_unused_nrs if nr > 60]

        if s1:
            qset = qset.filter(side1=s1)
        elif x1:
            qset = qset.exclude(side1=x1)

        if s2:
            qset = qset.filter(side2=s2)
        elif x2:
            qset = qset.exclude(side2=x2)

        if s3:
            qset = qset.filter(side3=s3)
        elif x3:
            qset = qset.exclude(side3=x3)

        if s4:
            qset = qset.filter(side4=s4)
        elif x4:
            qset = qset.exclude(side4=x4)

        if p1:
            qset = qset.filter(nr1=p1)
        else:
            qset = qset.filter(nr1__in=unused_nrs)

        if p2:
            qset = qset.filter(nr2=p2)
        else:
            qset = qset.filter(nr2__in=unused_nrs)

        if p3:
            qset = qset.filter(nr3=p3)
        else:
            qset = qset.filter(nr3__in=unused_nrs)

        if p4:
            qset = qset.filter(nr4=p4)
        else:
            qset = qset.filter(nr4__in=unused_nrs)

        # self.stdout.write(qset.explain())

        for p in qset:
            yield p
        # for

    def _can_fill_nrs_no_borders(self, nrs):

        unused_nrs = [nr for nr in self.board_unused_nrs if nr > 60]  # skip borders

        qset = Piece2x2.objects.all()
        qset = qset.filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs)

        for nr in nrs:
            if nr:
                s1, s2, s3, s4 = self._get_sides(nr)
                qset2 = qset

                if s1 and s2 and not s3 and not s4:
                    # s1-s2
                    qset2 = qset2.filter(side1=s1, side2=s2)

                elif not s1 and s2 and s3 and not s4:
                    # s2-s3
                    qset2 = qset2.filter(side2=s2, side3=s3)

                elif not s1 and not s2 and s3 and s4:
                    # s3-s4
                    qset2 = qset2.filter(side3=s3, side4=s4)

                elif s1 and not s2 and not s3 and s4:
                    # s4-s1
                    qset2 = qset2.filter(side4=s4, side1=s1)

                else:
                    if s1:
                        qset2 = qset2.filter(side1=s1)
                    if s2:
                        qset2 = qset2.filter(side2=s2)
                    if s3:
                        qset2 = qset2.filter(side3=s3)
                    if s4:
                        qset2 = qset2.filter(side4=s4)

                first = qset2.first()
                if first is None:
                    return False
        # for
        return True

    def _can_fill_nrs_border(self, nr_c):
        # verify one-site match with opposite side being a border

        """
                      side2
                    +---+---+  <-- border
                    |   |   |
                +---+---+---+
                |   | c | p |
          side1 +---+---+---+
                |   | p |
                +---+---+

        """

        if nr_c == 10:
            p18 = self.board[18]
            p10 = self.board[10]
            p11 = self.board[11]
            sides1 = (p18.exp_s4, p10.exp_s4)
            sides2 = (p10.exp_s1, p11.exp_s1)

        elif nr_c == 15:
            p14 = self.board[14]
            p15 = self.board[15]
            p23 = self.board[23]
            sides1 = (p14.exp_s1, p15.exp_s1)
            sides2 = (p15.exp_s2, p23.exp_s2)

        elif nr_c == 50:
            p51 = self.board[51]
            p50 = self.board[50]
            p42 = self.board[42]
            sides1 = (p51.exp_s3, p50.exp_s3)
            sides2 = (p50.exp_s4, p42.exp_s4)

        elif nr_c == 55:
            p47 = self.board[47]
            p55 = self.board[55]
            p54 = self.board[54]
            sides1 = (p47.exp_s2, p55.exp_s2)
            sides2 = (p55.exp_s3, p54.exp_s3)

        else:
            return False

        unused_nrs = self.board_unused_nrs

        qset = Piece2x2.objects.filter(side1=self.two_border)
        qset = qset.filter(nr1__in=unused_nrs, nr2__in=unused_nrs, nr3__in=unused_nrs, nr4__in=unused_nrs)

        """
                side1=border        
             +---+---+
             |   |   |  side2
             +---+---+
                side3
             
        """

        for p1 in qset.filter(side3=sides1[0]):
            exp_s4 = self.side_nr2reverse[p1.side2]
            p2 = qset.filter(side3=sides1[1], side4=exp_s4).first()
            if not p2:
                return False
            # found at least 1
            break
        # for

        for p3 in qset.filter(side3=sides2[0]):
            exp_s4 = self.side_nr2reverse[p3.side2]
            p4 = qset.filter(side3=sides2[1], side4=exp_s4).first()
            if not p4:
                return False
            # found at least 1
            break
        # for

        return True

    def _generate_quart6(self, nr_p1, nr_c, nr_p2, nr_4x4):
        count = 0
        count_rejected1 = count_rejected2 = 0
        bulk = list()
        for c1 in self._iter_for_nr_no_borders(nr_c):
            self._board_fill_nr(nr_c, c1)

            for p1 in self._iter_for_nr_no_borders(18):
                self._board_fill_nr(nr_p1, p1)

                for p2 in self._iter_for_nr_no_borders(11):
                    self._board_fill_nr(nr_p2, p2)

                    if self._can_fill_nrs_no_borders([nr_4x4]):

                        if self._can_fill_nrs_border(nr_c):

                            quart = Quart6(
                                        processor=0,
                                        based_on_4x4=0,
                                        type=nr_c,
                                        p1=p1.pk,
                                        c1=c1.pk,
                                        p2=p2.pk,
                                        nr1=p1.nr1,
                                        nr2=p1.nr2,
                                        nr3=p1.nr3,
                                        nr4=p1.nr4,
                                        nr5=c1.nr1,
                                        nr6=c1.nr2,
                                        nr7=c1.nr3,
                                        nr8=c1.nr4,
                                        nr9=p2.nr1,
                                        nr10=p2.nr2,
                                        nr11=p2.nr3,
                                        nr12=p2.nr4)

                            bulk.append(quart)
                            if len(bulk) >= 5:
                                count += len(bulk)
                                print('Quart6 type %s: %s (rejected: %s / %s)' % (
                                        nr_c, count, count_rejected1, count_rejected2))
                                Quart6.objects.bulk_create(bulk)
                                bulk = list()
                        else:
                            count_rejected1 += 1
                    else:
                        count_rejected2 += 1

                    self._board_free_nr(nr_p2)
                # for

                self._board_free_nr(nr_p1)
            # for

            self._board_free_nr(nr_c)
        # for

        if len(bulk) > 0:
            count += len(bulk)
            Quart6.objects.bulk_create(bulk)

        print('Quart6 type %s: %s (rejected: %s / %s)' % (nr_c, count, count_rejected1, count_rejected2))

    def handle(self, *args, **options):

        if options['verbose']:
            self.verbose += 1

        if options['reset']:
            self.stdout.write('[WARNING] Deleting all Quart6')
            Quart6.objects.all().delete()

        try:
            self._generate_quart6(18, 10, 11, 19)
            self._generate_quart6(14, 15, 23, 22)
            self._generate_quart6(51, 50, 42, 43)
            self._generate_quart6(47, 55, 54, 46)

        except KeyboardInterrupt:
            pass

# end of file
