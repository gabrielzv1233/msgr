simply just download the templates folder and main.py to a flask app and run main.py its that easy!! all other files will be created automatically<br><br>
to get your user UUID, go to route /get_UUID<br><br>
when applying new settings, bans, or special users, you must reload the server after applying changes<br><br>
SpecialUsers.py, message_logs.txt, message_log_all.txt and bans.py are hidden so peoples sensitive info isnt displayed<br><br>
for diagnostics please go to sentry.io and setup a flask app, get the text in the DSN var and set a secret named "sentryDSN"<br><br>
if you do not have flask, requests, or sentry installed please run init.sh<br><br>
message_log_all.txt logs all messages including the IP, incase if someone bypasses filters