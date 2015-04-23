# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["add_abstracts"]

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

from .mappings import arxiv_mappings


def add_abstracts(entries):
    # Build the action list generator.
    actions = (dict(
        _index="arxiv",
        _type="abstract",
        _id=entry["id"],
        _op_type="index",
        **entry) for entry in entries)

    # Connect to the database.
    es = Elasticsearch()

    # Make sure that the index exists with the correct mappings.
    if not es.indices.exists("arxiv"):
        es.indices.create(index="arxiv", body=dict(
            mappings=arxiv_mappings,
            settings={"number_of_shards": 1},
        ))

    # Add the abstracts as a stream. This won't execute until you iterate!
    return streaming_bulk(es, actions)
