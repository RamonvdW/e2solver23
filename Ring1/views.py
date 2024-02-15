# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from Pieces2x2.models import Piece2x2
from Ring1.models import Ring1, Corner1, Corner2, Corner3, Corner4, Corner12, Corner34
from WorkQueue.models import Work
from types import SimpleNamespace


TEMPLATE_SHOW = 'ring1/show.dtl'
TEMPLATE_STATUS = 'ring1/status.dtl'


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
            if first:
                context['url_first'] = reverse('Ring1:show', kwargs={'nr': first.pk})
            else:
                context['is_empty'] = True
        else:
            context['solution'] = ring1
            ring1.p2x2s = list()
            base_nrs = list()

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


class ShowCorner1View(TemplateView):

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

        context['title'] = 'Corner1'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring1:show-c1', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring1:show-c1', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring1:show-c1', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring1:show-c1', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring1:show-c1', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring1:show-c1', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring1:show-c1', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring1:show-c1', kwargs={'nr': nr+1000})

        try:
            corner1 = Corner1.objects.get(nr=nr)
        except Corner1.DoesNotExist:
            first = Corner1.objects.order_by('nr').first()
            if first:
                context['url_first'] = reverse('Ring1:show-c1', kwargs={'nr': first.pk})
        else:
            # convert to Ring1
            ring1 = Ring1()
            for nr in (1, 2, 3, 4, 9, 10, 11, 17, 18, 25):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner1, loc_str, 0))
            # for

            context['solution'] = ring1
            ring1.p2x2s = list()
            base_nrs = list()

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


class ShowCorner2View(TemplateView):

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

        context['title'] = 'Corner2'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring1:show-c2', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring1:show-c2', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring1:show-c2', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring1:show-c2', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring1:show-c2', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring1:show-c2', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring1:show-c2', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring1:show-c2', kwargs={'nr': nr+1000})

        try:
            corner2 = Corner2.objects.get(nr=nr)
        except Corner2.DoesNotExist:
            first = Corner2.objects.order_by('nr').first()
            if first:
                context['url_first'] = reverse('Ring1:show-c2', kwargs={'nr': first.pk})
        else:
            # convert to Ring1
            ring1 = Ring1()
            for nr in (5, 6, 7, 8, 14, 15, 16, 23, 24, 32):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner2, loc_str, 0))
            # for

            context['solution'] = ring1
            ring1.p2x2s = list()
            base_nrs = list()

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


class ShowCorner3View(TemplateView):

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

        context['title'] = 'Corner3'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring1:show-c3', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring1:show-c3', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring1:show-c3', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring1:show-c3', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring1:show-c3', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring1:show-c3', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring1:show-c3', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring1:show-c3', kwargs={'nr': nr+1000})

        try:
            corner3 = Corner3.objects.get(nr=nr)
        except Corner3.DoesNotExist:
            first = Corner3.objects.order_by('nr').first()
            if first:
                context['url_first'] = reverse('Ring1:show-c3', kwargs={'nr': first.pk})
        else:
            # convert to Ring1
            ring1 = Ring1()
            for nr in (61, 62, 63, 64, 54, 55, 56, 47, 48, 40):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner3, loc_str, 0))
            # for

            context['solution'] = ring1
            ring1.p2x2s = list()
            base_nrs = list()

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


class ShowCorner4View(TemplateView):

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

        context['title'] = 'Corner4'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring1:show-c4', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring1:show-c4', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring1:show-c4', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring1:show-c4', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring1:show-c4', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring1:show-c4', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring1:show-c4', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring1:show-c4', kwargs={'nr': nr+1000})

        try:
            corner4 = Corner4.objects.get(nr=nr)
        except Corner4.DoesNotExist:
            first = Corner4.objects.order_by('nr').first()
            if first:
                context['url_first'] = reverse('Ring1:show-c4', kwargs={'nr': first.pk})
        else:
            # convert to Ring1
            ring1 = Ring1()
            for nr in (57, 58, 59, 60, 49, 50, 51, 41, 42, 33):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner4, loc_str, 0))
            # for

            context['solution'] = ring1
            ring1.p2x2s = list()
            base_nrs = list()

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


class ShowCorner12View(TemplateView):

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

        context['title'] = 'Corner12'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring1:show-c12', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring1:show-c12', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring1:show-c12', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring1:show-c12', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring1:show-c12', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring1:show-c12', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring1:show-c12', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring1:show-c12', kwargs={'nr': nr+1000})

        try:
            corner12 = Corner12.objects.get(nr=nr)
        except Corner12.DoesNotExist:
            first = Corner12.objects.order_by('nr').first()
            if first:
                context['url_first'] = reverse('Ring1:show-c12', kwargs={'nr': first.pk})
        else:
            corner1 = Corner1.objects.get(nr=corner12.c1)
            corner2 = Corner2.objects.get(nr=corner12.c2)

            # convert to Ring1
            ring1 = Ring1()
            for nr in (1, 2, 3, 4, 9, 10, 11, 17, 18, 25):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner1, loc_str, 0))
            # for
            for nr in (5, 6, 7, 8, 14, 15, 16, 23, 24, 32):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner2, loc_str, 0))
            # for

            context['solution'] = ring1
            ring1.p2x2s = list()
            base_nrs = list()

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


class ShowCorner34View(TemplateView):

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

        context['title'] = 'Corner34'

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        if nr > 1000:
            context['url_prev1000'] = reverse('Ring1:show-c34', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Ring1:show-c34', kwargs={'nr': nr-100})
        if nr > 10:
            context['url_prev10'] = reverse('Ring1:show-c34', kwargs={'nr': nr-10})
        if nr > 1:
            context['url_prev1'] = reverse('Ring1:show-c34', kwargs={'nr': nr-1})
        context['url_next1'] = reverse('Ring1:show-c34', kwargs={'nr': nr+1})
        context['url_next10'] = reverse('Ring1:show-c34', kwargs={'nr': nr+10})
        context['url_next100'] = reverse('Ring1:show-c34', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Ring1:show-c34', kwargs={'nr': nr+1000})

        try:
            corner34 = Corner34.objects.get(nr=nr)
        except Corner34.DoesNotExist:
            first = Corner34.objects.order_by('nr').first()
            if first:
                context['url_first'] = reverse('Ring1:show-c34', kwargs={'nr': first.pk})
        else:
            corner3 = Corner3.objects.get(nr=corner34.c3)
            corner4 = Corner4.objects.get(nr=corner34.c4)

            # convert to Ring1
            ring1 = Ring1()
            for nr in (40, 47, 48, 54, 55, 56, 61, 62, 63, 64):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner3, loc_str, 0))
            # for
            for nr in (33, 41, 42, 49, 50, 51, 57, 58, 59, 60):
                nr_str = 'nr%s' % nr
                loc_str = 'loc%s' % nr
                setattr(ring1, nr_str, getattr(corner4, loc_str, 0))
            # for

            context['solution'] = ring1
            ring1.p2x2s = list()
            base_nrs = list()

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


class StatusView(TemplateView):

    template_name = TEMPLATE_STATUS

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        c1_seeds = list(Corner1.objects.distinct('seed').values_list('seed', flat=True))
        c2_seeds = list(Corner2.objects.distinct('seed').values_list('seed', flat=True))
        c3_seeds = list(Corner3.objects.distinct('seed').values_list('seed', flat=True))
        c4_seeds = list(Corner4.objects.distinct('seed').values_list('seed', flat=True))
        c12_seeds = list(Corner12.objects.distinct('seed').values_list('seed', flat=True))
        c34_seeds = list(Corner34.objects.distinct('seed').values_list('seed', flat=True))
        r1_seeds = list(Ring1.objects.distinct('seed').values_list('seed', flat=True))

        for work in Work.objects.exclude(seed=0):
            if work.job_type == 'make_c1':
                c1_seeds.append(work.seed)
            if work.job_type == 'make_c2':
                c2_seeds.append(work.seed)
            if work.job_type == 'make_c3':
                c3_seeds.append(work.seed)
            if work.job_type == 'make_c4':
                c4_seeds.append(work.seed)
            if work.job_type == 'make_c12':
                c12_seeds.append(work.seed)
            if work.job_type == 'make_c34':
                c34_seeds.append(work.seed)
            if work.job_type == 'make_ring1':
                r1_seeds.append(work.seed)
        # for

        all_seeds = frozenset(c1_seeds + c2_seeds + c3_seeds + c4_seeds + c12_seeds + c34_seeds + r1_seeds)
        all_seeds = list(all_seeds)
        all_seeds.sort()

        context['seeds'] = table = list()

        for seed in all_seeds:
            row = SimpleNamespace(seed=seed)

            if seed in c1_seeds:
                row.c1_count = Corner1.objects.filter(seed=seed).count()
                row.c1_work = Work.objects.filter(job_type='make_c1', seed=seed).first()

            if seed in c2_seeds:
                row.c2_count = Corner2.objects.filter(seed=seed).count()
                row.c2_work = Work.objects.filter(job_type='make_c2', seed=seed).first()

            if seed in c3_seeds:
                row.c3_count = Corner3.objects.filter(seed=seed).count()
                row.c3_work = Work.objects.filter(job_type='make_c3', seed=seed).first()

            if seed in c4_seeds:
                row.c4_count = Corner4.objects.filter(seed=seed).count()
                row.c4_work = Work.objects.filter(job_type='make_c4', seed=seed).first()

            if seed in c12_seeds:
                row.c12_count = Corner12.objects.filter(seed=seed).count()
                row.c12_work = Work.objects.filter(job_type='make_c12', seed=seed).first()

            if seed in c34_seeds:
                row.c34_count = Corner34.objects.filter(seed=seed).count()
                row.c34_work = Work.objects.filter(job_type='make_c34', seed=seed).first()

            if seed in r1_seeds:
                row.r1_count = Ring1.objects.filter(seed=seed).count()
                row.r1_work = Work.objects.filter(job_type='make_ring1', seed=seed).first()

            table.append(row)
        # for

        return context


# end of file
