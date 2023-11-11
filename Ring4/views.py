# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Borders4x2.models import Border4x2
from Pieces2x2.models import Piece2x2
from Pieces4x4.models import Piece4x4
from Ring4.models import Ring4


TEMPLATE_VIEW = 'ring4/show.dtl'


class ShowView(TemplateView):

    template_name = TEMPLATE_VIEW

    rot2transform = {
        # rotations are counter-clockwise, but CSS rotation are clockwise
        0: 'rotate(0deg)',
        1: 'rotate(270deg)',
        2: 'rotate(180deg)',
        3: 'rotate(90deg)',
        4: 'rotate(0deg)',
        5: 'rotate(270deg)',
        6: 'rotate(180deg)',
        7: 'rotate(90deg)',
    }

    # ring4 is built up clockwise
    # base piece rotations are counter-clockwise
    rot2rot = {
        0: 0,
        1: 3,
        2: 2,
        3: 1,
    }

    def _set_corner(self, piece4x4_nr, rot):
        piece4x4 = Piece4x4.objects.get(nr=piece4x4_nr)

        piece4x4.img1 = static('pieces/%s.png' % piece4x4.nr1)
        piece4x4.img2 = static('pieces/%s.png' % piece4x4.nr2)
        piece4x4.img3 = static('pieces/%s.png' % piece4x4.nr3)
        piece4x4.img4 = static('pieces/%s.png' % piece4x4.nr4)
        piece4x4.img5 = static('pieces/%s.png' % piece4x4.nr5)
        piece4x4.img6 = static('pieces/%s.png' % piece4x4.nr6)
        piece4x4.img7 = static('pieces/%s.png' % piece4x4.nr7)
        piece4x4.img8 = static('pieces/%s.png' % piece4x4.nr8)
        piece4x4.img9 = static('pieces/%s.png' % piece4x4.nr9)
        piece4x4.img10 = static('pieces/%s.png' % piece4x4.nr10)
        piece4x4.img11 = static('pieces/%s.png' % piece4x4.nr11)
        piece4x4.img12 = static('pieces/%s.png' % piece4x4.nr12)
        piece4x4.img13 = static('pieces/%s.png' % piece4x4.nr13)
        piece4x4.img14 = static('pieces/%s.png' % piece4x4.nr14)
        piece4x4.img15 = static('pieces/%s.png' % piece4x4.nr15)
        piece4x4.img16 = static('pieces/%s.png' % piece4x4.nr16)

        rot = self.rot2rot[rot]
        piece4x4.transform1 = self.rot2transform[piece4x4.rot1 + rot]
        piece4x4.transform2 = self.rot2transform[piece4x4.rot2 + rot]
        piece4x4.transform3 = self.rot2transform[piece4x4.rot3 + rot]
        piece4x4.transform4 = self.rot2transform[piece4x4.rot4 + rot]
        piece4x4.transform5 = self.rot2transform[piece4x4.rot5 + rot]
        piece4x4.transform6 = self.rot2transform[piece4x4.rot6 + rot]
        piece4x4.transform7 = self.rot2transform[piece4x4.rot7 + rot]
        piece4x4.transform8 = self.rot2transform[piece4x4.rot8 + rot]
        piece4x4.transform9 = self.rot2transform[piece4x4.rot9 + rot]
        piece4x4.transform10 = self.rot2transform[piece4x4.rot10 + rot]
        piece4x4.transform11 = self.rot2transform[piece4x4.rot11 + rot]
        piece4x4.transform12 = self.rot2transform[piece4x4.rot12 + rot]
        piece4x4.transform13 = self.rot2transform[piece4x4.rot13 + rot]
        piece4x4.transform14 = self.rot2transform[piece4x4.rot14 + rot]
        piece4x4.transform15 = self.rot2transform[piece4x4.rot15 + rot]
        piece4x4.transform16 = self.rot2transform[piece4x4.rot16 + rot]

        return piece4x4

    def _set_border(self, border4x2_nr, rot):
        border4x2 = Border4x2.objects.get(nr=border4x2_nr)

        border4x2.img1 = static('pieces/%s.png' % border4x2.nr1)
        border4x2.img2 = static('pieces/%s.png' % border4x2.nr2)
        border4x2.img3 = static('pieces/%s.png' % border4x2.nr3)
        border4x2.img4 = static('pieces/%s.png' % border4x2.nr4)
        border4x2.img5 = static('pieces/%s.png' % border4x2.nr5)
        border4x2.img6 = static('pieces/%s.png' % border4x2.nr6)
        border4x2.img7 = static('pieces/%s.png' % border4x2.nr7)
        border4x2.img8 = static('pieces/%s.png' % border4x2.nr8)

        rot = self.rot2rot[rot]
        border4x2.transform1 = self.rot2transform[border4x2.rot1 + rot]
        border4x2.transform2 = self.rot2transform[border4x2.rot2 + rot]
        border4x2.transform3 = self.rot2transform[border4x2.rot3 + rot]
        border4x2.transform4 = self.rot2transform[border4x2.rot4 + rot]
        border4x2.transform5 = self.rot2transform[border4x2.rot5 + rot]
        border4x2.transform6 = self.rot2transform[border4x2.rot6 + rot]
        border4x2.transform7 = self.rot2transform[border4x2.rot7 + rot]
        border4x2.transform8 = self.rot2transform[border4x2.rot8 + rot]

        return border4x2

    def _set_ring(self, piece2x2_nr, rot):
        piece = Piece2x2.objects.get(nr=piece2x2_nr)

        piece.img1 = static('pieces/%s.png' % piece.nr1)
        piece.img2 = static('pieces/%s.png' % piece.nr2)
        piece.img3 = static('pieces/%s.png' % piece.nr3)
        piece.img4 = static('pieces/%s.png' % piece.nr4)

        piece.transform1 = self.rot2transform[piece.rot1]
        piece.transform2 = self.rot2transform[piece.rot2]
        piece.transform3 = self.rot2transform[piece.rot3]
        piece.transform4 = self.rot2transform[piece.rot4]

        return piece

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:12])      # afkappen voor de veiligheid
            ring4 = Ring4.objects.get(nr=nr)
        except (ValueError, Ring4.DoesNotExist):
            raise Http404('Not found')

        context['ring4'] = ring4

        ring4.c1 = self._set_corner(ring4.c1, 0)
        ring4.c2 = self._set_corner(ring4.c2, 1)
        ring4.c3 = self._set_corner(ring4.c3, 2)
        ring4.c4 = self._set_corner(ring4.c4, 3)

        ring4.b1 = self._set_border(ring4.b1, 0)
        ring4.b2 = self._set_border(ring4.b2, 0)
        ring4.b3 = self._set_border(ring4.b3, 1)
        ring4.b4 = self._set_border(ring4.b4, 1)
        ring4.b5 = self._set_border(ring4.b5, 2)
        ring4.b6 = self._set_border(ring4.b6, 2)
        ring4.b7 = self._set_border(ring4.b7, 3)
        ring4.b8 = self._set_border(ring4.b8, 3)

        ring4.p1 = self._set_ring(ring4.p1, 0)
        ring4.p2 = self._set_ring(ring4.p2, 0)
        ring4.p3 = self._set_ring(ring4.p3, 0)
        ring4.p4 = self._set_ring(ring4.p4, 0)

        ring4.p5 = self._set_ring(ring4.p5, 1)
        ring4.p6 = self._set_ring(ring4.p6, 1)
        ring4.p7 = self._set_ring(ring4.p7, 1)
        ring4.p8 = self._set_ring(ring4.p8, 1)

        ring4.p9 = self._set_ring(ring4.p9, 2)
        ring4.p10 = self._set_ring(ring4.p10, 2)
        ring4.p11 = self._set_ring(ring4.p11, 2)
        ring4.p12 = self._set_ring(ring4.p12, 2)

        ring4.p13 = self._set_ring(ring4.p13, 3)
        ring4.p14 = self._set_ring(ring4.p14, 3)
        ring4.p15 = self._set_ring(ring4.p15, 3)
        ring4.p16 = self._set_ring(ring4.p16, 3)

        if nr > 1:
            context['url_prev'] = reverse('Ring4:show', kwargs={'nr': nr-1})
        context['url_next'] = reverse('Ring4:show', kwargs={'nr': nr+1})

        return context


# end of file
