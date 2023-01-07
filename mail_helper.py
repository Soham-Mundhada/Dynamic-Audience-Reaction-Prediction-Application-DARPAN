from flask import Flask
#from flask import current_app
from flask_mail import Mail, Message
from smtplib import SMTPRecipientsRefused
import datetime
 
# for timezone()
import pytz
 

app = Flask(__name__)
#mail = Mail(current_app)
mail = Mail(app) # instantiate the mail class
   
# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jatinjangir0220@gmail.com'
app.config['MAIL_PASSWORD'] = 'hhslnlgapqqdfnbk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def send_mail(receiverId,body):
    print("sending mail .....")
    print("receiver --- "+receiverId)
    # using now() to get current time
    current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    URLS=[]
    for url in body['top50']:
        print(url)
        URLS.append(body['top50'][url]['URL'])
    msg = Message('your results are out !!! please check',sender ='jatinjangir0220@gmail.com',recipients = [receiverId])
    results='''
        Dear User,
        Greetings from team DARPAN.

        Here are your results from your last search at '''+str(current_time)+''' on DARPAN.

        RESULTS :

        Expected Audience Reaction on the given topic : ''' +body['tags']+'''

        Expected Engagement that your video will incur : ''' +body['mode']+'''

        Other Statistics :

        Reactions : 
        positive : ''' +str(body['positive'])+'''
        negative : ''' +str(body['negative'])+'''
        neutral : ''' +str(body['neutral'])+'''

        Videos stattistics :
        average view count: ''' +str(body['average_views'])+'''
        average likes count : ''' +str(body['average_likes'])+'''
        average comments count : ''' +str(body['average_comments'])+'''

        We hope that we have been able to serve you and meet your expectations. Please fill the feedback that will help us improve our product further.

        Thanks and regards,
        Team DARPAN.


        Videos urls are -- 
    '''+str(URLS)
    
    msg.body = str(results)
    #print(msg)
    mail.send(msg)