import ast
import collections
import contextlib
import datetime
import functools
import hashlib
import hmac
import inspect
import logging
import mimetypes
import os
import pprint
import random
import re
import sys
import threading
import time
import traceback
import warnings
from os.path import join as opj
from zlib import adler32

import babel.core
from datetime import datetime, date
import passlib.utils
import psycopg2
import json
import werkzeug.contrib.sessions
import werkzeug.datastructures
import werkzeug.exceptions
import werkzeug.local
import werkzeug.routing
import werkzeug.wrappers
import werkzeug.wsgi
from werkzeug import urls
from werkzeug.wsgi import wrap_file

try:
    import psutil
except ImportError:
    psutil = None

import odoo
from odoo import fields
from odoo.service.server import memory_info
from odoo.service import security, model as service_model
from odoo.tools.func import lazy_property
from odoo.tools import ustr, consteq, frozendict, pycompat, unique, date_utils
from odoo.http import Response


from odoo.modules.module import module_manifest

_logger = logging.getLogger(__name__)
rpc_request = logging.getLogger(__name__ + '.rpc.request')
rpc_response = logging.getLogger(__name__ + '.rpc.response')

# 1 week cache for statics as advised by Google Page Speed
STATIC_CACHE = 60 * 60 * 24 * 7

# To remove when corrected in Babel
babel.core.LOCALE_ALIASES['nb'] = 'nb_NO'

#----------------------------------------------------------
# RequestHandler
#----------------------------------------------------------
# Thread local global request object
_request_stack = werkzeug.local.LocalStack()

request = _request_stack()
"""
    A global proxy that always redirect to the current request object.
"""


def route(route=None, **kw):
    """Decorator marking the decorated method as being a handler for
    requests. The method must be part of a subclass of ``Controller``.

    :param route: string or array. The route part that will determine which
                  http requests will match the decorated method. Can be a
                  single string or an array of strings. See werkzeug's routing
                  documentation for the format of route expression (
                  http://werkzeug.pocoo.org/docs/routing/ ).
    :param type: The type of request, can be ``'http'`` or ``'json'``.
    :param auth: The type of authentication method, can on of the following:

                 * ``user``: The user must be authenticated and the current request
                   will perform using the rights of the user.
                 * ``public``: The user may or may not be authenticated. If she isn't,
                   the current request will perform using the shared Public user.
                 * ``none``: The method is always active, even if there is no
                   database. Mainly used by the framework and authentication
                   modules. There request code will not have any facilities to access
                   the database nor have any configuration indicating the current
                   database nor the current user.
    :param methods: A sequence of http methods this route applies to. If not
                    specified, all methods are allowed.
    :param cors: The Access-Control-Allow-Origin cors directive value.
    :param bool csrf: Whether CSRF protection should be enabled for the route.

                      Defaults to ``True``. See :ref:`CSRF Protection
                      <csrf>` for more.

    .. _csrf:

    .. admonition:: CSRF Protection
        :class: alert-warning

        .. versionadded:: 9.0

        Odoo implements token-based `CSRF protection
        <https://en.wikipedia.org/wiki/CSRF>`_.

        CSRF protection is enabled by default and applies to *UNSAFE*
        HTTP methods as defined by :rfc:`7231` (all methods other than
        ``GET``, ``HEAD``, ``TRACE`` and ``OPTIONS``).

        CSRF protection is implemented by checking requests using
        unsafe methods for a value called ``csrf_token`` as part of
        the request's form data. That value is removed from the form
        as part of the validation and does not have to be taken in
        account by your own form processing.

        When adding a new controller for an unsafe method (mostly POST
        for e.g. forms):

        * if the form is generated in Python, a csrf token is
          available via :meth:`request.csrf_token()
          <odoo.http.WebRequest.csrf_token`, the
          :data:`~odoo.http.request` object is available by default
          in QWeb (python) templates, it may have to be added
          explicitly if you are not using QWeb.

        * if the form is generated in Javascript, the CSRF token is
          added by default to the QWeb (js) rendering context as
          ``csrf_token`` and is otherwise available as ``csrf_token``
          on the ``web.core`` module:

          .. code-block:: javascript

              require('web.core').csrf_token

        * if the endpoint can be called by external parties (not from
          Odoo) as e.g. it is a REST API or a `webhook
          <https://en.wikipedia.org/wiki/Webhook>`_, CSRF protection
          must be disabled on the endpoint. If possible, you may want
          to implement other methods of request validation (to ensure
          it is not called by an unrelated third-party).

    """
    routing = kw.copy()
    assert 'type' not in routing or routing['type'] in ("http", "json")
    def decorator(f):
        if route:
            if isinstance(route, list):
                routes = route
            else:
                routes = [route]
            routing['routes'] = routes
        @functools.wraps(f)
        def response_wrap(*args, **kw):
            response = f(*args, **kw)
            if isinstance(response, Response) or f.routing_type == 'json':
                return response

            if isinstance(response, (bytes, pycompat.text_type)):
                return Response(response)

            if isinstance(response, werkzeug.exceptions.HTTPException):
                response = response.get_response(request.httprequest.environ)
            if isinstance(response, werkzeug.wrappers.BaseResponse):
                response = Response.force_type(response)
                response.set_default()
                return response

            _logger.warn("<function %s.%s> returns an invalid response type for an http request" % (f.__module__, f.__name__))
            return response
        response_wrap.routing = routing
        response_wrap.original_func = f
        return response_wrap
    return decorator