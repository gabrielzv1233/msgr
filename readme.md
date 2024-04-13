Welcome to msgr v2, this is still work in progress<br>
to get started lets discuss the admin page<br>
to create an admin account, you must go to the directory `/admin/signup` it will ask you for a admin key, username, and password, the admin key is randomized and printed out into the console everytime the script runs (ex reloading from debug mode, starting the server ect), than just set the username and password to whatever you like<br>
the admin page is where you can see the username, password and uuid of a users account you can also delete others accounts from here with the delete account button<br>
you can also press the settings button to ban users by either entering their ip or UUID in the approprite list<br>
there is also special users, this is used when you want to for example mark someone as a admin, simply create a new dictionary entery like this<br>
`{"users UUID":'<b style="color:red;">{username}</b> <i>@{time}</i>: {message}<br>\n'}`<br>
you can change settings at `/admin/settings`, this includes ip and uuid banning, and special users<br>
you can also edit the messages using `/admin/messages` WARNING! messages dont update in the message editor, so it will overwrite newly sent messages<br>
you can also send a message as the console at `/admin/send`, this is just a extra feature that dose not need to be used but is still there<br>
<br>
in the chatting app (main route) you can use some common markdown styling and other additional stuff like `​```code```​` `___underline___` `**bold**` `*italic*` `~~srikethrough~~`  for links you can use the markdown method `[example.com](https://example.com)` or input a link like `!https://example.com/` (must have ! at the start, if i code it to not require that, it confilcts with the markdown method) and it will automatically form a \<a> link<br>
messages are limited to a lenth of 600 and usernames are limited to 22 chars in lenth<br>
<br>
in v1 i had it so if you scrolled up in the messages, it would stop the autoscroll until you reach the bottom of the page, but i cant seem to replicate that function so i made a toggle for it, if you would like to contribute and add that function, please submit the updated file in a github issue and i will glady credit you (as long as it works)