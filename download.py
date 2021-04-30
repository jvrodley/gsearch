#!/usr/bin/env python

"""
Download all the pdfs linked on a given webpage
Usage -
    python grab_pdfs.py url <path/to/directory>
        url is required
        path is optional. Path needs to be absolute
        will save in the current directory if no path is given
        will save in the current directory if given path does not exist
Requires - requests >= 1.0.4
           beautifulsoup >= 4.0.0
Download and install using

    pip install requests
    pip install beautifulsoup4
"""

__author__ = 'elssar <elssar@altrawcode.com>'
__license__ = 'MIT'
__version__ = '1.0.0'

from requests import get
from urllib.parse import urljoin
from urllib.parse import urlparse
from os import path, getcwd
from bs4 import BeautifulSoup as soup
from sys import argv
import os
import db
import psycopg2
import psycopg2.extras

dupe_count = 0

forbidden_urls = [
    "deray",
    "muckrock",
    "pdffiller",
    "watchdogri",
    "checkthepolice"
]

def get_page(base_url):
    req = get(base_url)
    if req.status_code == 200:
        return req.text
    raise Exception('Error {0}'.format(req.status_code))


def get_all_links(html):
    bs = soup(html)
    links = bs.findAll('a')
    return links


def get_pdf(base_url, base_dir):
    html = get_page()
    links = get_all_links(html)
    if len(links) == 0:
        raise Exception('No links found on the webpage')
    get_some_pdfs1( base_url, base_dir, links )

def get_some_pdfs1( base_url, base_dir, links ):
    n_pdfs = 0
    for link in links:
        if link['href'][-4:] == '.pdf':
            n_pdfs += 1
            content = get(urljoin(base_url, link['href']))
            if content.status == 200 and content.headers['content-type'] == 'application/pdf':
                with open(path.join(base_dir, link.text + '.pdf'), 'wb') as pdf:
                    pdf.write(content.content)
    if n_pdfs == 0:
        raise Exception('No pdfs found on the page')
    print("{0} pdfs downloaded and saved in {1}".format(n_pdfs, base_dir))

def get_some_pdfs( base_dir, links ):
    n_pdfs = 0
    for link in links:
        n_pdfs = get_a_link(link, base_dir, n_pdfs, 'contract')
    print("{0} pdfs downloaded and saved in {1}".format(n_pdfs, base_dir))
    return n_pdfs

def get_a_link(url_record, base_dir, n_pdfs, searchtype ):
    global dupe_count
    x = url_record['url'].find(".pdf")
    if x < 0:
        return n_pdfs

    for phrase in forbidden_urls:
        if url_record['url'].find(phrase) >= 0:
            print( phrase + " skipping")
            return n_pdfs

    a = urlparse(url_record['url'])
    #            print(os.path.basename(a.path))  # Output: 09-09-201315-47-571378756077.jpg
    basename = os.path.basename(a.path)
#    if( searchtype == 'foia' ):
    filename = str(url_record['urlid']) + "_" + basename
    filename = path.join(base_dir, filename)

    if (filename.endswith('.pdf') == False):
        filename = filename + '.pdf'

    # Exists?
    b = searchFile(base_dir, filename)
    if b == True:
        db.markRetrieved(url_record)
        print('File ' + filename + ' exists - skipping ')
        dupe_count = dupe_count+1
        return n_pdfs

    try:
        content = get(url_record['url'])
    except:
        print('error getting ' + url_record['url'])
        setErrorResult(url_record, "error??")
        return n_pdfs

    setFilename(url_record, filename)
    print('Writing ' + filename)
    with open(filename, 'wb') as pdf:
        pdf.write(content.content)
    n_pdfs += 1
    return n_pdfs


def RetrieveOrphanURLs(base_dir):
    ssql = 'select * from url where retrieved = false'
    # create a cursor
    cur = db.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql)

    # display the PostgreSQL database server version
    rows = cur.fetchall()

    results = []
    for row in rows:
        results.append(dict(row))

    # close the communication with the PostgreSQL
    cur.close()

    for result in results:
        filename = db.makeUnqualifiedFilenameFromUrl(result['url'])
        setFilename(result['urlid'], filename)

        # Exists?
        b = searchFile(base_dir, os.path.basename(filename))
        if b == True:
            db.markRetrieved(result)
            print('File ' + filename + ' exists - skipping ')
            continue

        try:
            content = get(result['url'])
        except:
            print('error getting ' + result['url'])
            return
        setFilename(result, filename)
        print('Writing ' + filename)
        fullfilename = base_dir + "/" + filename
        with open(fullfilename, 'wb') as pdf:
            pdf.write(content.content)


def append_to_file( filename, message):
    with open(filename, "a") as myfile:
        myfile.write(message)

def searchFile(base_dir, fileName):
    for root, dirs, files in os.walk(base_dir):
#        print('Looking in:',root)
        for Files in files:
            found = -1
            try:
                found = Files.find(fileName)
            except:
                return False
            if found != -1:
                return True
    return False

def setFilename(url_record,filename):
    ssql = 'update url set filename = $1 where urlid = $2'
    return

def setErrorResult(url_record,error):
    ssql = 'update url set error = $1 where urlid = $2'
    return


if __name__ == '__main__':
    if len(argv) not in (2, 3):
        print
        'Error! Invalid arguments'
        print
        __doc__
        exit(-1)
    arg = ''
    url = argv[1]
    if len(argv) == 3:
        arg = argv[2]
    base_dir = [getcwd(), arg][path.isdir(arg)]
    try:
        get_pdf(base_dir)
    except:
        exit(-1)