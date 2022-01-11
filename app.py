from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


@app.route('/')
def home():
    return render_template('addUser.html')




@app.route("/addUser", methods=["POST"])
def addUser():


    id = request.form['id']
    pw = request.form['pw']
    nickname = request.form['nickname']

    if (id == "" or pw == "" or nickname == ""):
        return jsonify({'result': 'fail', 'msg': 'please check input'});
    doc = {
        'id': id,
        'pw': pw,
        'nickname': nickname,

    }
    db.user.insert_one(doc);
    return jsonify({'msg': "입력."});





# @app.route('/check_dup', methods=['POST'])
# def check_dup():
#     check_id = request.form['check_id']
#     if db.userdb.find_one({'id': check_id}) is None:
#         return jsonify({'msg': "사용 가능한 아이디 입니다."})
#     else:
#         return jsonify({'exists': "이미 존재하는 아이디 입니다."})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    id = request.form['id']
    exists = bool(db.user.find_one({"id": id}))
    return jsonify({'result': 'success', 'exists': exists})




#
# @app.route("/deleteUser", methods=["POST"])
# def deleteUser():
#     id = request.form['id']
#     db.deleteUser(id)
#     return jsonify({'result': 'success'});


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)