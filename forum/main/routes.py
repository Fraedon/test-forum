from flask import render_template

from forum.main import main_bp
from forum.models import Board, BoardVisibility


@main_bp.route("/")
def index() -> None:
    # Retrieve all the boards
    boards = Board.query.filter(
        Board.visibility != BoardVisibility.Hidden).limit(20).all()
    return render_template("main.html", boards=boards)
