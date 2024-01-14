# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import IntegrityError
from WorkQueue.models import Work, ProcessorUsedPieces


def _segment_to_loc_1(segment):
    """ reverse of calc_segment
        returns the locations above/below or left/right of the segment
    """

    if 130 <= segment <= 192:
        loc_a = segment - 129       # left of the segment
        loc_b = segment - 128       # right of the segment

    elif 9 <= segment <= 64:
        loc_a = segment - 8         # above the segment
        loc_b = segment             # below the segment

    else:
        loc_a = 0
        loc_b = 0

    locs = list()
    if 1 <= loc_a <= 64:
        locs.append(loc_a)
    if 1 <= loc_b <= 64:
        locs.append(loc_b)

    return tuple(locs)


def _segment_to_loc_4(segment):
    """ reverse of calc_segment
        returns the locations where to run the eval_loc_4
    """

    loc1_a, loc1_b = _segment_to_loc_1(segment)

    if segment > 128:
        # left/right

        # loc1_a = -1, 0
        # loc1_b = +1, 0

        loc_a = loc1_a - 1 - 8  # -2, -1
        loc_b = loc_a + 1       # -1, -1
        loc_c = loc_b + 1       # +1, -1

        loc_d = loc_a + 8       # -2, 0
        loc_e = loc_b + 8       # -1, 0
        loc_f = loc_c + 8       # +1, 0

    else:
        # above/below

        # loc1_a = 0, -1
        # loc1_b = 0, +1

        loc_a = loc1_a - 8 - 1  # -1, -2
        loc_b = loc_a + 8       # -1, -1
        loc_c = loc_b + 8       # -1, +1

        loc_d = loc_a + 1       # 0, -2
        loc_e = loc_b + 1       # 0, -1
        loc_f = loc_c + 1       # 0, +1

    locs = list()
    for loc in (loc_a, loc_b, loc_c, loc_d, loc_e, loc_f):
        if 1 <= loc <= 55 and loc not in (8, 16, 24, 32, 40, 48):
            locs.append(loc)
        else:
            locs.append(-1)
    # for

    return tuple(locs)


def _segment_to_loc_9(segment):
    """ reverse of calc_segment
        returns the locations where to run the eval_loc_9
    """
    loc1_a, loc1_b = _segment_to_loc_1(segment)

    if segment > 128:
        # left/right

        # loc1_a = -1, 0
        # loc1_b = +1, 0

        loc_1 = loc1_a - 18     # -3, -2
        loc_2 = loc_1 + 1       # -2, -2
        loc_3 = loc_2 + 1       # -1, -2
        loc_4 = loc_3 + 1       # +1, -2

        loc_5 = loc_1 + 8       # -3, -1
        loc_6 = loc_2 + 8       # -2, -1
        loc_7 = loc_3 + 8       # -1, -1
        loc_8 = loc_4 + 8       # +1, -1

        loc_9 = loc_5 + 8       # -3, 0
        loc_10 = loc_6 + 8      # -2, 0
        loc_11 = loc_7 + 8      # -1, 0
        loc_12 = loc_8 + 8      # +1, 0

    else:
        # above/below

        # loc1_a = 0, -1
        # loc1_b = 0, +1

        loc_1 = loc1_a - 18     # -2, -3
        loc_2 = loc_1 + 1       # -1, -3
        loc_3 = loc_2 + 1       # _0, -3

        loc_4 = loc_1 + 8       # -2, -2
        loc_5 = loc_2 + 8       # -1, -2
        loc_6 = loc_3 + 8       # _0, -2

        loc_7 = loc_4 + 8       # -2, -1
        loc_8 = loc_5 + 8       # -1, -1
        loc_9 = loc_6 + 8       # _0, -1

        loc_10 = loc_7 + 8      # -2, +1
        loc_11 = loc_8 + 8      # -1, +1
        loc_12 = loc_9 + 8      # _0, +1

    locs = list()
    for loc in (loc_1, loc_2, loc_3, loc_4, loc_5, loc_6, loc_7, loc_8, loc_9, loc_10, loc_11, loc_12):
        if 1 <= loc <= 55 and loc not in (8, 16, 24, 32, 40, 48):
            locs.append(loc)
        else:
            locs.append(-1)
    # for

    return tuple(locs)


def _add_work(processor, priority, job_type, location):
    if location > 0:
        count = Work.objects.filter(done=False,
                                    processor=processor, job_type=job_type, location=location).count()

        if count == 0:
            # not a duplicate
            # (new duplicate due to race condition is still possible though)
            Work(done=False, doing=False,
                 processor=processor, job_type=job_type, location=location,
                 priority=priority).save()


def propagate_segment_reduction(processor, segment):

    # Note: propagating results in repeated evaluation of the same location

    # eval_loc_1
    loc_a, loc_b = _segment_to_loc_1(segment)

    _add_work(processor, 1, 'eval_loc_1', loc_a)
    _add_work(processor, 1, 'eval_loc_1', loc_b)

    # eval_loc_4
    loc_a, loc_b, loc_c, loc_d, loc_e, loc_f = _segment_to_loc_4(segment)

    _add_work(processor, 5, 'eval_loc_4', loc_a)
    _add_work(processor, 4, 'eval_loc_4', loc_b)
    _add_work(processor, 5, 'eval_loc_4', loc_c)
    _add_work(processor, 5, 'eval_loc_4', loc_d)
    _add_work(processor, 4, 'eval_loc_4', loc_e)
    _add_work(processor, 5, 'eval_loc_4', loc_f)

    # eval_loc_9
    # loc_1, loc_2, loc_3, loc_4, loc_5, loc_6, loc_7, loc_8, loc_9, loc_10, loc_11, loc_12 = _segment_to_loc_9(segment)
    #
    # _add_work(processor, 9, 'eval_loc_9', loc_1)
    # _add_work(processor, 9, 'eval_loc_9', loc_2)
    # _add_work(processor, 9, 'eval_loc_9', loc_3)
    # _add_work(processor, 9, 'eval_loc_9', loc_4)
    # _add_work(processor, 9, 'eval_loc_9', loc_5)
    # _add_work(processor, 9, 'eval_loc_9', loc_6)
    # _add_work(processor, 9, 'eval_loc_9', loc_7)
    # _add_work(processor, 9, 'eval_loc_9', loc_8)
    # _add_work(processor, 9, 'eval_loc_9', loc_9)
    # _add_work(processor, 9, 'eval_loc_9', loc_10)
    # _add_work(processor, 9, 'eval_loc_9', loc_11)
    # _add_work(processor, 9, 'eval_loc_9', loc_12)

    #location = segment_to_loc_16(segment)


def get_unused(processor):
    """ return the list with unused based piece numbers """

    unused = list(range(1, 256+1))
    try:
        used = ProcessorUsedPieces.objects.get(processor=processor)
    except ProcessorUsedPieces.DoesNotExist:
        # not available; so simple return all
        pass
    else:
        for nr in range(1, 256+1):
            nr_str = 'nr%s' % nr
            if getattr(used, nr_str, False):
                # this piece is used
                unused.remove(nr)
        # for

    return unused


def set_used(processor, base_nrs):
    try:
        used = ProcessorUsedPieces.objects.get(processor=processor)
    except ProcessorUsedPieces.DoesNotExist:
        # not available; so simple skip
        pass
    else:
        updated = list()
        for nr in base_nrs:
            nr_str = 'nr%s' % nr
            setattr(used, nr_str, True)
            updated.append(nr_str)
        # for
        used.save(update_fields=updated)


# end of file
