#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = []

import json
import requests
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

actions = []
with open("data.json", "r") as f:
    for entry in json.load(f):
        id_ = entry.pop("id")
        actions.append(dict(
            _type="abstract",
            _id=id_,
            _op_type="index",
            **entry
        ))
        # '_type': 'repos', '_id': 'elasticsearch-py', '_op_type': 'update',
        # es.index(index="arxiv", doc_type="abstract", id=id_, body=entry)

es = Elasticsearch()
r = bulk(es, actions, index="arxiv")
print(r)

assert 0

doc = {
    "first_name": "Dan",
    "last_name": "F-M",
    "age": 28,
    "about": "blah",
    "interests": [
        "music"
    ]
}
es.index(index="megacorp", doc_type="employee", body=doc)
