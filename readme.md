Welcome to msgr v2, this is still work in progress<br>
to get started lets discuss the admin page<br>
to create an admin account, you must go to the directory `/admin/signup` it will ask you for a admin key, username, and password, the admin key is randomized and printed out into the console everytime the script runs (ex reloading from debug mode, starting the server ect), than just set the username and password to whatever you like<br>
the admin page is where you can see the username, password and uuid of a users account you can also delete others accounts from here with the delete account button<br>
you can also press the settings button to ban users by either entering their ip or UUID in the approprite list<br>
there is also special users, this is used when you want to for example mark someone as a admin, simply create a new dictionary entery like this<br>
`{"users UUID":'<b style="color:red;">{username}</b> <i>@{time}</i>: {message}<br>\n'}`<br>
<br>
to change the chat filter, you must reload the server after setting the var near the start of the code called `filter`<br>
<br>
in the chatting app (main route) you can use some common markdown styling and other additional stuff like `​```code```​` `___underline___` `**bold**` `*italic*` `~~srikethrough~~` you can also input a link like `https://example.com/` and it will automatically form a \<a> link<br>
messages are limited to a lenth of 600 and usernames are limited to 22 chars in lenth<br>
<br>
in v1 i had it so if you scrolled up in the messages, it would stop the autoscroll until you reach the bottom of the page, but i cant seem to replicate that function so i made a toggle for it, if you would like to contribute and add that function, be my guest, i will glady credit you