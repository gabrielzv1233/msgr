import requests

mode = input("Please choose \"raw\" for raw format or \"plain\" for plain text\n» ")

if mode == "raw":
    url = 'https://msgr.gabrielzv1233.net/api/get/raw'
    response = requests.get(url)
    text = response.text.replace('<br>', '<br>\n')
    print(text)
    
elif mode == "plain":
    url = 'https://msgr.gabrielzv1233.net/api/get/raw'
    response = requests.get(url)
    response = response.text.replace('<br>', '\n')
    response = response.replace('<i>', '')
    response = response.replace('<b>', '')
    response = response.replace('<u>', '')
    response = response.replace('</i>', '')
    response = response.replace('</b>', '')
    response = response.replace('</u>', '')
    response = response.replace('&lt;', '<')
    response = response.replace('&gt;', '>')
    response = response.replace('&#x27;', "'")
    response = response.replace('&quot', '"')
    response = response.replace('&&#x0024;', '$')
    response = response.replace('&#x0025;', '%')
    print(response)
    
elif mode == "":
    print("Please do not leave this empty")
    
else:
    print("Invalid input")