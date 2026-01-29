from flask import Flask, render_template, request, redirect, url_for, session
from models import db
from models import Student
from models import Mess
from models import House
from models import Room
from models import HouseImage
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "studentnest_secret_key_123"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:vedant@localhost/studentnest"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Home / Category Page
@app.route("/")
def index_page():
    return render_template("category.html")

# Student Login
@app.route("/student/login", methods=["GET", "POST"])
def student_login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        student = Student.query.filter_by(email=email).first()

        if student and student.check_password(password):
            session['role'] = 'student'
            session['student_id'] = student.id
            return redirect(url_for("student_requirements_page"))
        else:
            return "Invalid email or password"

    return render_template("category_Student_Login.html")


# Student Registration
@app.route("/student/register")
def student_register_page():
    return render_template("category_Student_Register.html")

@app.route("/student/register/submit", methods=["POST"])
def student_register_submit_page():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")

    # Check if student already exists
    existing = Student.query.filter_by(email=email).first()
    if existing:
        return "Email already registered"

    student = Student(name=name, email=email, phone=phone)
    student.set_password(password)

    db.session.add(student)
    db.session.commit()

    return redirect(url_for("student_login_page"))

# Student Requirements Page
@app.route("/student/requirements")
def student_requirements_page():
    return render_template("student_Requirement.html")

# Rooms & Mess
# ---------------- STUDENT ROOMS SEARCH ----------------
@app.route("/student/rooms")
def student_rooms_page():
    search_text = (request.args.get("city") or "").strip()

    if search_text:
        words = search_text.split()
        query = House.query
        for word in words:
            query = query.filter(House.city.ilike(f"%{word}%"))
        houses = query.all()
    else:
        houses = House.query.all()

    return render_template("requirement_Room.html", houses=houses)

@app.route("/student/mess")
def student_mess_page():
    city = request.args.get("city", "").strip()

    query = Mess.query.filter(
        Mess.status == "OPEN",
        Mess.available_seats > 0
    )

    if city:
        query = query.filter(Mess.city.ilike(f"%{city}%"))

    mess_list = query.all()

    print("MESS FOUND:", mess_list)  # Debug

    return render_template("requirement_Mess.html", mess_list=mess_list)

# ---------------- OWNER LOGIN ----------------
@app.route("/owner/login", methods=["GET", "POST"])
def owner_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        owner = Owner.query.filter_by(email=email).first()

        if owner and owner.check_password(password):
            session['owner_logged_in'] = True
            session['owner_id'] = owner.id
            return redirect(url_for('owner_dashboard'))
        else:
            return "Invalid email or password"

    return render_template("category_Owner_Login.html")

# ---------------- OWNER REGISTER ----------------
from models import Owner

@app.route("/owner/register", methods=["GET", "POST"])
def owner_register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        # Prevent duplicate owner
        if Owner.query.filter_by(email=email).first():
            return "Email already registered"

        owner = Owner(name=name, email=email, phone=phone)
        owner.set_password(password)

        db.session.add(owner)
        db.session.commit()

        return redirect(url_for("owner_login"))

    return render_template("category_Owner_Register.html")

# ---------------- OWNER DASHBOARD ----------------
from werkzeug.utils import secure_filename
import os

@app.route("/owner/dashboard", methods=["GET", "POST"])
def owner_dashboard():
    # Check if owner is logged in
    if not session.get("owner_id"):
        return redirect(url_for("owner_login"))

    # Set upload folder
    UPLOAD_FOLDER = "static/uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    if request.method == "POST":
        house_name = request.form.get("house_name")
        phone = request.form.get("phone")
        rent = request.form.get("rent")
        seats = request.form.get("seats")
        features = request.form.get("features")
        location = request.form.get("location")
        city = request.form.get("city")
        owner_id = session["owner_id"]

        new_house = House(
            house_name=house_name,
            phone=phone,
            rent=rent,
            seats=seats,
            features=features,
            location=location,
            city=city,
            owner_id=owner_id
        )
        db.session.add(new_house)
        db.session.commit()

        # Save uploaded images
        files = request.files.getlist("images")
        
        print(request.files)
        for file in files:
            if file.filename != "":
                filename = secure_filename(file.filename)
                print(filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                print(filepath)
                file.save(filepath)

                house_image = HouseImage(
                    filename=filename,
                    house_id=new_house.id
                )
                db.session.add(house_image)

        db.session.commit()

    # Load all houses by this owner for display
    houses = House.query.filter_by(owner_id=session["owner_id"]).all()
    return render_template("owner_dashboard.html", houses=houses)

# ---------------- OWNER Add House ----------------
# =========================
# OWNER ADD HOUSE
# =========================
@app.route("/add-house", methods=["POST"])
def add_house():
    house = House(
        house_name=request.form["house_name"],
        location=request.form["location"],
        city=request.form["city"],
        owner_id=request.form["owner_id"]
    )
    db.session.add(house)
    db.session.commit()
    return "House added successfully"

# =========================
# ADD ROOM TO HOUSE
# =========================
@app.route("/add-room", methods=["POST"])
def add_room():
    room = Room(
        room_type=request.form["room_type"],
        capacity=request.form["capacity"],
        house_id=request.form["house_id"]
    )
    db.session.add(room)
    db.session.commit()
    return "Room added successfully"

@app.route('/house/<int:house_id>')
def house_details_page(house_id):
    house = House.query.get(house_id)
    if not house:
        return "House not found", 404
    return render_template('house_details.html', house=house)

@app.route('/edit_house/<int:house_id>', methods=['POST'])
def edit_house(house_id):
    house = House.query.get_or_404(house_id)
    house.house_name = request.form.get('house_name')
    house.rent = request.form.get('rent')
    house.seats = request.form.get('seats')
    # Add logic for saving images if request.files['images'] is present
    db.session.commit()
    return redirect(url_for('owner_dashboard'))

@app.route('/house/delete/<int:house_id>', methods=['POST'])
def delete_house(house_id):
    house = House.query.get(house_id)
    if not house:
        return "House not found", 404
    db.session.delete(house)
    db.session.commit()
    return "House deleted successfully!"
# =========================
# STUDENT VIEW AVAILABLE ROOMS
# =========================
@app.route("/available-rooms")
def available_rooms():
    rooms = Room.query.filter_by(available=True).all()
    return {
        "rooms": [
            {
                "room_id": r.id,
                "room_type": r.room_type,
                "house": r.house.house_name,
                "city": r.house.city
            }
            for r in rooms
        ]
    }

# ---------------- MESS ----------------
@app.route("/mess/login", methods=["GET", "POST"])
def mess_login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        mess = Mess.query.filter_by(email=email).first()

        if mess and mess.check_password(password):
            session['mess_id'] = mess.id
            return redirect(url_for("mess_dashboard_page"))
        else:
            return "Invalid email or password"

    return render_template("category_Mess_Login.html")

# ---------------- Mess REGISTER ----------------
@app.route("/mess/register", methods=["GET", "POST"])
def mess_register_page():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

        # Prevent duplicate mess
        if Mess.query.filter_by(email=email).first():
            return "Email already registered"

        mess = Mess(
            name=name,
            email=email,
            phone=phone,
            price=0,  # default value for registration
            available_seats=0,
            status="OPEN",
            veg_type="" 
        )
        mess.set_password(password)

        db.session.add(mess)
        db.session.commit()

        return redirect(url_for("mess_login_page"))

    return render_template("category_Mess_Register.html")

# ---------------- Mess Dashboard ----------------
@app.route("/mess/dashboard")
def mess_dashboard_page():
    if not session.get("mess_id"):
        return redirect(url_for("mess_login_page"))

    return render_template("mess_dashboard.html")

@app.route("/add_mess", methods=["GET", "POST"])
def add_mess():
    if request.method == "POST":
        mess = Mess(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form["phone"],
            address=request.form["address"],
            city=request.form["city"],
            price=int(request.form["price"]),
            veg_type=request.form["veg_type"],
            available_seats=int(request.form["available_seats"]),
            status="OPEN"
        )
        db.session.add(mess)
        db.session.commit()
        return redirect(url_for("add_mess"))

    return render_template("mess_dashboard.html")

@app.route('/mess/<int:mess_id>')
def mess_details_page(mess_id):
    # Fetch the specific mess by ID
    mess = Mess.query.get_or_404(mess_id)
    
    # We pass 'mess' to the template so the HTML can use {{ mess.name }}, etc.
    return render_template('mess_details.html', mess=mess)

# Logout
@app.route("/logout")
def logout_page():
    session.clear()
    return redirect(url_for('index_page'))


if __name__ == '__main__':
    app.run(debug=True)
