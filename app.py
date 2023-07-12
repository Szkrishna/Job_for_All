from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json
import math

with open('config.json','r') as c:
    params=json.load(c)["params"]
local_server = True

app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if local_server:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
    
db = SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    time = db.Column(db.String(11))


class Jobs(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    company = db.Column(db.String(30), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    posted_on = db.Column(db.String(11))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/jobs',methods = ['GET'])
def jobs():
    jobs = Jobs.query.filter_by().all()
    last = math.ceil(len(jobs)/int(params['no_of_jobs']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    jobs = jobs[(page-1)*int(params['no_of_jobs']):(page-1)*int(params['no_of_jobs'])+ int(params['no_of_jobs'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    return render_template('jobs.html', params=params, jobs=jobs, prev=prev, next=next)

@app.route('/employers')
def employers():
    return render_template('employers.html')

@app.route('/contact', methods = ['POST','GET'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(name=name, email=email, phone=phone, message=message, time=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone + "\n" + email
                          )
    return render_template('contact.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/user/login')
def user_login():
    return render_template('user_login.html')

@app.route('/user')
def user_dashboard():
    return render_template('user_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)



