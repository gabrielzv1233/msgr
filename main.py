from flask import Flask, request, render_template, redirect, url_for, send_file
import requests
import datetime
import os
from html import escape

app = Flask(__name__)

#Route for the 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def serve_html():
    return render_template('index.html')

@app.route('/send', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'POST':
        user = escape(request.form.get('user'))
        message = escape(request.form.get('msg'))

        if not user or not message:
            return redirect(url_for('send'))

        server_time = datetime.datetime.now().strftime("%H:%M")
        url = f"https://msgr.gabrielzv1233.repl.co/send?user={user}&msg={message}&time={server_time}"

        response = requests.get(url)

        if response.status_code == 200:
            with open('messages.txt', 'a') as file:
                file.write(f'<b>{user}</b> <i>@{server_time}/i>: {message}<br>\n')
            return render_template('message_sent.html')
        else:
            return 'Failed to send the message.'

    return redirect(url_for('send'))

@app.route('/api/send', methods=['GET'])
def send_message_query():
    user = request.args.get('user')
    message = request.args.get('msg')

    if not user or not message:
        return 'Invalid request.<br> make sure both username and message fields have a non-space character'

    user = escape(user)
    message = escape(message)

    server_time = datetime.datetime.now().strftime("%H:%M")

    with open('messages.txt', 'a') as file:
        file.write(f'<b>{user}</b> <i>@{server_time}</i>: {message}<br>\n')

    return 'Message sent successfully.'
  
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
@app.route('/info.html')
def info():
    return render_template('info.html')
@app.route('/api/get')
def get_messages():
    return send_file('messages.txt', mimetype='text/html')
  
@app.route('/api/get/raw')
def get_raw_messages():
    return send_file('messages.txt', mimetype='text/plain')
@app.route('/favicon')
def serve_image():
    filename = 'templates/favicon.png'
    return send_file(filename, mimetype='image/png')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)