# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["esdb", "get_db", "add_abstracts", "get_start_date"]

from flask import _app_ctx_stack as stack

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from elasticsearch.exceptions import NotFoundError, RequestError

from .mappings import arxiv_mappings

INDEX_NAME = "arxiv"
ABSTRACT_TYPE = "abstract"


def get_db(host="localhost:9200", **kwargs):
    return Elasticsearch(hosts=[host], **kwargs)


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
                since = v[:10]

    return since


class FlaskES(object):

    def __init__(self, app=None, **kwargs):
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        app.config.setdefault("ELASTICSEARCH_HOST", "localhost:9200")
        self.elasticsearch_options = kwargs
        app.teardown_appcontext(self.teardown)

    def __getattr__(self, item):
        es = self.get_es()
        if es is None:
            return None
        return getattr(es, item)

    def get_es(self):
        ctx = stack.top
        if ctx is None:
            return None
        if not hasattr(ctx, "elasticsearch"):
            ctx.elasticsearch = get_db(
                host=ctx.app.config.get('ELASTICSEARCH_HOST'),
                **(self.elasticsearch_options)
            )
        return ctx.elasticsearch

    def search(self, **kwargs):
        es = self.get_es()
        if es is None:
            return None
        kwargs["index"] = kwargs.get("index", INDEX_NAME)
        kwargs["doc_type"] = kwargs.get("doc_type", ABSTRACT_TYPE)
        return es.search(**kwargs)

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, "elasticsearch"):
            ctx.elasticsearch = None


esdb = FlaskES()
