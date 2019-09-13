import time
import uuid

from flask import g
from flask import request


def log_request(logger):
    g.start = time.time()
    g.request_id = str(uuid.uuid4())
    logger.info("Request {} {} {}".format(g.request_id, request.method, request.path))
    if request.method in ["POST", "PUT"]:
        logger.info("Request {} body: {}".format(g.request_id, request.get_json()))


def log_response(response, logger):
    msg = "Response {} {} {} {} {}".format(
        g.request_id,
        request.method,
        request.path,
        response.status_code,
        round(time.time() - g.start, 2),
    )
    logger.info(msg)
    return response
