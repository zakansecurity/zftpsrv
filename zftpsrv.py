#!/usr/bin/env python
# coding: utf-8
#===

'''
    Author : K. BEKKOUCHE
    Description : Simple FTP Server for Hacking.
    Site : http://www.zakansecurity.com
    Date : 17/06/2016
    Version : 1.0

'''

#==================================================================================================

import os
import socket
import threading
import time
import sys
import re
from optparse import OptionParser
from termcolor import colored
#import traceback

#==================================================================================================
class ZFTPSRV(threading.Thread):

    #===
    def __init__(self, (conn, addr), ip, user, pwd, homedir, whitelist_ip):

        self.ip = ip
        self.user = user
        self.pwd = pwd
        self.homedir = homedir
        self.whitelist_ip = whitelist_ip

        self.cwd=self.homedir
    
        self.conn=conn
        self.addr=addr
        self.datasrvsock = None
        self.datasock = None

        self.typemode = None
        self.pasvmode = None



        if addr[0] not in whitelist_ip.split(','):

            self.conn.send('The ftp server isn\'t in the scope ! Try Harder !\r\n')
            self.conn.close()

            print colored ("[-] FAIL : Access from unauthorized ip! Check the whitelist IP : %s." % (self.whitelist_ip), 'red')
            sys.exit(1)

        threading.Thread.__init__(self)

    #===
    def run(self):

        self.conn.send('220 Z FTP Server 1.0 (by ZAKAN Security)!\r\n')

        user = None
        pwd = None

        while True:

            try:

                cmd=self.conn.recv(256)

            except:

                if self.conn: self.conn.close()
                if self.datasrvsock: self.datasrvsock.close()
                if self.datasock: self.datasock.close()
                print colored ( "[-] FAIL : Connection is closed.", 'red')
                sys.exit(1)



            if not cmd: break

            else:

                try:

                    cmd = re.sub(' +', ' ', cmd)
                    func = getattr (self, cmd.split(' ')[0].strip().upper())

                    if cmd.split(' ')[0].upper() == 'USER': user = func (cmd)
                    elif cmd.split(' ')[0].upper() == 'PASS': 

                        pwd = func (re.sub(' +', ' ', cmd))

                        if self.user == user and self.pwd == pwd: self.conn.send( '230 User %s logged in\r\n' % user)
                        else: self.conn.send( '530 Login failed.\r\n' )

                    else: 
                        if self.user == user and self.pwd == pwd:
                            func (re.sub(' +', ' ', cmd))
                        else:
                            self.conn.send( '500 Not logged in.\r\n' )

                except Exception,err:

                    print colored("[-] FAIL : Requested Command isn\'t implemented yet !' : %s, ERROR = %s." % (cmd, err), 'red')
                    self.conn.send('500 Requested Command isn\'t implemented yet !\r\n')
                    #traceback.print_exc()

    #===
    def USER(self, cmd):
        
        self.conn.send( '331 Password required for %s' % cmd.split(' ')[1] )
        print ("[*] %s" % (cmd.strip()))
        return cmd.split(' ')[1].strip()

    #===
    def PASS(self, cmd):

        print ("[*] %s" % (cmd.strip()))
        return cmd.split(' ')[1].strip()

    #===
    def SYST(self, cmd):

        self.conn.send('215 UNIX Type: L8\r\n')
        print ("[*] %s" % (cmd.strip()))

    #===
    def QUIT(self, cmd):

        print ("[*] %s" % (cmd.strip()))
        
        self.conn.send('221 Goodbye.\r\n')
        
        if self.datasock : self.datasock.close()
        if self.datasrvsock : self.datasrvsock.close()
        #self.conn.close()

    #===
    def ABORT(self, cmd):

        print ("[*] %s" % (cmd.strip()))
        
        self.conn.send('221 Goodbye.\r\n')
        
        if self.datasock : self.datasock.close()
        if self.datasrvsock : self.datasrvsock.close()
        #self.conn.close()

    #===
    def CWD(self, cmd):

        print ("[*] %s" % (cmd.strip()))

        chwd = cmd.split(' ')[1].strip()

        if chwd[len(chwd) - 1] == '/': chwd = chwd[:len(chwd) - 1]

        if chwd == '/' or re.search (':', chwd): self.cwd = self.homedir
        elif chwd[0] == '/': self.cwd = os.path.join(self.homedir, chwd[1:])
        else: self.cwd = os.path.join(self.cwd, chwd)


        if not os.path.exists(self.cwd): self.cwd = self.homedir

        if self.homedir == self.cwd[:len(self.homedir)] :
            
            os.chdir(self.cwd)
            self.conn.send('250 CWD command successful.\r\n')
            print ("[*] CWD %s" % (self.cwd))

        else: self.conn.send('500 CWD failed.\r\n')

        print ("[*] Current Dir :  %s" % (self.cwd))



    #===
    def PWD(self, cmd):

        cwd = os.path.relpath(self.cwd,self.homedir)
    
        if cwd == '.': retcwd = '/'
        else: retcwd = '/' + cwd

        print ("[*] PWD\n%s" % (retcwd))
        self.conn.send('257 \"%s\"\r\n' % retcwd)

    #===
    def PASV(self, cmd): 

        print ("[*] %s" % (cmd.strip()))

        self.pasvmode = True
        self.datasrvsock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasrvsock.bind((self.ip,0))
        self.datasrvsock.listen(1)

        ip, port = self.datasrvsock.getsockname()

        print ("[*] Entering Passive Mode (%s, %s)" % (ip, port))
        self.conn.send('227 Entering Passive Mode (%s,%u,%u).\r\n' % (','.join(ip.split('.')), port>>8&0xFF, port&0xFF))

    #===
    def PORT(self, cmd): 

        print ("[*] %s" % (cmd.strip()))
        
        self.conn.send('500 YOU SHOULD USE PASSIVE MODE.\r\n')
        print colored ("[-] Passive Mode isn\'t enabled, asking to set it.", 'red')

        self.conn.send('227 Entering Passive Mode (%s,%u,%u).\r\n' % (','.join(ip.split('.')), port>>8&0xFF, port&0xFF))
        
    #===
    def start_datasock(self):

        if self.pasvmode:
            
            print ("[*] Waiting for data connection ...")
            self.datasock, addr = self.datasrvsock.accept()
            print colored ( "[+] SUCCESS : Data Connection from %s \n" % addr[0], 'green' )

        else:
            self.conn.send('500 YOU SHOULD USE PASSIVE MODE.\r\n')
            print colored ("[-] Passive Mode isn\'t enabled, asking to set it.", 'red')



    #===
    def stop_datasock(self):

        self.datasock.close()
        self.datasrvsock.close()

    #===
    def NLST(self, cmd):

        print ("[*] %s" % (cmd.strip()))
        print ("[*] Current Dir :  %s" % (self.cwd))
        self.conn.send('150 Opening ASCII mode data connection for file list.\r\n')
    
        self.start_datasock()

        if os.path.exists(self.cwd):
        
            for obj in os.listdir(self.cwd):

                self.datasock.send(obj + '\r\n')
                print ("%s" % (obj))

        else:
            print colored ("[-] FAIL : The Directory %s doesn\'t exist." % (self.cwd), 'red')
        
        self.stop_datasock()
        self.conn.send('226 Transfer complete.\r\n')


    #===
    def listitems(self,fn):
        
        st = os.stat(fn)
        fullmode = 'rwxrwxrwx'
        mode = ''
        
        for i in range(9):
        
            mode += ((st.st_mode>>(8-i))&1) and fullmode[i] or '-'
        
        d = (os.path.isdir(fn)) and 'd' or '-'
        ftime = time.strftime(' %b %d %H:%M ', time.gmtime(st.st_mtime))

        return d + mode + ' 1 user group ' + str(st.st_size)+ftime+os.path.basename(fn)

    #===
    def LIST(self, cmd):

        print ("[*] %s" % (cmd.strip()))
        print ("[*] Current Dir :  %s" % (self.cwd))
        self.conn.send('150 Opening ASCII mode data connection for file list.\r\n')
    
        self.start_datasock()

        if os.path.exists(self.cwd):
        
            for obj in os.listdir(self.cwd):

                f = self.listitems(os.path.join(self.cwd, obj))
                self.datasock.send( f + '\r\n')
                print ("%s" % (obj))

        else:
            print colored ("[-] FAIL : The Directory %s doesn\'t exist." % (self.cwd), 'red')
        
        self.stop_datasock()
        self.conn.send('226 Transfer complete.\r\n')

        print (colored ("[+]", 'green'), " Transfer complete.")


    #===
    def RETR(self, cmd):

        print ("[*] %s" % (cmd.strip()))

        fn=os.path.join(self.cwd, cmd.split(' ')[1].strip())  

        if self.typemode == 'I': fi=open(fn,'rb')
        else : fi=open(fn,'r')

        self.conn.send('150 Opening data connection.\r\n' )  

        data= fi.read(1024)
        
        self.start_datasock()

        while data:
            
            self.datasock.send(data)
            data=fi.read(1024)

        fi.close()
        
        
        self.conn.send('226 Transfer complete.\r\n')
        self.stop_datasock()
        
        print (colored ("[+]", 'green'), " Transfer complete.")

    #===

    def TYPE(self, cmd):

        self.typemode = cmd[5]

        if self.typemode == 'I': self.conn.send('200 Binary mode.\r\n')
        else : self.conn.send('200 ASCII mode.\r\n')

    #===


#==================================================================================================

class FTPLISTNER(threading.Thread):
    
    def __init__(self, ip, port, user, pwd, homedir, whitelist_ip):
    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        threading.Thread.__init__(self)

    def run(self):
    
        self.sock.listen(5)
    
        while True:
        
            worker=ZFTPSRV(self.sock.accept(), ip, user, pwd, homedir, whitelist_ip)
            worker.daemon=True
            worker.start()

    def stop(self):
    
        self.sock.close()

#==================================================================================================
if __name__=='__main__':

    print ("[*] Starting ZFTP Server.")

    usage = '%s [ --ip IP ] [ --port PORT ] [ --user USER ] [ --pwd PASSWORD] [--homedir HOMEDIR ] [ --wlist x.x.x.x,y.y.y.y,z.z.z.z ]\n \
        Example: %s --ip 192.168.1.2 --port 21 --user test --pwd pass123 --homedir /tmp/ftpsrv --wlist 192.168.1.3,192.168.1.4' % ( sys.argv[0], sys.argv[0] )

    version = "1.0"
    info = 'Simple Z FTP Server for Pentesting - %s, By K. BEKKOUCHE.' % version

    oparser = OptionParser (version = info, usage = usage)
    oparser.add_option ('--ip',  dest = 'ip', help = 'IP Address, to listen on.')
    oparser.add_option ('--port', dest='port', type=int, help='The port to listen on.', default=21)
    oparser.add_option ('--user', dest='user', help='The user account to use for the authentification.')
    oparser.add_option ('--pwd', dest='pwd', help='The password for the authentification.')
    oparser.add_option ('--homedir', dest='homedir', help='The Absolute path of Home Directory (ex, /tmp/).')
    oparser.add_option ('--wlist', dest='whitelist_ip', help='The source IPs, which are authorized to access this server.')


    (options, args) = oparser.parse_args()

    if not options.ip or not options.port or not options.user or not options.pwd or not options.homedir:

        oparser.print_help()
        sys.exit(1)

    ip = options.ip
    port = options.port
    user = options.user
    pwd = options.pwd
    homedir = options.homedir
    whitelist_ip = options.whitelist_ip

    if not whitelist_ip :
        whitelist_ip = '%s' % ip
    elif  not re.search ('%s' % ip, whitelist_ip):
        whitelist_ip = '%s,%s' % (whitelist_ip, ip)

    try:

        ftpsrv=FTPLISTNER(ip, port, user, pwd, homedir, whitelist_ip)
        ftpsrv.daemon=True
        ftpsrv.start()

        print ( colored ( "[+] SUCCESS : ", 'green') + "The Z FTP Server is started on (%s, %s)." % (ip, port) )
    
        raw_input ( colored("[*]", 'green') + " Tape [ENTER] or [CTRL+C to quit].\n" )

    except KeyboardInterrupt:

        ftpsrv.stop()

    print ("[*] End.")

#==================================================================================================

