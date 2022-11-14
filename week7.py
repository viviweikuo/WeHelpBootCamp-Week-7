import sys
import json
import mysql.connector
from flask import Flask
from flask import request 
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import json
from flask import jsonify

week7 = Flask(
    __name__,
    static_folder = "public",
    static_url_path = "/"
)
week7.config['JSON_AS_ASCII'] = False

week7.secret_key = "大正紅茶拿鐵微糖去冰"

website = mysql.connector.connect(
    host = "localhost",
    user = "viviweikuo",
    password = "****",
    database = "website"
)

mycursor = website.cursor(buffered=True)

@week7.route("/")
def index():
    if "username" in session:
        return redirect("/member")
    return render_template("index.html")

@week7.route("/signup", methods=["POST"])
def signup():

    member_new_name = request.form["name"]
    member_new_username = request.form["username"]
    member_new_password = request.form["password"]

    member_search = "SELECT username FROM member WHERE username = %s"
    mycursor.execute(member_search, (member_new_username,))
    search_result = mycursor.rowcount

    if (search_result == 1):
        return redirect(url_for("error", message = "此帳號已被註冊"))
    else:
        session["name"] =  member_new_name
        session["username"] = member_new_username
        session["password"] = member_new_password

        member_add = "INSERT INTO member(name, username, password) VALUES(%s, %s, %s)"
        value = (member_new_name, member_new_username, member_new_password)
        mycursor.execute(member_add, value)
        website.commit()
        return redirect("/")

@week7.route("/signin", methods=["POST"])
def signin():

    member_username = request.form["username"]
    member_password = request.form["password"]

    member_search = "SELECT username FROM member WHERE username = %s AND password = %s"
    mycursor.execute(member_search, (member_username, member_password,))
    search_result = mycursor.rowcount

    if (search_result == 1):
        session["username"] = member_username
        session["password"] = member_password
        return redirect("/member")
    else:
        return redirect(url_for("error", message = "帳號或密碼輸入錯誤"))

@week7.route("/member")
def member():
    if "username" in session:
        member_search = "SELECT * FROM member WHERE username = %s AND password = %s"
        mycursor.execute(member_search, (session["username"], session["password"],))
        member = mycursor.fetchone()
        
        return render_template("member.html", name = member[1])
    else:
        return redirect("/")

@week7.route("/error")
def error():
    result = request.args.get("message")
    return render_template("error.html", message = result)

@week7.route("/signout")
def signout():
    session.pop("name", None)
    session.pop("username", None)
    session.pop("password", None)
    return redirect("/")

@week7.route("/api/member")
def search_name():
    # search database
    username = request.args.get("username")
    search_value = "SELECT id, name, username FROM member WHERE username = %s"
    mycursor.execute(search_value, (username,))
    member_data = mycursor.fetchall()
    search_row = mycursor.rowcount

    search_data = {}

    if (search_row == 1):
        for result in member_data:
            search_data = {"data":{"id":result[0], "name":result[1], "username":result[2]}}
            json_string = jsonify(search_data)
            return json_string
    else:
        null = None
        search_data = {"data":null}
        json_string = jsonify(search_data)
        return json_string

@week7.route("/api/member", methods=["PATCH"])
def update_name():
    # save new name
    newNameArray = request.get_json("newName")
    username = session["username"]
    update_name = "UPDATE member SET name = %s WHERE username = %s"
    mycursor.execute(update_name, (newNameArray["name"], username,))
    website.commit()

    # find new name in database 
    search_value = "SELECT name FROM member WHERE name = %s"
    mycursor.execute(search_value, (newNameArray["name"],))
    member_data = mycursor.fetchall()
    search_row = mycursor.rowcount

    if (search_row == 1):
        res_data = {"ok": True} 
        return jsonify(res_data)
    else:
        res_data = {"error": True} 
        return jsonify(res_data)

week7.run(port=3000)
