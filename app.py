"""
Responsible for running our app instance
"""
from flask import *
#session
import pymysql
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
connection=pymysql.connect(host='localhost',user="root",password="",database="owenke")
connection.autocommit(True)


app=Flask(__name__)
app.secret_key="qwer1234tyui"

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def setup_admin_accounts():
    """Creates the officer/chief-admin tables if missing, and seeds one
    default login for each so the dashboard can be accessed on a fresh
    database. Passwords are stored hashed, never in plain text."""
    cursor=connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officials_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            badge_no VARCHAR(50) UNIQUE NOT NULL,
            tell VARCHAR(20),
            password VARCHAR(255) NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_panel (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chief_badge_no VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM officials_table")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO officials_table (badge_no, tell, password) VALUES (%s,%s,%s)",
            ("ADMIN001", "254700000000", generate_password_hash("Officer@123"))
        )
        connection.commit()

    # add a status column to wenotify if it isn't there yet, so existing
    # rows aren't broken by this feature being added later
    cursor.execute("SELECT COUNT(*) FROM admin_panel")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO admin_panel (chief_badge_no, password) VALUES (%s,%s)",
            ("CHIEF001", generate_password_hash("Chief@123"))
        )
        connection.commit()

    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_schema = DATABASE() AND table_name = 'wenotify' AND column_name = 'status'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute("ALTER TABLE wenotify ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'Pending'")
        connection.commit()

setup_admin_accounts()

@app.route("/")
def index():
    #create some code to ftch products from the database
    #sudo/opt/lampp/lampp start
    #connection to the database
    #define the sql query to be
    return render_template("index.html",)
   
@app.route("/home", methods=['POST','GET'])
def home():
    #insert into users (username,email,phone,password) values(%s,%s,%s,%s)
    #get the posted details
    #check if the details have been posted
    connection=pymysql.connect(host='localhost',user="root",password="",database="owenke")
    if request.method == 'POST':
        username=request.form['username']
        user_id=request.form['user_id']
        email=request.form['email']
        phone=request.form['phone']
        event_desc=request.form['event_desc']
        event_date=request.form['event_date']
        County=request.form['county']
        Location=request.form['location']
        contact_on=request.form['contact_on']
        gender=request.form['gender']

        # keep everything the user already typed, so a validation error
        # never wipes the form - re-render with these values pre-filled
        formdata={
            "username":username,
            "user_id":user_id,
            "email":email,
            "phone":phone,
            "event_desc":event_desc,
            "event_date":event_date,
            "county":County,
            "location":Location,
            "contact_on":contact_on,
            "gender":gender,
        }

        # the photo is optional - save it if one was actually chosen
        uploaded_photo = request.files.get('file_upload')
        file = ""
        if uploaded_photo and uploaded_photo.filename:
            if allowed_file(uploaded_photo.filename):
                safe_name = secure_filename(uploaded_photo.filename)
                # prefix with phone so two people's "photo.jpg" don't collide
                unique_name = f"{phone}_{safe_name}"
                uploaded_photo.save(os.path.join(UPLOAD_FOLDER, unique_name))
                file = unique_name
            else:
                return render_template("home.html", error="photo must be a png, jpg, jpeg, gif or webp file", formdata=formdata)

        #validation checks
        # if " " in username:
        #     return render_template("home.html",error="username cannot be left empty",formdata=formdata)
        if len(user_id)<7 or len(user_id)>8:
                return render_template("home.html",error="id should not be less than 7 characters or more than 8",formdata=formdata)
        elif "@" not in email:
            return render_template("home.html",error="email must have @",formdata=formdata)
        elif not phone.startswith("254"):
            return render_template("home.html",error="phone must start with 254*********",formdata=formdata)
        elif not event_desc.strip():
            return render_template("home.html",error="event description cannot be left empty",formdata=formdata)
        elif not event_date.strip():
                return render_template("home.html",error="date cannot be left empty",formdata=formdata)
        elif not County.strip():
                return render_template("home.html",error="county cannot be left empty",formdata=formdata)
        elif not Location.strip():
                return render_template("home.html",error="location cannot be left empty",formdata=formdata)
        elif not contact_on.strip():
                    return render_template("home.html",error="an option must be selected on contact_on",formdata=formdata)
        elif not gender.strip():
               return render_template("home.html",error="gender cannot be left unselected",formdata=formdata)
        else:
            sql="insert into wenotify(username,user_id,email,phone,event_desc,file_upload,event_date,county,location,contact_on,gender)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            #create cursor
            cursor=connection.cursor()
            #execute sql
            cursor.execute(sql,(username,user_id,email,phone,event_desc,file,event_date,County,Location,contact_on,gender))
            #commit
            connection.commit()
            # ADD the sms code
            import sms
            sms.send_sms(phone,"Hello {username}Thank you we have received your emergency and we shall act accordingly!!")
            return render_template("confirmation.html",
                username=username,
                user_id=user_id,
                email=email,
                phone=phone,
                event_desc=event_desc,
                event_date=event_date,
                county=County,
                location=Location,
                contact_on=contact_on,
                gender=gender,
                photo=file)
    else:
        return render_template("home.html")
        #TODO create a signin route that returns signin.html template
@app.route("/logoff", methods=['POST','GET'])
def logoff():
 if request.method == 'POST':
        badge_no=request.form['badge_no']
        tell=request.form['tell']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        #validation checks
        # if " " in badge_no:
        #     return render_template("logoff.html",error="badge_no has one word")
        if tell.startswith("+254"):
            return render_template("logoff.html",error="tell must start with 254******")
        elif len(password)<8:
            return render_template("logoff.html",error="password must have 8 or more characters")
        elif password !=confirm_password:
                        return render_template("logoff.html",error="password does not match confirm password")
        else:
            sql="insert into officials_table(badge_no,tell,password)VALUES(%s,%s,%s)"
            #create cursor
            cursor=connection.cursor()
            #execute sql
            cursor.execute(sql,(badge_no,tell,generate_password_hash(password)))
            #commit
            connection.commit()
            # ADD the sms code
            return render_template("logoff.html",success="Regisration successful")
        # chief admin login panel
            
@app.route("/login", methods=['POST','GET'])
def login():

      if request.method == 'POST':
        chief_badge_no=request.form['chief_badge_no']
        password=request.form['password']
        # look up the account by badge number only - password is checked
        # separately against its hash, never compared directly in SQL
        sql='select * from admin_panel where chief_badge_no=%s'
        #create the cursor
        cursor=connection.cursor(pymysql.cursors.DictCursor)
        #execute the sql
        cursor.execute(sql,(chief_badge_no,))
        account=cursor.fetchone()
        if account is None or not check_password_hash(account['password'], password):
            return render_template("login.html",error="Invalid login.please try again")
        else:
              session['chief_badge_no']=chief_badge_no
              return redirect(url_for('admin_dashboard'))
      else:
        return render_template("login.html")
    #   admin panel login
@app.route("/admin", methods=['POST','GET'])
def admin():

      if request.method == 'POST':
        badge_no=request.form['badge_no']
        password=request.form['password']
        # look up the account by badge number only - password is checked
        # separately against its hash, never compared directly in SQL
        sql='select * from officials_table where badge_no=%s'
        #create the cursor
        cursor=connection.cursor(pymysql.cursors.DictCursor)
        #execute the sql
        cursor.execute(sql,(badge_no,))
        officer=cursor.fetchone()
        if officer is None or not check_password_hash(officer['password'], password):
            return render_template("admin.html",error="Invalid login.please try again")
        else:
              session['badge_no']=badge_no
              return redirect(url_for('admin_dashboard'))
      else:
        return render_template("admin.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    # officers OR the chief admin can view this - either session key is enough
    if 'badge_no' not in session and 'chief_badge_no' not in session:
        return redirect(url_for('admin'))
    is_senior='chief_badge_no' in session
    cursor=connection.cursor(pymysql.cursors.DictCursor)

    selected_status=request.args.get('status','All')
    if selected_status in VALID_STATUSES:
        cursor.execute("select * from wenotify where status=%s order by id desc", (selected_status,))
    else:
        selected_status='All'
        cursor.execute("select * from wenotify order by id desc")
    cases=cursor.fetchall()

    # counts per status, for the filter tabs
    cursor.execute("select status, count(*) as c from wenotify group by status")
    counts_raw=cursor.fetchall()
    counts={row['status']: row['c'] for row in counts_raw}
    total_count=sum(counts.values())

    return render_template("admin_dashboard.html",
        cases=cases,
        badge_no=session.get('badge_no') or session.get('chief_badge_no'),
        is_senior=is_senior,
        selected_status=selected_status,
        counts=counts,
        total_count=total_count,
        valid_statuses=VALID_STATUSES)
  
VALID_STATUSES = ["Pending", "In Progress", "Resolved", "Closed"]

@app.route("/admin/update_status/<int:case_id>", methods=['POST'])
def update_status(case_id):
    # officers OR the chief admin can update a case's status
    if 'badge_no' not in session and 'chief_badge_no' not in session:
        return redirect(url_for('admin'))
    new_status=request.form.get('status','')
    if new_status in VALID_STATUSES:
        cursor=connection.cursor()
        cursor.execute("UPDATE wenotify SET status=%s WHERE id=%s", (new_status, case_id))
    keep_filter=request.form.get('current_filter','All')
    return redirect(url_for('admin_dashboard', status=keep_filter))

@app.route("/admin/delete_case/<int:case_id>", methods=['POST'])
def delete_case(case_id):
    # deleting a case is a senior/chief-admin-only action - a regular
    # officer session is NOT enough, even if they're logged in
    if 'chief_badge_no' not in session:   
        return redirect(url_for('admin_dashboard'))
    cursor=connection.cursor()
    cursor.execute("DELETE FROM wenotify WHERE id=%s", (case_id,))
    keep_filter=request.form.get('current_filter','All')
    return redirect(url_for('admin_dashboard', status=keep_filter))

@app.route("/admin/logout")
def admin_logout():
    session.pop('badge_no', None)
    session.pop('chief_badge_no', None)
    return redirect(url_for('admin'))

app.run(debug=True)