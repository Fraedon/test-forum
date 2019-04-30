from flask import Blueprint

thread_bp = Blueprint("thread", __name__)

from forum.thread import routes
