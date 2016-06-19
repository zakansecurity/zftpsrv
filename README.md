# zftpsrv
Z FTP Server, Simple Python FTP Server for Pentesting Purpose


Z FTP Server implements some FTP commands, it could be extended. It can be useful on some MITM Attacks.

# Usage :

zftpsrv.py [ --ip IP ] [ --port PORT ] [ --user USER ] [ --pwd PASSWORD] [--homedir HOMEDIR ] [ --wlist x.x.x.x,y.y.y.y,z.z.z.z ]

# Example: 

zftpsrv.py --ip 192.168.1.2 --port 21 --user test --pwd pass123 --homedir /tmp/ftpsrv --wlist 192.168.1.3,192.168.1.4


# Options:

      --version             show program's version number and exit
      -h, --help            show this help message and exit
      --ip=IP               IP Address, to listen on.
      --port=PORT           The port to listen on.
      --user=USER           The user account to use for the authentification.
      --pwd=PWD             The password for the authentification.
      --homedir=HOMEDIR     The Absolute path of Home Directory (ex, /tmp/).
      --wlist=WHITELIST_IP  The source IPs, which are authorized to access this server.

# Import:
	
The only mode implemented is "Passive Mode", then the client should specify it.
This script could be extended easly, by using the template. Each command is a function.
For example, you could add "def STOR" without touching the rest of the code, the command 
will be available.

Enjoy !