# importing Flask and other modules
from flask import Flask, request, render_template,redirect
# importing module
from pymongo import MongoClient
from youtube_API_service import api_service
import mail_helper
from youtube_API_service import db
import json
from youtube_API_service import total_reaction
from youtube_API_service import sentiments

global mail

def insert_data(na,ema,p):
    # creation of MongoClient
    print("entering user data ")
    client=MongoClient()

    # Connect with the portnumber and host
    client = MongoClient('mongodb://localhost:27017/')

    # Access database
    mydatabase = client['youtube_api']

    # Access collection of the database
    mycollection=mydatabase['users']
    # dictionary to be added in the database
    rec={
        "name": na,
        "email": ema,
        "password":p,
    }

    # inserting the data in the database
    mycollection.insert_one(rec)

def get_by_mail(email):
    # creation of MongoClient
    print("fetching user data ")
    client=MongoClient()

    # Connect with the portnumber and host
    client = MongoClient('mongodb://localhost:27017/')

    # Access database
    mydatabase = client['youtube_api']

    # Access collection of the database
    mycollection=mydatabase['users']

    #email=email.lower()
    element=mycollection.find_one({"email":email})
    return element

def top50_data(data):
    print("in url getter -----")
    top50={}
    print(type(data))
    #print(data)
    for i in range(len(data['URL'])):
        temp={}
        temp["URL"]=data["URL"][str(i)]
        temp["Title"]=data["Title"][str(i)]
        temp["PublishTime"]=data['PublishTime'][str(i)]
        temp["Channel_Name"]=data['Channel_Name'][str(i)]
        top50[i]=temp
    return top50

# Flask constructor
app = Flask(__name__)



@app.route('/home', methods =["GET", "POST"])
def home():
    if(request.method == "POST"):
        print("start analysis.... ")
        tags = request.form["tags"].lower()
        file1 = open("mail_list.txt","r+") 
        text_mail=file1.readlines()[0].rstrip()
        file1.close()
        user_query=str(request.args.get('top50')) # /top50/?top50=KEY_WORDS
        #print(user_query)
        ourDBread=db.get_data(tags)
        print("what we get .......")
        #print(ourDBread)
        if(ourDBread==""):
            print("generating new data ......")
            data=api_service.key_words(str(tags),300)
            data=sentiments.get_all_Sentiments(data)
            data=data.to_dict()            
            print("type of data --- "+str(type(data)))
            db.insert_data(tags,json.dumps(data))
        ourDBread=db.get_data(tags)
        data=json.loads(ourDBread)
        positive,neutral,negative,average_views,average_likes,average_comments,mode,x=total_reaction.get_total_reaction(data)
        results_message={
            "mail":str(text_mail),
            "tags":str(tags),
            "top50":top50_data(data),
            "positive":positive,
            "neutral":neutral,
            "negative":negative,
            "average_views":average_views,
            "average_likes":average_likes,
            "average_comments":average_comments,
            "mode":mode,
        }
        with app.app_context():
            print("our text_mail ---- "+text_mail)
            mail_helper.send_mail(str(text_mail),results_message)
        
        
        print("type of ------ "+str(type(results_message)))
        return render_template('results.html',messages=results_message)
    return render_template("index.html")

@app.route('/signup', methods =["GET", "POST"])
def FORM_up():
    if(request.method == "POST"):
        first_name = request.form["form_name"]
        email = request.form["form_email"]
        pas = request.form["form_passwosd"]
        insert_data(first_name,email,pas)
        file1 = open("mail_list.txt","w")
        file1.write(str(email)+"\n")
        file1.close()
        return redirect('/home')
    return render_template("signup.html")


@app.route('/aboutUs', methods =["GET", "POST"])
def aboutUs():
    return render_template("aboutus.html")

@app.route('/details', methods =["GET", "POST"])
def details():
    return render_template("projectdetails.html")
# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def FORM():
    if(request.method == "POST"):
        email = request.form["form_email"]
        pas = request.form["form_passwosd"]
        user=get_by_mail(email)
        if(user==None):
            return  redirect('/signup')
        if( user['password']==pas):
            file1 = open("mail_list.txt","w")
            file1.write(str(email)+"\n")
            file1.close()
            return redirect('/home')
    return render_template("signin.html")

if __name__=='__main__':
    app.run()
