from flask import redirect, render_template, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from forum import db
from forum.models import Board, Post, Thread
from forum.thread import thread_bp
from forum.thread.forms import CreatePostForm, CreateThreadForm, EditPostForm, \
    EditThreadForm


@thread_bp.route("/create", methods=["GET", "POST"])
def create_thread(board_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    form = CreateThreadForm()

    if form.validate_on_submit():
        thread = Thread(title=form.title.data, content=form.content.data,
                        readonly=form.readonly.data)
        thread.board_id = board.id
        thread.owner_id = current_user.id
        db.session.add(thread)
        db.session.commit()

        # Show a success message and redirect
        return redirect(
            url_for("thread.view", board_id=board.id, thread_id=thread.id))
    return render_template("thread/create_thread.html", board=board, form=form)


@thread_bp.route("/<string:thread_id>")
def view(board_id: str, thread_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    thread = Thread.query.filter_by(id=thread_id).first()
    return render_template("thread/view.html", board=board, thread=thread)


@thread_bp.route("/<string:thread_id>/edit", methods=["GET", "POST"])
def edit_thread(board_id: str, thread_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    thread = Thread.query.filter_by(id=thread_id).first()
    form = EditThreadForm(title=thread.title, content=thread.content,
                          readonly=thread.readonly)

    if form.validate_on_submit():
        thread.title = form.title.data
        thread.content = form.content.data
        thread.readonly = form.readonly.data
        db.session.commit()

        # Show a success message and redirect
        return redirect(
            url_for("thread.view", board_id=board.id, thread_id=thread.id))
    return render_template("thread/edit_thread.html", board=board,
                           thread=thread, form=form)


@thread_bp.route("/<string:thread_id>/posts/create", methods=["GET", "POST"])
def create_post(board_id: str, thread_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    thread = Thread.query.filter_by(id=thread_id).first()
    form = CreatePostForm()

    if form.validate_on_submit():
        post = Post(thread_id=thread.id, owner_id=current_user.id,
                    content=form.content.data)
        db.session.add(post)
        db.session.commit()

        # Show a success message and redirect
        return redirect(
            url_for("thread.view", board_id=board.id, thread_id=thread.id))

    return render_template("thread/create_post.html", board=board,
                           thread=thread, form=form)


@thread_bp.route("/<string:thread_id>/posts/<string:post_id>/edit",
                 methods=["GET", "POST"])
def edit_post(board_id: str, thread_id: str, post_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    thread = Thread.query.filter_by(id=thread_id).first()
    post = Post.query.filter_by(id=post_id).first()
    form = EditPostForm(content=post.content)

    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()

        # Show a success message and redirect
        return redirect(
            url_for("thread.view", board_id=board.id, thread_id=thread.id))
    return render_template("thread/edit_post.html", board=board, thread=thread,
                           post=post, form=form)


@thread_bp.route("/<string:thread_id>/posts/<string:post_id>/delete",
                 methods=["GET"])
def delete_post(board_id: str, thread_id: str, post_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()
    thread = Thread.query.filter_by(id=thread_id).first()

    # Delete the post and redirect
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()

    return redirect(
        url_for("thread.view", board_id=board.id, thread_id=thread.id))


@thread_bp.route("/<string:thread_id>/delete", methods=["GET"])
def delete_thread(board_id: str, thread_id: str) -> Response:
    board = Board.query.filter_by(id=board_id).first()

    # Delete the post and redirect
    Thread.query.filter_by(id=thread_id).delete()
    db.session.commit()

    return redirect(url_for("board.view", board_id=board.id))
