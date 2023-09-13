from flask import Flask, request, render_template, redirect, url_for, send_file
from collections import deque
import requests
import datetime
import os
from html import escape
import json
import settings
import bans
import re

Raw_message_mode = False

#add files if needed
files = {
    "bans.py": 'BANNED_IPS = {\n    "BannedPersonsIpHere": "example"\n}',
    "messages.txt": "",
    "message_log.txt": '',
    "settings.py": '''block = {
    "fuck": "f**k",
    "nigga": "n***a",
    "nigger": "n***er",
    "cunt": "c**t",          
    "cock": "pp",
    "penis": "pp",
    "✓": "",
    "kys": "your a nice person i wish i was you",
    "niggger": "n****er"
}

loggable_words = ["nigger", "nigga", "niggger"]'''
}
for filename, content in files.items():
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write(content)
        print(f"Created file: {filename}")
    else:
        print(f"File already exists: {filename}, skipping")
print()

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
    for word in settings.loggable_words:
        if word.lower() in message.lower():
            log_entry = f"[{ip}] {user} @{time}: {message}\n"
            with open('message_log.txt', 'a') as file:
                file.write(log_entry)
            break

# Define a deque to store the last messages
last_messages = deque(maxlen=10)  # Store the last 10 messages

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
        for word in settings.block:
            if word.lower() in user.lower():
                user = user.replace(word, settings.block[word])
            if word.lower() in message.lower():
                message = message.replace(word, settings.block[word])

        # Check for duplicate messages
        for last_user, last_message in last_messages:
            if user.lower() == last_user.lower() and message.lower() == last_message.lower():
                return redirect(url_for('anti-spam'))

        # Add the current message to the last_messages deque
        last_messages.append((user, message))

        url = f"https://msgr.gabrielzv1233.repl.co/send?user={user}&msg={message}&time={server_time}"

        response = requests.get(url)

        if response.status_code == 200:
            with open('messages.txt', 'a') as file:
                if Raw_message_mode == False:
                    file.write(f'<b>{user}</b> <i>@<u>{server_time}</u></i>: {message}<br>\n')
                else:
                    file.write(f'{user} @{server_time}: {message}<br>\n')
            print(f"New message sent by user {user} (IP: {client_ip})")
            return render_template('send.html')
        else:
            return 'Failed to send the message.'

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
    for word in settings.block:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(user):
            user = pattern.sub(settings.block[word], user)
        if pattern.search(message):
            message = pattern.sub(settings.block[word], message)

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

@app.route('/chatfilter')
def serve_filter():
    return send_file('settings.py', mimetype='text/plain')


@app.route('/anti-spam')
def anti_spam():
    return send_file('anti-spam.html', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)