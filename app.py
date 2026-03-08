import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date as dt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

# Windows-safe database path
db_path = os.path.join(os.getcwd(), 'database', 'medicine.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

# -----------------------------
# Database Models
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    guardian_phone = db.Column(db.String(15))

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    dosage = db.Column(db.String(50))
    time = db.Column(db.String(20))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    date = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")

# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def home():
    return render_template("login.html")

# ----- LOGIN -----
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email, password=password).first()
    if user:
        session['user_id'] = user.id  # Save logged-in user in session
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid Email or Password!")
        return redirect(url_for("home"))

# ----- REGISTER -----
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        guardian = request.form["guardian"]

        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered! Please login.")
            return redirect(url_for("home"))

        user = User(
            name=name,
            email=email,
            password=password,
            phone=phone,
            guardian_phone=guardian
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration Successful! Please login.")
        return redirect(url_for("home"))
    return render_template("register.html")

# ----- DASHBOARD -----
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for("home"))

    user_id = session['user_id']
    medicines = Medicine.query.filter_by(user_id=user_id).all()

    # Calculate streak
    streak = 0
    user_meds = Medicine.query.filter_by(user_id=user_id).order_by(Medicine.id.desc()).all()
    for med in user_meds:
        if med.status == "Taken":
            streak += 1
        else:
            break

    return render_template("dashboard.html", medicines=medicines, streak_count=streak)

# ----- ADD MEDICINE -----
@app.route("/add_medicine", methods=["GET","POST"])
def add_medicine():
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for("home"))

    if request.method == "POST":
        user_id = session['user_id']
        name = request.form["name"]
        dosage = request.form["dosage"]
        time = request.form["time"]
        start = request.form["start"]
        end = request.form["end"]

        medicine = Medicine(
            user_id=user_id,
            name=name,
            dosage=dosage,
            time=time,
            start_date=start,
            end_date=end,
            date=start
        )
        db.session.add(medicine)
        db.session.commit()
        flash(f"{name} added successfully!")
        return redirect(url_for("dashboard"))
    return render_template("add_medicine.html")

# ----- MARK TAKEN -----
@app.route("/take_medicine/<int:med_id>")
def take_medicine(med_id):
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for("home"))

    med = Medicine.query.get_or_404(med_id)
    if med.user_id != session['user_id']:
        flash("Not allowed!")
        return redirect(url_for("dashboard"))

    med.status = "Taken"
    med.date = dt.today().strftime("%Y-%m-%d")
    db.session.commit()
    flash(f"{med.name} marked as Taken!")
    return redirect(url_for("dashboard"))

# ----- MARK MISSED -----
@app.route("/miss_medicine/<int:med_id>")
def miss_medicine(med_id):
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for("home"))

    med = Medicine.query.get_or_404(med_id)
    if med.user_id != session['user_id']:
        flash("Not allowed!")
        return redirect(url_for("dashboard"))

    med.status = "Missed"
    med.date = dt.today().strftime("%Y-%m-%d")
    db.session.commit()
    flash(f"{med.name} marked as Missed! Guardian alerted.")
    # TODO: Integrate SMS to guardian
    return redirect(url_for("dashboard"))

# ----- HISTORY -----
@app.route("/history")
def history():
    if 'user_id' not in session:
        flash("Please login first!")
        return redirect(url_for("home"))

    user_id = session['user_id']
    medicines = Medicine.query.filter_by(user_id=user_id).all()
    return render_template("history.html", medicines=medicines)

# ----- LOGOUT -----
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!")
    return redirect(url_for("home"))

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), 'database'), exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)