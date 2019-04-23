import csv

path='/home/hello/Documents/code/python/dns_data/csv/'
feather_file = 'features.csv'
feather_file2 = 'features2.csv'
targets_file = 'targets.csv'

#统计1的行数，写入另一个文件
def kk():
    with open(path+'attackid.csv','a+') as f,open(path+targets_file,'r') as f2:
        lines2 = csv.reader(f2)
        # writer = csv.writer(f)
        count0 = 0 
        count1 = 0
        count2 = 0
        for line in lines2:
            if line[1]=='1':
                # writer.writerow(line)
                f.write(line[0]+',')
                count1+=1
            elif line[1]=='0':
                count0+=1
            else:
                count2+=1
        print (count0)
        print (count1)
        print (count2)

# alert中统计类别数
def ll(): 
    se = set()
    with open('/home/hello/Documents/code/python/dns_data/alert/alert','r') as f:
        for line in f:
            if "Classification" in line:
                se.add(line.split("]")[0].split(": ")[-1])
        for x in se:
            print (x)

# 统计数据集中1的包的id
def readid():
    x = []
    with open(path+'attackid.csv','r') as f:
        for line in f:
            x = line.split(",")
    x.pop()
    return x

def rewrite():
    x = readid()
    with open(path+feather_file,'r') as f,open(path+'featuresid2.csv','a+') as f2:
        lines = csv.reader(f)
        writer = csv.writer(f2)
        for line in lines:    # line是一个数组 []
            if line[0] in x:
                writer.writerow(line)

rewrite()


