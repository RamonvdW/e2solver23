# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from WorkQueue.models import Work


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
        returns the locations -2, -1 from the segment
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
        if 1 <= loc_a <= 55 and loc not in (8, 16, 24, 32, 40, 48):
            locs.append(loc)
        else:
            locs.append(-1)
    # for

    return tuple(locs)


def _add_work(processor, priority, job_type, location):
    if location > 0:
        work, _ = Work.objects.get_or_create(done=False, doing=False,
                                             processor=processor, priority=priority,
                                             job_type=job_type, location=location)
        work.save()


def propagate_segment_reduction(processor, segment):

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

    #location = segment_to_loc_9(segment)
    #location = segment_to_loc_16(segment)


# end of file