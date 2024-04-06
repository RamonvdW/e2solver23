# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.utils import timezone
from Pieces2x2.models import TwoSideOptions
from WorkQueue.models import Work, ProcessorUsedPieces


def _segment_to_loc_1(segment):
    """ reverse of calc_segment
        returns the locations above/below or left/right of the segment
    """

    if 102 <= segment <= 164:
        loc_a = segment - 101       # loc left of the segment
        loc_b = segment - 100       # loc right of the segment

    elif 9 <= segment <= 64:
        loc_a = segment - 8         # loc above the segment
        loc_b = segment             # loc below the segment

    else:
        loc_a = 0
        loc_b = 0

    locs = []
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
        # loc_c = loc_b + 1       # +1, -1

        # loc_d = loc_a + 8       # -2, 0
        loc_e = loc_b + 8       # -1, 0
        # loc_f = loc_c + 8       # +1, 0

    else:
        # above/below

        # loc1_a = 0, -1
        # loc1_b = 0, +1

        loc_a = loc1_a - 8 - 1  # -1, -2
        loc_b = loc_a + 8       # -1, -1
        # loc_c = loc_b + 8       # -1, +1

        # loc_d = loc_a + 1       # 0, -2
        loc_e = loc_b + 1       # 0, -1
        # loc_f = loc_c + 1       # 0, +1

    locs = []
    for loc in (loc_b, loc_e):  # (loc_a, loc_b, loc_c, loc_d, loc_e, loc_f):
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

    locs = []
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
    # loc_a, loc_b, loc_c, loc_d, loc_e, loc_f = _segment_to_loc_4(segment)
    loc_b, loc_e = _segment_to_loc_4(segment)

    # _add_work(processor, 5, 'eval_loc_4', loc_a)
    _add_work(processor, 4, 'eval_loc_4', loc_b)
    # _add_work(processor, 5, 'eval_loc_4', loc_c)
    # _add_work(processor, 5, 'eval_loc_4', loc_d)
    _add_work(processor, 4, 'eval_loc_4', loc_e)
    # _add_work(processor, 5, 'eval_loc_4', loc_f)

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

    # location = segment_to_loc_16(segment)


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


def get_unused_for_locs(processor, locs):
    """ return the list with unused based piece numbers
        when working on the given locations
    """

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

        for claim in used.claimed_nrs_single.split(','):
            if claim:
                nr_str, loc_str = claim.split(':')
                loc = int(loc_str)
                if loc not in locs:
                    nr = int(nr_str)
                    if nr in unused:
                        unused.remove(nr)
        # for

        for claim in used.claimed_nrs_double.split(','):
            if claim:
                nr_str, locs_str = claim.split(':')
                spl = locs_str.split(';')
                loc1 = int(spl[0])
                loc2 = int(spl[1])
                if loc1 not in locs and loc2 not in locs:
                    nr = int(nr_str)
                    if nr in unused:
                        unused.remove(nr)
        # for

    return unused


# def set_used(processor, base_nrs):
#     try:
#         used = ProcessorUsedPieces.objects.get(processor=processor)
#     except ProcessorUsedPieces.DoesNotExist:
#         # not available; so simple skip
#         pass
#     else:
#         updated = []
#         for nr in base_nrs:
#             nr_str = 'nr%s' % nr
#             setattr(used, nr_str, True)
#             updated.append(nr_str)
#         # for
#         used.save(update_fields=updated)


def set_loc_used(processor, loc, p2x2):
    try:
        used = ProcessorUsedPieces.objects.get(processor=processor)
    except ProcessorUsedPieces.DoesNotExist:
        # not available; so simple skip
        pass
    else:
        loc_str = 'loc%s' % loc
        setattr(used, loc_str, p2x2.nr)
        updated = [loc_str]
        for nr in [p2x2.nr1, p2x2.nr2, p2x2.nr3, p2x2.nr4]:
            nr_str = 'nr%s' % nr
            setattr(used, nr_str, True)
            updated.append(nr_str)
        # for
        used.save(update_fields=updated)


def used_note_add(processor, msg):
    try:
        used = ProcessorUsedPieces.objects.get(processor=processor)
    except ProcessorUsedPieces.DoesNotExist:
        # not available; so simple return all
        pass
    else:
        now = timezone.localtime(timezone.now())
        stamp_str = now.strftime('%Y-%m-%d %H:%M')
        used.choices += "[%s] %s\n" % (stamp_str, msg)
        used.save(update_fields=['choices'])


def request_eval_claims(processor):
    try:
        used = ProcessorUsedPieces.objects.get(processor=processor)
    except ProcessorUsedPieces.DoesNotExist:
        # not available; so simple skip
        pass
    else:
        count = TwoSideOptions.objects.filter(processor=processor).count()
        diff = used.claimed_at_twoside_count - count
        if diff > 5:
            perc = diff / count
            if perc > 0.05:
                # 5% reduction
                if Work.objects.filter(processor=processor, job_type='eval_claims', done=False).count() == 0:
                    Work(processor=processor, job_type='eval_claims', priority='2').save()


def set_dead_end(processor):
    """ Use this method to report a dead end that has been found
        This aborts further processing by all other evaluators.
    """
    ProcessorUsedPieces.objects.filter(processor=processor).update(reached_dead_end=True)


def check_dead_end(processor):
    """ Returns True when a dead end has been reached and processing should stop """
    try:
        used = ProcessorUsedPieces.objects.get(processor=processor)
    except ProcessorUsedPieces.DoesNotExist:
        # not available anymore; so assume deleted == dead end
        return True

    return used.reached_dead_end


# end of file
