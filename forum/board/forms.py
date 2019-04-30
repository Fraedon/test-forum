from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField

from forum.models import BoardVisibility


class CreateBoardForm(FlaskForm):
    title = StringField("Title")
    description = StringField("Description")
    content = TextAreaField("Content", render_kw={ "rows": "5" })
    visibility = SelectField("Visibility", choices=BoardVisibility.choices(),
                             coerce=BoardVisibility.coerce,
                             description="""Public boards are visible to 
                             everyone, whereas private boards are also 
                             visible to everyone, but post access is limited 
                             to members. Hidden boards are only visible to 
                             members.""")
    submit = SubmitField("Create board")


class BoardSettingsForm(FlaskForm):
    title = StringField("Title")
    description = StringField("Description")
    content = TextAreaField("Content")
    visibility = SelectField("Visibility", choices=BoardVisibility.choices(),
                             coerce=BoardVisibility.coerce,
                             description="""Public boards are visible to 
                             everyone, whereas private boards are also 
                             visible to everyone, but post access is limited 
                             to members. Hidden boards are only visible to 
                             members.""")
    submit = SubmitField("Save settings")
