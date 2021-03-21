from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app=Flask(__name__)
app.secret_key = "abc"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/blog'
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='', server='localhost', database='blog')
#app.config['SQLALCHEMY_DATABASE_URI'] =params["local_uri"]
app.config['UPLOAD_FOLDER']='static/temp'
db = SQLAlchemy(app)

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['user_id'],
    MAIL_PASSWORD = params['pass']
)
mail = Mail(app)

class Contact(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    Phone_number = db.Column(db.String(12), nullable=False)
    Message = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=False)
    Email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(12), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    image_file = db.Column(db.String(20), nullable=False)


@app.route('/post/<string:slug_no>')
def post(slug_no):
    posts=Posts.query.filter_by(slug=slug_no).first()
    return render_template("post.html",posts=posts,params=params)
@app.route("/login",methods=['GET','POST'])
def login():
    if 'user' in session and session['user']==params['admin']:
        print("Post request 1")
        posts=Posts.query.all()
        return render_template("dashboard.html",params=params ,posts=posts)
    if request.method=='POST':
        print("Post request 2")
        username=request.form.get('email')
        userpass=request.form.get('pass')
        if(username==params["admin"] and userpass==params['admin_pass']):
            session['user']=username
            print("Post request 3")
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts=posts)

    return render_template("login.html")
@app.route("/")
def home():
    posts=Posts.query.filter_by().all()[0:2]
    return  render_template("index.html",params=params,posts=posts)

@app.route('/about')
def about():
    return render_template("about.html",params=params)

@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']==params['admin']:
        if request.method=='POST':
            title=request.form.get('title')
            content=request.form.get('content')
            slug=request.form.get('slug')
            image_file=request.files['image_file']
            date=datetime.now()
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(image_file.filename)))

            if sno=='0':
                post=Posts(title=title,content=content,slug=slug,date=date,image_file=image_file.filename)
                db.session.add(post)
                db.session.commit()

            else:
                posts=Posts.query.filter_by(sno=sno).first()
                posts.title=title
                posts.content=content
                posts.slug=slug
                posts.image_file=image_file

                return redirect('/edit/'+sno)
    post = Posts.query.filter_by(sno=sno).first()
    return render_template("edit.html",params=params,post=post,sno=sno)
@app.route('/delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin']:
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/login")
@app.route('/logout')
def logout():
    session.pop('user')
    return render_template("login.html")
@app.route('/contact',methods=['POST','GET'])
def contact():
    p=0
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get("phone")
        msg=request.form.get('message')
        entry = Contact(Name=name, Phone_number = phone, Message = msg, Date= datetime.now(),Email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params["user_id"]],
                          body=msg
                          )
    return render_template("contact.html",params=params)



if __name__=="__main__":
    app.run(debug=True)
