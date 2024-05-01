# -*- coding: utf-8 -*-

#  Copyright (c) 2023-2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.http import Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.templatetags.static import static
from BasePieces.models import Block
from Blocks.models import Block2x1

TEMPLATE_SHOW = 'blocks/show2x1.dtl'


block_cache = dict()


class Show2x1View(TemplateView):

    template_name = TEMPLATE_SHOW

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        try:
            nr = int(kwargs['nr'][:8])      # afkappen voor de veiligheid
        except ValueError:
            raise Http404('Not found')

        # maak blokjes van 5 rijen van 4 breed = 20
        nr = int((nr - 1) / 20)
        nr = 1 + nr * 20

        if nr > 1000:
            context['url_prev1000'] = reverse('Blocks:show-2x1', kwargs={'nr': nr-1000})
        if nr > 100:
            context['url_prev100'] = reverse('Blocks:show-2x1', kwargs={'nr': nr-100})
        if nr > 20:
            context['url_prev20'] = reverse('Blocks:show-2x1', kwargs={'nr': nr-20})
        context['url_next20'] = reverse('Blocks:show-2x1', kwargs={'nr': nr+20})
        context['url_next100'] = reverse('Blocks:show-2x1', kwargs={'nr': nr+100})
        context['url_next1000'] = reverse('Blocks:show-2x1', kwargs={'nr': nr+1000})

        context['groups'] = groups = []
        group = []
        blocks = Block2x1.objects.filter(nr__gte=nr, nr__lt=nr+20).order_by('nr')
        for block in blocks:

            try:
                block1 = block_cache[block.block1_nr]
            except KeyError:
                block1 = Block.objects.get(nr=block.block1_nr)
                block_cache[block.block1_nr] = block1

            try:
                block2 = block_cache[block.block2_nr]
            except KeyError:
                block2 = Block.objects.get(nr=block.block2_nr)
                block_cache[block.block2_nr] = block2

            side1 = side1 = block1.get_side(1, block.rot1) + block2.get_side(1, block.rot2)
            block.img_b1 = static('blocks/block_%s.png' % side1[0])
            block.img_b2 = static('blocks/block_%s.png' % side1[1])
            block.img_b3 = static('blocks/block_%s.png' % side1[2])
            block.img_b4 = static('blocks/block_%s.png' % side1[3])

            side3 = block2.get_side(3, block.rot2) + block1.get_side(3, block.rot1)
            block.img_b5 = static('blocks/block_%s.png' % side3[0])
            block.img_b6 = static('blocks/block_%s.png' % side3[1])
            block.img_b7 = static('blocks/block_%s.png' % side3[2])
            block.img_b8 = static('blocks/block_%s.png' % side3[3])

            block.side1 = side1
            block.side2 = side1[3] + side3[0]
            block.side3 = side3
            block.side4 = side3[3] + side1[0]

            group.append(block)
            # print('group: %s' % group)
            if len(group) == 4:
                groups.append(group)
                group = []
        # for

        if len(group):
            groups.append(group)

        return context


# end of file
