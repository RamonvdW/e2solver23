# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.core.management.base import BaseCommand
from Blocks.models import Block2x1
from Pieces2x2.models import Piece2x2


class Command(BaseCommand):

    help = "Generate all Block2x1 based on the Piece2x2"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._created = set()

    def _create_from_piece2x2(self, nr1, rot1, nr2, rot2):
        tup1 = (nr1, nr2, rot1, rot2)
        self._created.add(tup1)
        tup2 = (nr2, nr1, (rot2 + 2) % 4, (rot1 + 2) % 4)
        self._created.add(tup2)

    def handle(self, *args, **options):

        self.stdout.write('[INFO] Deleting all Block2x1')
        Block2x1.objects.all().delete()

        self.stdout.write('[INFO] Generating all Block2x1 excluding border colors')

        """
            a Block2x1 consists of 8 basic blocks
            constructed from 2 Block that each consists of 4 basic blocks
                  
                      side1
              +----+----+----+----+
              | b1 | b2 | b3 | b4 |
        side4 +----+----+----+----+ side2
              | b8 | b7 | b6 | b5 |
              +----+----+----+----+
                      side3
                      
                      
            from a Piece2x2, two Block2x1 can be constructed over de diagonals
            the Piece2x2 guarantees that the two Block will occur next to each other legally
        """

        qset = Piece2x2.objects.filter(is_border=False).order_by('nr')
        todo = qset.count()
        todo_print = todo
        prev_count = 0
        for p in qset.iterator(chunk_size=100):
            todo -= 1
            if todo < todo_print:
                count = len(self._created)
                self.stdout.write('Piece2x2 todo: %s; Block2x1 generated: %s (+%s)' % (todo,
                                                                                       len(self._created),
                                                                                       count - prev_count))
                prev_count = count
                todo_print -= 100000

            """ a 2x2 piece consists of 4 base pieces, each under a certain rotation

                each side consists of 2 base piece sides and is given a new simple numeric reference

                         side 1
                       +---+---+
                       | 1 | 2 |
                side 4 +---+---+ side 2
                       | 3 | 4 |
                       +---+---+
                         side 3
            """

            # print('Piece2x2 nr: %s' % p.nr)
            # diagonal A: 1+4
            self._create_from_piece2x2(p.nr1, p.rot1,
                                       p.nr4, p.rot4)

            # diagonal B: 3+2
            # rotate the piece to get the right orientation
            self._create_from_piece2x2(p.nr3, (p.rot3 + 3) % 4,
                                       p.nr2, (p.rot2 + 3) % 4)
        # for

        count = len(self._created)
        self.stdout.write('[INFO] Generated %s Block2x1' % count)

        nr = 0
        bulk = list()
        for nr1, nr2, rot1, rot2 in self._created:
            nr += 1
            block2x1 = Block2x1(nr=nr, block1_nr=nr1, block2_nr=nr2, rot1=rot1, rot2=rot2)
            bulk.append(block2x1)
            if len(bulk) > 1000:
                Block2x1.objects.bulk_create(bulk)
                bulk = list()
        # for
        if len(bulk):
            Block2x1.objects.bulk_create(bulk)

# end of file
