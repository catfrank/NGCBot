from BotServer.MainServer import MainServer
from cprint import cprint

Bot_Logo = """
███▄▄▄▄      ▄██████▄   ▄████████ ▀█████████▄   ▄██████▄      ███     
███▀▀▀██▄   ███    ███ ███    ███   ███    ███ ███    ███ ▀█████████▄ 
███   ███   ███    █▀  ███    █▀    ███    ███ ███    ███    ▀███▀▀██ 
███   ███  ▄███        ███         ▄███▄▄▄██▀  ███    ███     ███   ▀ 
███   ███ ▀▀███ ████▄  ███        ▀▀███▀▀▀██▄  ███    ███     ███     
███   ███   ███    ███ ███    █▄    ███    ██▄ ███    ███     ███     
███   ███   ███    ███ ███    ███   ███    ███ ███    ███     ███     
 ▀█   █▀    ████████▀  ████████▀  ▄█████████▀   ▀██████▀     ▄████▀   
     Version: V2.2 蛇年贺岁版
     Author: 范可飘                                             

"""

if __name__ == '__main__':
    cprint.info(Bot_Logo.strip())
    Ms = MainServer()
    try:
        Ms.processMsg()
    except KeyboardInterrupt:
        Ms.Pms.stopPushServer()
