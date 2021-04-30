import pdfmining
from download import get_a_link, append_to_file
import time
import db
import download

if __name__ == '__main__':
    from googlesearch import search

    base_dir = "D:\downloads\policeunioncontracts"
    logfile = base_dir + "\good_urls.log"

    links = []

    db.connect()

    #    searchterms = [
    # done        'police cba pdf',
    # done        'fop contract pdf',
    # 697        'fop agreement pdf',
    # done        'police association contract pdf',
    # done        'police association agreement pdf',
    # done        'police contract pdf',
    # done        'ppa contract pdf',
    # done        'police union contract pdf',
    # done        'police union agreement pdf',
    # 1564        'ppa agreement pdf'
    #    ]

    # Make sure that files sorted into "contract" directory are marked as known-contract in database URL
    db.MineRequestFormPdfsForFOIAAddresses("D:\\downloads\\policeunioncontracts\\unprocessed_foia_forms\\","D:\\downloads\\policeunioncontracts\\parsed_foia_forms\\")
    db.MakeRegularFilenames("D:\\downloads\\policeunioncontracts\\contract\\","D:\\downloads\\policeunioncontracts\\regular_filename\\")
    db.FixFilenames()
    db.MarkKnown(base_dir + '\contract')
    db.MarkKnown(base_dir + '\contract1')
    download.RetrieveOrphanURLs(base_dir)

    npdfs = 0
    while( True ):
        try:
            searchterm_records = db.getSearchTerms('contract')
#            searchterm_records = db.getSearchTerms('foia')
            for searchterm_record in searchterm_records:
                result_count = 0
                dupe_count = 0
                st = searchterm_record['searchterm']
                start = searchterm_record['lastresult']
                stop = searchterm_record['lastresult'] + 1000
                db.setSearchDate(searchterm_record)
                urls = search(query=st, start=start, stop=stop)

                for url in urls:
                    x = db.urlExists(url)
                    if (x == True):
                        print("URL exists")
                        continue
                    print("new URL")

                    url_record = db.addUrlToSearchTerm(searchterm_record, url)
                    print(searchterm_record['searchterm'] + " result ", str(result_count))
                    result_count = result_count + 1
                    print(url)
                    i = npdfs
                    npdfs = get_a_link(url_record, base_dir, npdfs, searchterm_record['searchtype'])
                    if npdfs > i:
                        append_to_file(logfile, url + "\n")
                    db.markRetrieved(url_record)
                    links.append(url)
                    time.sleep(1)
                db.setLastResult(searchterm_record, result_count)
                db.setSaveCount(searchterm_record, npdfs)
                db.setDupeCount(searchterm_record, dupe_count)
                db.setResultCount(searchterm_record, result_count)
                db.markDone(searchterm_record)
            break
        except Exception as error:
            print('exception searching {0}'.format(error))
            print('Sleeping for 100 minutes')
            time.sleep(6000)

    db.close()
    print(f'Main done - wrote {npdfs} new files')
    exit(0)
