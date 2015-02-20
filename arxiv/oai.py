# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["download", "xml_to_json"]

import re
import time
import logging
import requests
import xml.etree.cElementTree as ET

# Download constants
resume_re = re.compile(r".*<resumptionToken.*?>(.*?)</resumptionToken>.*")
url = "http://export.arxiv.org/oai2"

# Parse constant
base_tag = ".//{{http://www.openarchives.org/OAI/2.0/}}{0}".format
arxiv_tag = ".//{{http://arxiv.org/OAI/{0}/}}{0}".format


def download(start_date=None, prefix="arXiv", max_tries=10):
    """
    This is a generator that downloads pages from the ArXiv OAI.

    """
    # Set up the request parameters.
    params = dict(verb="ListRecords", metadataPrefix=prefix)
    if start_date is not None:
        params["from"] = start_date

    # Keep going until we run out of pages.
    failures = 0
    while True:
        # Send the request.
        r = requests.post(url, data=params)
        code = r.status_code

        # Asked to retry
        if code == 503:
            to = int(r.headers["retry-after"])
            logging.info("Got 503. Retrying after {0:d} seconds.".format(to))

            time.sleep(to)
            failures += 1
            if failures >= max_tries:
                logging.warn("Failed too many times...")
                break

        elif code == 200:
            failures = 0

            # Grab the XML content.
            content = r.text
            for doc in xml_to_json(content, prefix):
                yield doc

            # Look for a resumption token.
            token = resume_re.search(content)
            if token is None:
                break
            token = token.groups()[0]

            # If there isn't one, we're all done.
            if token == "":
                logging.info("All done.")
                break

            logging.info("Resumption token: {0}.".format(token))

            # If there is a resumption token, rebuild the request.
            params = {"verb": "ListRecords", "resumptionToken": token}

            # Pause so as not to get banned.
            to = 20
            logging.info("Sleeping for {0:d} seconds so as not to get banned."
                         .format(to))
            time.sleep(to)

        else:
            # Wha happen'?
            r.raise_for_status()


def xml_to_json(xml_data, prefix):
    """
    A generator that parses through an XML listing from OAI and yields the
    documents as dictionaries.

    """
    tree = ET.fromstring(xml_data)
    for r in tree.findall(base_tag("metadata")):
        doc = _parse_node(r.find(arxiv_tag(prefix)), prefix)

        # Special case the category list.
        doc["categories"] = doc.get("categories", "").split()

        # Save the full author names too.
        doc["authors"] = [
            dict(a, fullname=" ".join(a[k] for k in ("forenames", "keyname")
                                      if k in a))
            for a in doc.get("authors", [])
        ]

        # Deal with dates.
        doc["updated"] = doc.get("updated", doc["created"])

        # Yield this document.
        yield doc


def _parse_node(node, prefix):
    # Get the actual name of the tag.
    nm = node.tag.split("}")[-1]

    # Check if the node has children.
    if len(node):
        # Recursively parse the children.
        lst = [_parse_node(n, prefix) for n in node]

        # If there are different keys or only one key, return it as a dict.
        if not isinstance(lst[0], dict) and (
                len(lst) == 1 or len(set(k[0] for k in lst)) > 1):
            return dict(lst)

        # Otherwise return it as a list.
        return (nm, lst)

    # This is a leaf node.
    return (nm, node.text)
