#! /usr/bin/env python
# -*- coding: gbk -*-
import curses
import sinaapi
import time

class UIclient(object):
    """docstring for UIclient"""
    def __init__(self):
        self.api = sinaapi.APIClient()
        self.menus = self.api.get_menus()
        self.col_list = self.api.col_list
        self.stdscr = curses.initscr()
        self.set_win()

    def set_win(self):
        self.stdscr.keypad(1)
        #ʹ����ɫ������Ҫ�����������
        curses.start_color()
        #���ֺͱ���ɫ���ã�����������color pair���ֱ�Ϊ1��2��3
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        #�ر���Ļ����
        curses.noecho()
        #����ʱ����Ҫ�س�ȷ��
        curses.cbreak()
        #����nodelay��ʹ�ÿ���̨�����Է������ķ�ʽ���ܿ���̨���룬��ʱ1��
        self.stdscr.nodelay(1)

    def unset_win(self):
        '''����̨����'''
        self.stdscr.keypad(0)
        #�ָ�����̨Ĭ�����ã������ָ����ᵼ�¼�ʹ��������˳��ˣ�����̨��Ȼ��û�л��Եģ�
        curses.nocbreak()
        curses.echo()
        #��������
        curses.endwin()

    def display_info(self, str, x, y, colorpair=1):
        '''ʹ��ָ����colorpair��ʾ����'''
        '''x, y ��ʾ��ʼ����'''
        self.stdscr.addstr(y, x, str, curses.color_pair(colorpair))
        self.stdscr.refresh()

    def get_ch_and_continue(self):
        '''��ʾpress any key to continue'''
        #����nodelay��Ϊ0ʱ��������ʽ�ȴ�
        self.stdscr.nodelay(0)
        #����һ���ַ�
        ch=self.stdscr.getch()
        #����nodelay��ʹ�ÿ���̨�����Է������ķ�ʽ���ܿ���̨���룬��ʱ1��
        self.stdscr.nodelay(1)
        return ch

    def show_menu(self):
        self.display_info('�й����򳬼���������ֱ��',25,0,2)
        string = "���   "
        for i in range(len(self.col_list)):
            string += str(self.col_list[i]) + "   "
        self.display_info(string+"\n",0,1,1)
        t = 2
        for i in range(len(self.menus)):
            string = str(i)+"    "
            for j in range(len(self.menus[i])-3):
                string += str(self.menus[i][j]) + "   "
            self.display_info(string+"\n",0,2+i,1)
            t += 1
        self.display_info("������������:",0,t,3)
        ch = self.get_ch_and_continue()
        self.show_live(ch)

    def show_header(self):
        match = self.api.avail_matches[self.api.match_id]
        title = match[3] + '   '+ match[4] + '   '+ match[5] + '\t'
        title += str(time.strftime('%Y-%m-%d %H:%M:%S'))
        self.display_info(title,20,0,2)
        self.display_info('״̬',0,1,3)
        self.display_info('ʱ��',8,1,3)
        self.display_info('�ȷ�',15,1,2)
        self.display_info('ʵ��',22,1,1)

    def show_live(self, ch):
        self.api.set_match_id(int(ch)-ord('0'))
        while True:
            lines = self.api.get_messages(5)
            key = self.stdscr.getch()
            if key == ord('q'):
                self.stdscr.erase()
                break
            self.stdscr.erase()
            if lines:
                self.show_header()
                y = 2
                for item in lines:
                    self.display_info(item['s'],0,y,3)
                    self.display_info(str(item['t']) if str(item['t']) else '0' ,8,y,3)
                    self.display_info(item['s1']+'-'+item['s2'],15,y,2)
                    item['m']=item['m'].decode('gbk','ignore')
                    num = len(item['m'])
                    p = 0
                    step = 27
                    while p < num:
                        substr = item['m'][p:((p+step) if (p+step<num) else (num-1))]
                        substr = substr.encode('gbk','ignore')
                        self.display_info(substr,22,y,1)
                        p += step
                        y += 1
                    y += 1
                self.display_info('����q�˳�',0,y,2)
                self.stdscr.refresh()
            else:
                if lines is None:
                    self.stdscr.addstr(0, 20, '�����ѽ���', 2)
                    self.stdscr.refresh()
            time.sleep(1)

if __name__=='__main__':
    ui = UIclient()
    ui.show_menu()
    ui.unset_win()