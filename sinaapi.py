#coding=gbk
import json
import urllib
import urllib2
from lxml import html
import re
import time


class APIClient(object):

    def __init__(self):
        self.menu_url = r'https://www.baidu.com/baidu?tn=monline_6_dg&ie=utf-8&wd=%E4%B8%AD%E8%B6%85'
        self.basic_url = 'http://g.hupu.com/nba/homepage/getMatchBasicInfo?matchId={0}'
        self.live_url = ('http://g.hupu.com/node/playbyplay/matchLives?'
                's_count={0}&match_id={1}&homeTeamName={2}&awayTeamName={3}'
                )
        self.avail_matches = []
        self.match_id = 0
        self.last_sid = 0
        self.home_team = ''
        self.away_team = ''
        self.match_info = []

    def init_match(self, idx):
        self.match_id = self.avail_matches[idx]
        self.last_sid = 0
        self.set_basic()

    def get_menus(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'} 
        req = urllib2.Request(self.menu_url, headers=headers) 
        text = urllib2.urlopen(req).read()
        text = text.decode('utf8','ignore')
        tree = html.fromstring(text)
        #print tree

        match_list = tree.xpath('//*[@id="1"]')
        table_csl = match_list[0].xpath('./div[1]/div[1]/table')[0]
        self.col_list = []
        for i in range(5):
            self.col_list.append(table_csl[0].xpath('./th')[i].text_content().encode('gbk','ignore'))
        self.avail_matches = []
        self.match_info = []
        menu_list = []
        for i in range(1,len(table_csl)):
            #print i
            item = []
            for j in range(8):
                item.append(table_csl[i].xpath('./td')[j].text_content().strip().encode('gbk','ignore'))
            url_table = table_csl[i].xpath('./td[8]/a')
            if len(url_table) != 0:
                url = url_table[0].get('href').strip()
            else:
                url = None
                self.match_info.append({})
            item.append(url)
            self.avail_matches.append(item)
            menu_list.append(item)
            #count = 0
            while url:
                #print url
                text = urllib2.urlopen(url=url, timeout=8).read()
                pattern = re.compile(r"\sappkey : (.+),\s+appflag : '(.+)',\s+appid : (.+),\s+liverid : '(.+)',\s+mid : '(.+)',\s+lid : '(.+)',\s+rnd : '(.+)',")
                match_key = pattern.search(text)
                #print url
                if match_key:
                    match_info_item = {}
                    match_info_item['appkey'] = match_key.group(1)
                    match_info_item['appflag'] = match_key.group(2)
                    match_info_item['appid'] = match_key.group(3)
                    match_info_item['liverid'] = match_key.group(4)
                    match_info_item['mid'] = match_key.group(5)
                    match_info_item['lid'] = match_key.group(6)
                    match_info_item['rnd'] = match_key.group(7)
                    self.match_info.append(match_info_item)
                    break
                else:
                    pattern = re.compile(r"var id = (.+);\s")
                    match_key = pattern.search(text)
                    if match_key:
                        url = "http://match.sports.sina.com.cn/livecast/n/live.php?id=%s&dpc=1&sina-fr=360.ala.zc.sc&dpc=1" % match_key.group(1)
                    else:
                        self.match_info.append({})
                        break
                    #time.sleep(1)

           
        return menu_list

    def set_match_id(self, id):
        self.match_id = id

    def decode_messages(self, text):
        ss=json.loads(text)
        #string=ss['result']['data'][0]['s'].encode('gbk', 'ignore')
        #print ss['result']['data'][0]['m'].encode('gbk', 'ignore')
        #id":"4833307","s1":"2","s2":"2","s":"\u4e0b","t":"40'",
        data = ss['result']['data']
        msg = []
        for i in range(len(data)):
            item = {}
            item['id'] = data[i]['id']
            item['s1'] = data[i]['s1']
            item['s2'] = data[i]['s2']
            item['t'] = data[i]['t']
            item['s'] = data[i]['s'].encode('gbk', 'ignore')
            item['m'] = data[i]['m'].encode('gbk', 'ignore')
            msg.append(item)
        return msg

    def get_messages(self, n=1):
        info = self.match_info[self.match_id]
        if len(info)==0:
            print "game is over"
            return None
        args = (info['appkey'], info['mid'], n)
        #print args
        url = "http://platform.sina.com.cn/sports_all/client_api?app_key=%s&_sport_t_=livecast&_sport_a_=livelog&id=%s&nolink=0&order=1&num=%d&orderid=0" % args
        try:
            r = urllib2.urlopen(url)
            #print url
            text = r.read().decode('utf8', 'ignore')
            msg_list = self.decode_messages(text)
        except Exception as e:
            return []

        #print msg_list
        return msg_list


if __name__ == '__main__':
    api = APIClient()
    api.get_menus()
    api.set_match_id(5)
    msg = api.get_messages(n=2)
    print msg[0]['m']
    print msg[1]['m']
    
