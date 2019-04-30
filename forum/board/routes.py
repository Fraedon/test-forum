from flask import redirect, render_template, url_for
from flask_login import current_user
from werkzeug.wrappers.response import Response

from forum import db
from forum.board import board_bp
from forum.board.forms import BoardSettingsForm, CreateBoardForm
from forum.models import Board, BoardMember, MemberRole


@board_bp.route("/<int:board_id>")
def view(board_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    return render_template("board/board.html", board=board)


@board_bp.route("/<string:board_id>/settings", methods=["GET", "POST"])
def settings(board_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    form = BoardSettingsForm(title=board.title, description=board.description,
                             content=board.content, visibility=board.visibility)

    if form.validate_on_submit():
        board.title = form.title.data
        board.description = form.description.data
        board.content = form.content.data
        board.visibility = form.visibility.data
        db.session.commit()

        # Show a success message and redirect
        return redirect(url_for("board.view", board_id=board.id))

    return render_template("board/settings.html", board=board, form=form)


@board_bp.route("/<string:board_id>/delete")
def delete(board_id: str) -> Response:
    # Delete the board and redirect
    Board.query.filter_by(id=board_id).delete()
    db.session.commit()

    return redirect(url_for("main.index"))


@board_bp.route("/create", methods=["GET", "POST"])
def create() -> Response:
    form = CreateBoardForm()
    if form.validate_on_submit():
        # Create the new board and owner
        session = db.session()
        try:
            board = Board(title=form.title.data,
                          description=form.description.data,
                          content=form.content.data,
                          visibility=form.visibility.data)
            session.add(board)
            session.flush()
            owner = BoardMember(board_id=board.id, user_id=current_user.id,
                                role=MemberRole.Owner)
            session.add(owner)
            session.commit()
        except:
            session.rollback()
            raise

        # Show a success message and redirect
        return redirect(url_for("main.index"))

    return render_template("board/create.html", form=form)
