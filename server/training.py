from sklearn import svm
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from calcoloArea import calcoloFeatures
import numpy as np
import sqlite3

def loadfile(filename):
    with open(filename,"r") as f:
        lettura = f.read().split("\n")
        X=[]
        Y=[]
        Z=[]
        for ind,v in enumerate(lettura):
            try:
                splitted=v.split(",")
                X.append(splitted[1])
                Y.append(splitted[2])
                Z.append(splitted[3])
            except:
                pass

    for i in range(0,len(X)):
        X[i] = float(X[i])
        Y[i] = float(Y[i])
        Z[i] = float(Z[i])
    return X,Y,Z

def loaddatabase(filename):
    clf=svm.SVC()
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    c.execute("SELECT * FROM Componente INNER JOIN Coordinate ON Componente.Nome=Coordinate.Nome_Componente")
    data=c.fetchall()
    dataX={}
    dataY={}
    dataZ={}

    for d in data:
        if (d[0] not in dataX):
            dataX[d[0]]=[]
            dataY[d[0]]=[]
            dataZ[d[0]]=[]
        dataX[d[0]].append(d[3])
        dataY[d[0]].append(d[4])
        dataZ[d[0]].append(d[5])


    data=[]
    stats=[]
    features=[]
    for k in dataX.keys():
        for i in range(1,int(len(dataX[k])/100)-1):
            print("Dataset n."+str(i))
            tempx=dataX[k][(i-1)*100:i*100]
            tempy=dataY[k][(i-1)*100:i*100]
            tempz=dataZ[k][(i-1)*100:i*100]

            featX1,featX2,featX3,featX4,featX5,featX6=calcoloFeatures(tempx)
            featY1,featY2,featY3,featY4,featY5,featY6=calcoloFeatures(tempy)
            featZ1,featZ2,featZ3,featZ4,featZ5,featZ6=calcoloFeatures(tempz)
            features.append([featX1,featX2,featX3,featX4,featX5,featX6,featY1,featY2,featY3,featY4,featY5,featY6,featZ1,featZ2,featZ3,featZ4,featZ5,featZ6])
            print("Feature di X:")
            print(featX1,featX2,featX3,featX4,featX5,featX6)
            print("Feature di Y:")
            print(featY1,featY2,featY3,featY4,featY5,featY6)
            print("Feature di Z:")
            print(featZ1,featZ2,featZ3,featZ4,featZ5,featZ6)
            if(k=="Ventola-Buona"):
                stats.append(2)
            elif(k=="Ventola-Rotta"):
                stats.append(0)
    print(len(features),len(stats))
    X_train, X_test, y_train, y_test = train_test_split(
    features, stats, test_size=0.20, random_state=42)
    clf.fit(X_train,y_train)
    
    y_pred=clf.predict(X_test)
    
    acc=accuracy_score(y_test,y_pred)
    print("accuracy:",acc)
    
    clf.fit(features,stats)
    joblib.dump(clf,"net4.pkl")

loaddatabase("data.db")
label=["broken","damaged","good"]
#fs=["dataset/A.csv","dataset/B.csv","dataset/C.csv","dataset/D.csv","dataset/E.csv"]
#statoventola=[2,1,0,2,0]
#clf=svm.NuSVC()

# features=[]
# stats=[]
# for idx,f in enumerate(fs):
#     print("Carico file: "+f)
#     x,y,z=loadfile(f)
#     for i in range(1,int(len(x)/100)-1):
#         print("Dataset n."+str(i))
#         tempx=x[(i-1)*100:i*100]
#         tempy=y[(i-1)*100:i*100]
#         tempz=z[(i-1)*100:i*100]
#         featX1,featX2,featX3,featX4,featX5,featX6=calcoloFeatures(tempx)
#         featY1,featY2,featY3,featY4,featY5,featY6=calcoloFeatures(tempy)
#         featZ1,featZ2,featZ3,featZ4,featZ5,featZ6=calcoloFeatures(tempz)
#         features.append([featX1,featX2,featX3,featX4,featX5,featX6,featY1,featY2,featY3,featY4,featY5,featY6,featZ1,featZ2,featZ3,featZ4,featZ5,featZ6])
#         stats.append(statoventola[idx])
#         print("Feature di X:")
#         print(featX1,featX2,featX3,featX4,featX5,featX6)
#         print("Feature di Y:")
#         print(featY1,featY2,featY3,featY4,featY5,featY6)
#         print("Feature di Z:")
#         print(featZ1,featZ2,featZ3,featZ4,featZ5,featZ6)
#         #print("\n\n\n\n\n",features)
# clf.fit(features,stats)
# joblib.dump(clf, 'net2.pkl')
