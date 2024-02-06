from datetime import datetime
from flask import Flask, request, redirect, render_template, session, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

app.secret_key = 'qwerty123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),nullable=False)
    occupation = db.Column(db.String(30),nullable=False)
    username = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(20),nullable=False)
    img_filename = db.Column(db.String(255))
    todos = db.relationship("Todos", backref= "user")

    def __init__(self,name,username,password,occupation,img_filename):
        self.name = name
        self.username = username
        self.password = password
        self.occupation = occupation
        self.img_filename = img_filename

  

class Todos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todoName = db.Column(db.String(20),nullable=False)
    todoDesc = db.Column(db.String(30),nullable=False)
    time = db.Column(db.DateTime , default=datetime.now)
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean , default = False)
    user_id = db.Column(db.String, db.ForeignKey('user.username'))
    
    def __init__(self,todoName,todoDesc,user_id,duetime=None):
        self.todoName = todoName
        self.todoDesc = todoDesc
        self.user_id = user_id
        self.due_date = duetime


@app.route('/addtodo',methods=["GET","POST"])
def addtodo():
    if request.method == "POST":
        todoName = request.form['todoName']
        todoDesc = request.form['todoDesc']
        due_time_str = request.form['duetime']
        due_date = datetime.fromisoformat(due_time_str)
        user_id = session['user_id']
        newtodo = Todos(todoName=todoName, todoDesc=todoDesc, duetime=due_date , user_id=user_id)
       
        db.session.add(newtodo)
        db.session.commit()
        return redirect('/dashboard')
        
    return render_template('dashboard.html')


@app.route("/")
def home():
    user_id = session.get('user_id')

    if user_id:
        return render_template('home.html', user=user_id)
    
    return render_template('home.html')

@app.route("/login",methods=["GET","POST"])
def login():
    if 'user_id' in session:
        return redirect('/dashboard')
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username,password=password).first()
        if user:
            session['user_id'] = user.username
            return redirect('/dashboard')
        else:
            return render_template('login.html',msj="Invalid Credentials")
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop('user_id')
    return redirect('/login')



@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form['name']
        
        occupation = request.form['occupation']
        
        username = request.form['username']
        
        password = request.form['password']

        img = request.files['file']

        img_filename = secure_filename(img.filename)

        
        img_path = os.path.join(app.config['UPLOAD_FOLDER'] , img_filename)
        img.save(img_path)
        print("Image object:", img)
        print("Image filename:", img_filename)
        print("Image path:", img_path)
        user = User.query.filter_by(username=username).first()


        if user:
            return render_template("signup.html", msg="User Already Exists")

        new_user = User(name=name,occupation=occupation,username=username,password=password , img_filename=img_filename)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    
    return render_template("signup.html")


@app.route('/dashboard')
def dashboard():
    user_id = session['user_id']
    user = User.query.filter_by(username=user_id).first()
    data = Todos.query.filter_by(user_id=user_id)
    return render_template('dashboard.html', data=data , user=user_id , img_filename = user.img_filename )


@app.route('/delete/<int:id>')
def delete(id):
    todos = Todos.query.filter_by(id=id).first()
    db.session.delete(todos)
    db.session.commit()
    return redirect('/dashboard')
    

@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        name = request.form['name']
        occupation = request.form['occupation']
        password = request.form['password']
        user_id = session['user_id']
        new_user = User.query.filter_by(username=user_id).first()
       
        new_user.name = name
        new_user.occupation = occupation
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()

    
        return redirect('/dashboard')
    return render_template('profileupdate.html')

@app.route('/edit/<int:id>',methods=["GET",'POST'])
def edit(id):
    if request.method== 'POST':
        name = request.form['todoName']
        desc = request.form['todoDesc']
        new_todo = Todos.query.filter_by(id=id).first()
        new_todo.todoName = name
        new_todo.todoDesc = desc
        db.session.add(new_todo)
        db.session.commit()
        return redirect('/dashboard')
    todo = Todos.query.filter_by(id=id).first()
    return render_template('edit.html',todo=todo)


@app.route('/complete/<int:id>')
def complete(id):
    todo = Todos.query.get(id)
    print(todo)
    todo.completed = not todo.completed  
    db.session.commit()
    return redirect("/dashboard")

@app.route('/api/todos')
def todos():
    user_id = session['user_id']
    data = Todos.query.filter_by(user_id=user_id)

    return {}

if __name__ == "__main__":
    app.run(debug=False,host="0.0.0.0")

