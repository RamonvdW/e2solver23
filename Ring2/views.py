# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2
from Ring2.models import Ring2
from types import SimpleNamespace


TEMPLATE_SHOW = 'ring2/show.dtl'


class ShowRing2View(TemplateView):

    template_name = TEMPLATE_SHOW

    rot2transform = {
        # rotations are counter-clockwise, but CSS rotation are clockwise
        0: 'rotate(0deg)',
        1: 'rotate(270deg)',
        2: 'rotate(180deg)',
        3: 'rotate(90deg)',
    }

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        context['title'] = 'Ring2'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring2:show', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring2:show', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring2:show', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring2:show', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring2:show', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring2:show', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring2:show', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring2:show', kwargs={'nr': nr+1000})

        try:
            ring2 = Ring2.objects.get(nr=nr)
        except Ring2.DoesNotExist:
            first = Ring2.objects.order_by('nr').first()
            last = Ring2.objects.order_by('nr').last()
            if first:
                context['url_first'] = reverse('Ring2:show', kwargs={'nr': first.pk})
                if last.pk != first.pk:
                    context['url_last'] = reverse('Ring2:show', kwargs={'nr': last.pk})
            else:
                context['is_empty'] = True
        else:
            context['solution'] = ring2
            ring2.p2x2s = []
            base_nrs = []

            for loc in range(1, 64+1):
                if loc in (1, 2, 3, 4, 5, 6, 7, 8,
                           9, 10, 11, 12, 13, 14, 15, 16,
                           17, 18, 23, 24,
                           25, 26, 31, 32,
                           33, 34, 39, 40,
                           41, 42, 47, 48,
                           49, 50, 51, 52, 53, 54, 55, 56,
                           57, 58, 59, 60, 61, 62, 63, 64):

                    loc_str = 'loc%s' % loc
                    nr = getattr(ring2, loc_str, 0)
                    if nr:
                        p2x2 = Piece2x2.objects.get(nr=nr)

                        p2x2.img1 = static('pieces/%s.png' % p2x2.nr1)
                        p2x2.img2 = static('pieces/%s.png' % p2x2.nr2)
                        p2x2.img3 = static('pieces/%s.png' % p2x2.nr3)
                        p2x2.img4 = static('pieces/%s.png' % p2x2.nr4)

                        p2x2.transform1 = self.rot2transform[p2x2.rot1]
                        p2x2.transform2 = self.rot2transform[p2x2.rot2]
                        p2x2.transform3 = self.rot2transform[p2x2.rot3]
                        p2x2.transform4 = self.rot2transform[p2x2.rot4]

                        base_nrs.extend([p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4])
                    else:
                        p2x2 = SimpleNamespace(is_empty=True,
                                               break_after=False)

                    p2x2.break_after = (loc % 8 == 0)
                else:
                    p2x2 = SimpleNamespace(is_empty=True,
                                           break_after=False)

                ring2.p2x2s.append(p2x2)
            # for

            base_nrs.sort()
            context['base_nrs'] = base_nrs

        return context


# end of file
