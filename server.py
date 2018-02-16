from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import datetime #time stuff
import time
import re #Regex
import md5 #hasing
import os, binascii #for hasing


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
mysql = MySQLConnector(app,'users')
app.secret_key = '0118999881999119725'


@app.route('/')
def index():                         # run query with query_db()
	query = "SELECT id, CONCAT(first_name, ' ' , last_name) as name, DATE_FORMAT(created_at, '%m/%d/%Y') as date1, email FROM users"
	result = mysql.query_db(query)
	print result
	return render_template('index.html', users=result)


@app.route('/users/new')
def newuser():
	return render_template('newuser.html')

@app.route('/users/<id>')
def showuser(id):
	query = "SELECT id, CONCAT(first_name, ' ' , last_name) as name, DATE_FORMAT(created_at, '%m/%d/%Y') as date1, email FROM users WHERE id=:id"
	data = {'id': id}
	result = mysql.query_db(query, data)
	return render_template("showuser.html", user=result[0])


#UPDATE USER post page (EMAIL MUST BE DIFFERENT)
@app.route('/users/<id>', methods=['POST'])
def updateuser(id):
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email=request.form['email']

	if(len(first_name)==0):
		flash("First Name cannot be empty!")
		return redirect('/users/'+str(id)+"/edit")
	elif(not first_name.isalpha()):
		flash("First Name cannot contain numbers")
		return redirect('/users/'+str(id)+"/edit")

	if(len(last_name)==0):
   		flash("Last Name cannot be empty!")
		return redirect('/users/'+str(id)+"/edit")
   	elif(not last_name.isalpha()):
   		flash("Last Name cannot contain numbers")
		return redirect('/users/'+str(id)+"/edit")

	if(len(email) < 1):
		flash("Email cannot be empty!")
		return redirect('/users/'+str(id)+"/edit")
	elif not EMAIL_REGEX.match(email):
		flash("Invalid Email Address!") 
		return redirect('/users/'+str(id)+"/edit")

    #check if email exists in database already
	query = "SELECT * FROM users WHERE email=:email"
	data = {'email': email}
	i = mysql.query_db(query, data)
	if len(i)<1:
		query = "UPDATE users SET first_name=:first_name, last_name=:last_name, email=:email, updated_at=Now() WHERE id=:id"
		data = {
		'id': id,
		'first_name':first_name,
		'last_name':last_name,
		'email':email
	}
		result = mysql.query_db(query, data)
		flash("Please login")
	else:
		flash("Email already exists")
		return redirect('/users/'+str(id)+"/edit")

	return redirect('/')

#View Edit page
@app.route('/users/<id>/edit')
def edituser(id):
	query = "SELECT id, first_name, last_name, email FROM users WHERE id=:id"
	data = {'id': id}
	result = mysql.query_db(query, data)
	return render_template("edituser.html", user=result[0])

#Post create page
@app.route('/users/create', methods=['POST'])
def createuser():
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email=request.form['email']


    #Validations Below
	if(len(first_name)==0):
		flash("First Name cannot be empty!")
		return redirect('/')
	elif(not first_name.isalpha()):
		flash("First Name cannot contain numbers")
		return redirect('/')

	if(len(last_name)==0):
   		flash("Last Name cannot be empty!")
   		return redirect('/')
   	elif(not last_name.isalpha()):
   		flash("Last Name cannot contain numbers")
   		return redirect('/')

	if(len(email) < 1):
		flash("Email cannot be empty!")
		return redirect('/')
	elif not EMAIL_REGEX.match(email):
		flash("Invalid Email Address!") 
		return redirect('/')

    #check if email exists in database already
	query = "SELECT * FROM users WHERE email=:email"
	data = {'email': email}
	i = mysql.query_db(query, data)
	if len(i)<1:
		data =  {'first_name': first_name,'last_name': last_name,'email' : email}
		query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES (:first_name, :last_name, :email, Now(), Now())"
		mysql.query_db(query, data)
		flash("Please login")
	else:
		flash("Email already exists")
		return redirect('/users/new')
	return redirect('/')


@app.route('/users/<id>/destroy')
def destroy(id):
	query = "DELETE  FROM users WHERE id=:id"
	data = {'id': id}
	result = mysql.query_db(query, data)
	return redirect('/')

app.run(debug=True)
