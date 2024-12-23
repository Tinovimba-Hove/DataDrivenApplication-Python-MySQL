from user import user
from baseObject import baseObject


u = user()
u.truncate()
u.set({'name':'thove','password':'134','password2':'134','role':'admin', 'phone':'3155900409', 'email':'hovett@gmaill.com'})
if u.verify_new():
    u.insert()
else:
    print(u.errors)


u = user()
if u.tryLogin("thove","134"):
    print("Login ok.")
else:
    print("Login failed.")
