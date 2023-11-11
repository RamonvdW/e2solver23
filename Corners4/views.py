# -*- coding: utf-8 -*-

#  Copyright (c) 2023 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Borders4x2.models import Border4x2
from Corners4.models import Corner4
from Pieces2x2.models import Piece2x2
from Pieces4x4.models import Piece4x4


TEMPLATE_VIEW = 'corners4/show.dtl'


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

    # corners4 is built up clockwise
    # base piece rotations are counter-clockwise
    rot2rot = {
        0: 0,
        1: 3,
        2: 2,
        3: 1,
    }

    def _set_corner(self, piece4x4_nr):
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

        piece4x4.transform1 = self.rot2transform[piece4x4.rot1]
        piece4x4.transform2 = self.rot2transform[piece4x4.rot2]
        piece4x4.transform3 = self.rot2transform[piece4x4.rot3]
        piece4x4.transform4 = self.rot2transform[piece4x4.rot4]
        piece4x4.transform5 = self.rot2transform[piece4x4.rot5]
        piece4x4.transform6 = self.rot2transform[piece4x4.rot6]
        piece4x4.transform7 = self.rot2transform[piece4x4.rot7]
        piece4x4.transform8 = self.rot2transform[piece4x4.rot8]
        piece4x4.transform9 = self.rot2transform[piece4x4.rot9]
        piece4x4.transform10 = self.rot2transform[piece4x4.rot10]
        piece4x4.transform11 = self.rot2transform[piece4x4.rot11]
        piece4x4.transform12 = self.rot2transform[piece4x4.rot12]
        piece4x4.transform13 = self.rot2transform[piece4x4.rot13]
        piece4x4.transform14 = self.rot2transform[piece4x4.rot14]
        piece4x4.transform15 = self.rot2transform[piece4x4.rot15]
        piece4x4.transform16 = self.rot2transform[piece4x4.rot16]

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

    def _set_piece2x2(self, nr):
        piece = Piece2x2.objects.get(nr=nr)

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
            corner = Corner4.objects.get(nr=nr)
        except (ValueError, Corner4.DoesNotExist):
            raise Http404('Not found')

        context['corner'] = corner

        corner.c = self._set_corner(corner.c)

        corner.b1 = self._set_border(corner.b1, 3)
        corner.b2 = self._set_border(corner.b2, 0)

        corner.p1 = self._set_piece2x2(corner.p1)
        corner.p2 = self._set_piece2x2(corner.p2)

        if nr > 1:
            context['url_prev1'] = reverse('Corners4:show', kwargs={'nr': nr-1})
        if nr > 10:
            context['url_prev10'] = reverse('Corners4:show', kwargs={'nr': nr - 10})
        if nr > 100:
            context['url_prev100'] = reverse('Corners4:show', kwargs={'nr': nr - 100})
        if nr > 1000:
            context['url_prev1000'] = reverse('Corners4:show', kwargs={'nr': nr - 1000})
        context['url_next1'] = reverse('Corners4:show', kwargs={'nr': nr + 1})
        context['url_next10'] = reverse('Corners4:show', kwargs={'nr': nr + 10})
        context['url_next100'] = reverse('Corners4:show', kwargs={'nr': nr + 100})
        context['url_next1000'] = reverse('Corners4:show', kwargs={'nr': nr + 1000})

        return context


# end of file
