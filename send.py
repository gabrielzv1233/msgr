#support disabled sorry

import requests
import time
import os

# Define the URL of the server
username = input("Please choose your username:\n» ")
def clear_console():
    if os.name == 'nt':  # for Windows
        os.system("cls")
    else:  # for Linux and macOS
        os.system("clear")
clear_console()
url = 'https://msgr.gabrielzv1233.repl.co/api/send'
print(f"sending to {url}")
print(f"as \"{username}\"\n")

# Generate the message and time
message = input("Please enter your message:\n» ")
current_time = time.strftime('%H:%M')

# Construct the request parameters
params = {
    'user': username,
    'msg': message
}

# Send the HTTP request
response = requests.get(url, params=params)

print(f"\nSending as: {url}?user={username}&msg={message}\n")

# Check the response status
if response.status_code == 200:
    formatted_response = response.text.replace("<br>", "\n")
    print(formatted_response)
else:
    formatted_response = response.text.replace("<br>", "\n")  
    print(formatted_response)