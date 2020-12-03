from flask import Flask, render_template, request, redirect, url_for, session, json
import psycopg2 as dbapi2
from configurations import db_url
from passlib.hash import pbkdf2_sha256 as hasher

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

INIT_STATEMENTS = [
]

with dbapi2.connect(db_url) as connection:
    cursor = connection.cursor()
    for statement in INIT_STATEMENTS:
        cursor.execute(statement)
    cursor.close()

@app.route("/")
@app.route("/Exit/",  methods=['GET', 'POST'])
def home_page():
    return render_template('home.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        tup = (uname,)
        state = "SELECT ID, ISADMIN, PASSWORD FROM USERS WHERE USERNAME=%s"
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            cursor.execute(state, tup)
            record = cursor.fetchone()
            if record != None:
                if record[1]: # admin
                    if hasher.verify(passw, record[2]):
                        session["is_admin"] = "yes"
                        return redirect(url_for("admin_page"))
                    else: ###################################### hatalı şifre
                        render_template("login.html")
                else: # user
                    if hasher.verify(passw, record[2]):
                        session["is_doctor"] = "yes"
                        return render_template('doctor.html', display="none")
                    else:  ###################################### hatalı şifre
                        render_template("login.html")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        state = "SELECT ID FROM USERS WHERE USERNAME=%s"
        tup = (uname,)
        with dbapi2.connect(db_url) as connection:
            cursor = connection.cursor()
            cursor.execute(state, tup)
            record = cursor.fetchone()
            cursor.close()
        if record == None:
            mail = request.form['mail']
            passw = request.form['passw']
            hashed = hasher.hash(passw)
            state = "INSERT INTO USERS(USERNAME, PASSWORD, MAIL) VALUES(%s, %s, %s) "
            with dbapi2.connect(db_url) as connection:
                cursor = connection.cursor()
                cursor.execute(state, (uname, hashed, mail))
                cursor.close()
        else:
            return render_template("register.html")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/save_leads", methods=["GET", "POST"])
def save_leads():
    result = request.json('x')
    result = json.loads(result)
    print(result)

if __name__ == "__main__":
    app.run()
