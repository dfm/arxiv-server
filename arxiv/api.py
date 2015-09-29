# -*- coding: utf-8 -*-

from __future__ import print_function

__all__ = ["api"]

from functools import wraps

import flask
from .database import esdb

api = flask.Blueprint("api", __name__)


def paginate(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            limit = int(flask.request.args.get("per_page", 50))
            page = int(flask.request.args.get("page", 1))
        except TypeError:
            return flask.jsonify(message="Invalid request"), 400

        if page < 1:
            return flask.jsonify(message="Invalid request"), 400
        kwargs["skip"] = (page-1) * limit
        kwargs["limit"] = limit
        return f(*args, **kwargs)
    return wrapped


@api.errorhandler(404)
def error_handler(e):
    resp = flask.jsonify(message="Not Found")
    resp.status_code = 404
    return resp


@api.route("/")
def index():
    return flask.jsonify(message="hi")


def _query_esdb(query, category=None, skip=0, limit=50, **extra_body):
    if query is None:
        return flask.jsonify(message="Invalid query"), 400
    if category is not None:
        query = dict(filtered={"filter": {"regexp": {"categories":
                                                     category + ".*"}},
                               "query": query})
    body = dict({
        "query": query, "from": skip, "size": limit,
    }, **extra_body)
    r = esdb.search(body=body)
    listings = r.get("hits", {}).get("hits", [])
    return flask.jsonify(count=len(listings), listings=listings)


@api.route("/recent")
@api.route("/recent/<category>")
@paginate
def recent(category=None, **kwargs):
    kwargs["sort"] = [
        {"updated": {"order": "desc"}},
        {"created": {"order": "desc"}},
        {"id": {"order": "asc"}}
    ]
    kwargs["_source"] = ["id", "title", "authors", "created", "updated",
                         "categories", ]
    return _query_esdb({"match_all": {}}, category=category, **kwargs)


@api.route("/search")
@api.route("/search/<category>")
@paginate
def search(category=None, **kwargs):
    query = flask.request.args.get("q", None)
    if query is not None:
        query = {"query_string": {"query": query,
                                  "fields": ["_all", "title^2"]}}
    return _query_esdb(query, category=category, **kwargs)


# @login_manager.request_loader
# def load_user_from_request(request):
#     api_key = request.args.get("api_key")
#     if api_key:
#         user = User.query.filter_by(api_key=api_key).first()
#         if user:
#             return user

#     api_key = request.headers.get("Authorization")
#     if api_key:
#         api_key = api_key.replace("Basic ", "", 1)
#         try:
#             api_key = base64.b64decode(api_key)
#         except TypeError:
#             pass
#         user = User.query.filter_by(api_key=api_key).first()
#         if user:
#             return user

#     return None


# @api.route("/")
# def index():
#     if current_user.is_authenticated():
#         return flask.jsonify(current_user.to_dict())
#     return flask.jsonify(message="s'up")


# @api.route("/sups/list")
# @login_required
# @paginate
# def list_sups(limit=None, skip=None):
#     q = Sup.query.filter(Sup.to_user == current_user)
#     q = q.order_by(Sup.when.desc())
#     q = q.offset(skip).limit(limit)
#     results = q.all()
#     return flask.jsonify(dict(count=len(results), results=[
#         s.to_dict() for s in results
#     ]))


# @api.route("/sups/send/<username>")
# @login_required
# def send_sup(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         return (flask.jsonify(message="Unknown user '{0}'".format(username)),
#                 404)

#     try:
#         lat = float(flask.request.args.get("lat", None))
#         lng = float(flask.request.args.get("lng", None))
#     except (ValueError, TypeError):
#         return flask.jsonify(message="Invalid request"), 400

#     sup = Sup(current_user, user, lat, lng)
#     db.session.add(sup)
#     db.session.commit()

#     return flask.jsonify(message="Success")
