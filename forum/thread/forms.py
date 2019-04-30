from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField


class CreateThreadForm(FlaskForm):
    title = StringField("Title")
    content = TextAreaField("Content")
    readonly = BooleanField("Read-only?")
    submit = SubmitField("Create thread")


class EditThreadForm(FlaskForm):
    title = StringField("Title")
    content = TextAreaField("Content")
    readonly = BooleanField("Read-only?")
    submit = SubmitField("Save changes")


class CreatePostForm(FlaskForm):
    content = TextAreaField("Content")
    submit = SubmitField("Create post")


class EditPostForm(FlaskForm):
    content = TextAreaField("Content")
    submit = SubmitField("Save changes")
