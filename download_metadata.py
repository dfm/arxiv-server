#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
from arxiv.oai import download
from arxiv.database import add_abstracts, get_start_date

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--since", default="2000-01-01")
args = parser.parse_args()

start_date = get_start_date(since=args.since)
print("Starting from {0}".format(start_date))
r = list(add_abstracts(download(start_date=start_date)))
print("Indexed {0} abstracts.".format(len(r)))
