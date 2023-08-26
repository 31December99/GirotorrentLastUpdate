#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import asyncio
import json
import os
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from decouple import config
from telethon import TelegramClient
import aiosqlite
import requests

USER = config('user')
PASSW = config('passw')
DOWNLOAD_TORFILE = config('download_folder')
NOTIFY = config('notify')
INTERVAL = int(config('interval'))
API_ID = config('api_id')
API_KEY = config('api_key')
BOT_TOKEN = config('bot_token')

# Nessuna categoria
CATEGORIA = "Nessuna/"
DOWNLOAD_TORFILE += CATEGORIA

client = TelegramClient("girotorrent", API_ID, API_KEY, retry_delay=10)
client.start(bot_token=BOT_TOKEN)


# Corsaro 0.0 - 19/08/2023 - versione modificato di headcorsare 0.6 per girotorrent
# Corsaro 0.1 - 25/08/2023 -
# controlla novità in homepage e le confronta con le prcedenti salvate nel database

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Utility:

    @staticmethod
    def console(message: str, level: int):
        now = datetime.now()
        date_now = datetime.today().strftime('%d-%m-%Y')
        time_now = now.strftime("%H:%M:%S")
        if level == 1:
            print(f"<{date_now} {time_now}>{bcolors.FAIL}{message}{bcolors.ENDC}")
        if level == 2:
            print(f"<{date_now} {time_now}>{bcolors.OKGREEN}{message}{bcolors.ENDC}")


class MyBrowser:
    """
    Classe browser per chrome

    """

    @property
    def newagent(self):
        """
        Ritorna un agente random
        :return:
        """
        uastrings = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 "
            "Safari/537.36",
            "Lynx: Lynx/2.8.8pre.4 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.12.23",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 "
            "Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 "
            "Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 "
            "Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 "
            "Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 "
            "Safari/605.1.15",
            "like Gecko) SamsungBrowser/4.0 Chrome/44.0.2403.133 Mobile Safari/537.36",
        ]
        return random.choice(uastrings)

    def __init__(self):
        """

        Nuovo Driver undetectable chrome
        disabilita scritta Automation Controlled
        Crea un nuovo profilo
        Crea una nuova cartella per il profilo 'gtorrents'
        Non tiene conto degli errori di certificato SSL
        Cambia Agente ad ogni avvio
        Abilita il log  - ora non utilizzato -
        Svuota il buffer performance - ora non utilizzato -
        Installa o aggiorna il webdriver

        """

        self.database = None
        opts = uc.ChromeOptions()
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--profile-directory=Profile 2")
        opts.add_argument("--user-data-dir=/home/midnight/.config/gtorrents/")

        # opts.add_argument('--headless')
        # opts.add_argument('--disable-gpu')
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument(f"--user-agent={self.newagent}")
        opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        self.driver_exec_path = ChromeDriverManager().install()
        self.driver = uc.Chrome(
            driver_executable_path=self.driver_exec_path, options=opts
        )

        self.driver.execute_script("window.performance.clearResourceTimings();")
        self.php_sess_id = None
        self.cookies_dict = None
        self.cookies = None

        self.BASE_URL = (
            "https://girotorrent.org/index.php?page=torrents&active=1&category="
        )
        self.categoria = {
            "Nessuna": "0",
        }
        self.ACTIVE_ONLY = (
            "https://girotorrent.org/index.php?page=torrents&active=1&search=&&options=0&order=3&by=2"
            "&pages="
        )

        self.HOME_LAST_UPDATE = (
            "https://girotorrent.org/index.php"
        )

    async def filterTag(self, torrent_name: str) -> bool:

        word_list = torrent_name.lower().strip().split(" ")
        lista = [
            "cam",
            "bdrip",
            "dlrip",
            "dlmux",
            "dvdrip",
            "e-ac3-ac3",
            "web-dl",
            "web",
            "dl",
            "webmux",
            "bdmux",
            "bdremux",
            "bluray",
            "webrip",
            "hdtv",
            "1]hdtv",
            "2]hdtv",
            "h264",
            "h265",
            "x264",
            "x265",
            "avi",
            "mkv",
            "mpg4",
            "2160p",
            "HDR",
            "hdtv",
            "remux",
            "dv",
            "mk3d",
            "mp4",
            "m2ts",
            "ts",

        ]

        for word in word_list:
            if word in lista:
                return True

    async def login(self) -> bool:
        """
        Accede alla pagina di Login
        Controllo se esiste già un profilo di chrome (Profile 2) dove ho già i cookies di un precedente login
        altrimenti logga con user e password
        TODO: gestire eventuali errori

        """
        self.database = Database("girotorrent.db")
        await self.database.connect()

        self.driver.get("https://girotorrent.org/index.php?page=login")
        self.cookies = self.driver.get_cookies()
        self.cookies_dict = {cookie["name"]: cookie["value"] for cookie in self.cookies}
        self.php_sess_id = (
            self.cookies_dict["PHPSESSID"]
            if "PHPSESSID" in self.cookies_dict
            else self.cookies()
        )
        Utility.console("LOG IN OK..", 2)
        Utility.console(f"Interval {INTERVAL} s", 2)

        return True

    async def cookies(self) -> bool:
        """
        Legge i cookies dopo aver loggato
        Per fare questo cerco un xpath corripospondente a username e password
        :return: vero o falso
        TODO: gestire eventuali errori ad esempio su Xpath

        """
        wait = WebDriverWait(self.driver, 15)
        username_field = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="want_username"]'))
        )  # Sostituisci con il vero nome o ID
        password_field = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="want_password"]'))
        )  # Sostituisci con il vero nome o ID

        # Se tutto è ok proseguo ed invio i dati
        username_field.send_keys(USER)
        password_field.send_keys(PASSW)
        password_field.send_keys(Keys.RETURN)

        # Una volta loggato , salvo in memoria i cookies
        self.cookies = self.driver.get_cookies()
        self.cookies_dict = {cookie["name"]: cookie["value"] for cookie in self.cookies}
        print(self.cookies_dict)
        return True

    async def browser_close(self):
        """
        Chiudo tutto
        :return:
        """
        self.driver.quit()

    async def scan_home(self) -> list:
        """
        Ricevo il link di una prima pagina che ha come categoria TORRENTS MENU> TORRENT > ACTIVE ONLY

        :param page:
        :return:
        TODO: gestire eventuali errori

        """
        self.driver.get(self.HOME_LAST_UPDATE)

        # Ottengo il sorgente html della pagina
        html_content = self.driver.page_source

        # Analizza il contenuto HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        #
        last_upload = soup.find('div', class_='collapse multi-collapse show', id='LASTUPLOAD')
        table_elements = last_upload.find_all('table')

        last_torrents = []
        for table_element in table_elements:
            tr_elements = table_element.find_all('tr')
            for tr_element in tr_elements:
                td_elements = tr_element.find_all('td')
                for td in td_elements:
                    if a := td.find('a'):
                        if 'index.php?page=torrent-details&id' in a['href']:
                            last_torrents.append([f"https://girotorrent.org/{a['href']}", a.get_text(strip=True)])

        # ritorno l'elenco appena creato
        return last_torrents

    async def torrent(self, link: str):
        """
        Ricevo un nuovo link della pagina di dettaglio di un torrent
        :param link:
        :return:
        TODO: gestire eventuali errori
        """
        # Accedo alla pagina dettagli
        self.driver.get(link)

        # Utility.console(f"---> {link}")

        # Ottengo il sorgente html della pagina
        html_content = self.driver.page_source

        # Identifico i vari elmenti (Parsing)
        soup = BeautifulSoup(html_content, "html.parser")

        # Cerco l'elemento input_tag per leggere l'info hash del torrent
        input_tag = soup.find("input", {"name": "info_hash"})

        # Leggo il valore dell'elemento input_tag
        info_hash = input_tag.get("value") if input_tag else None

        return info_hash


class Pages(MyBrowser):

    def __init__(self, sel_categoria: str):
        super().__init__()
        self.sel_categoria = sel_categoria.replace("/", "").strip()
        self.categoria_url = (f"{self.BASE_URL}{self.categoria[self.sel_categoria]}&search=&&options=0&order=3&by=2"
                              f"&pages=")

    async def last_upload(self) -> []:
        # Leggo la pagine delle novità in homepage
        return await self.scan_home()


class Database:

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    async def connect(self):
        try:
            self.connection = await aiosqlite.connect(self.db_name)
            self.cursor = await self.connection.cursor()
        except aiosqlite.Error as e:
            print(f"Error connecting to the database: {e}")

    async def close(self):
        try:
            if self.connection:
                await self.connection.close()
        except aiosqlite.Error as e:
            print(f"Error closing the database connection: {e}")

    async def new_table(self, table_name: str):
        try:
            await self.connect()
            table_query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                                         id             INTEGER PRIMARY KEY AUTOINCREMENT,
                                         link       TEXT UNIQUE NOT NULL,
                                         titolo     TEXT
                                     );"""

            await self.cursor.execute(table_query)
            await self.connection.commit()
        except aiosqlite.Error as e:
            print(f"Error creating the table: {e}")
        finally:
            await self.close()

    @property
    async def downloaded(self):
        res = await self.cursor.execute("SELECT link,titolo FROM Page")
        return [[i[0], i[1]] for i in await res.fetchall()]

    async def update_db(self, link: str, titolo: str):
        await self.cursor.execute("INSERT INTO Page (link, titolo) values (?,?)", (link, titolo,))
        await self.connection.commit()


class Forum(Pages):

    def __init__(self, sel_categoria: str):
        super().__init__(sel_categoria)

    @property
    async def downloaded(self) -> json:
        return await self.database.downloaded

    async def last_video_torrents(self) -> bool:
        last = await self.last_upload()
        downloaded = await self.downloaded

        for url_first, title in last:
            if any(url_first == url_second for url_second, _ in downloaded):
                return False
            else:
                Utility.console(f"[NUOVO] {title}", 2)
                response = requests.get(url_first, cookies=self.cookies_dict)
                if os.path.exists(f"{DOWNLOAD_TORFILE}{title}.torrent"):
                    Utility.console(f"file esistente !! {DOWNLOAD_TORFILE}{title}.torrent", 1)
                    continue
                with open(f"{DOWNLOAD_TORFILE}{title}.torrent", "wb") as file:
                    file.write(response.content)
                await self.database.update_db(url_first, title)
                await client.send_file(entity=NOTIFY, file=f"{DOWNLOAD_TORFILE}{title}.torrent")
        return True


async def start():
    forum = Forum(CATEGORIA)
    print(f"[{bcolors.OKGREEN}ctrl-c per uscire{bcolors.ENDC}]")

    # Crea la tabella se non esiste
    await (Database("girotorrent.db")).new_table('Page')

    # Si logga
    if not await forum.login():
        loop.stop()
        return

    while True:
        # Verifica gli ultimi uploads
        if not await forum.last_video_torrents():
            Utility.console(" Nessuna novità", 2)
        await asyncio.sleep(10)


# ..................................................................
# Abilita color in windows…
# ..................................................................
if os.name == 'nt':
    os.system('color')

loop = asyncio.get_event_loop()
try:
    print()
    print(f"[{bcolors.OKGREEN}START !{bcolors.ENDC}]")
    task_start = loop.create_task(start())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    pass
