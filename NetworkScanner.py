import re
import sqlite3
import nmap
import socket


class NetworkScanner:
    def __init__(self): #ускоренное сканирование , top_ports=1000
        self.scan_results = None
        self.network_graph = None
        self.save_mode = True
    def scan_network_fast(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        ip_address = ip_address[0:-3]
        if ip_address[-1]=='.':ip_address=ip_address+'0/24'
        else:ip_address=ip_address+'.0/24'
        self.ip_range=ip_address
        nm = nmap.PortScanner()
        nm.scan(hosts=self.ip_range, arguments='-T4 -F -O')
        self.scan_results = nm # получаем список устройств в локальной сети
        self.r=1

    def scan_network(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        ip_address = ip_address[0:-3]
        if ip_address[-1]=='.':ip_address=ip_address+'0/24'
        else:ip_address=ip_address+'.0/24'
        self.ip_range=ip_address
        nm = nmap.PortScanner()
        nm.scan(hosts=self.ip_range, arguments='-p-')
        self.scan_results = nm # получаем список устройств в локальной сети

    def set_save_mode(self,import_save_mode):
        self.save_mode=import_save_mode
        #print(self.save_mode)

    def create_graph(self):
        #print(self.r)
        if self.scan_results is None:
            raise ValueError("Scan results are not available. Please run scan_network() first.")
        pattern_mac='[0-9A-Z]{2}:[0-9A-Z]{2}:[0-9A-Z]{2}:[0-9A-Z]{2}:[0-9A-Z]{2}:[0-9A-Z]{2}'
        '''создаем/подключаемся к базе данных'''
        conn = sqlite3.connect('Device_parametres.db')
        cursor = conn.cursor()

        conn.execute("PRAGMA foreign_keys = ON")
        # Создаем основную таблицу devices
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS devices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        IP TEXT NOT NULL unique,
                        System INTEGER,
                        Activity INTEGER
                    )
                    ''')
        # Создаем таблицу MAC-адресов
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS MAC (
                        id INTEGER PRIMARY KEY AUTOINCREMENT ,
                        IP_id INTEGER,
                        MAC_addr TEXT NOT NULL unique,
                        FOREIGN KEY (IP_id) REFERENCES devices(id) ON DELETE CASCADE
                    )
                    ''')
        # Создаем таблицу портов
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Ports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        IP_id INTEGER,
                        Port INTEGER NOT NULL,
                        FOREIGN KEY (IP_id) REFERENCES devices(id) ON DELETE CASCADE
                    )
                    ''')
        for host in self.scan_results.all_hosts():
            text_scan = str(self.scan_results[host])

            '''добавление элементов в БД'''

            index_windows=text_scan.find('Windows')
            index_android = text_scan.find('Android')
            index_linux = text_scan.find('Linux')
            if index_windows>0:system ='Windows'
            if index_android > 0: system ='Android'
            if index_linux>0 and index_android<0 :system ='Linux'
            activity_name=self.scan_results[host].state()
            if activity_name=='up':activity=1
            else:activity=0
            try:
                cursor.execute('INSERT INTO devices (IP, System, Activity) VALUES (?, ?, ?)', (host, system, activity))
                MAC=re.findall(pattern_mac,text_scan)
                ip_id = cursor.lastrowid
                if len(MAC) > 0:mac_addr=MAC[0]
                else:mac_addr='my PC'
                cursor.execute('INSERT INTO MAC (IP_id, MAC_addr) VALUES (?, ?)', (ip_id, mac_addr))
                for proto in self.scan_results[host].all_protocols():
                    for port in self.scan_results[host][proto].keys():
                        cursor.execute('INSERT INTO Ports (IP_id, Port) VALUES (?, ?)', (ip_id, port))
            except:
                print('this ip is already exist')
        print('fun')
        conn.commit()
        conn.close()
        '''  тестовая часть'''
        '''
        cursor.execute('SELECT * FROM devices');
        rows = cursor.fetchall()
        # Выводим результат
        for row in rows:
            print(row)
        print(row)
        cursor.execute('SELECT * FROM MAC');
        rows = cursor.fetchall()
        # Выводим результат
        for row in rows:
            print(row)
        print(row)
        cursor.execute('SELECT * FROM Ports');
        rows = cursor.fetchall()
        # Выводим результат
        for row in rows:
            print(row)
        print(row)
        '''

if __name__ == "__main__":
    scanner = NetworkScanner()
    scanner.scan_network_fast()
    scanner.create_graph()

    #scanner.visualize_graph()