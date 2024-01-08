# -*- coding: utf-8 -*-

#  Copyright (c) 2024 Ramon van der Winkel.
#  All rights reserved.
#  Licensed under BSD-3-Clause-Clear. See LICENSE file for details.

from django.db import models


class Work(models.Model):

    """ Some work waiting to be executed """

    # has it been completed?
    done = models.BooleanField(default=False)

    # has it been picked up?
    # after restarting the worker queue all 'doing' tasks are reset
    doing = models.BooleanField(default=False)

    # free-format description of the task to execute
    job_type = models.CharField(max_length=20, default='')

    # lower number is higher priority
    priority = models.PositiveSmallIntegerField(default=0)

    # related to which processor?
    processor = models.PositiveIntegerField(default=0)

    # which location (1..64)?
    location = models.PositiveSmallIntegerField(default=0)

    # when was this job requested?
    when_added = models.DateTimeField(auto_now_add=True)

    when_done = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '[%s] %s %s %s %s' % (self.pk,
                                     self.when_added.strftime('%Y-%m-%d %H:%M'),
                                     self.job_type, self.processor, self.location)

    class Meta:
        verbose_name_plural = verbose_name = 'Work'

    objects = models.Manager()  # for the editor only


# end of file
