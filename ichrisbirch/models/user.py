import uuid
from datetime import datetime
from typing import Any

from flask_login import UserMixin
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy_json import mutable_json_type
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from ichrisbirch.database.sqlalchemy.base import Base

MutableJSONB = mutable_json_type(dbtype=JSONB, nested=True)

DEFAULT_USER_PREFERENCES = {
    'theme': 'turquoise',
    'dark_mode': True,
    'notifications': False,
    'dashboard_layout': [
        ['tasks_priority', 'countdowns', 'events'],
        ['habits', 'brainlog', 'devlog'],
    ],
}


class User(UserMixin, Base):
    __tablename__ = 'users'

    @staticmethod
    def generate_64_bit_int():
        """Generate a 64-bit integer to use as alternative_id."""
        return uuid.uuid4().int >> 64

    @staticmethod
    def default_preferences():
        return DEFAULT_USER_PREFERENCES

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alternative_id: Mapped[int] = mapped_column(Integer, unique=True, default=generate_64_bit_int)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=False)
    email: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), primary_key=False, unique=False, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=False, unique=False, nullable=True)
    preferences: Mapped[Any] = mapped_column(MutableJSONB, index=False, unique=False, default=default_preferences)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        """Return the alternative_id to keep primary id consistent upon session invalidation."""
        return str(self.alternative_id)

    def set_alternative_id(self):
        """Set alternative_id as 64-bit integer."""
        self.alternative_id = self.generate_64_bit_int()

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'User(name={self.name}, email={self.email}, created_on={self.created_on}, last_login={self.last_login})'
