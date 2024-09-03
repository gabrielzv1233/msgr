import shelve
from flask import Flask, make_response, request, render_template, redirect, url_for
import uuid
import datetime
import logging
import hashlib
from markupsafe import escape
import re
import os

app = Flask(__name__)

initial_value = {"IP": "reason"}
os.makedirs('data', exist_ok=True)
os.makedirs('static/conversations', exist_ok=True)
with shelve.open('data/settings') as db:
    if 'banned_ips' not in db:
        db['banned_ips'] =  r"""{"ip":'reason'}"""
with shelve.open('data/settings') as db:
    if 'banned_uuids' not in db:
        db['banned_uuids'] =  r"""{"uuid":'reason'}"""
with shelve.open('data/settings') as db:
    if 'special_users' not in db:
        db['special_users'] =  r"""{"uuid":'<b>{username}</b> <i>@{time}</i>: {message}<br>\n'}"""
        
        
last_messages = []

def short_uuid():
    # Generate a UUID
    uuid_value = uuid.uuid4()

    # Convert UUID to a bytes object
    uuid_bytes = uuid_value.bytes

    # Hash the UUID bytes using MD5 or SHA1
    hashed_uuid = hashlib.md5(uuid_bytes).digest()

    # Convert hashed UUID to a hexadecimal string
    hex_hashed_uuid = hashed_uuid.hex()

    # Truncate the hexadecimal string to 6 characters
    short_uuid = hex_hashed_uuid[:6]

    return short_uuid

filter = {
    "fuck": "f**k",
    "nigga": "n***a",
    "nigger": "n****r",
    "cunt": "c**t",
    "cock": "pp",
    "penis": "pp",
    "niggger": "n*****r",
    "niger": "n**er",
    "niga": "n**a",
    "faggot": "f****t",
    "fagot": "f***t",
    "kill your self": "i hope you have a long happy life :D", "kill your self": "i hope you have a long happy life :D",
    "pornhub.com": "[banned-URL]",
    "suck it": "s**t it",
    "niiga": "n***a",
    "卐": "",
    "nigg3r": "n****r"
}

admin_key = short_uuid()
print("admin key: " + admin_key + "\n")

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/admin/settings", strict_slashes=False)
def settings():
    db = shelve.open('data/admindata')
    username = request.cookies.get('admin_un')
    login_token = request.cookies.get('admin_LOGIN_TOKEN')
    if not username or not login_token:
        response = make_response("not logged in")
        response.delete_cookie("admin_un")
        response.delete_cookie("admin_LOGIN_TOKEN")
        response.headers["Location"] = "/admin/login"
        return response, 302
    else:
        if username in db:
            data = db[username]
            if login_token == data[1]:
                db.close()
                db = shelve.open('data/settings')
                if "banned_ips" in db:
                    ips = db["banned_ips"]
                else:
                    ips = r"""{"ip":'reason'}"""
                    
                if "banned_uuids" in db:
                    uuids = db["banned_uuids"]
                else:
                    uuids = r"""{"uuid":'reason'}"""
            
                    
                if "special_users" in db:
                    special_users = db["special_users"]
                else:
                    special_users = r"""{"uuid":'<b>{username}</b> <i>@{time}</i>: {message}<br>\n'}"""
                db["banned_ips"] = ips
                db["banned_uuids"] = uuids
                db["special_users"] = special_users
                db.close()
                return f"""<!DOCTYPE html>
            <html>
            <head>
            <meta charset='UTF-8'>
            <meta name='description' content='A free messaging app complete with accounts and special styling for your message'>
            <meta name='author' content='Gabrielzv1233'>
            <title>msgr v2</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                textarea {{
                    resize: both;
                    width: 100%;
                    height: 27vh;
                }}
            
                body {{
                    background-color: #1C2333;
                    color: white;
                }}
            
                textarea {{
                    background-color: #1C2333;
                    color: white;
                    border-radius: 10px;
                    border: 1px solid white;
                }}
            
                input[type="submit"] {{
                    border-radius: 5px;
                }}
            </style>
            <script>
                document.addEventListener("keydown", function(event) {{
                    if (event.ctrlKey && event.key === "s") {{
                        event.preventDefault(); // Prevent the default browser save function
                        document.querySelector('input[type="submit"]').click(); // Trigger the submit button click event
                    }}
                }});
            </script>
            </head>
            <body>
            <form method="POST" action="/admin/_settings">
                <input type="hidden" name="admin_key" value="{admin_key}">
                banned IPs:<br>
                <textarea name="ips">{ips}</textarea><br>
                banned UUIDs:<br>
                <textarea name="uuids">{uuids}</textarea><br>
                Special users:<br>
                <textarea name="special_users">{special_users}</textarea><br>
                <input type="submit" value="Save">
            </form>
            </body>
            </html>"""
            else:
                db.close()
                response = make_response("not logged in")
                response.delete_cookie("admin_un")
                response.delete_cookie("admin_LOGIN_TOKEN")
                response.headers["Location"] = "/admin/login"
                return response, 302

@app.route("/admin/_settings", methods=["POST"], strict_slashes=False)
def change_settings():
    get_admin_key = request.form["admin_key"]
    if admin_key != get_admin_key:
        redirect(url_for("admin"))
    db = shelve.open('data/settings')
    ips = request.form["ips"]
    uuids = request.form["uuids"]
    special_users = request.form["special_users"]
    db["banned_ips"] = ips
    db["banned_uuids"] = uuids
    db["special_users"] = special_users
    db.close()
    return redirect(url_for("settings"))

@app.route("/admin/messages", strict_slashes=False)
def messages():
    file = "messages.html"
    db = shelve.open('data/admindata')
    username = request.cookies.get('admin_un')
    login_token = request.cookies.get('admin_LOGIN_TOKEN')
    if not username or not login_token:
        response = make_response("not logged in")
        response.delete_cookie("admin_un")
        response.delete_cookie("admin_LOGIN_TOKEN")
        response.headers["Location"] = "/admin/login"
        return response, 302
    else:
        if username in db:
            data = db[username]
            if login_token == data[1]:
                db.close()
                with open(f'static/conversations/{file}', 'r') as file:
                    messages = file.read()
                return f"""<!DOCTYPE html>
            <html>
            <head>
            <meta charset='UTF-8'>
            <meta name='description' content='A free messaging app complete with accounts and special styling for your message'>
            <meta name='author' content='Gabrielzv1233'>
            <title>msgr v2</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                textarea {{
                    resize: both;
                    width: 100%;
                    height: 90vh;
                }}
            
                body {{
                    background-color: #1C2333;
                    color: white;
                }}
            
                textarea {{
                    background-color: #1C2333;
                    color: white;
                    border-radius: 10px;
                    border: 1px solid white;
                }}
            
                input[type="submit"] {{
                    border-radius: 5px;
                }}
            </style>
            <script>
                document.addEventListener("keydown", function(event) {{
                    if (event.ctrlKey && event.key === "s") {{
                        event.preventDefault();
                        document.querySelector('input[type="submit"]').click();
                    }}
                }});
            </script>
            </head>
            <body>
            <form method="POST" action="/admin/_messages">
                <input type="hidden" name="admin_key" value="{admin_key}">
                messages:<br>
                <textarea name="messages">{messages}</textarea><br>
                <input type="submit" value="Save">
            </form>
            </body>
            </html>"""
            else:
                db.close()
                response = make_response("not logged in")
                response.delete_cookie("admin_un")
                response.delete_cookie("admin_LOGIN_TOKEN")
                response.headers["Location"] = "/admin/login"
                return response, 302

@app.route("/admin/_messages", methods=["POST"], strict_slashes=False)
def change_messages():
    file = "messages.html"
    get_admin_key = request.form["admin_key"]
    if admin_key != get_admin_key:
        redirect(url_for("admin"))
    db = shelve.open('data/settings')
    messages = request.form["messages"]
    messages = messages.splitlines()
    messages = "\n".join(messages)
    with open(f"static/conversations/{file}", 'w') as file:
        file.write(messages + '\n')
    db.close()
    return redirect(url_for("messages"))

@app.errorhandler(404)
def page_not_found(e):
    return f"""<html><meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>
  <head>
    <meta charset="UTF-8">
    <title>404 Page Not Found</title>
  </head>
<body>
<h1>Page not found</h1>
<p>This page dose not exist, please check the url</p>
<a href="/">main page</a>&emsp;<a href="/login">login</a>&emsp;<a href="/signup">signup</a>&emsp;
</body>
</html>""", 404


@app.route("/admin/send", strict_slashes=False)
def admin_send():
    file = "messages.html"
    db = shelve.open('data/admindata')
    username = request.cookies.get('admin_un')
    login_token = request.cookies.get('admin_LOGIN_TOKEN')
    if not username or not login_token:
        response = make_response("not logged in")
        response.delete_cookie("admin_un")
        response.delete_cookie("admin_LOGIN_TOKEN")
        response.headers["Location"] = "/admin/login"
        return response, 302
    else:
        if username in db:
            data = db[username]
            if login_token == data[1]:
                db.close()
                return render_template("console message.html", admin_key=admin_key, file=file)
            else:
                db.close()
                response = make_response("not logged in")
                response.delete_cookie("admin_un")
                response.delete_cookie("admin_LOGIN_TOKEN")
                response.headers["Location"] = "/admin/login"
                return response, 302
            
@app.route("/admin/_send", methods=["POST"], strict_slashes=False)
def send_admin():
    file = "messages.html"
    time = datetime.datetime.now().strftime("%H:%M")
    get_admin_key = request.form["admin_key"]
    if admin_key != get_admin_key:
        redirect(url_for("admin"))
    message = request.form["message"]
    with open(f'static/conversations/{file}', 'a') as file:
        message = message.replace("<", "&#60;")
        message = message.replace(">", "&#62;")
        message = message.replace('"', "&#34;")
        message = message.replace("'", "&#39;")
        if message == "" or not message:
            return redirect(url_for('main'))
        message = re.sub(r'!(https?://\S+)', r'<a href="\1">\1</a>', message)
        message = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', message)
        message = re.sub(r"___(.*?)___", r'<u>\1</u>', message)
        message = re.sub(r"~~(.*?)~~", r'<s>\1</s>', message)
        message = re.sub(r"```(.*?)```", r'<div class="code">\1</div>', message)
        message = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', message)
        message = re.sub(r"\*(.*?)\*", r'<i>\1</i>', message)
        file.write(f"""<b style="color:cyan;">[</b><b style="color:red;">CONSOLE</b><b style="color:cyan;">]</b></b> <i>@{time}</i>: {message}<br>\n""")
    return redirect(url_for("admin_send"))

@app.route("/")
def main():
    file = "messages.html"
    print('Connection: "/" code: 200')
    db = shelve.open('data/userdata')
    username = request.cookies.get('un')
    login_token = request.cookies.get('LOGIN_TOKEN')
    if not username or not login_token:
        response = make_response(render_template('no_account.html', signup=url_for('signup'), login=url_for('login'), file=file))
        response.delete_cookie("LOGIN_TOKEN")
        response.delete_cookie("un")
        return response
    else: 
        if username in db:
            data = db[username]
            if login_token == data[1]:
                db.close()
                if request.cookies.get('admin_un') and request.cookies.get('admin_LOGIN_TOKEN'):
                    adminbutton = """<button style="position: absolute;top: 10px;left: 10px;" onclick="window.open('/admin', '_blank');">admin panel</button>"""
                else:
                    adminbutton = ""
                return render_template('index.html', username=username, adminbutton=adminbutton, file=file)
            else:
                db.close()
                response = make_response(render_template('no_account.html', signup=url_for('signup'), login=url_for('login'), file=file))
                response.delete_cookie("LOGIN_TOKEN")
                response.delete_cookie("un")
                return response
    response = make_response("Something went wrong, clearing cookies")
    response.delete_cookie("LOGIN_TOKEN")
    response.delete_cookie("un")
    response.headers["Location"] = "/"
    return response, 302

@app.route("/raw", strict_slashes=False)
def raw():
    file = "messages.html"
    return render_template('raw.html', file=file)

@app.route('/account', strict_slashes=False)
def account():
    db = shelve.open('data/userdata')
    username = request.cookies.get('un')
    login_token = request.cookies.get('LOGIN_TOKEN')
    if not username or not login_token:
        response = make_response("not logged in")
        response.delete_cookie("LOGIN_TOKEN")
        response.delete_cookie("un")
        response.headers["Location"] = "/login"
        return response
    else: 
        if username in db:
            data = db[username]
            if login_token == data[1]:
                db.close()
                return render_template('account.html', username=username)
            else:
                db.close()
                response = make_response("not logged in")
                response.delete_cookie("LOGIN_TOKEN")
                response.delete_cookie("un")
                response.headers["Location"] = "/login"
                return response
    response = make_response("Something went wrong, clearing cookies")
    response.delete_cookie("LOGIN_TOKEN")
    response.delete_cookie("un")
    response.headers["Location"] = "/"
    return response, 302
            
@app.route("/change_password", methods=["POST"], strict_slashes=False)
def change_password():
    db = shelve.open('data/userdata')
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    username = request.cookies.get('un')
    login_token = request.cookies.get('LOGIN_TOKEN')
    if not username or not login_token:
        return "<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Unable to delete account: not logged in"
    else:
        if username in db:
            data = db[username]
            if not current_password == data[0]:
                return "<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Unable to delete account: not logged in"
            if login_token == data[1]:
                db[username] = [new_password, data[1], data[2]]
                db.close()
                response = make_response("Password changed")
                
                response.headers["Location"] = "/account"
                return response, 302
            else:
                db.close()
                return "<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Unable to delete account: not logged in"    

@app.route('/send', methods=["POST"], strict_slashes=False)
def send():
    file = "messages.html"
    db = shelve.open('data/settings')
    banned_ips = eval(db["banned_ips"])
    banned_uuids = eval(db["banned_uuids"])
    special_users = eval(db["special_users"])
    db.close()
    db = shelve.open('data/userdata')
    username = request.cookies.get('un')
    login_token = request.cookies.get('LOGIN_TOKEN')
    if not username or not login_token:
        response = make_response("not logged in")
        response.delete_cookie("un")
        response.delete_cookie("LOGIN_TOKEN")
        response.headers["Location"] = "/login"
        return response, 302
    else: 
        if username in db:
            data = db[username]
            if login_token == data[1]:
                db.close()
                db = shelve.open('data/userdata')
                time = datetime.datetime.now().strftime("%H:%M")
                username = request.cookies.get('un')
                login_token = request.cookies.get('LOGIN_TOKEN')
                client_ip = request.headers.get('X-Forwarded-For')
                if client_ip in banned_ips:
                    return f"<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>You have been banned<br>Reason:<br>{banned_ips[client_ip]}"
                if not username or not login_token:
                    response = make_response(render_template('no_account.html', signup=url_for('signup'), login=url_for('login')))
                    response.delete_cookie("LOGIN_TOKEN")
                    response.delete_cookie("un")
                    return response
                else: 
                    if username in db:
                        data = db[username]
                        if login_token == data[1]:
                            db.close()
                            if data[1] in banned_uuids:
                                return f"<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>You have been banned<br>Reason:<br>{banned_uuids[data[1]]}"
                            message = request.form["message"][:600]
                            with open(f'static/conversations/{file}', 'a') as file:
                                message = message.replace("<", "&#60;")
                                message = message.replace(">", "&#62;")
                                message = message.replace('"', "&#34;")
                                message = message.replace("'", "&#39;")
                                for word in filter:
                                    message = re.sub(re.compile(re.escape(word), re.IGNORECASE), filter[word], message)
                                if message == "" or not message:
                                    return redirect(url_for('main'))
                                message = re.sub(r'!(https?://\S+)', r'<a href="\1">\1</a>', message)
                                message = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', message)
                                message = re.sub(r"___(.*?)___", r'<u>\1</u>', message)
                                message = re.sub(r"~~(.*?)~~", r'<s>\1</s>', message)
                                message = re.sub(r"```(.*?)```", r'<div class="code">\1</div>', message)
                                message = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', message)
                                message = re.sub(r"\*(.*?)\*", r'<i>\1</i>', message)
                                message = message.lstrip('\n')
                                message = message.rstrip()
                                message = message.replace("\n", "<br>")
                                message = re.sub(r"(<br>\s*){6,}", "<br><br><br>", message)
                                key = data[1]
                                if data[1] in special_users:
                                    format = special_users[key]
                                    format = format.format(username=escape(username), time=time, message=message)
                                else:
                                    format = f'<b>{escape(username)}</b> <i>@{time}</i>: {message}<br>\n'
                                if last_messages and key.lower() == last_messages[0][0].lower() and message.lower() == last_messages[0][1].lower():
                                    response = make_response("<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Cannot send the same message twice")
                                    response.headers["Location"] = "/"
                                    return response, 302
                                file.write(format)
                                last_messages.insert(0, (key, message))
                                print(f'Message sent by {username} at IP {client_ip}')
                            return redirect(url_for('main'))
                        else:
                            db.close()
                            response = make_response(render_template('no_account.html', signup=url_for('signup'), login=url_for('login')))
                            response.delete_cookie("LOGIN_TOKEN")
                            response.delete_cookie("un")
                            return response
    
@app.route("/delete_account", methods=["POST"], strict_slashes=False)
def delete_account():
    db = shelve.open('data/userdata')
    username = request.cookies.get('un')
    login_token = request.cookies.get('LOGIN_TOKEN')
    if not username or not login_token:
        return "<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Unable to delete account: not logged in"
    else:
        if username in db:
            data = db[username]
            if login_token == data[1]:
                del db[username]
                db.close()
                response = make_response("Deleted account")
                response.delete_cookie("LOGIN_TOKEN")
                response.delete_cookie("un")
                response.headers["Location"] = "/"
                return response, 302
            else:
                db.close()
                return "<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Unable to delete account: not logged in"

@app.route("/admin/delete_account", methods=["POST"], strict_slashes=False)
def delete_admin_account():
    db = shelve.open('data/admindata')
    username = request.cookies.get('admin_un')
    login_token = request.cookies.get('admin_LOGIN_TOKEN')
    if not username or not login_token:
        return "<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Unable to delete account: not logged in"
    else:
        if username in db:
            data = db[username]
            if login_token == data[1]:
                del db[username]
                db.close()
                response = make_response("Deleted account")
                response.delete_cookie("admin_LOGIN_TOKEN")
                response.delete_cookie("admin_un")
                response.headers["Location"] = "/admin/signup"
                return response, 302
            else:
                db.close()
                return "<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Unable to delete account: not logged in"


@app.route('/logout', methods=["POST"], strict_slashes=False)
def logout():
    response = make_response("Logged out")
    response.delete_cookie("LOGIN_TOKEN")
    response.delete_cookie("un")
    response.headers["Location"] = "/"
    return response, 302

@app.route('/li', methods=['POST'], strict_slashes=False)
def li():
    settings = shelve.open('data/settings')
    banned_ips = settings["banned_ips"]
    settings.close()
    db = shelve.open('data/userdata')
    username = str(request.form.get('username'))
    password = str(request.form.get('password')) 
    client_ip = request.headers.get('X-Forwarded-For')
    if client_ip in banned_ips:
        return f"<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>You have been banned<br>Reason:<br>{banned_ips[client_ip]}"
    if username in db:
        data = db[username]
        userpass = data[0]
        if password == userpass:
            db.close()
            response = make_response(f"logged in")
            expiration = datetime.datetime.now() + datetime.timedelta(days=365 * 10)
            response.set_cookie('LOGIN_TOKEN', data[1], expires=expiration)
            response.set_cookie('un', username, expires=expiration)
            response.headers["Location"] = "/"
            return response, 302
        else:
            return "login info incorrect"
    else:
        db.close()
        return "login info incorrect"

@app.route('/si', methods=['POST'], strict_slashes=False)
def si():
    settings = shelve.open('data/settings')
    banned_ips = settings["banned_ips"]
    settings.close()
    client_ip = request.headers.get('X-Forwarded-For')
    if client_ip in banned_ips:
        return f"<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>You have been banned<br>Reason:<br>{banned_ips[client_ip]}"
    with shelve.open('data/userdata') as db:
        username = str(escape(request.form.get('username')[:22]))
        if username in filter:
            return f"<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'>Username is not allowed"
        data = [str(request.form.get('password')), str(uuid.uuid4()), client_ip]
        if username.lower() in [key.lower() for key in db.keys()]:
            return "Account already exists", 200
        else:
            db[username] = data
            response = make_response(f"Created account<br>{username}<br>{str(data)}")
            expiration = datetime.datetime.now() + datetime.timedelta(days=365 * 10)
            response.set_cookie('LOGIN_TOKEN', data[1], expires=expiration)
            response.set_cookie('un', username, expires=expiration)
            response.headers["Location"] = "/"
            return response, 302
 
@app.route("/login", strict_slashes=False)
def login():
    return """<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'><form method="POST" action="/li">
    username: <input type="text" name="username" required maxlength="22"><br>
    password: <input type="password" name="password" required><br>
    <input type="submit" value="login">
</form>"""

@app.route("/signup", strict_slashes=False)
def signup():
    return """<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'><form method="POST" action="/si" autocomplete="off">
    username: <input type="text" name="username" required maxlength="22"><br>
    passsword: <input type="text" name="password" required><br>
    <input type="submit" value="signup">
</form>"""

@app.route("/admin/signup", strict_slashes=False)
def signup_form():
    return """<form method="POST" action="/admin/_signup">
    admin key: <input type="text" name="admin_key" required><br>
    username: <input type="text" name="username" required><br>
    password: <input type="text" name="password" required><br>
    <input type="submit" value="signup">
</form>"""

@app.route('/admin/_signup', methods=['POST'], strict_slashes=False)
def admmin_signup():
    db = shelve.open('data/admindata')
    admin_login_key = str(request.form.get('admin_key'))
    username = str(request.form.get('username'))
    data = [str(request.form.get('password')), str(uuid.uuid4())]
    if not admin_login_key == admin_key:
        return "Admin key incorrect"
    if username in db:
        db.close()
        return "Account already exists"
    else:
        db[username] = data
        response = make_response(f"Created account<br>{username}<br>{str(data)}")
        expiration = datetime.datetime.now() + datetime.timedelta(days=365 * 10)
        response.set_cookie('admin_LOGIN_TOKEN', data[1], expires=expiration)
        response.set_cookie('admin_un', username, expires=expiration)
        response.headers["Location"] = "/admin"
        db.close()
        return response, 302
    
@app.route("/admin/login", strict_slashes=False)
def admin():
    return """<meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name='viewport' content='width=device-width, initial-scale=1'><form method="POST" action="/admin/_login">
    username: <input type="text" name="username" required><br>
    password: <input type="text" name="password" required><br>
    <input type="submit" value="login">
</form>"""

@app.route('/admin/_login', methods=['POST'], strict_slashes=False)
def admin_login():
    db = shelve.open('data/admindata')
    username = str(request.form.get('username'))
    password = str(request.form.get('password')) 
    if username in db:
        data = db[username]
        userpass = data[0]
        if password == userpass:
            db.close()
            response = make_response(f"logged in")
            expiration = datetime.datetime.now() + datetime.timedelta(days=365 * 10)
            response.set_cookie('admin_LOGIN_TOKEN', data[1], expires=expiration)
            response.set_cookie('admin_un', username, expires=expiration)
            response.headers["Location"] = "/admin"
            return response, 302
        else:
            return "login info incorrect"
    else:
        db.close()
        return "login info incorrect"
    
@app.route("/admin", strict_slashes=False)
def panel():
    db = shelve.open('data/admindata')
    username = request.cookies.get('admin_un')
    login_token = request.cookies.get('admin_LOGIN_TOKEN')
    if not username or not login_token:
        response = make_response("not logged in")
        response.delete_cookie("admin_un")
        response.delete_cookie("admin_LOGIN_TOKEN")
        response.headers["Location"] = "/admin/login"
        return response, 302
    else:
        if username in db:
            data = db[username]
            if login_token == data[1]:
                db.close()
                db = shelve.open('data/userdata')
                all_values = []
                all_values.append("users:")
                for key, value in db.items():
                    if len(value) > 2:
                        OG_IP = value[2]
                    else:
                        OG_IP = "None"
                    all_values.append(f'{key} [ Password: "{value[0]}", UUID: "{value[1]}", OG-IP: "{OG_IP}" ] <form method="POST" action="/admin/delete_others"><input type="text" name="admin_key" value="{login_token}" hidden><input name="username" type="text" value="{key}" hidden><input type="submit" value="Delete account"></form>')
                db.close()
                accounts = '<br>'.join(all_values)
                return f"""<html><head><meta charset='UTF-8'><meta name='description' content='A free messaging app complete with accounts and special styling for your message'><meta name='author' content='Gabrielzv1233'><title>msgr v2</title><meta name="viewport" content="width=device-width, initial-scale=1"><style>body {{background-color: #1C2333;color:white;}}input[type="submit"] {{border-radius: 5px;}}button {{border-radius: 5px;}}</style></head><body><a href="/admin/send"><button>Send from console</button></a><br><a href="/admin/messages"><button>Messages</button></a><br><a href="/admin/settings"><button>Settings</button></a><br><br>logged in as {username}<form method="POST" action="/logout_admin"><form id="deleteForm" method="POST" action="/delete_account">
            <input type="submit" value="Logout"></form><form method="POST" action="/admin/delete_account"><input type="checkbox" id="deleteCheckbox" required>Check this and click the button below to delete your account<br>
            <input type="submit" value="Delete account">
        </form>
            {accounts}
            </body></html>
            """
            else:
                db.close()
                response = make_response("not logged in")
                response.delete_cookie("admin_un")
                response.delete_cookie("admin_LOGIN_TOKEN")
                response.headers["Location"] = "/admin/login"
                return response, 302
    response = make_response("not logged in")
    response.delete_cookie("admin_un")
    response.delete_cookie("admin_LOGIN_TOKEN")
    response.headers["Location"] = "/admin/login"
    return response, 302

@app.route('/logout_admin', methods=["POST"], strict_slashes=False)
def admin_logout():
    response = make_response("Logged out")
    response.delete_cookie("admin_LOGIN_TOKEN")
    response.delete_cookie("admin_un")
    response.headers["Location"] = "/admin/login"
    return response, 302

@app.route("/admin/delete_others", methods=["POST"], strict_slashes=False)
def admin_delete_other_account():
    db = shelve.open('data/userdata')
    username = request.form.get('username')
    login_token = request.form.get('admin_key')
    if not username or not login_token:
        response = make_response("not logged in")
        response.delete_cookie("admin_un")
        response.delete_cookie("admin_LOGIN_TOKEN")
        response.headers["Location"] = "/admin/login"
        return response, 302
    else:
        if username in db:
            if login_token == request.form.get('admin_key'):
                del db[username]
                db.close()
                response = make_response("Deleted account")
                response.headers["Location"] = "/admin"
                return response, 302
            else:
                db.close()
                response = make_response("admin key incorrect")
                print("admin key incorrect")
                response.headers["Location"] = "/admin"
                return response, 302
        else:
            response = make_response("account dose not exist")
            response.headers["Location"] = "/admin"
            return response, 3020
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
