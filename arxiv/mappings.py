# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["arxiv_mappings"]


arxiv_mappings = {
    "abstract": {
        "properties": {
            "abstract": {
                "type": "string",
                "analyzer": "english"
            },
            "acm-class": {
                "type": "string"
            },
            "first_author": {
                "properties": {
                    "affiliation": {
                        "type": "string"
                    },
                    "forenames": {
                        "type": "string"
                    },
                    "fullname": {
                        "type": "string"
                    },
                    "keyname": {
                        "type": "string"
                    },
                    "suffix": {
                        "type": "string"
                    }
                }
            },
            "authors": {
                "properties": {
                    "affiliation": {
                        "type": "string"
                    },
                    "forenames": {
                        "type": "string"
                    },
                    "fullname": {
                        "type": "string"
                    },
                    "keyname": {
                        "type": "string"
                    },
                    "suffix": {
                        "type": "string"
                    }
                }
            },
            "categories": {
                "type": "string",
                "index": "not_analyzed"
            },
            "comments": {
                "type": "string",
                "analyzer": "english"
            },
            "created": {
                "type": "date",
                "format": "dateOptionalTime"
            },
            "doi": {
                "type": "string"
            },
            "id": {
                "type": "string"
            },
            "journal-ref": {
                "type": "string"
            },
            "license": {
                "type": "string"
            },
            "msc-class": {
                "type": "string"
            },
            "proxy": {
                "type": "string"
            },
            "report-no": {
                "type": "string"
            },
            "title": {
                "type": "string",
                "analyzer": "english"
            },
            "updated": {
                "type": "date",
                "format": "dateOptionalTime"
            }
        }
    }
}
