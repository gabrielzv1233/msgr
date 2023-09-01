import requests

mode = input("Please choose \"raw\" for raw format or \"plain\" for plain text\n» ")

if mode == "raw":
    url = 'https://msgr.gabrielzv1233.repl.co/api/get/raw'
    response = requests.get(url)
    text = response.text.replace('<br>', '<br>\n')
    print(text)
    
elif mode == "plain":
    url = 'https://msgr.gabrielzv1233.repl.co/api/get/raw'
    response = requests.get(url)
    text = response.text.replace('<br>', '\n')
    text1 = text.replace('<i>', '')
    text2 = text1.replace('<b>', '')
    text3 = text2.replace('</i>', '')
    text4 = text3.replace('</b>', '')
    text5 = text4.replace('&lt;', '<')
    text6 = text5.replace('&gt;', '>')
    text7 = text6.replace('&#x27;', "'")
    text8 = text7.replace('&quot', '"')
    print(text8)
    
elif mode == "":
    print("Please do not leave this empty")
    
else:
    print("Invalid input")