"""
Responsible for running our app instance
"""
from flask import *
#session
app.secret_key="qwer1234tyui"
import pymysql
connection=pymysql.connect(host='localhost',user="root",password="",database="owenke")


app=Flask(__name__)
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
        file=request.form['file_upload']
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

        #validation checks
        if " " in username:
            return render_template("home.html",error="username cannot be left empty",formdata=formdata)
        if len(user_id)<7 or len(user_id)>8:
                return render_template("home.html",error="id should not be less than 7 characters or more than 8",formdata=formdata)
        elif "@" not in email:
            return render_template("home.html",error="email must have @",formdata=formdata)
        elif not phone.startswith("254"):
            return render_template("home.html",error="phone must start with 254*********",formdata=formdata)
        elif " " in event_desc:
            return render_template("home.html",error="eventdesc cannot be left empty",formdata=formdata)
        elif " " in file:
                return render_template("home.html",error="fileupload cannot be left empty",formdata=formdata)
        elif " " in event_date:
                return render_template("home.html",error="date cannot be left empty",formdata=formdata)
        elif " " in County:
                return render_template("home.html",error="county cannot be left empty",formdata=formdata)
        elif " " in Location:
                return render_template("home.html",error="location cannot be left empty",formdata=formdata)
        elif " " in contact_on:
                    return render_template("home.html",error="an option must be selected on contact_on",formdata=formdata)
        elif " " in gender:
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
                gender=gender)
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
            cursor.execute(sql,(badge_no,tell,password))
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
        # create sql to select badge_noo  and password
        sql='select * from admin_panel where chief_badge_no=%sand password=%s'
        #create the cursor
        cursor=connection.cursor()
        #execute the sql
        cursor.execute(sql,(chief_badge_no,password))
        #check if there is a user with the above details
        # session['badge_no']=badge_no
        if cursor.rowcount==0:
            return render_template("login.html",error="Invalid login.please try again")
        else:
              return render_template("logoff.html")
      else:
        return render_template("login.html")
    #   admin panel login
@app.route("/admin", methods=['POST','GET'])
def admin():

      if request.method == 'POST':
        badge_no=request.form['badge_no']
        password=request.form['password']
        # create sql to select badge_noo  and password
        sql='select * from officials_table where badge_no=%sand password=%s'
        #create the cursor
        cursor=connection.cursor()
        #execute the sql
        cursor.execute(sql,(badge_no,password))
        #check if there is a user with the above details
        # session['badge_no']=badge_no
        if cursor.rowcount==0:
            return render_template("admin.html",error="Invalid login.please try again")
        else:
              return redirect("http://localhost/phpmyadmin/index.php?route=/sql&pos=0&db=owenke&table=wenotify")
      else:
        return render_template("admin.html")
app.run(debug=True)