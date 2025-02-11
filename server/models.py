from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy import exc
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'


    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False, unique = True)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    _password_hash = db.Column(db.String)
    
    recipes = db.relationship('Recipe', backref='user')

    serialize_rules = (
        "-recipes.user",
    )
    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hashes may not be viewed.')
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )
    
    def __repr__(self):
        return f'User {self.username}, ID: {self.id}'


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    __table_args__ = (
        db.CheckConstraint('length(instructions) >= 50'),
    )

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    instructions = db.Column(db.String, nullable = False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # @validates('instructions')
    # def validate_title(self, key, instruction):
    #     if len(instruction)<50:
    #         raise AttributeError("Requires at least 50 characters")
    #     return instruction
