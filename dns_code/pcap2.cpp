#include <stdio.h>
#include <stdlib.h>
#include <pcap.h>
#include <netinet/in.h>
#include <time.h>
#include <string.h>

#define DNSPORT 53

/* 4字节的IP地址 */
typedef struct ip_address
{
    u_char byte1;
    u_char byte2;
    u_char byte3;
    u_char byte4;
} ip_address;
ip_address myipaddr;

/* IPv4 首部 */
typedef struct ip_header
{
    u_char ver_ihl;         // 版本 (4 bits) + 首部长度 (4 bits)
    u_char tos;             // 服务类型(Type of service)
    u_short tlen;           // 总长(Total length)
    u_short identification; // 标识(Identification)
    u_short flags_fo;       // 标志位(Flags) (3 bits) + 段偏移量(Fragment offset) (13 bits)
    u_char ttl;             // 存活时间(Time to live)
    u_char proto;           // 协议(Protocol)
    u_short crc;            // 首部校验和(Header checksum)
    ip_address saddr;       // 源地址(Source address)
    ip_address daddr;       // 目的地址(Destination address)
    u_int op_pad;           // 选项与填充(Option + Padding)
} ip_header;

/* UDP 首部 ...u_char占一个字节，u_short占2个字节*/
typedef struct udp_header
{
    u_short sport; // 源端口(Source port)
    u_short dport; // 目的端口(Destination port)
    u_short len;   // UDP数据包长度(Datagram length)
    u_short crc;   // 校验和(Checksum)
} udp_header;

/*dns 包（头+数据）*/
typedef struct dns_packet //报文head+data
{
    u_short id;    //每一个占2个字节，共12个字节
    u_short flags; //标志第一个为0代表查询报文
    u_short ques;
    u_short answer;
    u_short author;
    u_short addition;
    u_char dns_data; //查询问题部分
} dns_packet;

typedef struct DNS_HEADER
{
    unsigned short id; // identification number

    unsigned char rd : 1;     // recursion desired
    unsigned char tc : 1;     // truncated message
    unsigned char aa : 1;     // authoritive answer
    unsigned char opcode : 4; // purpose of message
    unsigned char qr : 1;     // query/response flag

    unsigned char rcode : 4; // response code
    unsigned char cd : 1;    // checking disabled
    unsigned char ad : 1;    // authenticated data
    unsigned char z : 1;     // its z! reserved
    unsigned char ra : 1;    // recursion available

    unsigned short q_count;    // number of question entries
    unsigned short ans_count;  // number of answer entries
    unsigned short auth_count; // number of authority entries
    unsigned short add_count;  // number of resource entries
} dns_header;

typedef struct QUERY
{
    unsigned char *name;
    unsigned short qtype;
    unsigned short qclass;
} query;

typedef struct RESPONSE
{
    unsigned char *name;
    unsigned short rtype;
    unsigned short rclass; 
    unsigned int ttl;   //time to live
    unsigned short dl;  //data length
    unsigned char *rdata;
} query;

void packet_handler(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data);

int main()
{
    char ebuf[PCAP_ERRBUF_SIZE];
    // const char *pcap_file = "/home/hello/Documents/code/python/dns_data/dns_q1/q1_final.pcap.back";
    const char *pcap_file = "/home/hello/Documents/code/python/dns_data/dns_q1/q1_final.pcap";
    pcap_t *p = pcap_open_offline(pcap_file, ebuf);
    struct pcap_pkthdr pkthdr;
    while (1)
    {
        const u_char *pktStr = pcap_next(p, &pkthdr);
        if (!pktStr)
        {
            printf("Pcap file parse over !\n");
            break;
        }
        else
        {
            packet_handler(NULL, &pkthdr, pktStr);
        }
        printf("Length: %d\n", pkthdr.len);
    }
    pcap_close(p);
    return 0;
}

void packet_handler(u_char *param, const struct pcap_pkthdr *header, const u_char *pkt_data)
{
    struct tm *ltime; //定义时间
    char timestr[16];
    ip_header *ih;
    udp_header *uh;
    u_int ip_len;
    u_short sport, dport;
    time_t local_tv_sec;

    /* 将时间戳转换成可识别的格式 */ //....二进制转换....
    local_tv_sec = header->ts.tv_sec;
    ltime = localtime(&local_tv_sec);
    strftime(timestr, sizeof timestr, "%H:%M:%S", ltime);

    /* 打印数据包的时间戳和长度 */
    //printf("%s.%.2d / len:%d /", timestr, header->ts.tv_usec, header->len); //..........显示时间和数据包长度..........显示2

    /* 获得IP数据包头部的位置 */
    ih = (ip_header *)(pkt_data + 14); //14是以太网头部长度

    /* 获得UDP首部的位置 */
    uh = (udp_header *)(pkt_data + 14+20); //20是ip的头长度

    /* 将网络字节序列转换成主机字节序列 */
    sport = ntohs(uh->sport);
    dport = ntohs(uh->dport);

    /* 打印IP地址和UDP端口 */
    printf(" %d.%d.%d.%d:%d -> %d.%d.%d.%d:%d\n",
           ih->saddr.byte1,
           ih->saddr.byte2,
           ih->saddr.byte3,
           ih->saddr.byte4,
           sport,
           ih->daddr.byte1,
           ih->daddr.byte2,
           ih->daddr.byte3,
           ih->daddr.byte4,
           dport);

    // 整个DNS包
    struct dns_packet *pdns;
    pdns = (struct dns_packet *)(pkt_data+14+20+8); // sport+dport+length+checksum,DNS头指针
    u_char *query=&(pdns->dns_data);//定位到查询部分头部
    printf("id is : %x\n",pdns->id);
    printf("flags is : %x\n",pdns->flags);
    printf("ques is : %x\n",pdns->ques);
    printf("answer is : %x\n",pdns->answer);
    printf("author is : %x\n",pdns->author);
    printf("addition is : %x\n",pdns->addition);
    // printf("dns_data is : %x\n",pdns->dns_data);

          //03 77 77 77 05 61 70 70 6c 65 03 63 6f 6d 00
    //指明长度   w  w  w     a  p  p  l  e     c  o  m  结束符
    int len=0;
    char domainname[64];    //64可能有点小暂时先用着
    query++;    //第一个.不要
    while(*query){
    	if(*query < 0x10)//48以后出现数字和英文字母  域名最大长度就是16
    	{
    		domainname[len]='.';    //小于16的一般是长度字段，刚好可以用.填充
    	}
    	else
    	{
    		domainname[len]=*query;
    	}
        query++;
        len++;   //求name的长度
    }

    
    

    // qu = (struct QUERY *)(pkt_data + 14 + 20 + 8 + 12);  //12是DNS的头长
    // qu->name = (pkt_data + 14 + 20 + 8 + 12);
    // qu->qclass = (pkt_data + 14 + 20 + 8 + 12 + i);


    struct RESPONSE *response;
    response = (struct RESPONSE *)(pkt_data + 14 + 20 + 8 + 12 + (i+4)); //i+4是query字段的长度


    // DNS 头
    struct DNS_HEADER *dns_h;
    dns_h = (struct DNS_HEADER *)(pkt_data + 14 + 20 + 8);  //8是udp头长
    printf("%x\n", dns_h->id);
    printf("%x\n", dns_h->rcode);



    // int len = sizeof(struct DNS_HEADER);
    // struct QUERY *query;
    // // query = (struct QUERY *)(pkt_data+34+8+sizeof(struct DNS_HEADER)+strlen((const char*)question));
    // query = (struct QUERY *)(pkt_data + 14 + 20 + 8 + len);
    // printf("query is : %s\n", query->name );
    // printf("query is : %x\n", query->ques->qtype);
    // printf("query is : %x\n", query->ques->qclass);

    printf("QueryDomain=");
    u_char domainname[64]={0};   //域名的最大长度是64位
    u_int i=0;
    query++;//把点去了
    while(*query)
    {
    	if(*query < 0x10)//48以后出现数字和英文字母
    	{
    		domainname[i]='.';
    	}
    	else
    	{
    		domainname[i]=*query;
    	}

    	query++;
    	i++;
    }
    printf("domainname is : %s\n",domainname);

    // //.....写入文本
    // FILE *fp;
    // fp=fopen("dns.txt","a");
    // while(fp != NULL)
    // {
    // 	fprintf(fp,"%d.%d.%d.%d:%d -> %d.%d.%d.%d:%d\t%s\n",ih->saddr.byte1,
    // 		ih->saddr.byte2,
    // 		ih->saddr.byte3,
    // 		ih->saddr.byte4,
    // 		sport,

    // 		ih->daddr.byte1,
    // 		ih->daddr.byte2,
    // 		ih->daddr.byte3,
    // 		ih->daddr.byte4,
    // 		dport,domainname);
    // 	break;
    // }
    // printf("READ ALL INTO FILE OK\n");
    // fclose (fp);
}
