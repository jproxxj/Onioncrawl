#!/usr/bin/env python3


import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import json
from urllib.parse import urljoin, urlparse
import sys
import os
import socket
from datetime import datetime
import logging


# ========================= CONFIG =========================
VERSION=0.1
DEBUG=True

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0'
MAX_DOMAINS = 1000
REQUEST_TIMEOUT = 20
DELAY = 2.0
DB = 'onion_crawl.db'
JSON_FILE = 'db_dump.json'


INITIAL_SEEDS = [
    'http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion/wiki/index.php/Main_Page',

]

CONNECTION_HOST="127.0.0.1"
CONNECTION_PORT=9050
CONNECTION_TIMEOUT=4
CONNECTION_TEST_HOST="http://check.torproject.org"
DEFAULT_TIMEOUT=5

PROXIES = {
    'http':  'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
    }
#🗹
#☒

def test_tor_connection() -> bool:
    try:
        socket.create_connection((CONNECTION_HOST, CONNECTION_PORT), timeout=DEFAULT_TIMEOUT).close()
        r = requests.get(CONNECTION_TEST_HOST,
                         proxies=PROXIES,
                         headers={'User-Agent': USER_AGENT},
                         timeout=REQUEST_TIMEOUT)
        logging.info(f"🗹 Connection to {CONNECTION_TEST_HOST} via {CONNECTION_HOST}:{CONNECTION_PORT} completed ")
        return True
    #needs proper exception handling
    except:
        logging.critical(f"☒ Connection to {CONNECTION_TEST_HOST} via {CONNECTION_HOST}:{CONNECTION_PORT} failed ")
        logging.critical("Exiting..")
        sys.exit(1)

#Table onions {
#  id integer [primary key]
#  domain varchar
#  header varchar
#  parent varchar
#}


# ==== Should be in one function in the future

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS onions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            header TEXT,
            parent TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_onion(domain: str, header: str, parent: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO onions (domain, header, parent) VALUES (?, ?, ?)",
        (domain, header, parent)
    )
    conn.commit()
    conn.close()

def get_domains():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT domain FROM onions")
    results = [row[0] for row in cur.fetchall()]
    conn.close()
    return results

def count_domains():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM onions")
    results = [row[0] for row in cur.fetchall()]
    conn.close()
    results=results[0]
    return results

def get_random_domain():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT o.id, o.domain, o.header, o.parent
        FROM onions o
        LEFT JOIN (
            SELECT parent, COUNT(*) AS freq
            FROM onions
            WHERE parent IS NOT NULL
            GROUP BY parent
        ) p ON o.parent = p.parent
        ORDER BY COALESCE(p.freq, 0) ASC, RANDOM()
        LIMIT 1
    """)
    result = cur.fetchone()


    conn.close()

    return result

def db_export_json():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, domain, header, parent FROM onions")
    rows = cur.fetchall()
    data = [
        {
            "id": row[0],
            "domain": row[1],
            "header": row[2],
            "parent": row[3]
        }
        for row in rows
    ]

    conn.close()
    logging.info(f"Dumping current DB to JSON blob")
    return json.dumps(data, indent=2)

# ==== Should be in one function in the future

def dump_to_file(data: str):
    with open(JSON_FILE,'w') as f:
        f.write(data)
    logging.info(f"Dumping current JSON blob to {JSON_FILE}")
    return

def is_onion_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ('http', 'https') and p.netloc.lower().endswith('.onion')
    except:
        return False

def cleanup_url(url: str) -> str:
    ind=url.find('.onion')
    url=url[:(ind+6)]
    if len(url) >= 69: 
        return url
    else:
        return

def walk_site(domain):    
    try:
        r = requests.get(domain,
                        proxies=PROXIES,
                        headers={'User-Agent': USER_AGENT},
                        timeout=REQUEST_TIMEOUT)

        soup = BeautifulSoup(r.text, 'html.parser')
        title = (soup.title.string.strip() if soup.title and soup.title.string else "(no title)")[:180]
        links = []
        for a in soup.find_all('a', href=True):
            link = urljoin(domain, a['href'])
            if is_onion_url(link):

                link=cleanup_url(link)
                links.append(link)
        links=list(set(links))
        logging.info(f"Found {len(links)} 🌐 in {domain}")
        for n in links:
            if n != domain:
                title=''
            insert_onion(n, title, domain)
        return links
    except:
        logging.info(f"Timeout for {domain} exceeded, moving on.")
        return None



#logging.debug("Debug")
#logging.info("Info")
#logging.warning("Warning")
#logging.error("Error")
#logging.critical("Critical")

def main():


    onions=[]

    logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s %(levelname)s: %(message)s",
       datefmt="%b %d %H:%M:%S",
       force=True
    )

    # Doing pre run tasks
    test_tor_connection()
    init_db()

    domain_count=count_domains()+MAX_DOMAINS
    print(get_random_domain())
    # First seeds
    logging.info(f"Trying to find out if the database has been seeded")
    if not get_random_domain():
        logging.info(f"Database not seeded, using seed {INITIAL_SEEDS}")
        for w in INITIAL_SEEDS:
            walk_site(w)

    # After initial seed do crawls
    else:
        logging.info(f"Seeds found, using a random seed from the database")
        while domain_count >= count_domains():
            walk_site((get_random_domain()[1]))

    dump_to_file(db_export_json())
    return 0




if __name__ == '__main__':
    main()


# it broke when we moved the db out of the way and fucked around with writing null to the header fields...
