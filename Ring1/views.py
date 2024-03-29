# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2
from Ring1.models import Ring1
from types import SimpleNamespace


TEMPLATE_SHOW = 'ring1/show.dtl'


class ShowRing1View(TemplateView):

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

        context['title'] = 'Ring1'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring1:show', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring1:show', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring1:show', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring1:show', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring1:show', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring1:show', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring1:show', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring1:show', kwargs={'nr': nr+1000})

        try:
            ring1 = Ring1.objects.get(nr=nr)
        except Ring1.DoesNotExist:
            first = Ring1.objects.order_by('nr').first()
            last = Ring1.objects.order_by('nr').last()
            if first:
                context['url_first'] = reverse('Ring1:show', kwargs={'nr': first.pk})
                if last.pk != first.pk:
                    context['url_last'] = reverse('Ring1:show', kwargs={'nr': last.pk})
            else:
                context['is_empty'] = True
        else:
            context['solution'] = ring1
            ring1.p2x2s = []
            base_nrs = []

            for p_nr in range(1, 64+1):
                if p_nr in (1, 2, 3, 4, 5, 6, 7, 8,
                            9, 16, 17, 24, 25, 32, 33, 40, 41, 48, 49, 56, 57,
                            58, 59, 60, 61, 62, 63, 64,
                            10, 11, 18,
                            14, 15, 23,
                            42, 50, 51,
                            54, 55, 47,
                            36):

                    nr_str = 'nr%s' % p_nr
                    nr = getattr(ring1, nr_str, 0)
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

                    p2x2.break_after = (p_nr % 8 == 0)
                else:
                    p2x2 = SimpleNamespace(is_empty=True,
                                           break_after=False)

                ring1.p2x2s.append(p2x2)
            # for

            base_nrs.sort()
            context['base_nrs'] = base_nrs

        return context


# end of file
