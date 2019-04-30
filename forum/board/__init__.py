from flask import Blueprint

board_bp = Blueprint("board", __name__)

from forum.board import routes
