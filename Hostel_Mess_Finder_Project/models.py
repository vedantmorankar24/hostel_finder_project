from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# =========================
# STUDENT MODEL
# =========================
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(256), nullable=False)

    mess_id = db.Column(db.Integer, db.ForeignKey("messes.id"))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =========================
# HOSTEL / PG OWNER MODEL
# =========================
class Owner(db.Model):
    __tablename__ = "owners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(256), nullable=False)

    houses = db.relationship("House", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# =========================
# HOUSE / HOSTEL MODEL
# =========================
class House(db.Model):
    __tablename__ = "houses"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.id"), nullable=False)
    house_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    rent = db.Column(db.Integer)
    seats = db.Column(db.Integer)
    features = db.Column(db.String(200))
    location = db.Column(db.String(200))
    city = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.now())

    images = db.relationship(
        "HouseImage",
        backref="house",
        cascade="all, delete-orphan",
        lazy=True
    )
    
    rooms = db.relationship("Room", backref="house", lazy=True)
    images = db.relationship("HouseImage", backref="house", lazy=True)

# =========================
# HOUSE IMAGE MODEL
# =========================
class HouseImage(db.Model):
    __tablename__ = "house_images"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey("houses.id"), nullable=False)

House.images = db.relationship("HouseImage", backref="house", lazy=True)

# =========================
# ROOM MODEL
# =========================
class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String(50))  # Single / Double
    capacity = db.Column(db.Integer)
    available = db.Column(db.Boolean, default=True)

    house_id = db.Column(db.Integer, db.ForeignKey("houses.id"), nullable=False)

# =========================
# MESS MODEL (LOGIN ENTITY)
# =========================
class Mess(db.Model):
    __tablename__ = "messes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(200))

    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    price = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="OPEN")
    veg_type = db.Column(db.String(50))
    
    # Relationship with students
    students = db.relationship("Student", backref="mess", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
