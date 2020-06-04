import os
import hashlib
import ast 
from flask import Flask, render_template, request
from AESCode import AESCode
from os import listdir
from os.path import isfile, join



k = AESCode()


app = Flask(__name__, static_folder="store")

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("encrypt.html", ranKey = k.random_key_gen())

@app.route("/encrypt", methods = ["POST"])



def encrypt():
    target = os.path.join(APP_ROOT, "store")
    
    secret_key = request.form["key"]
    store_files = []
    encrypted_file = []
    md5Value = []

    for file in request.files.getlist("folder"):
        if file.filename != '':
            file.filename = file.filename.split('/')[-1] 
            store_files.append(file)
    for file in request.files.getlist("file"):
        if file.filename != '': 
            store_files.append(file)

    if len(store_files) == 0:
        return render_template("empty_error.html")

    if not os.path.isdir(target):
        os.mkdir(target)
        
    for upload in store_files:
        filename = upload.filename
        destination = "/".join([target, filename])
        print("Save it to:", destination)
        upload.save(destination)

        md5_hash = hashlib.md5()
        openFile = open(destination, "rb")
        content = openFile.read()
        md5_hash.update(content)
        md5Value.append(md5_hash.hexdigest())

        encrypted_file.append(k.encrypt_file(destination, secret_key))

    return render_template("complete.html", file_name = encrypted_file, md5hash = md5Value)


@app.route("/decrypt", methods = ["POST"])
def decrypt():

    secret_key = request.form["key"]
    destination = request.form["path"]
    md5hashOld = request.form["md5hashOld"]


    decrypted_file = []
    decrypted_file_name = []
    md5Value = []

    print("destination: ", destination)
    destination = destination.strip('][').split(', ')
    print("destination: ", destination)

    for upload in destination:
        decrypt = k.decrypt_file(upload.strip('\''), secret_key)
        decrypted_file.append(decrypt)
        print("decrypted_file: ", decrypted_file)

        check = "There aren't the same file!"

        if decrypt != None:

            md5_hash = hashlib.md5()
            openFile = open(decrypt, "rb")
            content = openFile.read()
            md5_hash.update(content)
            print(md5_hash)
            md5Value.append(md5_hash.hexdigest())

            decrypted_file_array = decrypt.split('/')
            decrypted_file_name.append(decrypted_file_array[-1])

            check = "There are the same file!"

    if len(decrypted_file) == len(decrypted_file_name):
        return render_template("result.html", path = decrypted_file, file_name = decrypted_file_name, md5hashNew = md5Value, md5hashOld = md5hashOld, check = check)
    
    else:
        return render_template("error_result.html")

if __name__ == "__main__":
    app.run(port = 4556, debug=True)

