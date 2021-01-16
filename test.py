def getMessage(content):
    firstCarrot = content.index('<')
    secondCarrot = content.index('>')
    return content[firstCarrot+3:secondCarrot]

y = getMessage('GG <@!799778925936246804>, you just advanced to level 5')
print(y)