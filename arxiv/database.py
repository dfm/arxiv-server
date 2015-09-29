# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["get_db", "add_abstracts", "get_start_date"]

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from elasticsearch.exceptions import NotFoundError, RequestError

from .mappings import arxiv_mappings

INDEX_NAME = "arxiv"
ABSTRACT_TYPE = "abstract"


def get_db():
    return Elasticsearch()


def add_abstracts(entries):
    # Build the action list generator.
    actions = (dict(
        _index=INDEX_NAME,
        _type=ABSTRACT_TYPE,
        _id=entry["id"],
        _op_type="index",
        **entry) for entry in entries)

    # Connect to the database.
    es = get_db()

    # Make sure that the index exists with the correct mappings.
    if not es.indices.exists(INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=dict(
            mappings=arxiv_mappings,
            settings={"number_of_shards": 1},
        ))

    # Don't forget to iterate to run the generator.
    return streaming_bulk(es, actions)


def get_start_date(since="2000-01-01"):
    es = get_db()

    try:
        # Try to get a document with a "fetched" entry.
        r = es.search(index=INDEX_NAME, doc_type=ABSTRACT_TYPE, body=dict(
            sort=[{"fetched": {"order": "desc"}}],
            size=1,
            query={
                "match_all": {},
            }
        ))

    except (NotFoundError, RequestError):
        # If none exist, accept the default.
        pass

    else:
        if len(r["hits"]["hits"]):
            v = r["hits"]["hits"][0]["_source"]["fetched"]
            if v != "null":
                since = v

    return since
