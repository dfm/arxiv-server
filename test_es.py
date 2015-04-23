#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = []

import json
from arxiv.database import add_abstracts

with open("data.json", "r") as f:
    abstracts = json.load(f)

r = list(add_abstracts(abstracts))
print(len(r))
