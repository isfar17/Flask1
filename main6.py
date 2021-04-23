from datetime import date
from operator import pos
import re
from flask import Flask, render_template,redirect
from flask.globals import request
from flask_sqlalchemy import SQLAlchemy
import datetime
import json
from flask_mail import Mail

with open("config.json","r") as f:
    params=json.load(f)
params=params["var"]

localserver=params["localserver"]

app = Flask(__name__)

app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["email_user"],
    MAIL_PASSWORD=params["email_pass"],
)
mail=Mail(app)#must give the parameter,name will be the name of app

if localserver:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["database_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_database_uri"]
db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=False, nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(20), nullable=False)
    messege = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True,default=datetime.datetime.now)

    def __repr__(self):
        return f'{self.name} -  {self.messege}'
class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), unique=False, nullable=False)
    author = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(20), nullable=False)
    slug=db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True,default=datetime.datetime.now)

    def __repr__(self):
        return f'{self.title}  : by  {self.author}'


@app.route("/")
def index():
    posts=Post.query.filter_by().all()[0:5]
    return render_template("layout.html",val=params,posts=posts)  # name will be used in jinja template
    # x is taken from the code
@app.route("/about")
def about():
    return render_template("about.html",val=params)

@app.route("/edit/<string:sno>", methods=["GET", "POST"])
def edit(sno):
    if (request.method=="POST"):
        title =request.form.get("title")
        author = request.form.get("author")
        content =request.form.get("content")
        slug=request.form.get("slug")
        date =datetime.datetime.now()
        if sno=="0":
            npost=Post(title=title,author=author,content=content,slug=slug,date=date)
            db.session.add(npost)
            db.session.commit()
 
        else:
            npost=Post.query.filter_by(sno=sno).first()

            npost.title=title
            npost.author=author
            npost.slug=slug
            npost.content=content
            npost.date=date
            db.session.add(npost)
            db.session.commit()
            
            return redirect("/edit/"+sno)
    npost=Post.query.filter_by(sno=sno).first()
    return render_template("edit.html",val=params,post=npost,sno=sno)

@app.route("/delete/<string:sno>")
def delete(sno):
    post=Post.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    posts=Post.query.filter_by().all()
    return render_template("dashboard.html",posts=posts,val=params)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if (request.method == "POST"):
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        saveval = Contact(name=name, email=email, phone_num=phone,
                          messege=message, date=datetime.datetime.now())
        db.session.add(saveval)
        db.session.commit()
        mail.send_message("New message from "+name,sender=email,recipients=[params["email_user"]],body=message+"\n"+phone)
    return render_template("contact.html",val=params)

@app.route("/post",methods=["GET","POST"])
def post():
    return render_template("post.html",val=params)

@app.route("/post/<string:post_slug>",methods=["GET"])
def clickedpost(post_slug):
    posts=Post.query.filter_by(slug=post_slug).first()
    return render_template("post.html",val=posts)

app.run(debug=True)
