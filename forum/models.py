import enum
from datetime import datetime
from typing import Any, Union

from flask_login import UserMixin, current_user
from markdown2 import markdown
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateColumn
from werkzeug.routing import BaseConverter
from werkzeug.security import check_password_hash, generate_password_hash

from forum import db, login


@compiles(CreateColumn, "postgresql")
def use_identity(element: Any, compiler: Any, **kw: Any) -> str:
    text = compiler.visit_create_column(element, **kw)
    text = text.replace("SERIAL", "INT GENERATED BY DEFAULT AS IDENTITY")
    return text


class HashIDConverter(BaseConverter):
    def __init__(self, map: Any, strict: bool = True):
        super(HashIDConverter, self).__init__(map)
        self.strict = strict


class FormEnum(enum.Enum):
    @classmethod
    def choices(cls) -> Any:
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item: Any) -> Any:
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self) -> Any:
        return str(self.value)


class BoardVisibility(FormEnum):
    Public = 0
    Private = 1
    Hidden = 2


class MemberRole(enum.Enum):
    Member = 0
    Admin = 1
    Owner = 2

    def __str__(self) -> str:
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User {self.display_name}>"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id: str) -> Union[User, None]:
    try:
        return User.query.filter_by(id=user_id).first()
    except:
        return None


class BoardMember(db.Model):
    board_id = db.Column(db.Integer,
                         db.ForeignKey("board.id", ondelete="CASCADE"),
                         primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id", ondelete="CASCADE"),
                        primary_key=True)
    role = db.Column(db.Enum(MemberRole), nullable=False,
                     default=MemberRole.Member)

    def __repr__(self) -> str:
        return f"<Member {self.board_id}, {self.user_id}, {self.role}>"


class RollResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer,
                        db.ForeignKey("post.id", ondelete="CASCADE"))
    roll = db.Column(db.Text, nullable=False)
    label = db.Column(db.Text)
    result = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer,
                        db.ForeignKey("post.id", ondelete="CASCADE"))
    owner_id = db.Column(db.Integer,
                         db.ForeignKey("user.id", ondelete="CASCADE"))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer,
                          db.ForeignKey("thread.id", ondelete="CASCADE"))
    owner_id = db.Column(db.Integer,
                         db.ForeignKey("user.id", ondelete="SET NULL"))
    content = db.Column(db.Text, nullable=False)
    roll_results = db.relationship(RollResult)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def get_owner(self) -> User:
        return User.query.filter_by(id=self.owner_id).first()

    def get_owner_as_member(self) -> BoardMember:
        return BoardMember.query.filter_by(user_id=self.owner_id).first()

    def get_content_markdown(self) -> str:
        return markdown(self.content, safe_mode=True,
                        extras={ "cuddled-lists": { }, "tables": { },
                                 "html-classes": {
                                     "table": "table table-striped "
                                              "table-bordered table-sm" } })


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer,
                         db.ForeignKey("board.id", ondelete="CASCADE"))
    owner_id = db.Column(db.Integer,
                         db.ForeignKey("user.id", ondelete="SET NULL"))
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    posts = db.relationship(Post)
    readonly = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())

    def get_owner(self) -> User:
        return User.query.filter_by(id=self.owner_id).first()

    def get_owner_as_member(self) -> BoardMember:
        return BoardMember.query.filter_by(user_id=self.owner_id).first()

    def get_content_markdown(self) -> str:
        return markdown(self.content, safe_mode=True,
                        extras={ "cuddled-lists": { }, "tables": { },
                                 "html-classes": {
                                     "table": "table table-striped "
                                              "table-bordered table-sm",
                                     "img": "img-fluid img-thumbnail" } })


class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    visibility = db.Column(db.Enum(BoardVisibility), nullable=False,
                           default=BoardVisibility.Public)
    members = db.relationship(BoardMember)
    threads = db.relationship(Thread)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Board {self.title}>"

    def add_member(self, user: User, role: BoardVisibility) -> None:
        member = BoardMember(board_id=self.id, user_id=user.id, role=role)
        self.members.append(member)

    def kick_member(self, user: User) -> None:
        member = BoardMember.query.filter_by(board_id=self.id,
                                             user_id=user.id).first()
        db.session.delete(member)

    def get_content_markdown(self) -> str:
        return markdown(self.content, safe_mode=True,
                        extras=["cuddled-lists", "tables"])

    def get_current_contributor(self) -> BoardMember:
        return BoardMember.query.filter_by(board_id=self.id,
                                           user_id=current_user.id).first()
