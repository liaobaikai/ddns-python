# -*- coding:utf-8 -*-

import time
import random
import base64
import urllib.parse
import urllib.request
import hmac
import hashlib
import json
import requests
import logging
import requests
import os
import psycopg2


conn = psycopg2.connect(database="test", user="baikai", password="baikai#1234",
                                                host="localhost",
                                                port="5432")
print("Opened database successfully.")

def getIPAddress(iplink_ip, password):

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': iplink_ip,
        'Origin': 'http://%s' % iplink_ip,
        'Referer': 'http://%s/' % iplink_ip,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    loginResult = requests.post(url='http://%s' % iplink_ip, headers=headers,
                                data=('{"method":"do","login":{"password":"%s"}}' % password))

    result = json.loads(loginResult.text)

    #
    ds_page = requests.post('http://%s/stok=%s/ds' % (iplink_ip, result['stok']), headers=headers,
                            data='{"protocol":{"name":["wan","pppoe"]},"network":{"name":["wan_status","iface_mac"]},"method":"get"}')

    result = json.loads(ds_page.text)
    ipaddr = result['network']['wan_status']['ipaddr']

    return ipaddr


def execute():

        logging.captureWarnings(True)
        #
        # with open('run.log', 'w+') as f:
        #       f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        #
        #
        #result = requests.get('https://10000.gd.cn/getClientIP.php', verify=False)
        #result.encoding = result.apparent_encoding
        ip = getIPAddress('192.168.3.1', 'rH8w2PAULe9fbwK')
        #ip = result.text
        #import socket
        #ip = socket.getaddrinfo('termjs.tpddns.cn', 'http')[0][4][0]
        #resp = requests.post('https://n-wap.tplinkcloud.com.cn//?token=34782b28-3e183a6189ff49b18a4d8fa', json={"method":"passthrough","params":{"deviceId":"000008BB150BEB39C12DEF1923329EE61B56847B","requestData":{"method":"get","network":{"name":"wan_status"}}}}, verify=False)
        #ip=json.loads(resp.text)['result']['responseData']['network']['wan_status']['ipaddr']
        print(ip)
        cache_ip = ''

        ip_file = 'C:/Users/baikai/PycharmProjects/ddbs-python/logs/public-ip.txt'
        try:
                f = open(ip_file, 'r')
                cache_ip = f.read()
        except(IOError):
                f = open(ip_file, 'w+')
                cache_ip = ''
        finally:
                if f:
                        f.close()

        if ip == cache_ip:

                cur = conn.cursor()
                cur.execute("insert into ddns_info (request_time, ip) "
                            "values (now(), '{}')".format(ip))
                conn.commit()
                #print('%s : IP[%s] is not change...' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ip))
        else:
                f = open(ip_file, 'w');
                f.write(ip)
                f.close()

                secretId = 'AKIDugBVrqNJn1yeKkkTRBgYzA4h2MXLlgU0'
                secretKey = 'QKyxhGk266IgsoS5i4bsGdmFUewc8e8S'
                api = 'cns.api.qcloud.com/v2/index.php'

                def updateDNS(domain, subDomain, recordType, ttl, recordId):
                        timestamp = int(time.time())
                        notice = random.randint(1000, 1000000)
                        print(notice)
                        recordLine = '默认'
                        params = '&'.join(sorted(
                                         'SecretId={0}' \
                                         '&Region=ap-guangzhou' \
                                         '&Timestamp={1}' \
                                         '&Nonce={2}' \
                                         '&SignatureMethod=HmacSHA256' \
                                         '&Action=RecordModify' \
                                         '&domain={3}' \
                                         '&subDomain={4}' \
                                         '&recordType={5}' \
                                         '&recordLine={6}' \
                                         '&ttl={7}' \
                                         '&value={8}'
                                         '&recordId={9}'.format(secretId, timestamp, notice, domain,
                                                                         subDomain, recordType, recordLine, ttl, ip, recordId).split('&')))

                        url = '{0}{1}?{2}'.format('GET', api, params)
                        j = hmac.new(secretKey.encode(), digestmod=hashlib.sha256)
                        j.update(url.encode())
                        encode = base64.b64encode(j.digest())

                        signature = urllib.parse.quote(encode)
                        url = 'https://{0}?{1}&Signature={2}'.format(api, params, signature)

                        r = requests.get(url)
                        r.encoding = "utf-8"
                        #print(r, r.text)
                        data = json.loads(r.text)
                        print(data)

                        cur = conn.cursor()
                        cur.execute("insert into ddns_info (request_time, ip, domain, sub_domain) "
                                    "values (now(), '{}', '{}', '{}')".format(ip, domain, subDomain))
                        conn.commit()
                        # if data['code'] != 0:
                        #    #print('update fail...')
                        #
                        # else:
                        #       print('%s.%s ok.' % (subDomain, domain))


                #print('%s : IP[%s] begin update...' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ip))
                updateDNS('baikai.top', 'a', 'A', 600, 411999847)
                updateDNS('baikai.top', 'www', 'A', 600, 412002164)
                updateDNS('baikai.top', 'mirrors', 'A', 600, 412165820)
                updateDNS('baikai.top', 'mail', 'A', 600, 412165854)
                updateDNS('baikai.top', 'termjs', 'A', 600, 413928106)
                updateDNS('baikai.top', '@', 'A', 600, 416693961)
                updateDNS('baikai.top', 'term', 'A', 600, 416695319)
                updateDNS('baikai.top', 'term-channel', 'A', 600, 416695767)
                updateDNS('baikai.top', 'channel.term', 'A', 600, 416696074)
                updateDNS('baikai.top', 'bridge.term', 'A', 600, 417973904)

                updateDNS('liaobaikai.com', 'www', 'A', 600, 434250421)
                updateDNS('liaobaikai.com', '@', 'A', 600, 434250430)
                updateDNS('liaobaikai.com', '*', 'A', 600, 434250444)
                #print('%s : IP[%s] updated.' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ip))




if __name__ == '__main__':
        execute()
