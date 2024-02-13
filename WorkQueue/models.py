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

    # limit to pass along: 1..289
    # (0 = not in use)
    limit = models.PositiveSmallIntegerField(default=0)

    # which seed (for Ring1)
    seed = models.PositiveSmallIntegerField(default=0)

    # when was this job requested?
    when_added = models.DateTimeField(auto_now_add=True)

    when_done = models.DateTimeField(auto_now_add=True)

    # delayed start?
    start_after = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '[%s] %s %s %s %s' % (self.pk,
                                     self.when_added.strftime('%Y-%m-%d %H:%M'),
                                     self.job_type, self.processor, self.location)

    class Meta:
        verbose_name_plural = verbose_name = 'Work'

    objects = models.Manager()  # for the editor only


class ProcessorUsedPieces(models.Model):

    # related to which processor?
    processor = models.PositiveIntegerField(default=0)

    # from which processor was duplication done?
    created_from = models.PositiveIntegerField(default=0)

    # out of all 256 base pieces, which ones are in use?
    nr1 = models.BooleanField(default=False)
    nr2 = models.BooleanField(default=False)
    nr3 = models.BooleanField(default=False)
    nr4 = models.BooleanField(default=False)
    nr5 = models.BooleanField(default=False)
    nr6 = models.BooleanField(default=False)
    nr7 = models.BooleanField(default=False)
    nr8 = models.BooleanField(default=False)
    nr9 = models.BooleanField(default=False)
    nr10 = models.BooleanField(default=False)
    nr11 = models.BooleanField(default=False)
    nr12 = models.BooleanField(default=False)
    nr13 = models.BooleanField(default=False)
    nr14 = models.BooleanField(default=False)
    nr15 = models.BooleanField(default=False)
    nr16 = models.BooleanField(default=False)
    nr17 = models.BooleanField(default=False)
    nr18 = models.BooleanField(default=False)
    nr19 = models.BooleanField(default=False)
    nr20 = models.BooleanField(default=False)
    nr21 = models.BooleanField(default=False)
    nr22 = models.BooleanField(default=False)
    nr23 = models.BooleanField(default=False)
    nr24 = models.BooleanField(default=False)
    nr25 = models.BooleanField(default=False)
    nr26 = models.BooleanField(default=False)
    nr27 = models.BooleanField(default=False)
    nr28 = models.BooleanField(default=False)
    nr29 = models.BooleanField(default=False)
    nr30 = models.BooleanField(default=False)
    nr31 = models.BooleanField(default=False)
    nr32 = models.BooleanField(default=False)
    nr33 = models.BooleanField(default=False)
    nr34 = models.BooleanField(default=False)
    nr35 = models.BooleanField(default=False)
    nr36 = models.BooleanField(default=False)
    nr37 = models.BooleanField(default=False)
    nr38 = models.BooleanField(default=False)
    nr39 = models.BooleanField(default=False)
    nr40 = models.BooleanField(default=False)
    nr41 = models.BooleanField(default=False)
    nr42 = models.BooleanField(default=False)
    nr43 = models.BooleanField(default=False)
    nr44 = models.BooleanField(default=False)
    nr45 = models.BooleanField(default=False)
    nr46 = models.BooleanField(default=False)
    nr47 = models.BooleanField(default=False)
    nr48 = models.BooleanField(default=False)
    nr49 = models.BooleanField(default=False)
    nr50 = models.BooleanField(default=False)
    nr51 = models.BooleanField(default=False)
    nr52 = models.BooleanField(default=False)
    nr53 = models.BooleanField(default=False)
    nr54 = models.BooleanField(default=False)
    nr55 = models.BooleanField(default=False)
    nr56 = models.BooleanField(default=False)
    nr57 = models.BooleanField(default=False)
    nr58 = models.BooleanField(default=False)
    nr59 = models.BooleanField(default=False)
    nr60 = models.BooleanField(default=False)
    nr61 = models.BooleanField(default=False)
    nr62 = models.BooleanField(default=False)
    nr63 = models.BooleanField(default=False)
    nr64 = models.BooleanField(default=False)
    nr65 = models.BooleanField(default=False)
    nr66 = models.BooleanField(default=False)
    nr67 = models.BooleanField(default=False)
    nr68 = models.BooleanField(default=False)
    nr69 = models.BooleanField(default=False)
    nr70 = models.BooleanField(default=False)
    nr71 = models.BooleanField(default=False)
    nr72 = models.BooleanField(default=False)
    nr73 = models.BooleanField(default=False)
    nr74 = models.BooleanField(default=False)
    nr75 = models.BooleanField(default=False)
    nr76 = models.BooleanField(default=False)
    nr77 = models.BooleanField(default=False)
    nr78 = models.BooleanField(default=False)
    nr79 = models.BooleanField(default=False)
    nr80 = models.BooleanField(default=False)
    nr81 = models.BooleanField(default=False)
    nr82 = models.BooleanField(default=False)
    nr83 = models.BooleanField(default=False)
    nr84 = models.BooleanField(default=False)
    nr85 = models.BooleanField(default=False)
    nr86 = models.BooleanField(default=False)
    nr87 = models.BooleanField(default=False)
    nr88 = models.BooleanField(default=False)
    nr89 = models.BooleanField(default=False)
    nr90 = models.BooleanField(default=False)
    nr91 = models.BooleanField(default=False)
    nr92 = models.BooleanField(default=False)
    nr93 = models.BooleanField(default=False)
    nr94 = models.BooleanField(default=False)
    nr95 = models.BooleanField(default=False)
    nr96 = models.BooleanField(default=False)
    nr97 = models.BooleanField(default=False)
    nr98 = models.BooleanField(default=False)
    nr99 = models.BooleanField(default=False)
    nr100 = models.BooleanField(default=False)
    nr101 = models.BooleanField(default=False)
    nr102 = models.BooleanField(default=False)
    nr103 = models.BooleanField(default=False)
    nr104 = models.BooleanField(default=False)
    nr105 = models.BooleanField(default=False)
    nr106 = models.BooleanField(default=False)
    nr107 = models.BooleanField(default=False)
    nr108 = models.BooleanField(default=False)
    nr109 = models.BooleanField(default=False)
    nr110 = models.BooleanField(default=False)
    nr111 = models.BooleanField(default=False)
    nr112 = models.BooleanField(default=False)
    nr113 = models.BooleanField(default=False)
    nr114 = models.BooleanField(default=False)
    nr115 = models.BooleanField(default=False)
    nr116 = models.BooleanField(default=False)
    nr117 = models.BooleanField(default=False)
    nr118 = models.BooleanField(default=False)
    nr119 = models.BooleanField(default=False)
    nr120 = models.BooleanField(default=False)
    nr121 = models.BooleanField(default=False)
    nr122 = models.BooleanField(default=False)
    nr123 = models.BooleanField(default=False)
    nr124 = models.BooleanField(default=False)
    nr125 = models.BooleanField(default=False)
    nr126 = models.BooleanField(default=False)
    nr127 = models.BooleanField(default=False)
    nr128 = models.BooleanField(default=False)
    nr129 = models.BooleanField(default=False)
    nr130 = models.BooleanField(default=False)
    nr131 = models.BooleanField(default=False)
    nr132 = models.BooleanField(default=False)
    nr133 = models.BooleanField(default=False)
    nr134 = models.BooleanField(default=False)
    nr135 = models.BooleanField(default=False)
    nr136 = models.BooleanField(default=False)
    nr137 = models.BooleanField(default=False)
    nr138 = models.BooleanField(default=False)
    nr139 = models.BooleanField(default=False)
    nr140 = models.BooleanField(default=False)
    nr141 = models.BooleanField(default=False)
    nr142 = models.BooleanField(default=False)
    nr143 = models.BooleanField(default=False)
    nr144 = models.BooleanField(default=False)
    nr145 = models.BooleanField(default=False)
    nr146 = models.BooleanField(default=False)
    nr147 = models.BooleanField(default=False)
    nr148 = models.BooleanField(default=False)
    nr149 = models.BooleanField(default=False)
    nr150 = models.BooleanField(default=False)
    nr151 = models.BooleanField(default=False)
    nr152 = models.BooleanField(default=False)
    nr153 = models.BooleanField(default=False)
    nr154 = models.BooleanField(default=False)
    nr155 = models.BooleanField(default=False)
    nr156 = models.BooleanField(default=False)
    nr157 = models.BooleanField(default=False)
    nr158 = models.BooleanField(default=False)
    nr159 = models.BooleanField(default=False)
    nr160 = models.BooleanField(default=False)
    nr161 = models.BooleanField(default=False)
    nr162 = models.BooleanField(default=False)
    nr163 = models.BooleanField(default=False)
    nr164 = models.BooleanField(default=False)
    nr165 = models.BooleanField(default=False)
    nr166 = models.BooleanField(default=False)
    nr167 = models.BooleanField(default=False)
    nr168 = models.BooleanField(default=False)
    nr169 = models.BooleanField(default=False)
    nr170 = models.BooleanField(default=False)
    nr171 = models.BooleanField(default=False)
    nr172 = models.BooleanField(default=False)
    nr173 = models.BooleanField(default=False)
    nr174 = models.BooleanField(default=False)
    nr175 = models.BooleanField(default=False)
    nr176 = models.BooleanField(default=False)
    nr177 = models.BooleanField(default=False)
    nr178 = models.BooleanField(default=False)
    nr179 = models.BooleanField(default=False)
    nr180 = models.BooleanField(default=False)
    nr181 = models.BooleanField(default=False)
    nr182 = models.BooleanField(default=False)
    nr183 = models.BooleanField(default=False)
    nr184 = models.BooleanField(default=False)
    nr185 = models.BooleanField(default=False)
    nr186 = models.BooleanField(default=False)
    nr187 = models.BooleanField(default=False)
    nr188 = models.BooleanField(default=False)
    nr189 = models.BooleanField(default=False)
    nr190 = models.BooleanField(default=False)
    nr191 = models.BooleanField(default=False)
    nr192 = models.BooleanField(default=False)
    nr193 = models.BooleanField(default=False)
    nr194 = models.BooleanField(default=False)
    nr195 = models.BooleanField(default=False)
    nr196 = models.BooleanField(default=False)
    nr197 = models.BooleanField(default=False)
    nr198 = models.BooleanField(default=False)
    nr199 = models.BooleanField(default=False)
    nr200 = models.BooleanField(default=False)
    nr201 = models.BooleanField(default=False)
    nr202 = models.BooleanField(default=False)
    nr203 = models.BooleanField(default=False)
    nr204 = models.BooleanField(default=False)
    nr205 = models.BooleanField(default=False)
    nr206 = models.BooleanField(default=False)
    nr207 = models.BooleanField(default=False)
    nr208 = models.BooleanField(default=False)
    nr209 = models.BooleanField(default=False)
    nr210 = models.BooleanField(default=False)
    nr211 = models.BooleanField(default=False)
    nr212 = models.BooleanField(default=False)
    nr213 = models.BooleanField(default=False)
    nr214 = models.BooleanField(default=False)
    nr215 = models.BooleanField(default=False)
    nr216 = models.BooleanField(default=False)
    nr217 = models.BooleanField(default=False)
    nr218 = models.BooleanField(default=False)
    nr219 = models.BooleanField(default=False)
    nr220 = models.BooleanField(default=False)
    nr221 = models.BooleanField(default=False)
    nr222 = models.BooleanField(default=False)
    nr223 = models.BooleanField(default=False)
    nr224 = models.BooleanField(default=False)
    nr225 = models.BooleanField(default=False)
    nr226 = models.BooleanField(default=False)
    nr227 = models.BooleanField(default=False)
    nr228 = models.BooleanField(default=False)
    nr229 = models.BooleanField(default=False)
    nr230 = models.BooleanField(default=False)
    nr231 = models.BooleanField(default=False)
    nr232 = models.BooleanField(default=False)
    nr233 = models.BooleanField(default=False)
    nr234 = models.BooleanField(default=False)
    nr235 = models.BooleanField(default=False)
    nr236 = models.BooleanField(default=False)
    nr237 = models.BooleanField(default=False)
    nr238 = models.BooleanField(default=False)
    nr239 = models.BooleanField(default=False)
    nr240 = models.BooleanField(default=False)
    nr241 = models.BooleanField(default=False)
    nr242 = models.BooleanField(default=False)
    nr243 = models.BooleanField(default=False)
    nr244 = models.BooleanField(default=False)
    nr245 = models.BooleanField(default=False)
    nr246 = models.BooleanField(default=False)
    nr247 = models.BooleanField(default=False)
    nr248 = models.BooleanField(default=False)
    nr249 = models.BooleanField(default=False)
    nr250 = models.BooleanField(default=False)
    nr251 = models.BooleanField(default=False)
    nr252 = models.BooleanField(default=False)
    nr253 = models.BooleanField(default=False)
    nr254 = models.BooleanField(default=False)
    nr255 = models.BooleanField(default=False)
    nr256 = models.BooleanField(default=False)

    # p2x2 nr for each location
    loc1 = models.PositiveIntegerField(default=0)
    loc2 = models.PositiveIntegerField(default=0)
    loc3 = models.PositiveIntegerField(default=0)
    loc4 = models.PositiveIntegerField(default=0)
    loc5 = models.PositiveIntegerField(default=0)
    loc6 = models.PositiveIntegerField(default=0)
    loc7 = models.PositiveIntegerField(default=0)
    loc8 = models.PositiveIntegerField(default=0)
    loc9 = models.PositiveIntegerField(default=0)
    loc10 = models.PositiveIntegerField(default=0)
    loc11 = models.PositiveIntegerField(default=0)
    loc12 = models.PositiveIntegerField(default=0)
    loc13 = models.PositiveIntegerField(default=0)
    loc14 = models.PositiveIntegerField(default=0)
    loc15 = models.PositiveIntegerField(default=0)
    loc16 = models.PositiveIntegerField(default=0)
    loc17 = models.PositiveIntegerField(default=0)
    loc18 = models.PositiveIntegerField(default=0)
    loc19 = models.PositiveIntegerField(default=0)
    loc20 = models.PositiveIntegerField(default=0)
    loc21 = models.PositiveIntegerField(default=0)
    loc22 = models.PositiveIntegerField(default=0)
    loc23 = models.PositiveIntegerField(default=0)
    loc24 = models.PositiveIntegerField(default=0)
    loc25 = models.PositiveIntegerField(default=0)
    loc26 = models.PositiveIntegerField(default=0)
    loc27 = models.PositiveIntegerField(default=0)
    loc28 = models.PositiveIntegerField(default=0)
    loc29 = models.PositiveIntegerField(default=0)
    loc30 = models.PositiveIntegerField(default=0)
    loc31 = models.PositiveIntegerField(default=0)
    loc32 = models.PositiveIntegerField(default=0)
    loc33 = models.PositiveIntegerField(default=0)
    loc34 = models.PositiveIntegerField(default=0)
    loc35 = models.PositiveIntegerField(default=0)
    loc36 = models.PositiveIntegerField(default=0)
    loc37 = models.PositiveIntegerField(default=0)
    loc38 = models.PositiveIntegerField(default=0)
    loc39 = models.PositiveIntegerField(default=0)
    loc40 = models.PositiveIntegerField(default=0)
    loc41 = models.PositiveIntegerField(default=0)
    loc42 = models.PositiveIntegerField(default=0)
    loc43 = models.PositiveIntegerField(default=0)
    loc44 = models.PositiveIntegerField(default=0)
    loc45 = models.PositiveIntegerField(default=0)
    loc46 = models.PositiveIntegerField(default=0)
    loc47 = models.PositiveIntegerField(default=0)
    loc48 = models.PositiveIntegerField(default=0)
    loc49 = models.PositiveIntegerField(default=0)
    loc50 = models.PositiveIntegerField(default=0)
    loc51 = models.PositiveIntegerField(default=0)
    loc52 = models.PositiveIntegerField(default=0)
    loc53 = models.PositiveIntegerField(default=0)
    loc54 = models.PositiveIntegerField(default=0)
    loc55 = models.PositiveIntegerField(default=0)
    loc56 = models.PositiveIntegerField(default=0)
    loc57 = models.PositiveIntegerField(default=0)
    loc58 = models.PositiveIntegerField(default=0)
    loc59 = models.PositiveIntegerField(default=0)
    loc60 = models.PositiveIntegerField(default=0)
    loc61 = models.PositiveIntegerField(default=0)
    loc62 = models.PositiveIntegerField(default=0)
    loc63 = models.PositiveIntegerField(default=0)
    loc64 = models.PositiveIntegerField(default=0)

    # claimed_nrs_single: "nr:loc,nr:loc" etc
    claimed_nrs_single = models.CharField(max_length=512, default='', blank=True)

    # claimed_nrs_double: "nr:loc;loc,nr:loc;loc" etc.
    claimed_nrs_double = models.CharField(max_length=512, default='', blank=True)

    # track when the claim was last evaluated, for automatically triggering a new check
    claimed_at_twoside_count = models.PositiveIntegerField(default=99999)

    # set to True when any segments reaches zero options
    # this is monitored by all the solvers and ends the searches
    reached_dead_end = models.BooleanField(default=False)

    # logbook of the manual fixes
    choices = models.TextField(default='', blank=True)

    def __str__(self):
        msg = "Processor %s" % self.processor
        if self.reached_dead_end:
            msg += " (dead end)"
        return msg


# end of file
