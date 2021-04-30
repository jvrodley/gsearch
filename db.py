#!/usr/bin/python
import os
from sys import path
from urllib.parse import urlparse
import shutil
import psycopg2
import psycopg2.extras
from config import config
import download
import pdfmining

conn = None



def FixFilenames():
    ssql = 'select * from url where filename is null'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        filename = makeUnqualifiedFilenameFromUrl(result['url'])
        setFilename(result['urlid'], filename)

    return

def MakeRegularFilenames(contract_dir, regular_dir):
    print("copying known contracts from "+contract_dir+" to regularized filenames in " + regular_dir)
    ssql = 'select filename, regular_filename from url where filename is not null and knowntobeacontract = true and regular_filename is not null'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        dest_filename = result['regular_filename']
        src_filename = result['filename']
        source_filename = contract_dir + src_filename
        destination_filename = regular_dir + dest_filename
        try:
            x = download.searchFile(regular_dir, dest_filename)
            if( x == False):
                print('regular filename = ' + dest_filename)
                shutil.copyfile(source_filename, destination_filename)
                print("copied")
        except:
            print("error copying " + source_filename)

    return

def getSearchTerms(searchtype):
    ssql = 'select * from searchterm where searchtype = %s and done = False'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,[searchtype])

    # display the PostgreSQL database server version
    rows = cur.fetchall()

    results = []
    for row in rows:
        results.append(dict(row))

    # close the communication with the PostgreSQL
    cur.close()

    return results


def markRetrieved(url_record):
    ssql = 'update url set retrieved = true where urlid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,[url_record['urlid']])
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()
    return


def markDone(searchterm_record):
    ssql = 'update searchterm set done = %s where searchtermid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,(True,searchterm_record['searchtermid']))
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()
    return


def addUrlToSearchTerm(searchterm_record,url):
    ssql = 'insert into url(searchtermid_searchterm,filename,url) values (%s,%s,%s) RETURNING urlid'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    filename = makeUnqualifiedFilenameFromUrl(url)

    # execute a statement
    cur.execute(ssql, (searchterm_record['searchtermid'], filename, url))
    conn.commit()
    count = cur.rowcount

    url_record = {}
    url_record['urlid'] = cur.fetchone()[0]
    url_record['url'] = url
    url_record['searchtermid_searchterm'] = searchterm_record['searchtermid']

    # close the communication with the PostgreSQL
    cur.close()

    return url_record


def urlExists(url):
    ssql = 'select * from url where url = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql, [url])

    # display the PostgreSQL database server version
    rows = cur.fetchall()

    retval = False
    if( len(rows) > 0 ):
        retval = True

    # close the communication with the PostgreSQL
    cur.close()

    return retval


def FileExistsInDB(filename):
    ssql = 'select urlid from url where filename = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql, [filename])

    # display the PostgreSQL database server version
    rows = cur.fetchall()

    retval = -1
    if( len(rows) > 0 ):
        retval = rows[0]['urlid']

    # close the communication with the PostgreSQL
    cur.close()

    return retval


def setKnownToBeAContract(urlid):
    ssql = 'update url set knowntobeacontract = True where urlid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,[urlid])
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()

    return


def makeUnqualifiedFilenameFromUrl(url):
    a = urlparse(url)
    #            print(os.path.basename(a.path))  # Output: 09-09-201315-47-571378756077.jpg
    filename = os.path.basename(a.path)
    if(len(filename) >= 90):
        filename = filename[0:90]

    if (filename.endswith('.pdf') == False):
        filename = filename + '.pdf'

    return filename

def MineRequestFormPdfsForFOIAAddresses(source_directory, destination_directory):
    print("MinePdfsForFOIAAddresses")
    ssql = 'select * from url where knowntobeacontract = false'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
        fullpath = source_directory + result['filename']
#        fullpath = source_directory + "1cjh6bpe0_355592.pdf"
        if fileExists(fullpath) == True:
            pdfmining.mineForMichiganFOIAInfo(fullpath, destination_directory, result['url'])

def fileExists(fullpath):
    retval = False
    try:
        f = open(fullpath)
        # Do something with the file
        retval = True
        f.close()
    except IOError:
        retval = False
    return retval

def makeFOIAUnqualifiedFilenameFromUrl(url_record):
    a = urlparse(url_record['url'])
    #            print(os.path.basename(a.path))  # Output: 09-09-201315-47-571378756077.jpg
    filename = str(url_record['urlid']) + "_" + os.path.basename(a.path)
    if(len(filename) >= 90):
        filename = filename[0:90]

    if (filename.endswith('.pdf') == False):
        filename = filename + '.pdf'

    return filename


def setFilename(urlid,filename):
    ssql = 'update url set filename = %s where urlid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,[filename, urlid])
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()

    return


def MarkKnown( directory ):
        for root, dirs, files in os.walk(directory):
            #        print('Looking in:',root)
            for Files in files:
                found = -1
                try:
                    urlid = FileExistsInDB(Files)
                    if( urlid > 0 ):
                        setKnownToBeAContract(urlid)
                except:
                    return False
        return False


def setLastResult(searchterm_record,count):
    ssql = 'update searchterm set lastresult = %s where searchtermid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,( count,searchterm_record['searchtermid']))
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()

    return


def setResultCount(searchterm_record,count):
    ssql = 'update searchterm set resultcount = %s where searchtermid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,( count,searchterm_record['searchtermid']))
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()

    return


def setSaveCount(searchterm_record,count):
    ssql = 'update searchterm set savecount = %s where searchtermid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,(count,searchterm_record['searchtermid']))
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()

    return


def setDupeCount(searchterm_record,count):
    ssql = 'update searchterm set dupecount = %s where searchtermid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,(count,searchterm_record['searchtermid']))
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()
    return


def setSearchDate(searchterm_record):
    ssql = 'update searchterm set searchdate = Now() where searchtermid = %s'
    # create a cursor
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # execute a statement
    cur.execute(ssql,[searchterm_record['searchtermid']])
    conn.commit()
    # close the communication with the PostgreSQL
    cur.close()
    return


def connect():
    global conn
    """ Connect to the PostgreSQL database server """
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def close():
    global conn
    if conn is not None:
        conn.close()
        print('Database connection closed.')


if __name__ == '__main__':
    connect()