# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.views.generic import TemplateView
from django.templatetags.static import static
from BasePieces.models import Block
from types import SimpleNamespace

TEMPLATE_BASE_PIECES = 'basepieces/base_pieces.dtl'
TEMPLATE_BLOCKS = 'basepieces/blocks.dtl'


class PiecesView(TemplateView):

    template_name = TEMPLATE_BASE_PIECES

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        context['groups'] = groups = []
        group = []
        for nr in range(1, 256+1):
            piece = SimpleNamespace(nr=nr, img=static('pieces/%s.png' % nr))
            group.append(piece)
            if len(group) == 8:
                groups.append(group)
                group = []
        # for

        return context


class BlocksView(TemplateView):

    template_name = TEMPLATE_BLOCKS

    def get_context_data(self, **kwargs):
        """ called by the template system to get the context data for the template """
        context = super().get_context_data(**kwargs)

        context['groups'] = groups = []
        group = []
        for block in Block.objects.order_by('nr'):
            block.img_b1 = static('blocks/block_%s.png' % block.b1)
            block.img_b2 = static('blocks/block_%s.png' % block.b2)
            block.img_b3 = static('blocks/block_%s.png' % block.b3)
            block.img_b4 = static('blocks/block_%s.png' % block.b4)

            group.append(block)
            if len(group) == 8:
                groups.append(group)
                group = []
        # for

        return context


# end of file
