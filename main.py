from flask import Flask, request, render_template, redirect, url_for, send_file, make_response
from sentry_sdk.integrations.flask import FlaskIntegration
from collections import deque
from html import escape
import user_agents
import sentry_sdk
import requests
import datetime
import json
import sys
import re
import os

# start config
Raw_message_mode = False
block = {
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
    "kill your self": "i hope you have a long happy life :D",
    "pornhub.com": "[banned-URL]",
    "suck it": "s**t it",
    "niiga": "n***a",
    "卐": "",
    "nigg3r": "n****r"
}

loggable_words = ["nigger", "nigga", "niggger", "niger", "niga", "faggot", "fagot", "n*gger", "n*gga", "kill your self", "pornhub.com", "niiga","nigg3r"]
# end config

#add files if needed
try:
   import SpecialUsers
except ModuleNotFoundError:
    # Create SpecialUsers.py file
    with open("SpecialUsers.py", "w") as file:
        file.write('''Special_users = {
    "OwnersUUID": "<b style=\\"color:gold;\\">{user} <sup> ✓</sup></b> <i>@<u>{server_time}</u></i>: {message}<br>\\n"
}''')
    exit("please re-run server")

try:
   import bans
except ModuleNotFoundError:
    # Create SpecialUsers.py file
    with open("bans.py", "w") as file:
        file.write('''BANNED_IPS = {
"BannedPersonsIpHere": "example"
}
BANNED_UUIDS = {
"BannedUUIDHere": "example"
}''')
    exit("please re-run server")

files = {
    "message_log_all.txt": "",
    "messages.html": "",
    "message_log.txt": ''
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

# sentery anylitics and diagnostics
sentry_sdk.init(
    dsn=os.environ.get("sentryDSN"),
    integrations=[FlaskIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,

)


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
  message = message.replace('$', '&#x0024;')
  message = message.replace('%', '&#x0025;')
  for word in loggable_words:
      if word.lower() in message.lower():
          log_entry = f"[{ip}] {user} @{time}: {message}\n"
          with open('message_log.txt', 'a') as file:
              file.write(log_entry)
          break
def log_message_all(ip, user, UUID, time, message):
  message = message.replace('$', '&#x0024;')
  message = message.replace('%', '&#x0025;')
  log_entry = f"[{ip}] ({UUID}) {user} @{time}: {message}\n"
  with open('message_log_all.txt', 'a') as file:
        file.write(log_entry)

# Define a deque to store the last messages
last_messages = []

@app.route('/send', methods=['GET', 'POST'])
def receive_message():
    if request.method == 'POST':
        user = escape(request.form.get('user'))
        message = escape(request.form.get('msg'))
        client_ip = request.headers.get('X-Forwarded-For')
        message_unmodified = request.form.get('msg')
        user_unmodified = user = request.form.get('user')
        user_agent = request.headers.get('User-Agent')
        user_agent_obj = user_agents.parse(user_agent)
        if 'CustomDomain' in os.environ:
          custom_domain = os.environ['CustomDomain']
          request_domain = request.headers.get('Host')
          if request_domain != custom_domain:
              return "This service is not accessible from this URL"
          # disable Safari usage
        if 'Safari' in user_agent_obj.browser.family:
          return "Safari browser is unsupported<br>platform will not work as supposed to"
        # Check if the UUID is banned
        fingerprint = request.cookies.get('fingerprint')

        if fingerprint in bans.BANNED_UUIDS:
          ban_reason = bans.BANNED_UUIDS[fingerprint]
          return f'You have been banned.<br>Reason: {ban_reason}'
        # Check if the IP is banned
        if client_ip in bans.BANNED_IPS:
            ban_reason = bans.BANNED_IPS[client_ip]
            return f'You have been banned.<br>Reason: {ban_reason}'

        if not user or not message:
            return redirect(url_for('send'))

        if len(message) > 1000:
            return redirect(url_for('too_long'))

        server_time = datetime.datetime.now().strftime("%H:%M")

        # Call the log_message function before applying the chat filter
        log_message(client_ip, user_unmodified,  server_time, message_unmodified)
        # also log all messages in case if users bypass filters (comment out if not needed ex when making a private room)
        fingerprint = request.cookies.get('fingerprint')
        log_message_all(client_ip, user_unmodified, fingerprint, server_time, message_unmodified)
        # Apply case-insensitive chat filtering to username and message
        for word in block:
    # Use regular expression with case-insensitive flag to replace filtered words
          user = re.sub(re.compile(re.escape(word), re.IGNORECASE), block[word], user)
          message = re.sub(re.compile(re.escape(word), re.IGNORECASE), block[word], message)
        message = message.replace('$', '&#x0024;')
        message = message.replace('%', '&#x0025;')
        # Convert URLs to clickable links
        message = re.sub(r'(https?://\S+)', r'<a target=\"_blank\" href="\1">\1</a>', message)

        if last_messages and user.lower() == last_messages[0][0].lower() and message.lower() == last_messages[0][1].lower():
            return redirect(url_for('anti_spam'))

        # Add the current message to the last_messages deque
        last_messages.insert(0, (user, message))

        # Check if the fingerprint cookie exists
        if fingerprint:
            if fingerprint in SpecialUsers.Special_users:
                message_format = SpecialUsers.Special_users[fingerprint]
                formatted_message = message_format.format(user=user, server_time=server_time, message=message)
            else:
                formatted_message = f"<b>{user}</b> <i>@<u>{server_time}</u></i>: {message}<br>\n"
        else:
            formatted_message = f"<b>{user}</b> <i>@<u>{server_time}</u></i>: {message}<br>\n"

        with open('messages.html', 'a') as file:
            if Raw_message_mode == False:
                file.write(formatted_message)
            else:
                file.write(f'{user} @{server_time}: {message}<br>\n')

        fingerprint = request.cookies.get('fingerprint')
        print(f"New message sent by user {user} (IP: {client_ip}, UUID: {fingerprint} Browser: {user_agent_obj}")
        return render_template('send.html')
      # The filter for censoring words isn’t properly censoring words that sent the same case, ex it censors “faggot” but not “FAGGot”

    return redirect(url_for('send'))

@app.route('/too-long.html')
def too_long():
    return render_template('too_long.html')

@app.route('/full', methods=['GET'])
def display_messages():
    if os.stat('messages.html').st_size == 0:
        pass

    with open('messages.html', 'r') as file:
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
    return send_file('messages.html', mimetype='text/html')

@app.route('/api/get/raw')
def get_raw_messages():
    return send_file('messages.html', mimetype='text/plain')

@app.route('/favicon.png')
def serve_image():
    return send_file("templates/favicon.png", mimetype='image/png')

@app.route('/anti_spam')
def anti_spam():
    return render_template('anti-spam.html')

@app.route('/get_uuid', methods=['GET'])
@app.route('/get_UUID', methods=['GET'])
def get_UUID():
    fingerprint = request.cookies.get('fingerprint')

    if fingerprint:
        return render_template('get_UUID.html', UUID=fingerprint)
    else:
        fingerprint = "not set"
        render_template('get_UUID.html', UUID=fingerprint)

@app.route('/jquery-3.6.0.min.js')
def jquery():
    return send_file("templates/jquery-3.6.0.min.js", mimetype="text/javascript")
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)