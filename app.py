from flask import Flask, render_template, redirect, url_for
from database import db, sqlite
from extensions import argon2
from forms.user_forms import RegisterForm, LoginForm
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from models.user import User
from sqlalchemy import text

app = Flask(__name__)

argon2.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = sqlite
app.config["SECRET_KEY"] = "hackathonMock"

db.init_app(app)

with app.app_context():
  db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "Login"

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
  form = LoginForm()

  if form.validate_on_submit():
    user = User.query.filter_by(username = form.username.data).first()

    if user and argon2.check_password_hash(user.password, form.password.data):
      login_user(user)

      return redirect(url_for("dashboard"))
    
    else: 
      return render_template("login.html", form= form)
    
  return render_template("login.html", form = form)


@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect("/")

@app.route("/register", methods= ["GET", "POST"])
def register():
  form = RegisterForm()

  if form.validate_on_submit():
    hashed_password = argon2.generate_password_hash(form.password.data)

    new_user = User(username=form.username.data, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return  redirect(url_for("login"))
  
  return render_template("register.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
  return render_template("dashboard.html")



@app.route("/findOutMore")
def moreInformation():
  return render_template("findOutMore.html")

if   __name__ == "__main__":
  app.run(debug= True)



