#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = []

from arxiv.oai import download
from arxiv.database import add_abstracts

r = list(add_abstracts(download(start_date="2015-04-22")))
print(len(r))
