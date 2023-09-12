from flask import Flask, request, render_template, redirect, url_for, send_file
import requests
import datetime
import os
from html import escape
import json
import settings
import bans
import re

app = Flask(__name__)

# Route for the 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def Server_died_oof():
    return render_template('500.html'), 500

@app.route('/500.html')
def error_500():
    return render_template('500.html')

@app.route('/')
def serve_html():
    return render_template('index.html')

# Log loggable messages (ex messages with the N-word)
# Create a logger function
def log_message(ip, user, time, message):
    for word in settings.loggable_words:
        if word.lower() in message.lower():
            log_entry = f"[{ip}] {user} @ {time}: {message}\n"
            with open('message_log.txt', 'a') as file:
                file.write(log_entry)
            break

@app.route('/send', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'POST':
        user = escape(request.form.get('user'))
        message = escape(request.form.get('msg'))
        client_ip = request.headers.get('X-Forwarded-For')

        if client_ip in bans.BANNED_IPS:
          ban_reason = bans.BANNED_IPS[client_ip]
          return f'You have been banned.<br>Reason: {ban_reason}'

        if not user or not message:
            return redirect(url_for('send'))

        server_time = datetime.datetime.now().strftime("%H:%M")
        
        # Call the log_message function before applying the chat filter
        log_message(client_ip, user, server_time, message)

        # Apply case-insensitive chat filtering to username and message
        for word in settings.block:
            if word.lower() in user.lower():
                user = user.replace(word, settings.block[word])
            if word.lower() in message.lower():
                message = message.replace(word, settings.block[word])

        url = f"https://msgr.gabrielzv1233.repl.co/send?user={user}&msg={message}&time={server_time}"

        response = requests.get(url)

        if response.status_code == 200:
            with open('messages.txt', 'a') as file:
                file.write(f'<b>{user}</b> <i>@<u>{server_time}</u></i>: {message}<br>\n')
            print(f"New message sent by user {user} (IP: {client_ip})")
            return render_template('message_sent.html')
        else:
            return 'Failed to send the message.'

    return redirect(url_for('send'))

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
    if not os.path.exists('messages.txt'):
        with open('messages.txt', 'w') as file:
            pass
    elif os.stat('messages.txt').st_size == 0:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)