from flask import Flask, request, render_template, session, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string
import csv
import sqlite3
'''
    The password is stored as it is, but in a production environment 
    we will have to encrypt it with something like flask_bcrypt.

'''
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
#cursor.execute('drop table files;')
#cursor.execute("CREATE TABLE files (filename VARCHAR(100), hash VARCHAR(255) NOT NULL);")
#table - files - name and hash
app = Flask(__name__)

cwd = f"os.getcwd()/files"

app.config['UPLOAD_FOLDER'] = "C:/Users/GB/Desktop/dummy projects/files/"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    msg = ''
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        file = request.files['hello']
        filename = file.filename
        print(filename)
        extension = filename.split(".")[-1]
        print(extension)
        hash = ''.join(random.choices(string.ascii_letters, k=30))
        print(hash)
        path = os.path.join(app.config['UPLOAD_FOLDER'], (hash +"."+ extension))
        print(path)
        file.save(path)
        cur.execute("INSERT INTO files (filename, hash) VALUES (?, ?)", (filename, hash))

        # commit the transacti on and close the connection
        conn.commit()
        conn.close()
        return render_template('msg.html', message=hash)

    return render_template('send.html')

@app.route('/recieve', methods=['POST', 'GET'])
@app.route('/recieve/<string:hash>')
def recieve(hash='none'):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    if hash != 'none':
        cursor.execute("SELECT * FROM files WHERE hash=?", (hash,))
        file_name_hash = cursor.fetchone()
        if file_name_hash == None:
            message = "Wrong Hash"
            return render_template('recieve.html', message=message)
        else: 
            file_name = file_name_hash[0]
            hash = file_name_hash[1]
            extension = file_name.split(".")[-1]
            path = os.path.join(app.config['UPLOAD_FOLDER'], (hash +"."+ extension))
            return send_file(path, as_attachment=True,download_name=file_name)
            return render_template('msg.html', message="downloaded successfuly")
            
    elif request.method == 'POST':
        hash = request.form['hash']
        cursor.execute("SELECT * FROM files where hash=?", (hash,))
        file_name_hash = cursor.fetchone()
        print(file_name_hash)
        if file_name_hash == None:
            message = "Wrong Hash"
            return render_template("recieve.html", message=message)
        else:
            file_name = file_name_hash[0]
            hash = file_name_hash[1]
            extension = file_name.split(".")[-1]
            path = os.path.join(app.config['UPLOAD_FOLDER'], (hash +"."+ extension))
            return send_file(path, as_attachment=True,download_name=file_name)
            return render_template('msg.html', message="downloaded successfuly")

    return render_template('recieve.html')

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        name_='anonfuckingminion'
        password_ = 'its3423averylongpasswndlkjfdjkl'
        name = request.form.get('name')
        password = request.form.get('password')
        if name == name_ and password == password_:
            message = ''
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute('drop table files;')
            cur.execute("CREATE TABLE files (filename VARCHAR(100), hash VARCHAR(255) NOT NULL);")
            try: 
                os.system('rm-rf files')
                os.system('mkdir files')
            except:
                message = 'unable to delete directory files'
            conn.close()
            return render_template('admin.html', message=message)
    return render_template('admin.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)