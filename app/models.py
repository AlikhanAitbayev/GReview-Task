from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class UserGroups(db.Model):
    __tablename__ = 'user_groups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

GroupPermissions = db.Table("group_permissions",
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True)
)

UserPermissions = db.Table('user_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

ResourcePermissions = db.Table('resource_permissions',
    db.Column('resource_id', db.Integer, db.ForeignKey('resource.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    groups = db.relationship('Groups', secondary='user_groups', lazy=True, back_populates='users')
    reservations = db.relationship("Reservations", back_populates="user")
    permissions = db.relationship('Permissions', secondary=UserPermissions, back_populates='users')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    users = db.relationship('Users', secondary='user_groups', lazy=True, back_populates='groups')
    permissions = db.relationship("Permissions", secondary=GroupPermissions, back_populates="groups")

class Permissions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    users = db.relationship("Users", secondary=UserPermissions, back_populates="permissions")
    groups = db.relationship("Groups", secondary=GroupPermissions, back_populates="permissions")
    resources = db.relationship("Resource", secondary=ResourcePermissions, back_populates="permissions")

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    capacity = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.String(255), nullable=True)
    permissions = db.relationship('Permissions', secondary=ResourcePermissions, back_populates='resources')
    reservations = db.relationship('Reservations', back_populates='resource')

class Reservations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    user = db.relationship('Users', back_populates='reservations')
    resource = db.relationship('Resource', back_populates='reservations')