#!/bin/python
import sys
import os
import itertools
import csv
import numpy as np
from sklearn import svm
import random
import time
from sklearn import metrics
from sklearn.metrics import roc_auc_score

path='/home/hello/Documents/code/python/dns_data/csv/'
feather_file = 'features.csv'
feather_file2 = 'features2.csv'
targets_file = 'targets.csv'

# 暂时用不到 用来统计数据集的信息
def aaa():
    f3 = open(path+'features_0',"a")
    f4 = open(path+'features_1',"a")    
    # with open(path+feather_file,'r') as f,open(path+targets_file) as f2:
    with open(path+targets_file) as f2:
        num1 = 0
        num2 = 0
        num3 = 0
        num4 = 0
        num5 = 0
        num6 = 0
        for line2 in f2:
            # line = f.readline()
            line2 = line2.strip('\n')
            if len(line2.split(','))==2:
                if line2.split(',')[1]=='0':
                    num1+=1    
                    # f3.write(str(line)+','+str(line1))
                elif line2.split(',')[1]=='1':
                    # f3.write(str(line)+','+str(line1))
                    num2+=1
                elif line2.split(',')[1]=='2':
                    # f3.write(str(line)+','+str(line1))
                    num3+=1
                elif line2.split(',')[1]=='3':
                    # f3.write(str(line)+','+str(line1))
                    num4+=1
                elif line2.split(',')[1]=='4':
                    # f3.write(str(line)+','+str(line1))
                    num5+=1
                else:
                    num6+=1
            else:
                print("hhh")
    print(num1)   
    print(num2)   
    print(num3)   
    print(num4)   
    print(num5)   
    print(num6)   

#从尾行开始读取n行的数据
def tail(filename,n=10):
    con = os.popen('tail -n '+str(n)+' '+filename).read()
    return con.split('\n')

#读取第i到j行的数据
def readallcsv(i,j):   #起始行和结束航
    X = []
    Y = []
    with open(path+feather_file,'r') as f,open(path+targets_file,'r') as f2:
        lines = csv.reader(f)
        lines2 = csv.reader(f2)
        for line in itertools.islice(lines,i+1,j+1):    # line是一个数组 []
            X.append(np.array(line).astype(np.float64))
        for line in itertools.islice(lines2,i,j):  # line2是一个数组 []  0-29999
            if len(line)>1:
                Y.append(np.int(line[1]))
    X = np.array(X)
    X = X[:,1:]   #把第一个标号去掉
    return X,np.array(Y)

# 读取csv文件  返回特征和结果   取开头30000 结尾30000
def readcsv():
    X = []
    y = []
    with open(path+feather_file,'r') as f,open(path+targets_file,'r') as f2:
        lines = csv.reader(f)
        lines2 = csv.reader(f2)
        for line in itertools.islice(lines,1,30000):    # line是一个数组 []
            # np.array(line).astype(np.float64)
            X.append(np.array(line).astype(np.float64))
        for line in itertools.islice(lines2,0,29999):  # line2是一个数组 []
            y.append(np.int(line[1]))
        for line in tail(path+feather_file,30000):
            if line is not None:
                try:
                    X.append(np.array(line.split(",")).astype(np.float64))
                except Exception as e:
                    print (line)
            else:
                continue
        for line in tail(path+targets_file,30000):
            if len(line.split(","))>1:
                y.append(np.int(line.split(",")[1]))
    arr_file = np.array(X)
    line_id = arr_file[:,0]
    data = arr_file[:,1:]
    return data,np.array(y)

# svm 训练  第i,j的数据进行训练
def svm_train(clf,i,j,gap):
    
    #读取数据
    # X, Y = readcsv()
    X, Y = readallcsv(i,j) 
    
    #随机打乱数据
    randnum = random.randint(0,gap-1)   
    random.seed(randnum)
    random.shuffle(X)
    random.seed(randnum)
    random.shuffle(Y)

    #训练
    start = time.time()
    clf.fit(X,Y)
    end = time.time()
    print ("fit use time： "+str(end-start))

# 训练2
def svm_train(clf,X,Y,gap):
    #随机打乱数据
    randnum = random.randint(0,gap-1)   
    random.seed(randnum)
    random.shuffle(X)
    random.seed(randnum)
    random.shuffle(Y)

    #训练
    clf.fit(X,Y)

# 第i,j行的数据进行测试
def svm_test(clf,i,j,gap):
    #读取数据
    # X, Y = readcsv()
    X, Y = readallcsv(i,j) 
    
    #随机打乱数据
    randnum = random.randint(0,gap-1)   
    random.seed(randnum)
    random.shuffle(X)
    random.seed(randnum)
    random.shuffle(Y)

    #预测
    y_hat = clf.predict(X) # predict the target of testing samples

    #准确率
    accury = clf.score(X, Y)
    print ("accury is : ",accury)

    #roc值
    roc_value = roc_auc_score(Y, y_hat)
    print ("roc_auc_score is : ",roc_value)

    #查看auc值
    test_auc = metrics.roc_auc_score(Y, y_hat)#验证集上的auc值
    print ("AUC: ",test_auc)
    
    #查看具体的不正确的个数
    number=0    
    number1=0    
    number2=0    
    for x,z in zip(y_hat, Y):
        if x==z:
            pass
        else:
            number+=1
        if z==1:
            number1+=1
        if x==1:
            number2+=1
    print ("len Y is : ",len(Y))
    print ("not right number is "+str(number))
    print ("Y has 1 number is "+str(number1))
    print ("result Y has 1 number is "+str(number2))

#没用的函数
def notim():
    # #定好模型
    # clf = svm.SVC(C=0.4, kernel='linear', gamma=20, decision_function_shape='ovo')
    # #读取数据
    # # X, Y = readcsv()
    # X, Y = readallcsv()
    # #随机打乱数据
    # randnum = random.randint(0,100)   
    # random.seed(randnum)
    # random.shuffle(X)
    # random.seed(randnum)
    # random.shuffle(Y)
    # #训练
    # clf.fit(X[0:25000],Y[0:25000])

    # #预测
    # y_hat = clf.predict(X[25001:29990]) # predict the target of testing samples 
    # #查看auc值
    # test_auc = metrics.roc_auc_score(Y[25001:29990], y_hat)#验证集上的auc值
    # print ("AUC:",test_auc)
    # #查看具体的不正确的个数
    # number=0    
    # for x,z in zip(y_hat, Y[25001:29990]):
    #     if x==z:
    #         pass
    #     else:
    #         number+=1
    # print ("not right number is "+str(number))
    print ("heh")

def main():
    gap = 30000  # 每次读文件的行数

    start = time.time()
    # clf1 = svm.SVC(C=0.4, kernel='poly', gamma=0.03, coef0=18,degree=3,decision_function_shape='ovo')
    clf2 = svm.SVC(C=0.4, kernel='rbf',decision_function_shape='ovo')
    clf3 = svm.SVC(C=0.4, kernel='sigmoid', coef0=8,decision_function_shape='ovo')
    clf4 = svm.SVC(C=0.3, kernel='linear', decision_function_shape='ovo')
    for i in range(2):
        X, Y = readallcsv(0+gap*i,gap-1+gap*i) 
        # svm_train(clf1,X, Y,gap)
        svm_train(clf2,X, Y,gap)
        svm_train(clf3,X, Y,gap)
        svm_train(clf4,X, Y,gap)
    # svm_test(clf1,0+gap*100,gap-1+gap*100,gap)
    svm_test(clf2,0+gap*100,gap-1+gap*100,gap)
    svm_test(clf3,0+gap*100,gap-1+gap*100,gap)
    svm_test(clf4,0+gap*100,gap-1+gap*100,gap)
    end = time.time()
    print ("use time： "+str(end-start))

    # start = time.time()
    # #定好模型
    # clf = svm.SVC(C=0.4, kernel='poly', gamma=0.03, coef0=18,degree=3,decision_function_shape='ovo')
    # for i in range(2):
    #     svm_train(clf,0+gap*i,gap-1+gap*i,gap)
    # svm_test(clf,0+gap*100,gap-1+gap*100,gap)
    # end = time.time()
    # print ("first use time： "+str(end-start))

    # start = time.time()
    # clf = svm.SVC(C=0.4, kernel='rbf',decision_function_shape='ovo')
    # for i in range(2):
    #     svm_train(clf,0+gap*i,gap-1+gap*i,gap)
    # svm_test(clf,0+gap*100,gap-1+gap*100,gap)
    # end = time.time()
    # print ("second use time： "+str(end-start))

    # start = time.time()
    # clf = svm.SVC(C=0.4, kernel='sigmoid', coef0=8,decision_function_shape='ovo')
    # for i in range(2):
    #     svm_train(clf,0+gap*i,gap-1+gap*i,gap)
    # svm_test(clf,0+gap*100,gap-1+gap*100,gap)
    # end = time.time()
    # print ("third use time： "+str(end-start))

    # start = time.time()
    # clf = svm.SVC(C=0.3, kernel='linear', decision_function_shape='ovo')
    # for i in range(2):
    #     svm_train(clf,0+gap*i,gap-1+gap*i,gap)
    # svm_test(clf,0+gap*100,gap-1+gap*100,gap)
    # end = time.time()
    # print ("forth use time： "+str(end-start))

# 读6万行 各3万行
def readcsv2():
    attacklines = []
    with open(path+'attackid.csv','r') as f:
        for line in f:
            attacklines = line.split(",")
    attacklines.pop()

    X = []
    Y = []
    with open(path+'featuresid.csv','r') as f,open(path+'attackattack.csv','r') as f2:
        lines = csv.reader(f)
        lines2 = csv.reader(f2)
        for line in lines:    # line是一个数组 []
            X.append(np.array(line).astype(np.float64))
        for line in line2:  # line2是一个数组 []
            Y.append(np.int(line[1]))
    length = len(X)
    with open(path+feather_file,'r') as f,open(path+targets_file,'r') as f2:
        lines = csv.reader(f)
        lines2 = csv.reader(f2)
        n=0
        for line in lines:    # line是一个数组 []
            if line[0] not in attacklines:
                X.append(np.array(line).astype(np.float64))
                n+=1
            if n==length:
                break
        n=0
        for line in line2:  # line2是一个数组 []
            if line[0] not in attacklines:
                Y.append(np.int(line[1]))
                n+=1
            if n==length:
                break
    arr_file = np.array(X)
    data = arr_file[:,1:]
    return data,np.array(Y)

if __name__ == '__main__':
    main()

# ValueError: Unknown label type: 'continuous'  修改  y的值必须为int 不能为float
# ValueError: The number of classes has to be greater than one (python)   类型单一  y的类型只有0
