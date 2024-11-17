import os, pickledb, random
from flask import Flask, flash, request, redirect, url_for, send_from_directory, Response, jsonify
from werkzeug.utils import secure_filename
import json

app = Flask(__name__, static_url_path="", static_folder="public")
info = {}

db = pickledb.load("data.db", True)
dbplayers = pickledb.load("player.db", True)


UPLOAD_FOLDER = './F24_309-Final-Project/public/gameImages'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not db.get('images'):
    db.lcreate('images')

if not db.get('accounts'):
    db.lcreate('accounts')

@app.get("/")
def start():
    return redirect("start.html")


@app.get('/images')
def get_info():
    data = db.lgetall("images")
    randNum = random.randint(0, len(data) -1)
    data = json.dumps(data[randNum])
    return Response(data, status=200,
                          headers = {
                               "Content-Type": "application/json"
                          })

@app.post('/account')
def addAccount():
    info = {}
    data = db.lgetall("accounts")
    if request.form.get("username") == "" or  request.form.get("password") == "":
         return redirect("create.html")
    for user in data:
        if user["username"] == request.form.get("username"):
            return redirect("create.html") 
    info["username"] = request.form.get("username")
    info["password"] = request.form.get("password")
    data.append(info)
    db.set("accounts", data)
    return redirect("/login.html")

@app.post("/login")
def getLogin():
    data = db.lgetall("accounts")
    currUser = request.form.get("username")
    currPassword = request.form.get("password")
    for user in data:
        if(user["username"] == currUser):
            if(user["password"] == currPassword):
                return redirect("/play.html")
    
    return redirect("/login.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/imagesTemp")
def tempMethod():
    if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
    if file and allowed_file(file.filename):
            info = {}
            data = db.lgetall("images")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            info["file"] = filename
            info["caption"] = request.form.get('caption')
            data.append(info)
            db.set("images", data)
            return redirect("addPhotos.html")
    return redirect("addPhotos.html")

@app.post("/sendScores")
def handleScores():
    data = request.get_json()
    user =  dbplayers.get(data['username'])
    if not user:
        dbplayers.lcreate(data['username'])
        user = dbplayers.get(data['username'])
    
    #order in database is num correct out of how many then time in seconds
    game = [data["correct"], data["total"], data["timer"]]
    print(user)

    if len(user) == 0:
        user.append(game)
    else:
        for i in range(len(user)):
            if user[i][0] < game[0]:
                 user.insert(i, game)
                 break
            elif user[i][0] == game[0]:
                 if(user[i][2] >= game[2]):
                      user.insert(i, game)
                      break
            elif i == len(user) - 1:
                 user.append(game)
    dbplayers.set(data['username'], user)
    return jsonify({"message": "Score received successfully"}), 200
        
@app.get("/getGlobalLeaderboard")
def sendGlobal():
    temp = dbplayers.getall()
    data = {}
    for key in temp:
        data[key] = dbplayers[key][0]

    return jsonify(data)

@app.post("/getPersonalLeaderboard")
def sendPersonal():
    data = request.get_json()
    user = data['username']
    db_Data = dbplayers.get(user)
    returnData = {user : db_Data}
    return jsonify(returnData), 200


if __name__ == '__main__':
    app.run(port=22080, debug=True)