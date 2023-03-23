import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
from flask import Flask, Response, render_template, request, session, redirect, url_for
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup
import requests
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from flask_mysqldb import MySQL
import smtplib
detector = HandDetector(maxHands=1)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")
offset = 20
imgSize = 300
labels = ["A", "B", "C", "D", "F", "H", "L", "U", "V", "W", "X", "Y"]
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = '@@Sathyamass08'
app.config["MYSQL_DB"] = 'eris'
mysql = MySQL(app)
smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
smtpObj.ehlo()
smtpObj.starttls()
smtpObj.login('deafmutebeyonddark@gmail.com', 'tptfzhwtfappyxjv')
video = cv2.VideoCapture(0)
msg_num_add_game = '0'
num_add_score = 0
num_add_count = '0'
msg_num_sub_game = '0'
num_sub_score = 0
num_sub_count = '0'
alp_miss_count = ''
alp_miss_score = 0
alp_score = 0
alp_count = ''
num_score = 0
num_count = ''
msg_src = ''
msg_alp_game = 'img'
msg_num_game = '0'
msg_alp = 'img'
msg_num = '0'
msg_alp_miss = 'img'
msg_words = 'img'
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'Email_ID' in request.form and 'password' in request.form:
        email = request.form['Email_ID']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute('select * from Account WHERE Emailid = % s AND Password = % s', (email, password))
        account = cur.fetchone()
        cur.connection.commit()
        cur.close()
        if account:
            session['loggedin'] = True
            session['email_id'] = account[0]
            session['password'] = account[1]
            return redirect(url_for('home'))
        else:
            Notif = 'Incorrect username / password !'
            return render_template('login.html', msg=Notif)
    return render_template('login.html')
@app.route('/Forget_Email', methods=['GET', 'POST'])
def Forget_Email():
    if request.method == 'POST':
        user = request.form
        email = user['forgot_email']
        cur = mysql.connection.cursor()
        cur.execute('select Emailid from Account')
        cur.fetchall()
        for i in cur:
            if i[0] == email:
                body = ("Hi! Did you forget your password?\n Click on this link to change your password:"
                        '"http://127.0.0.1:5000/reset_password\n"'
                        '"If you did not request a password reset, then simply ignore this email and no changes will be'
                        'made."'
                        '"Have a great day!"')
                print('Sending email to %s...' % email)
                smtpObj.sendmail('sender email', email, body)
                smtpObj.quit()
                Notif = "Successfully Sent"
                Forget_Email.var = email
                return render_template('Forget_Email.html', msg=Notif)
            else:
                Notif = 'Incorrect Email'
                return render_template('Forget_Email.html', msg=Notif)
    return render_template('Forget_Email.html')
@app.route('/Sign_Up', methods=['GET', 'POST'])
def Sign_Up():
    if request.method == "POST":
        signup_details = request.form
        First_Name = signup_details['First_Name']
        Last_Name = signup_details['Last_Name']
        User_Name = signup_details['User_Name']
        Email_ID = signup_details['Email_ID']
        password = signup_details['password']
        re_password = signup_details['re_password']
        DOB = signup_details['DOB']
        if password == re_password:
            cur = mysql.connection.cursor()
            Values = Email_ID, First_Name, Last_Name, User_Name, password, DOB, re_password
            cur.execute(
                "INSERT into Account(Emailid,First_Name,Last_Name,user_name,Password,Date_of_birth,confirm_Password)"
                "values(%s, %s, %s, %s,%s, %s, %s)",
                Values)
            cur.connection.commit()
            cur.close()
            body = ("Subject: New Register User.\n\n"
                    "Dear %s,\n"
                    "We would like to thank you for your interest in our website ERIS Learning."
                    "We are thrilled to have you on board as\n"
                    "a member of our community.To get started, we invite you to create your account on our website."
                    "Creating an account\n"
                    "will allow you to access all the features of our website and make the most of our services."
                    "To create an account,\n"
                    "please visit our website 'http://127.0.0.1:5000/login' and click on the 'Login' button."
                    "You will be asked to provide\n"
                    "some basic information, such as your name, email address, and a password."
                    "Once you have completed the registration\n"
                    "process, you will receive an email confirmation with further instructions.\n"
                    "As a registered user, you will be able to:\n"
                    "Access all our services and features\n"
                    "Save your preferences and settings\n"
                    "Receive updates and notifications\n"
                    "Connect with other\n"
                    "members of our community Enjoy a personalized experience on our website\n"
                    "We value your privacy and assure you that your personal information will "
                    "be kept secure and confidential at all times.\n"
                    "For more information,please refer to our Privacy Policy on our website.If you have any questions"
                    "or concerns,\n"
                    "please do not hesitate to contact us at 'deafmutebeyonddark@gmail.com'."
                    "Our team is always available to assist you with any queries\n"
                    "you may have."
                    "Thank you for choosing ERIS. We look forward to seeing you on our website soon! "
                    "Best regards \n"
                    "Team ERIS \n") % User_Name
            smtpObj.sendmail('sender email', Email_ID, body)
            smtpObj.quit()
            return redirect(url_for("login"))
        else:
            msg = "Password not Match "
            return render_template('sign_up.html', msg=msg)
    return render_template('sign_up.html')
@app.route('/Reset_Password', methods=['GET', 'POST'])
def Reset_Password():
    email = Forget_Email.var
    if request.method == 'POST':
        password = request.form['password']
        verify_password = request.form['re_enter_password']
        if password == verify_password:
            cur = mysql.connection.cursor()
            cur.execute('update Account set Password = %s where Emailid=%s', (password, email))
            cur.connection.commit()
            cur.close()
            return redirect(url_for('login'))
        else:
            Notif = "Password don't match"
            return render_template('Reset_Password.html', msg=Notif)
    return render_template('Reset_Password.html')
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('Home.html')
@app.route('/eris_deaf', methods=['GET', 'POST'])
def eris_deaf():
    return render_template('Eris_Deaf.html')
@app.route('/Alphabet_Games', methods=['GET', 'POST'])
def Alphabet_Games():
    return render_template('Alphabet_Games.html')
@app.route('/Number_Games', methods=['GET', 'POST'])
def Number_Games():
    return render_template('Number_Games.html')
@app.route('/alphabet', methods=['GET', 'POST'])
def alphabet():
    if request.method == 'POST':
        todo = request.form.get("todo")
        global msg_alp
        msg_alp = todo
        return render_template('Alphabet.html', Message=msg_alp)
    return render_template('Alphabet.html')
def alphabet_gen(video):
    while True:
        success, img = video.read()
        imgOutput = img.copy()
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
            aspectRatio = h / w
            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
            global msg_alp
            if labels[index] == msg_alp:
                cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90, y - offset - 50 + 50),
                              (255, 0, 255), cv2.FILLED)
                cv2.putText(imgOutput, labels[index], (x, y - 26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (255, 0, 255), 4)
        ret, jpeg = cv2.imencode('.jpg', imgOutput)
        frame = jpeg.tobytes()
        yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
def alphabet_img():
    global msg_alp
    data = msg_alp
    img = cv2.imread("./static/Alphabet/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/alphabet_video_feed')
def alphabet_video_feed():
    global video
    return Response(alphabet_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/alphabet_image_feed')
def alphabet_image_feed():
    return Response(alphabet_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/number', methods=['GET', 'POST'])
def number():
    global msg_num
    if request.method == 'POST':
        todo = request.form.get("todo")
        global msg_num
        msg_num = todo
        return render_template('Number.html', Message=msg_num)
    return render_template('Number.html', Message=msg_num)
def number_gen(video):
    FingerCount = ''
    while True:
        _, img = video.read()
        img = cv2.flip(img, 1)
        hand = detector.findHands(img, draw=False)
        if hand:
            lmlist = hand[0]
            if lmlist:
                fingerup = detector.fingersUp(lmlist)
                if fingerup == [0, 0, 0, 0, 0]:
                    FingerCount = 0
                if fingerup == [0, 1, 0, 0, 0]:
                    FingerCount = 1
                if fingerup == [0, 1, 1, 0, 0]:
                    FingerCount = 2
                if fingerup == [1, 1, 1, 0, 0]:
                    FingerCount = 3
                if fingerup == [0, 1, 1, 1, 1]:
                    FingerCount = 4
                if fingerup == [1, 1, 1, 1, 1]:
                    FingerCount = 5
                if fingerup == [0, 0, 1, 1, 1]:
                    FingerCount = 9
                if fingerup == [0, 1, 1, 0, 1]:
                    FingerCount = 7
                if fingerup == [0, 1, 0, 1, 1]:
                    FingerCount = 8
                if fingerup == [0, 1, 1, 1, 0]:
                    FingerCount = 6
                if fingerup == [1, 0, 0, 0, 0]:
                    FingerCount = 10
            global msg_num
            if int(msg_num) == FingerCount:
                cv2.putText(img, str(FingerCount), (150, 150), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 12)
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
def number_img():
    global msg_num
    data = msg_num
    img = cv2.imread("./static/Number/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/number_video_feed')
def number_video_feed():
    global video
    return Response(number_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/number_image_feed')
def number_image_feed():
    return Response(number_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Words', methods=['GET', 'POST'])
def Words():
    global msg_words
    if request.method == 'POST':
        todo = request.form.get("todo")
        global msg_words
        msg_words = todo
        return render_template('Words.html', Message=msg_words)
    return render_template('Words.html', Message=msg_words)
def Words_gen(video):
    FingerCount = ''
    while True:
        _, img = video.read()
        img = cv2.flip(img, 1)
        hand = detector.findHands(img, draw=False)
        if hand:
            lmlist = hand[0]
            if lmlist:
                fingerup = detector.fingersUp(lmlist)
                if fingerup == [1, 1, 0, 0, 0]:
                    FingerCount = "Birds"
                if fingerup == [0, 1, 1, 1, 0]:
                    FingerCount = "Ocean"
                if fingerup == [0, 0, 1, 1, 1]:
                    FingerCount = "Cat"
                if fingerup == [1, 0, 0, 0, 1]:
                    FingerCount = "Phone"
                if fingerup == [0, 1, 0, 0, 0]:
                    FingerCount = "YOU"
                if fingerup == [1, 1, 1, 1, 1]:
                    FingerCount = "Plants"
                if fingerup == [1, 1, 0, 0, 1]:
                    FingerCount = "Airline"
            global msg_words
            if FingerCount == msg_words:
                cv2.putText(img, str(FingerCount), (150, 150), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 12)
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
def Words_img():
    global msg_words
    data = msg_words
    img = cv2.imread("./static/Words/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/Words_video_feed')
def Words_video_feed():
    global video
    return Response(Words_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Words_image_feed')
def Words_image_feed():
    return Response(Words_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Alphabet_Game', methods=['GET', 'POST'])
def Alphabet_Game():
    global msg_alp_game, alp_count, alp_score
    notif = ""
    if request.method == 'POST':
        todo = request.form.get("todo")
        msg_alp_game = todo
        global alp_count
        if alp_count == "YES%s" % todo:
            alp_score += 10
            notif += "Congratulations!"
            return render_template('Alphabet_Game.html', Message=msg_alp_game, SCORE=alp_score, NOTI_SCORE=notif)
        return render_template('Alphabet_Game.html', Message=msg_alp_game, SCORE=alp_score)
    return render_template('Alphabet_Game.html', SCORE=alp_score)
def Alphabet_Game_gen(video):
    while True:
        success, img = video.read()
        imgOutput = img.copy()
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
            aspectRatio = h / w
            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
            global msg_alp, alp_count
            if labels[index] == msg_alp_game:
                alp_count = "YES{}".format(labels[index])
                cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90, y - offset - 50 + 50),
                              (255, 0, 255), cv2.FILLED)
                cv2.putText(imgOutput, labels[index], (x, y - 26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (255, 0, 255), 4)
        ret, jpeg = cv2.imencode('.jpg', imgOutput)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
def Alphabet_Game_img():
    global msg_alp_game
    data = msg_alp_game
    img = cv2.imread("./static/Alphabet_Game/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/Alphabet_Game_video_feed')
def Alphabet_Game_video_feed():
    global video
    return Response(Alphabet_Game_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Alphabet_Game_image_feed')
def Alphabet_Game_image_feed():
    return Response(Alphabet_Game_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Number_Game', methods=['GET', 'POST'])
def Number_Game():
    global msg_num_game, num_score
    notif = ""
    if request.method == 'POST':
        todo = request.form.get("todo")
        msg_num_game = todo
        global num_count
        if num_count == "YES%s" % todo:
            num_score += 10
            notif += "Congratulations!"
            return render_template('Number_Game.html', Message=msg_num_game, SCORE=num_score, NOTI_SCORE=notif)
        return render_template('Number_Game.html', Message=msg_num_game, SCORE=num_score)
    return render_template('Number_Game.html', Message=msg_num_game, SCORE=num_score)
def Number_Game_gen(video):
    FingerCount = ''
    while True:
        _, img = video.read()
        img = cv2.flip(img, 1)
        hand = detector.findHands(img, draw=False)
        if hand:
            lmlist = hand[0]
            if lmlist:
                fingerup = detector.fingersUp(lmlist)
                if fingerup == [0, 0, 0, 0, 0]:
                    FingerCount = 0
                if fingerup == [0, 1, 0, 0, 0]:
                    FingerCount = 1
                if fingerup == [0, 1, 1, 0, 0]:
                    FingerCount = 2
                if fingerup == [1, 1, 1, 0, 0]:
                    FingerCount = 3
                if fingerup == [0, 1, 1, 1, 1]:
                    FingerCount = 4
                if fingerup == [1, 1, 1, 1, 1]:
                    FingerCount = 5
                if fingerup == [0, 0, 1, 1, 1]:
                    FingerCount = 9
                if fingerup == [0, 1, 1, 0, 1]:
                    FingerCount = 7
                if fingerup == [0, 1, 0, 1, 1]:
                    FingerCount = 8
                if fingerup == [0, 1, 1, 1, 0]:
                    FingerCount = 6
                if fingerup == [1, 0, 0, 0, 0]:
                    FingerCount = 10
            global msg_num_game, num_count
            if int(msg_num_game) == FingerCount:
                num_count = "YES{}".format(FingerCount)
                cv2.putText(img, str(FingerCount), (150, 150), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 12)
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
def Number_Game_img():
    global msg_num_game
    data = msg_num_game
    img = cv2.imread("./static/Number_Game/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/Number_Game_video_feed')
def Number_Game_video_feed():
    global video
    return Response(Number_Game_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Number_Game_image_feed')
def Number_Game_image_feed():
    return Response(Number_Game_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Number_Add_Game', methods=['GET', 'POST'])
def Number_Add_Game():
    global msg_num_add_game, num_add_score
    notif = ""
    if request.method == 'POST':
        todo = request.form.get("todo")
        msg_num_add_game = todo
        global num_add_count
        if num_add_count == "YES%s" % todo:
            num_add_score += 10
            notif += "Congratulations!"
            return render_template('Number_Add_Game.html', Message=msg_num_add_game, SCORE=num_add_score, NOTI_SCORE=notif)
        return render_template('Number_Add_Game.html', Message=msg_num_add_game, SCORE=num_add_score)
    return render_template('Number_Add_Game.html', Message=msg_num_add_game, SCORE=num_add_score)
def Number_Add_Game_gen(video):
    FingerCount = ''
    while True:
        _, img = video.read()
        img = cv2.flip(img, 1)
        hand = detector.findHands(img, draw=False)
        if hand:
            lmlist = hand[0]
            if lmlist:
                fingerup = detector.fingersUp(lmlist)
                if fingerup == [0, 0, 0, 0, 0]:
                    FingerCount = 0
                if fingerup == [0, 1, 0, 0, 0]:
                    FingerCount = 1
                if fingerup == [0, 1, 1, 0, 0]:
                    FingerCount = 2
                if fingerup == [1, 1, 1, 0, 0]:
                    FingerCount = 3
                if fingerup == [0, 1, 1, 1, 1]:
                    FingerCount = 4
                if fingerup == [1, 1, 1, 1, 1]:
                    FingerCount = 5
                if fingerup == [0, 0, 1, 1, 1]:
                    FingerCount = 9
                if fingerup == [0, 1, 1, 0, 1]:
                    FingerCount = 7
                if fingerup == [0, 1, 0, 1, 1]:
                    FingerCount = 8
                if fingerup == [0, 1, 1, 1, 0]:
                    FingerCount = 6
                if fingerup == [1, 0, 0, 0, 0]:
                    FingerCount = 10
            global msg_num_add_game, num_add_count
            if int(msg_num_add_game) == FingerCount:
                num_add_count = "YES{}".format(FingerCount)
                cv2.putText(img, str(FingerCount), (150, 150), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 12)
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
def Number_Add_Game_img():
    global msg_num_add_game
    data = msg_num_add_game
    img = cv2.imread("./static/Number_Add_Game/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/Number_Add_Game_video_feed')
def Number_Add_Game_video_feed():
    global video
    return Response(Number_Add_Game_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Number_Add_Game_image_feed')
def Number_Add_Game_image_feed():
    return Response(Number_Add_Game_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Number_Sub_Game', methods=['GET', 'POST'])
def Number_Sub_Game():
    global msg_num_sub_game, num_sub_score
    notif = ""
    if request.method == 'POST':
        todo = request.form.get("todo")
        msg_num_sub_game = todo
        global num_sub_count
        if num_sub_count == "YES%s" % todo:
            num_sub_score += 10
            notif += "Congratulations!"
            return render_template('Number_Sub_Game.html', Message=msg_num_sub_game, SCORE=num_sub_score, NOTI_SCORE=notif)
        return render_template('Number_Sub_Game.html', Message=msg_num_sub_game, SCORE=num_sub_score)
    return render_template('Number_Sub_Game.html', Message=msg_num_sub_game, SCORE=num_sub_score)
def Number_Sub_Game_gen(video):
    FingerCount = ''
    while True:
        _, img = video.read()
        img = cv2.flip(img, 1)
        hand = detector.findHands(img, draw=False)
        if hand:
            lmlist = hand[0]
            if lmlist:
                fingerup = detector.fingersUp(lmlist)
                if fingerup == [0, 0, 0, 0, 0]:
                    FingerCount = 0
                if fingerup == [0, 1, 0, 0, 0]:
                    FingerCount = 1
                if fingerup == [0, 1, 1, 0, 0]:
                    FingerCount = 2
                if fingerup == [1, 1, 1, 0, 0]:
                    FingerCount = 3
                if fingerup == [0, 1, 1, 1, 1]:
                    FingerCount = 4
                if fingerup == [1, 1, 1, 1, 1]:
                    FingerCount = 5
                if fingerup == [0, 0, 1, 1, 1]:
                    FingerCount = 9
                if fingerup == [0, 1, 1, 0, 1]:
                    FingerCount = 7
                if fingerup == [0, 1, 0, 1, 1]:
                    FingerCount = 8
                if fingerup == [0, 1, 1, 1, 0]:
                    FingerCount = 6
                if fingerup == [1, 0, 0, 0, 0]:
                    FingerCount = 10
            global msg_num_sub_game, num_sub_count
            if int(msg_num_sub_game) == FingerCount:
                num_sub_count = "YES{}".format(FingerCount)
                cv2.putText(img, str(FingerCount), (150, 150), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 12)
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
def Number_Sub_Game_img():
    global msg_num_sub_game
    data = msg_num_sub_game
    img = cv2.imread("./static/Number_Sub_Game/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/Number_Sub_Game_video_feed')
def Number_Sub_Game_video_feed():
    global video
    return Response(Number_Sub_Game_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Number_Sub_Game_image_feed')
def Number_Sub_Game_image_feed():
    return Response(Number_Sub_Game_img(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Miss_Word', methods=['GET', 'POST'])
def Miss_Word():
    global msg_alp_miss, alp_miss_count, alp_miss_score
    notif = ''
    if request.method == 'POST':
        todo = request.form.get("todo")
        msg_alp_miss = todo
        global alp_miss_count
        if alp_miss_count == "YES%s" % todo:
            alp_miss_score += 10
            notif += "Congratulations!"
            return render_template('Miss_Word.html', Message=msg_alp_miss, SCORE=alp_miss_score, NOTI_SCORE=notif)
        return render_template('Miss_Word.html', Message=msg_alp_miss, SCORE=alp_miss_score)
    return render_template('Miss_Word.html', SCORE=alp_miss_score)
def Miss_Word_gen(video):
    while True:
        success, img = video.read()
        imgOutput = img.copy()
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
            imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
            aspectRatio = h / w
            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize
                prediction, index = classifier.getPrediction(imgWhite, draw=False)
            global msg_alp_miss, alp_miss_count
            if labels[index] == msg_alp_miss:
                alp_miss_count = "YES{}".format(labels[index])
                cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90, y - offset - 50 + 50),
                              (255, 0, 255), cv2.FILLED)
                cv2.putText(imgOutput, labels[index], (x, y - 26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
                cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (255, 0, 255), 4)
        ret, jpeg = cv2.imencode('.jpg', imgOutput)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
def Miss_Word_img():
    global msg_alp_miss
    data = msg_alp_miss
    img = cv2.imread("./static/Miss_Word/%s.png" % data)
    frame = cv2.imencode('.jpg', img)[1].tobytes()
    yield b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
@app.route('/Miss_Word_video_feed')
def Miss_Word_video_feed():
    global video
    return Response(Miss_Word_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/Miss_Word_image_feed')
def Miss_Word_image_feed():
    return Response(Miss_Word_img(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Web_search', methods=['GET', 'POST'])
def Web_search():
    if request.method == 'POST':
        # location
        geolocator = Nominatim(user_agent="geoapiExercises")
        city = request.form['messages']
        location = geolocator.geocode(city)
        result = TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude)
        dateandtime = datetime.now(timezone(result)).strftime('%I:%M:%p')
        # weather
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'}
        city_weather = city + " weather"
        city_weather = city_weather.replace(" ", "+")
        res = requests.get(
            f'https://www.google.com/search?q={city_weather}&oq={city_weather}&aqs=chrome.0.35i39l2j0l4j46j69i60'
            f'.6128j1j7&sourceid=chrome&ie=UTF-8',
            headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        info = soup.select('#wob_dc')[0].getText().strip()
        weather = soup.select('#wob_tm')[0].getText().strip()
        location = soup.select('#wob_loc')[0].getText().strip()
        weather = weather + '°C', info
        location = location
        return render_template('Web_search.html', dateandtime=dateandtime, location=location, weather=weather)
    else:
        geolocator = Nominatim(user_agent="geoapiExercises")
        city = "chennai"
        location = geolocator.geocode(city)
        result = TimezoneFinder().timezone_at(lng=location.longitude, lat=location.latitude)
        dateandtime = datetime.now(timezone(result)).strftime('%I:%M:%p')
        # weather
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'}
        city_weather = city + " weather"
        city_weather = city_weather.replace(" ", "+")
        res = requests.get(
            f'https://www.google.com/search?q={city_weather}&oq={city_weather}&aqs=chrome.0.35i39l2j0l4j46j69i60'
            f'.6128j1j7&sourceid=chrome&ie=UTF-8',
            headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        info = soup.select('#wob_dc')[0].getText().strip()
        weather = soup.select('#wob_tm')[0].getText().strip()
        location = soup.select('#wob_loc')[0].getText().strip()
        weather = weather + '°C', info
        location = location
        return render_template('Web_search.html', dateandtime=dateandtime, location=location, weather=weather)
@app.route('/Web_search_index', methods=['GET', 'POST'])
def Web_search_index():
    if request.method == 'POST':
        search = request.form
        messages = search['messages']
        cur = mysql.connection.cursor()
        result = cur.execute('select Search_Name,url from Search_item WHERE category=%s', (messages,))
        if result > 0:
            result_all = cur.fetchall()
            return render_template('Web_search_page.html', result_all=result_all, Name_search=messages)
    return render_template('Web_search.html')
@app.route('/Web_search_page', methods=['GET', 'POST'])
def Web_search_page():
    if request.method == "POST":
        Name = request.form["messages"]
        cur = mysql.connection.cursor()
        result = cur.execute('select Search_Name,url from Search_item WHERE category=%s', (Name,))
        if result > 0:
            result_all = cur.fetchall()
            return render_template('Web_search_page.html', result_all=result_all, Name_search=Name)
    return render_template('Web_search_page.html')
@app.route('/ERIS_VS', methods=['GET', 'POST'])
def ERIS_VS():
    global msg_src
    cur = mysql.connection.cursor()
    result = cur.execute('select Search_Name,url,About from Search_item WHERE category=%s', (msg_src,))
    if result > 0:
        result_all = cur.fetchall()
        return render_template('ERIS_VS.html', Name_search=msg_src, result_all=result_all)
    return render_template('ERIS_VS.html', Name_search=msg_src)
def ERIS_VS_gen(video):
    lis = ["Birds", "Ocean", "Cat", "Phone", "YOU", "Plants", "Airline"]
    FingerCount = ''
    while True:
        _, img = video.read()
        img = cv2.flip(img, 1)
        hand = detector.findHands(img, draw=False)
        if hand:
            lmlist = hand[0]
            if lmlist:
                fingerup = detector.fingersUp(lmlist)
                if fingerup == [1, 1, 0, 0, 0]:
                    FingerCount = "Birds"
                if fingerup == [0, 1, 1, 1, 0]:
                    FingerCount = "Ocean"
                if fingerup == [0, 0, 1, 1, 1]:
                    FingerCount = "Cat"
                if fingerup == [1, 0, 0, 0, 1]:
                    FingerCount = "Phone"
                if fingerup == [0, 1, 0, 0, 0]:
                    FingerCount = "YOU"
                if fingerup == [1, 1, 1, 1, 1]:
                    FingerCount = "Plants"
                if fingerup == [1, 1, 0, 0, 1]:
                    FingerCount = "Airline"
            if FingerCount in lis:
                global msg_src
                msg_src = FingerCount
                cv2.putText(img, str(FingerCount), (150, 150), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 12)
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'
@app.route('/ERIS_VS_video_feed')
def ERIS_VS_video_feed():
    global video
    return Response(ERIS_VS_gen(video), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=True)