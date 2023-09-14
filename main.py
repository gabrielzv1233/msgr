from flask import Flask, request, render_template, redirect, url_for, send_file, make_response
from collections import deque
import requests
import datetime
import os
from html import escape
import json
import bans
import sys
import re

try:
    import SpecialUsers
except ModuleNotFoundError:
    # Create SpecialUsers.py file
    with open("SpecialUsers.py", "w") as file:
        file.write('''Special_users = {
    "OwnersUUID": "<b style=\\"color:gold;\\">{user} <sup> ✓</sup></b> <i>@<u>{server_time}</u></i>: {message}<br>\\n"
}''')
    exit("please re-run server")

Raw_message_mode = False

#add files if needed

import os

# start config
block = {
    "fuck": "f**k",
    "nigga": "n***a",
    "nigger": "n***er",
    "cunt": "c**t",
    "cock": "pp",
    "penis": "pp",
    "kys": "your a nice person i wish i was you",
    "niggger": "n****er",
    "niger": "n**er",
    "niga": "n**a",
    "faggot": "f****t",
    "fagot": "f***t"
}

loggable_words = ["nigger", "nigga", "niggger", "niger", "niga", "faggot", "fagot"]
# end config

files = {
    "bans.py": 'BANNED_IPS = {\n    "BannedPersonsIpHere": "example"\n}',
    "messages.txt": "",
    "message_log.txt": '',
    "SpecialUsers.py": '''Special_users = {
  "OwnersUUID": "<b style="color:gold;">{user} &#x2713;</b> <i>@<u>{server_time}</u></i>: {message}<br>\n"
}'''
}

failed_files = []

for filename, content in files.items():
    if not os.path.exists(filename):
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Created file: {filename}")
        except IOError:
            failed_files.append(filename)
            print(f"Error creating file: {filename}")
    else:
        print(f"File already exists: {filename}, skipping")

print()

if failed_files:
    print("Required files failed to be created. Please re-run the program.")
    sys.exit(1)

app = Flask(__name__)

# Route for the 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def Server_died_oof(e):
    return render_template('500.html'), 500

@app.route('/500.html')
def error_500():
    return render_template('500.html')

@app.route('/')
def serve_html():
    return render_template('index.html')

# Log loggable messages (ex messages with the N-word)
def log_message(ip, user, time, message):
    for word in loggable_words:
        if word.lower() in message.lower():
            log_entry = f"[{ip}] {user} @{time}: {message}\n"
            with open('message_log.txt', 'a') as file:
                file.write(log_entry)
            break

# Define a deque to store the last messages
last_messages = []

@app.route('/send', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'POST':
        user = escape(request.form.get('user'))
        message = escape(request.form.get('msg'))
        client_ip = request.headers.get('X-Forwarded-For')

        # Check if the IP is in the database
        if client_ip in bans.BANNED_IPS:
            ban_reason = bans.BANNED_IPS[client_ip]
            return f'You have been banned.<br>Reason: {ban_reason}'

        if not user or not message:
            return redirect(url_for('send'))

        if len(message) > 1000:
            return redirect(url_for('too_long'))

        server_time = datetime.datetime.now().strftime("%H:%M")

        # Call the log_message function before applying the chat filter
        log_message(client_ip, user, server_time, message)

        # Apply case-insensitive chat filtering to username and message
        for word in block:
            if word.lower() in user.lower():
                user = user.replace(word, block[word])
            if word.lower() in message.lower():
                message = message.replace(word, block[word])

        # Convert [display](url) to <a href="https://url">display</a>
        message = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="https://\2">\1</a>', message)

        # Check for duplicate messages
        for last_user, last_message in last_messages:
            if user.lower() == last_user.lower() and message.lower() == last_message.lower():
                return redirect(url_for('anti_spam'))

        # Add the current message to the last_messages deque
        last_messages.insert(0, (user, message))

        # Check if the fingerprint cookie exists
        fingerprint = request.cookies.get('fingerprint')
        if fingerprint:
            if fingerprint in SpecialUsers.Special_users:
                message_format = SpecialUsers.Special_users[fingerprint]
                formatted_message = message_format.format(user=user, server_time=server_time, message=message)
            else:
                formatted_message = f"<b>{user}</b> <i>@<u>{server_time}</u></i>: {message}<br>\n"
        else:
            formatted_message = f"<b>{user}</b> <i>@<u>{server_time}</u></i>: {message}<br>\n"

        with open('messages.txt', 'a') as file:
            if Raw_message_mode == False:
                file.write(formatted_message)
            else:
                file.write(f'{user} @{server_time}: {message}<br>\n')
        fingerprint = request.cookies.get('fingerprint')
        print(f"New message sent by user {user} (IP: {client_ip}, UUID: {fingerprint}")
        return render_template('send.html')

    return redirect(url_for('send'))

@app.route('/too-long.html')
def too_long():
    return render_template('too_long.html')

# feature removed bc im not maintaining it
@app.route('/api/send', methods=['GET'])
def send_message_query():
    user = request.args.get('user')
    message = request.args.get('msg')
    client_ip = request.headers.get('X-Forwarded-For')

    if not user or not message:
        return 'Invalid request.<br> make sure both username and message fields have a non-space character'

    user = escape(user)
    message = escape(message)

    # Apply case-insensitive chat filtering to username and message
    for word in block:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(user):
            user = pattern.sub(block[word], user)
        if pattern.search(message):
            message = pattern.sub(block[word], message)

    server_time = datetime.datetime.now().strftime("%H:%M")

    with open('messages.txt', 'a') as file:
         #file.write(f'<b>{user}</b> <i>@<u>{server_time}</u></i>: {message}<br>\n')

      print(f"New message sent by user {user} (IP: {client_ip})")
    #return 'Message sent successfully.'
    return 'Failed, sending API is disabled as it is to hard to keep censorship and automatic moderation up to date'
@app.route('/full', methods=['GET'])
def display_messages():
    if os.stat('messages.txt').st_size == 0:
        pass

    with open('messages.txt', 'r') as file:
        messages = file.read()

    return render_template('full.html', messages=messages)

@app.route('/send.html', methods=['GET'])
def send():
    return render_template('send.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/api/get')
def get_messages():
    return send_file('messages.txt', mimetype='text/html')
  
@app.route('/api/get/raw')
def get_raw_messages():
    return send_file('messages.txt', mimetype='text/plain')

@app.route('/favicon.png')
def serve_image():
    faviconimg = 'templates/favicon.png'
    return send_file(faviconimg, mimetype='image/png')

@app.route('/anti_spam')
def anti_spam():
    return render_template('anti-spam.html')

@app.route('/get_uuid', methods=['GET'])
def get_UUID_lower():
    fingerprint = request.cookies.get('fingerprint')
    
    if fingerprint:
        return f"The value of the fingerprint cookie is: {fingerprint}"
    else:
        return "The fingerprint cookie is not set."

@app.route('/get_UUID', methods=['GET'])
def get_UUID_upper():
    fingerprint = request.cookies.get('fingerprint')
    
    if fingerprint:
        return f"The value of the fingerprint cookie is: {fingerprint}"
    else:
        return "The fingerprint cookie is not set."
      
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)