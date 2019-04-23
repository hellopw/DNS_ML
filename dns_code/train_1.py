#!/usr/bin/python
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
from sklearn.metrics import f1_score

from sklearn.neural_network import MLPClassifier

path='/home/hello/Documents/code/python/dns_data/csv/'
feather_file = 'features.csv'
feather_file2 = 'features2.csv'
targets_file = 'targets.csv'

# 读6万行 各3万行
def readcsv2():
    attacklines = []
    with open(path+'attackid.csv','r') as f:
        for line in f:
            attacklines = line.split(",")
    attacklines.pop()

    X = []
    Y = []
    with open(path+'featuresid.csv','r') as f:
        lines = csv.reader(f)
        for line in lines:    # line是一个数组 []
            X.append(np.array(line).astype(np.float64))
            Y.append(1)
    length = len(X)
    with open(path+feather_file,'r') as f,open(path+targets_file,'r') as f2:
        lines = csv.reader(f)
        lines2 = csv.reader(f2)
        n=0
        for line in itertools.islice(lines,1,None):    # line是一个数组 []
            if line[0] not in attacklines:
                X.append(np.array(line).astype(np.float64))
                n+=1
            if n==length:
                break
        n=0
        for line in itertools.islice(lines2,1,None):  # line2是一个数组 []
            if line[0] not in attacklines:
                Y.append(np.int(line[1]))
                n+=1
            if n==length:
                break
    arr_file = np.array(X)
    data = arr_file[:,1:]
    return data,np.array(Y)

def svm_train(clf,X,Y):

    #训练
    clf.fit(X,Y)

def svm_test(clf,X,Y):

    #预测
    y_hat = clf.predict(X) # predict the target of testing samples

    #准确率
    accury = clf.score(X, Y)
    print ("accury is : ",accury)

    #recall
    recall_macro = metrics.recall_score(Y, y_hat, average='macro')
    print ("recall_macro is : ",recall_macro)
    recall_micro = metrics.recall_score(Y, y_hat, average='micro')
    print ("recall_micro is : ",recall_micro)

    #roc值
    roc_value = roc_auc_score(Y, y_hat)
    print ("roc_auc_score is : ",roc_value)

    #查看auc值
    test_auc = metrics.roc_auc_score(Y, y_hat)#验证集上的auc值
    print ("AUC: ",test_auc)

    #查看f1
    test_f1_macro = f1_score(Y, y_hat, average='macro') 
    print ("f1 macro : ",test_f1_macro)
    test_f1_micro = f1_score(Y, y_hat, average='micro') 
    print ("f1 micro : ",test_f1_micro)
    test_f1_weight = f1_score(Y, y_hat, average='weighted') 
    print ("f1 weighted : ",test_f1_weight)
    test_f1_none = f1_score(Y, y_hat, average=None) 
    print ("f1 none : ",test_f1_none)
    
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
    print ("not right number is : ",str(number))
    print ("Y has 1 number is : ",str(number1))
    print ("result Y has 1 number is : ",str(number2))

def main():
    X, Y = readcsv2() 
    randnum = random.randint(0,len(X))   
    random.seed(randnum)
    random.shuffle(X)
    random.seed(randnum)
    random.shuffle(Y)
    x_train = X[0:30000]
    x_test = X[30001:39401]
    y_train = Y[0:30000]
    y_test = Y[30001:39401]
    # print ("\n  linear ")
    # clf4 = svm.SVC(C=0.3, kernel='linear', decision_function_shape='ovo')
    # clf4.fit(X[0:30000],Y[0:30000])
    # svm_test(clf4,X[30001:39401],Y[30001:39401])

    print (" \n rbf ")
    clf2 = svm.SVC(C=0.4, kernel='rbf',gamma=0.001,decision_function_shape='ovo')
    clf2.fit(x_train,y_train)
    svm_test(clf2,x_test,y_test)
    print (" \n rbf ")
    clf2 = svm.SVC(C=0.5, kernel='rbf',gamma=0.001,decision_function_shape='ovo')
    clf2.fit(x_train,y_train)
    svm_test(clf2,x_test,y_test)
    print (" \n rbf ")
    clf2 = svm.SVC(C=0.6, kernel='rbf',gamma=0.001,decision_function_shape='ovo')
    clf2.fit(x_train,y_train)
    svm_test(clf2,x_test,y_test)
    print (" \n rbf ")
    clf2 = svm.SVC(C=0.7, kernel='rbf',gamma=0.001,decision_function_shape='ovo')
    clf2.fit(x_train,y_train)
    svm_test(clf2,x_test,y_test)

    # print ("\n sigmoid ")
    # clf3 = svm.SVC(C=0.4, kernel='sigmoid', coef0=8,decision_function_shape='ovo')
    # clf3.fit(X[0:30000],Y[0:30000])
    # svm_test(clf3,X[30001:39401],Y[30001:39401])

    print ("\n mlp ")
    mlp = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(3, 1), random_state=1)
    mlp.fit(x_train, y_train)           
    print (mlp.score(x_test, y_test))
    print (mlp.n_layers_)
    print (mlp.n_iter_)
    print (mlp.loss_)
    print (mlp.out_activation_)

if __name__ == '__main__':
    main()