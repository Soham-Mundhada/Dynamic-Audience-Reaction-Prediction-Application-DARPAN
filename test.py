import mail_helper
from flask import Flask

app = Flask(__name__)
with app.app_context():
    data={
        "1":"jatin",
        "asfdkhbf":"kjasdhb",
    }
    mail_helper.send_mail('jatinjangir0220@gmail.com',str(data))

print("done")