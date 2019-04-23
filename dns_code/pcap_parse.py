#!/usr/bin/python
#coding = utf-8
import struct
import dpkt
import sys
import socket
import binascii

DNS_Q = 0
DNS_R = 1

# Opcodes
DNS_QUERY = 0
DNS_IQUERY = 1
DNS_STATUS = 2
DNS_NOTIFY = 4
DNS_UPDATE = 5

# Flags
DNS_CD = 0x0010 # checking disabled
DNS_AD = 0x0020 # authenticated data
DNS_Z =  0x0040 # unused
DNS_RA = 0x0080 # recursion available
DNS_RD = 0x0100 # recursion desired
DNS_TC = 0x0200 # truncated
DNS_AA = 0x0400 # authoritative answer

# Response codes
DNS_RCODE_NOERR = 0
DNS_RCODE_FORMERR = 1
DNS_RCODE_SERVFAIL = 2
DNS_RCODE_NXDOMAIN = 3
DNS_RCODE_NOTIMP = 4
DNS_RCODE_REFUSED = 5
DNS_RCODE_YXDOMAIN = 6
DNS_RCODE_YXRRSET = 7
DNS_RCODE_NXRRSET = 8
DNS_RCODE_NOTAUTH = 9
DNS_RCODE_NOTZONE = 10

# RR types
DNS_A = 1
DNS_NS = 2
DNS_CNAME = 5
DNS_SOA = 6
DNS_PTR = 12
DNS_HINFO = 13
DNS_MX = 15
DNS_TXT = 16
DNS_AAAA = 28
DNS_SRV = 33

# RR classes
DNS_IN = 1
DNS_CHAOS = 3
DNS_HESIOD = 4
DNS_ANY = 255

def addr2str(addrobj):
    if len(addrobj) != 4:
        return "addr error!"
    else:
        return str(ord(addrobj[0]))+"."+str(ord(addrobj[1]))+"."+str(ord(addrobj[2]))+"."+str(ord(addrobj[3]))

def TCPorUDP(obj):
    if (ord(obj) == 0x01):
        return "ICMP"
    elif (ord(obj) == 0x02):
        return "IGMP"
    elif (ord(obj) == 0x06):
        return "TCP"
    elif (ord(obj) == 0x08):
        return "EGP"
    elif (ord(obj) == 0x09):
        return "IGP"
    elif (ord(obj) == 0x11):
        return "UDP"
    elif (ord(obj) == 41):
        return "IPv6"
    elif (ord(obj) == 89):
        return "OSPF"
    else:
        return "error"

def dns_response_body_parse(body):        # parse the response message's body
    identification = body[0:2]
    flag = body[2:4]
    num_ques = body[4:6]
    num_ans_RR = body[6:8]
    num_auth_RR = body[8:10]
    num_addi_RR = body[10:12]
    query_name = ''
    ans_ip = []
    flag = 12
    while(ord(body[flag])!=0x0):
        query_name = query_name + body[flag+1:flag+ord(body[flag])+1]
        flag = flag + ord(body[flag]) + 1
        try:
            if ord(body[flag]) != 0x0:
                query_name = query_name+'.'
        except Exception as e:
            print ("error when parse query domain name")
    #print query_name
    flag = flag + 1
    query_type = ord(body[flag])*256 + ord(body[flag+1])
    if query_type == 0x01:            # use domain query IP addr
        flag = flag + 4
        i = 1
        answer_num = ord(num_ans_RR[0])*256 + ord(num_ans_RR[1])
        while(i<=answer_num):
            if ord(body[flag]) == 0xc0:
                flag = flag + 2
            else:
                while(ord(body[flag])!=0x0):
                    flag = flag + ord(body[flag]) + 1
                flag = flag + 1
            if (    ord(body[flag])*256+ord(body[flag+1]) == DNS_A 
                and ord(body[flag+2])*256+ord(body[flag+3]) == DNS_IN):
                flag = flag + 8
                RR_data_len = ord(body[flag])*256 + ord(body[flag+1])
                if RR_data_len == 4:
                    ans_ip.append(addr2str(body[flag+2:flag+6]))
                flag = flag + ord(body[flag])*256 + ord(body[flag+1]) + 2
            else:
                flag = flag + 8
                flag = flag + ord(body[flag])*256 + ord(body[flag+1]) + 2
            i = i + 1
    else:
        print ("query type is PTR not A")
        return
    return "%s\t%s"%(query_name,ans_ip)

def main():
    # paralen = len(sys.argv)
    # if paralen != 3:
    #     print ("there is only %d parameter, %s"%(paralen,sys.argv))
    #     print "no enough parameter!"
    #     print "command should be: python *.py result.txt src_pcap_file.pcap"
    #     return
    # print "parse result will write to:"+sys.argv[1]
    # print "strat parse the pcap file:"+sys.argv[2]
    # fw = open(sys.argv[1],"w")
    # f = file(sys.argv[2],"rb")

    f = open("/home/hello/Documents/code/python/dns_data/dns_q1/q1_final.pcap","rb")
    pcap = dpkt.pcap.Reader(f)
    print type(pcap)
    for ts,buf in pcap:
        
        #fw.writelines("timestamp:"+str(ts)+"\tpacket len:"+str(len(buf))+"\n")
        ethheader = buf[0:14]
        dstmac = ethheader[0:6]
        srcmac = ethheader[6:12]
        netlayer_type = ethheader[12:14]
        #fw.writelines("dstMAC:"+str(binascii.b2a_hex(dstmac))+"\tsrcMAC:"+str(binascii.b2a_hex(srcmac))+"\n")

        pktheader = buf[14:34]
        trans_type = pktheader[9]
        srcip = pktheader[12:16]
        dstip = pktheader[16:20]

        #fw.writelines("dstIP:"+addr2str(dstip)+"\tsrcIP:"+addr2str(srcip)+"\n")
        #fw.writelines("packet type:"+TCPorUDP(trans_type)+"\n")

        if (ord(trans_type) == 0x11):     #UDP
        # if (hex(trans_type) == '0x11'):     #UDP
            udpheader = buf[34:42]
            srcport = udpheader[0:2]
            dstport = udpheader[2:4]
            udplen = udpheader[4:6]
            #fw.writelines("srcport:"+str(ord(srcport[1])+ord(srcport[0])*16*16)+"\tdstport:"+str(ord(dstport[1])+ord(dstport[0])*16*16)+"\n\n")
            bodylen = ord(udplen[0])*256+ord(udplen[1])-8
            print ("\ndns body length is "+str(bodylen))
            dnsbody = buf[42:(42+bodylen)]
            if (ord(dstport[0]) == 0x00 and ord(dstport[1]) == 0x35):
                print ("this is a DNS Request")
            elif (ord(srcport[0]) == 0x00 and ord(srcport[1]) == 0x35):
                print ("this is a DNS Response")
                print (dns_response_body_parse(dnsbody))
                # fw.writelines(dns_response_body_parse(dnsbody)+"\n")    # wirte result to file
            else:
                print (ord(srcport[0]),ord(srcport[0]))
        elif (ord(trans_type) == 0x06):     #TCP
            tcpheader = buf[34:54]
            srcport = tcpheader[0:2]
            dstport = tcpheader[2:4]
            #fw.writelines("srcport:"+str(ord(srcport[1])+ord(srcport[0])*16*16)+"\tdstport:"+str(ord(dstport[1])+ord(dstport[0])*16*16)+"\n\n")
    f.close()
    print ("process %s has finished, the result was in file %s"%(sys.argv[2],sys.argv[1]))
if __name__ == "__main__":
    main()