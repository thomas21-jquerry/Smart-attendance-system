from flask.helpers import send_file
import numpy as np
from flask import Flask, request, jsonify, render_template,session
import pickle
import face_recognition
import cv2
import os
from numpy.lib.function_base import append
from werkzeug.utils import secure_filename
import pymongo
from datetime import date
import csv
from pathlib import Path

client = pymongo.MongoClient("mongodb+srv://nandhu:hinandhu100@cluster0.q49fb.mongodb.net/attendance?retryWrites=true&w=majority")
db = client['attendance']
col = db['encoding']
coll=db['present']
log=db['login']


app = Flask(__name__)
app.secret_key="hi"

@app.route('/')
def home():
    return render_template('landing.html')

@app.route("/firstlog")
def firstlog():
    return render_template('login.html')

@app.route("/logging", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        credentials = request.form.to_dict()
        existing_user = log.find_one(({"_id": credentials['check_id']}))
    
        if existing_user is None:
            return render_template("login.html")
        else:
            if credentials['check_id'] == existing_user["_id"] and credentials['check_name'] == existing_user['password']:
                session['college_id']=existing_user["c_id"]
                session['college_name']=existing_user['c_name']
                session['personal_id']=existing_user['_id']
                session['personal_name']=existing_user['name']
                session['role']=existing_user['role']

                if existing_user['role']=="admin":
                    cla=db[session['college_id']+"_classes"]
                    tr=db[session['college_id']+"_teachers"]
                    y=cla.find({})
                    z=tr.find({})
                   
                    return render_template('adminview.html',data=existing_user,cl=y,t=z)
                elif existing_user['role']=="teacher":
                    cla=db[session['college_id']+"_classes"]
                    y=cla.find({})   



                    return render_template('teacherview.html',data=existing_user,cl=y)
                elif existing_user['role']=="student":
                    att=db[session['college_id']+"_"+existing_user['class_id']+"_attendance"]
                    x=att.find({})
                    # sub = db[session['college_id']+"_classes"]
                    # sub = sub.findOne({ "_id":existing_user['class_id']})

                    subjectName=set()
                    for i in x:
                        subjectName.add(i['subject'])
                    subjectName = list(subjectName)
                    countatt=[]
                    
                    print(subjectName)
                    for i in subjectName:
                        countatt.append(0)
                    
                    dupli = att.find({})
                    for i in dupli:
                        if [session['personal_name'],session['personal_id']] in i['present']:
                            a = subjectName.index(i['subject'])
                            countatt[a]+=1
                   
                    
                    dupli = att.find({})
                    totalAttendance = [0 for i in subjectName]
                    for i in dupli:
                        ind = subjectName.index(i['subject'])
                        totalAttendance[ind]+=1
                    avgAttendance = [0 for i in subjectName]
                   
                    for i in range(len(countatt)):
                        avgAttendance[i] = int((countatt[i]/totalAttendance[i])*100)
                    
                
                    dupli = att.find({})
                    
                    x=att.find({})
                    # x = list(x)
                    
                    # filename = "university_records.csv"
  
                    # # writing to csv file
                    # with open(filename, 'w') as csvfile:
                    #     # creating a csv writer object
                    #     csvwriter = csv.writer(csvfile)
                        
                    #     # writing the fields
                    #     fields = [x[0]['_id'],x[0]['subject'],x[0]['class_id']]
                    #     csvwriter.writerow(fields)
                        
                        
                        
           
                    
                
                   


                    return render_template('studentview.html',data=existing_user,teachernames=subjectName,countatt= countatt,at=dupli,nam = [session['personal_name'],session['personal_id']],avgAttendance = avgAttendance, totalAttendance=totalAttendance,subjectNames=subjectName,presentAtt = countatt)
            else:
                return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/redirect')
def redirect():
    existing_user = log.find_one(({"_id": session['personal_id']}))
    if existing_user['role']=="admin":
        cla=db[session['college_id']+"_classes"]
        tr=db[session['college_id']+"_teachers"]
        y=cla.find({})
        z=tr.find({})
        return render_template('adminview.html',data=existing_user,cl=y,t=z)
    elif existing_user['role']=="teacher":
            cla=db[session['college_id']+"_classes"]
            
            y=cla.find({})                    
            return render_template('teacherview.html',data=existing_user,cl=y)
    elif existing_user['role']=="student":
            att=db[session['college_id']+"_"+existing_user['class_id']+"_attendance"]
            x=att.find({})
            
            subjectName=set()
            for i in x:
                subjectName.add(i['subject'])
            subjectName = list(subjectName)
            countatt=[]
            
           
            for i in subjectName:
                countatt.append(0)
            
            dupli = att.find({})
            for i in dupli:
                if [session['personal_name'],session['personal_id']] in i['present']:
                    a = subjectName.index(i['subject'])
                    countatt[a]+=1
            
            
            dupli = att.find({})
            totalAttendance = [0 for i in subjectName]
            for i in dupli:
                ind = subjectName.index(i['subject'])
                totalAttendance[ind]+=1
            avgAttendance = [0 for i in subjectName]
            
            for i in range(len(countatt)):
                avgAttendance[i] = int((countatt[i]/totalAttendance[i])*100)
            
        
            dupli = att.find({})
            
            x=att.find({})
                
           
                    
            return render_template('studentview.html',data=existing_user,teachernames=subjectName,countatt= countatt,at=dupli,nam = [session['personal_name'],session['personal_id']],avgAttendance = avgAttendance, totalAttendance=totalAttendance,subjectNames=subjectName,presentAtt = countatt)
            


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/sigup',methods=['GET','POST'])
def sigup():
    if request.method == 'POST':
        req = request.form
        a_name = req.get("a_name")
        a_id = req.get("a_id")
        c_id = req.get("c_id")
        c_name = req.get("c_name")
        passw = req.get("pwd")
        role=str("admin")
        log=db['login']
        existing_user = log.find_one(({"_id":a_id}))
        try_user = log.find_one(({"c_id":c_id}))
        
        if existing_user is not  None:
            if try_user is not None:
                return render_template('signup.html',kk=1,kkk=1)
                
        if existing_user is not  None:
            return render_template('signup.html',kk=0,kkk=1)
        
        if try_user is not None:
            return render_template('signup.html',kk=1,kkk=0)

        image = request.files['imagefile']
        basepath = os.path.dirname(__file__)
        image.filename=a_id+".jpg"
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))
        image.save(file_path)

        past = {"_id": a_id,"name":a_name,"c_id":c_id,"c_name":c_name,"password":passw,"role":role,"image":image.filename}

        log.insert_one(past)
        return render_template('login.html')
    else:
        return render_template('signup.html')


@app.route('/createclass')
def createclass():
    return render_template('class.html')


@app.route('/creatingclass',methods=['GET','POST'])
def creatingclass():
    if request.method =='POST':
        req = request.form
        class_id = req.get("class_id")
        class_name = req.get("class_name")
        infoc=db[session['college_id']+"_classes"]
        tput=req.get("tags-input")
        tput=list(tput.split(",")) 
       
        sah=[]
        for x in tput:
            sah.append(class_name+"/"+x)


        existing_user = infoc.find_one(({"_id":class_id}))
        try_user=infoc.find_one(({"class_name":class_name}))
        
        if existing_user is not  None:
            if try_user is not None:
                return render_template('class.html',kk=1,kkk=1)
                
        if existing_user is not  None:
            return render_template('class.html',kk=0,kkk=1)
        
        if try_user is not None:
            return render_template('class.html',kk=1,kkk=0)

        post={"_id": class_id,"class_name":class_name,"subjects":tput,"inter":sah}
        
        infoc.insert_one(post)
        return render_template('class.html')
    else:
        return render_template('class.html')


@app.route('/createteacher')
def createteacher():
    data=db[session['college_id']+"_classes"]
    x=data.find({})
    cd=[]
    for y in x:
        for k in y['subjects']:
            cd.append(y['class_name']+"/"+k)
    return render_template('teacheradd.html',dt=cd,kkk=0)

@app.route('/creatingteacher',methods=['GET','POST'])
def creatingteacher():
    if request.method == 'POST':
        credent = request.form.to_dict()
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            cd.append(y['class_name'])
        k=cd
        ls=[]
        sb=[]
        classes = request.form.getlist('class')
        print(classes)
        for v in classes:
            ka,sp=list(v.split("/"))
            ls.append(ka)
            sb.append(sp)
        
        
        try_user = log.find_one(({"_id":credent['p_id']}))
        
        if try_user is not None:
            return render_template('teacheradd.html',dt=k,kkk=1)
        
        image = request.files['imagefile']
        basepath = os.path.dirname(__file__)
        image.filename=credent['p_id']+".jpg"
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))
        image.save(file_path)
        
        pt={"_id":credent['p_id'],"name":credent['t_name'],"college_id":session['college_id'],"college_name":session['college_name'],"password":credent['pwd'],"classes":ls,"subject":sb,"intermediate":classes}
        infot=db[session['college_id']+"_teachers"]
        infot.insert_one(pt)
        lg=db['login']
        p={"_id":credent['p_id'],"name":credent['t_name'],"c_id":session['college_id'],"c_name":session['college_name'],"password":credent['pwd'],"role":str("teacher"),"image":image.filename}
        lg.insert_one(p)
        
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            for k in y['subjects']:
                cd.append(y['class_name']+"/"+k)

        return render_template('teacheradd.html',dt=cd,kkk=0)



@app.route('/createstudent')
def createstudent():
    if(session['role']=="admin"):
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            cd.append(y['class_name'])
        return render_template('add.html',dt=cd)
    elif(session['role']=="teacher"):
        data=db[session['college_id']+"_teachers"]
        existing_user = data.find_one(({"_id":session['personal_id']}))
        cd=[]
        cd=existing_user['classes']
        return render_template('add.html',dt=cd)


@app.route('/creatingstudent',methods=['GET','POST'])
def creating():
    if request.method == 'POST':
        credent = request.form.to_dict()
        p_id=credent['p_id']
        name=credent['name']
        clas=credent['class']
        pwd=credent['pwd']
        l=db['login']

        try_user = l.find_one(({"_id":credent['p_id']}))
        
        if try_user is not None:
            data=db[session['college_id']+"_classes"]
            x=data.find({})
            cd=[]
            for y in x:
                cd.append(y['class_name'])
            return render_template('add.html',dt=cd,ex=1)

        
        image = request.files['imagefile']
        basepath = os.path.dirname(__file__)
        image.filename=p_id+".jpg"
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))
        image.save(file_path)
        
        img = face_recognition.load_image_file(file_path)
        
        encode = face_recognition.face_encodings(img)
        enc=list(encode.pop())
        
        
        check=db[session['college_id']+"_classes"]        
        existing_user = check.find_one(({"class_name":clas}))

        infocs=db[session['college_id']+"_"+existing_user['_id']]
        post = {"_id": p_id,"name":name,"c_id":session['college_id'],"c_name":session['college_name'],"password":pwd,"role":"student","class_id":existing_user['_id'],"image":image.filename}
        pot = {"_id": p_id, "name":name,"encode":enc,"c_id":session['college_id'],"c_name":session['college_name'],"password":pwd,"class_id":existing_user['_id'],"class_name":clas}
        infocs.insert_one(pot)
        l.insert_one(post)

        return render_template('added.html',val_name=name,val_id=p_id,st=1,usi=image.filename)


@app.route('/attendance')
def attendance():
    if(session['role']=="admin"):
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            for z in y['inter']:
                cd.append(z)
        return render_template('attendance.html',dt=cd,teacher=0)
    elif(session['role']=="teacher"):
        data=db[session['college_id']+"_teachers"]
        existing_user = data.find_one(({"_id":session['personal_id']}))
        cd=[]
        cd=existing_user['intermediate']
        return render_template('attendance.html',dt=cd,dp=session['personal_name'],teacher=1)



@app.route('/find',methods=['Post'])
def find():
    if request.method == 'POST':
        credent = request.form.to_dict()
        clas=credent['class']
        time=credent['time']
        time = str(time)
        time = time[:2]
        d2=credent['dat']
        image=request.files['imgfile']
        d1=str(time+"-"+d2)

        only_classname,_=clas.split("/")
        check=db[session['college_id']+"_classes"]
        existing_user = check.find_one(({"class_name":only_classname}))
        coll=db[session['college_id']+"_"+existing_user['_id']+"_attendance"]
        e_user = coll.find_one(({"_id":d1}))
        if e_user is not  None:
            if(session['role']=="admin"):
                data=db[session['college_id']+"_classes"]
                x=data.find({})
                cd=[]
                for y in x:
                     cd.append(y['inter'])
                return render_template('attendance.html',dt=cd,xs=1)
            elif(session['role']=="teacher"):
                data=db[session['college_id']+"_teachers"]
                existing_user = data.find_one(({"_id":session['personal_id']}))
                cd=[]
                cd=existing_user['intermediate']
                return render_template('attendance.html',dt=cd,xs=1)

        
        
        filename = str(d1)
        filename = filename+".jpg"
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
                basepath, 'static/attended', secure_filename(filename))
        
        image.save(file_path)
        
        img = face_recognition.load_image_file(file_path)
        
        facesCurFrame = face_recognition.face_locations(img)
        encodesCurFrame = face_recognition.face_encodings(img,facesCurFrame)
        
        



        col=db[session['college_id']+"_"+existing_user['_id']]
        results= col.find({})
        classNames=[]
        encodeListKnown=[]
        for result in results:
            classNames.append(result["name"])
            encodeListKnown.append(result['encode'])
        
        PresentNames=[]
        for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
            if min(faceDis) < 0.54:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = classNames[matchIndex]
                    
                    used=col.find_one(({"name":name}))
                    PresentNames.append([name,used['_id']])
        present=list()
        
        for names in PresentNames:
            if names not in present:
                present.append(names)


        present_dupli=[]
        for i in range(len(present)):
            present_dupli.append(present[i][0])
             
        absent=[]
        for a in classNames:
            if a not in present_dupli:
                used=col.find_one(({"name":a}))
                absent.append([a,used['_id']])
        
        
    
        
        print(present)
        postp = {"_id":d1,"subject":clas,"present":present,"absent":absent,"class_id":existing_user['_id']}
        coll.insert_one(postp)

        # os.remove(file_path)
        print(d1)
        return render_template('attended.html',val=present,vall=absent,divasam=d2,samayam=time,class_info=existing_user['_id'],simple=d1,fname = filename)


@app.route('/logout')
def logout():
    session.pop("college_id",None)
    session.pop("college_name",None)
    session.pop("personal_id",None)
    session.pop("personal_name",None)
    session.pop("role",None)
    file = "attendance.csv"
    my_file = Path(file)
    if my_file.is_file():
         os.remove("attendance.csv")
   
    return render_template('login.html')


@app.route('/previous')
def previous():
    if(session['role']=="admin"):
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            for k in y['inter']:
                cd.append(k)
        print(cd)
        return render_template('previous.html',dt=cd)
    elif(session['role']=="teacher"):
        data=db[session['college_id']+"_teachers"]
        existing_user = data.find_one(({"_id":session['personal_id']}))
        cd=[]
        cd=existing_user['intermediate']
        
        return render_template('previous.html',dt=cd)


@app.route('/processing',methods=['GET','POST'])
def processing():
    if request.method == 'POST':
        if(session['role']=="admin"):
            data=db[session['college_id']+"_classes"]
            x=data.find({})
            cd=[]
            for y in x:
                for k in y['inter']:
                    cd.append(k)
            credent = request.form.to_dict()
            clas=credent['class']
            only_classname,_=clas.split("/")
            check=db[session['college_id']+"_classes"]        
            existing_user = check.find_one(({"class_name":only_classname}))
            infocs=db[session['college_id']+"_"+existing_user['_id']+"_attendance"]
            x=infocs.find({"subject":clas})
    
            return render_template('previous1.html',dt=cd,inf=x)
        elif(session['role']=="teacher"):
            data=db[session['college_id']+"_teachers"]
            existing_user = data.find_one(({"_id":session['personal_id']}))
            cd=[]
            cd=existing_user['intermediate']
            credent = request.form.to_dict()
            clas=credent['class']
            check=db[session['college_id']+"_classes"]     
            only_classname,_=clas.split("/")   
            existing_user = check.find_one(({"class_name":only_classname }))
            infocs=db[session['college_id']+"_"+existing_user['_id']+"_attendance"]
            x=infocs.find({"subject":clas})
           
            tri=db[session['college_id']+"_"+existing_user['_id']]
            y=tri.find({},{"_id":0,"name":1})
            studentNames = []
            # temp = x[0]['present']
            
            # for i in range(len(temp)):
            #     studentNames.append(temp[i][0])
            # temp = x[0]['absent']
            # for i in range(len(temp)):
            #     studentNames.append(temp[i][0])
            studentNam = list(y)
            for i in range(len(studentNam)):
                studentNames.append(studentNam[i]["name"])
                
            
           
            

            x = list(x)
            idlist = ["Names"]

            for i in range(len(x)):
                idlist.append(x[i]['_id'])
            # print(x[5]['present'][0][0])
            attend = []
            attend.append(idlist)
            
            for i in range(len(studentNames)):
                dummy = [studentNames[i]]
                for j in range(len(x)):
                    if x[j]['present']:
                        # if studentNames[i] in x[j]['present'][0]:
                        #     dummy.append("present")
                        # else:
                        #     dummy.append("absent")
                        fla = 0
                        for k in range(len(x[j]['present'])):
                            if studentNames[i] == x[j]['present'][k][0]:
                                dummy.append("present")
                                fla = 1
                                break
                        if fla == 0:
                            dummy.append("absent")  
                            
                    else:
                        dummy.append("absent")
                attend.append(dummy)


            
            filename = "attendance1.csv"
            
          
            # writing to csv file
            with open(filename, 'w') as csvfile:
                csvwriter = csv.writer(csvfile)
            # creating a csv writer object
           
                for i in range(len(attend)):

                    csvwriter.writerow(attend[i])


                
                        
             # writing the fields
            
               




            
            return render_template('previous.html',dt=cd,inf=x)

@app.route('/download')
def download():
    
    
    # path = os.path.join(app.instance_path, filename)

    # def generate():
    #     with open(path) as f:
    #         yield from f

    #     os.remove(path)

    # r = app.response_class(generate(), mimetype='text/csv')
    # r.headers.set('Content-Disposition', 'attachment', filename='data.csv')
    # return r
#****************************************************************************************
    # p = "attendance.csv"
    
    # return send_file(p, as_attachment=True)
    
    path = "attendance1.csv"
    return send_file(path, as_attachment=True)

   




@app.route('/updateatt')
def updateatt():
    if(session['role']=="admin"):
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            for k in y['inter']:
                cd.append(k)

        return render_template('updateattendance.html',dt=cd)
    elif(session['role']=="teacher"):
        data=db[session['college_id']+"_teachers"]
        existing_user = data.find_one(({"_id":session['personal_id']}))
        cd=[]
        cd=existing_user['intermediate']
        return render_template('updateattendance.html',dt=cd)
        

    
@app.route('/update',methods=['GET','POST'])
def update():
    if request.method == 'POST':
        if(session['role']=="admin"):
            data=db[session['college_id']+"_classes"]
            x=data.find({})
            cd=[]
            for y in x:
                for k in y['inter']:
                    cd.append(k)
        elif(session['role']=="teacher"):
            data=db[session['college_id']+"_teachers"]
            existing_user = data.find_one(({"_id":session['personal_id']}))
            cd=[]
            cd=existing_user['intermediate']


        credent = request.form.to_dict()
        clas=credent['class']
        uniq_d=credent['day']
        uniq_t=credent['time']
        uniq=str(uniq_t+"-"+uniq_d)
        only_classname,_=clas.split("/")
        
        check=db[session['college_id']+"_classes"]        
        existing_user = check.find_one(({"class_name":only_classname}))
        infocs=db[session['college_id']+"_"+existing_user['_id']+"_attendance"]
        copy = infocs.find_one(({"_id":uniq}))
        
        return render_template('attended.html',val=copy['present'],vall=copy['absent'],divasam=uniq_d,samayam=uniq_t,class_info=existing_user['_id'],simple=uniq)
        

@app.route('/editing',methods=['GET','POST'])
def editing():
    if(session['role']=="admin"):
        data=db[session['college_id']+"_classes"]
        x=data.find({})
        cd=[]
        for y in x:
            cd.append(y['class_name'])
            return render_template('edit.html',dt=cd)
    elif(session['role']=="teacher"):
        data=db[session['college_id']+"_teachers"]
        existing_user = data.find_one(({"_id":session['personal_id']}))
        cd=[]
        cd=existing_user['classes']  
        return render_template('edit.html',dt=cd)


@app.route('/edit',methods=['GET','POST'])
def edit():
    if request.method == 'POST':
        credent = request.form.to_dict()
        p_id=credent['p_id']
        name=credent['name']
        clas=credent['class']
        pwd=credent['pwd']
        
        image = request.files['imagefile']

        basepath = os.path.dirname(__file__)
        image.filename = str(p_id)+".jpg"
        file_path = os.path.join(basepath, 'static', secure_filename(image.filename))

        image.save(file_path)
        print(file_path)
        img = face_recognition.load_image_file(file_path)
        
        encode = face_recognition.face_encodings(img)
        enc=list(encode.pop())
        l=db['login']
        
        check=db[session['college_id']+"_classes"]        
        existing_user = check.find_one(({"class_name":clas}))

        infocs=db[session['college_id']+"_"+existing_user['_id']]

        
        myquery = { "_id":p_id }
        newvalues = { "$set": { "encode":enc} }
        infocs.update_one(myquery, newvalues)
        
        

        return render_template('added.html',val_name=name,val_id=p_id,st=1,usi=image.filename)



@app.route('/file',methods=['GET','POST'])
def file():
    dat=db[session['college_id']+"_teachers"]
    tr=[]
    y=dat.find({})
    for i in y:
        tr.append(i['name'])
    return render_template('complaint.html',dp=tr)

    


@app.route('/complaint',methods=['GET','POST'])
def complaint():
    if request.method =='POST':
        req = request.form
        t_name = req.get("teach")
        complaint = req.get("complaint")
        dat=db[session['college_id']+"_complaint"]
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")

        postp = {"teacher":t_name,"date":d1,"compaint":complaint,"student":session['personal_name']}
        dat.insert_one(postp)
        datt=db[session['college_id']+"_teachers"]
        tr=[]
        y=datt.find({})
        for i in y:
            tr.append(i['name'])    
    return render_template('complaint.html',dp=tr,c=1)

@app.route('/view',methods=['GET','POST'])
def view():
    dat=db[session['college_id']+"_complaint"]
    copy = dat.find(({"teacher":session['personal_name']}))
    return render_template('complaintview.html',information=copy)

@app.route('/sendstat',methods=['GET','POST'])
def sendstat():
    if request.method =='POST':
        req = request.form

        student = req.get("student")
        ird=req.get("id")
        classno = req.get("class_no")
        change_state = req.get("change_State")
        class_id = req.get("class_id")
        class_data = req.get("dates")
        class_time = req.get("times")
    
        
        chgd=db[session['college_id']+"_"+class_id+"_attendance"]
        copy = chgd.find_one(({"_id":classno}))
        oldp=copy['present']
        olda=copy['absent']

       

        
        if(change_state=="absent"):
            olda.append([student,ird])
            oldp.remove([student,ird])
        elif(change_state=="present"):
            oldp.append([student,ird])
            olda.remove([student,ird])
        
        myquery = { "_id":classno }
        newvalues = { "$set": { "present":oldp,"absent":olda } }
        chgd.update_one(myquery, newvalues)
        now = chgd.find_one(({"_id":classno}))
       
        return render_template('attended.html',val=now['present'],vall=now['absent'],divasam=class_data,samayam=class_time,class_info=now['class_id'],simple=classno)

    

       

if __name__ == '__main__':
    app.run(debug=True)