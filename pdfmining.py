import PyPDF2

import shutil

addressee_done = False
addressee = ''
street_address = ''
areacode = ''
exchange = ''
lastfour = ''
extension = ''
fullphonenumber = ''
state = ''
city = ''

secondtolastword = ''
thirdtolastword = ''
lastword = ''

def mineForMichiganFOIAInfo(fullfilepath,destination_dir, url):
    global areacode
    global exchange
    global lastfour
    global fullphonenumber
    global lastword
    global secondtolastword
    global thirdtolastword
    global city
    global state
    global zipcode
    global addressee
    global street_address
    global addressee_done
    global street_addressee_done

#    print(fullfilepath)
    pdfFileObj = open(fullfilepath, 'rb')
    found = False
    address_string = ''

    try:
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
        for pageNum in range(0, 1):
            if( found is True ):
                break
            pageObj = pdfReader.getPage(pageNum)
            text = pageObj.extractText().encode('utf-8')

            text1 = text.replace(b'\n',b'~')
            str_text = str(text1,'utf-8')
            str_text2 = str_text.replace("~ ~", "\n")
            str_text3 = str_text2.replace("~", "")
#        text = str_text3       uncomment this for weirdo files

            search_text = text.lower().split()
            addressee = ''
            street_address = ''
            citystatezip = ''
            phone = ''
            inaddressee = False
            city = ''
            state = ''
            areacode = ''
            exchange = ''
            lastfour = ''
            zipcode = ''
            extension = ''
            fullphonenumber = ''
            sword = ''
            secondtolastword = ''
            addressee_done = False
            street_addressee_done = False

            for word in search_text:
                thirdtolastword = secondtolastword
                secondtolastword = lastword
                lastword = sword
                try:
                    if wereDone() == True:
                        fullphonenumber = "("+areacode+")"+" "+exchange+"-"+lastfour
                        filename = makeDestinationFilename()+"_request.pdf"
                        destfile = destination_dir + filename
                        shutil.copy(fullfilepath,destfile)
                        break
#                   sword = word.decode('ascii')
                    sword = ''
                    try:
                        sword = word.decode(encoding='ascii',errors='strict')
                    except:
                        sword = word
                        print('filename '+fullfilepath+' word failed to decode, breaking')
                        break
                    if( sword == 'foia' or sword == "freedom"):
                        fullphonenumber = "("+areacode+")"+" "+exchange+"-"+lastfour
#                       print("full phone number - " + fullphonenumber)
                        found = True
                        if len(city) == 0:
#                            print("fail - "+fullfilepath)
                            x = 1
                        else:
                            try:
                                filename = makeDestinationFilename()+"_request.pdf"
                                destfile = destination_dir + filename
                                shutil.copy(fullfilepath,destfile)
                            except Exception as eee:
                                print("filename error '+filename+'- bad addressee? " + addressee)
                        break
                    if sword == "phone:":
                        continue
                    if addressee_done == False:
                        if is_addressee(sword) == True:
                            continue
                    if street_addressee_done == False:
                        if is_streetaddress(sword) == True:
                            continue
                        print(street_address)
                    if is_city(sword):
#                    print("found a city named " + city)
                        continue
                    if is_complete_michigan_phone_number(sword):
 #                   print('got a complete phone number ' + sword)
                        fullphonenumber = sword
#                    print(fullphonenumber)
                        continue

                    if is_michigan_zip_code(sword):
                        print(city + "/" + state + "/" + zipcode)
                        continue

                    if is_part_of_michigan_phone_number(sword):
                        continue
#                   print ('----- ' + sword)
                except Exception as e:
                    print( 'unprocessed_foia_forms ' + e )
                    x = 1
                    return
            print(addressee)
            print( street_address+'\t\t'+city+'\t'+state+'\t'+zipcode+'\t'+url+'\t\t'+fullphonenumber)
            print()
#            print(street_address)
#            print( city + " " + state + " " + zipcode)
 #           print(fullphonenumber)
 #               print("decode error")
    except Exception as ee:
        print("mineForMichiganFOIAInfo "+ee)
        return
def makeDestinationFilename():
    global commaAfter
    global addressee
    filename = addressee.strip().replace(" ", "_")
    return filename

def is_streetaddress(s):
    global street_address
    global street_addressee_done

    if len(street_address) == 0:
        street_address = s
    else:
        street_address = street_address + " " + s

    if s.find('st') >= 0 or s.find('rd') >= 0 or s.find('street') >= 0:
        street_addressee_done = True
        return False
    return True

def wereDone():
    global areacode
    global exchange
    global lastfour
    global fullphonenumber
    global lastword
    global secondtolastword
    global thirdtolastword
    global city
    global state
    global zipcode
    if len(city) > 0 and len(state) > 0 and len(zipcode) > 0 and len(lastfour) > 0:
        return True
    return False

def is_addressee(s):
    global addressee
    global addressee_done

    if is_number(s):
#        print("Addressee = " + addressee)
        addressee_done = True
        return False
    addressee = addressee + " " + s

    return True

def is_city(s):
    global city
    global addressee

    if len(addressee) == 0:
        return False
    if len(city) == 0:
        if str.find(s,":") >= 0:
            return False
        if str.endswith(s,","):
            city = str.replace(s,",",'')
            city = str.replace(city,":",'')
            city = city.strip()
#            if str.upper(city) == "TOWNSHIP":
#                city = lastword + " " + city
            return True
    return False

def is_complete_michigan_phone_number(s1):
    s2= str.replace(s1,'(','')
    s3 = str.replace(s2,')','')
    s4 = str.replace(s3,'-','')
    s = str.replace(s4,' ','')
    if len(s) != 10:
        return False
    if is_number(s) == True:
        return True
    return False


def is_part_of_michigan_phone_number(s1):
    global areacode
    global exchange
    global lastfour

    s2= str.replace(s1, '(', '')
    s3 = str.replace(s2, ')', '')
    s = str.replace(s3, '-', '')
    if is_number(s) == False:
        return False
    if len(s) == 7:
        if len(areacode) != 0:
            exchange = s[0:3]
            lastfour = s[3:7]
#            print( "got exchange+lastfour " + s1)
            return True
        else:
            return False

    if len(s) == 3:
        if s1.find(')') and len(areacode) == 0:
#            print("Got area code " + s)
            areacode = s
            exchange = ''
            lastfour = ''
        else:
            if len(areacode) > 0:
#                print("Got exchange " + s1)
                exchange = s1
            else:
                print("Got areacode/exchange can't tell " + s1)

        return True
    if len(s) == 4:
        if areacode != '' and exchange != '':
#            print("Got lastfour " + s)
            lastfour = s
        else:
#            print("stranded digits " + s)
            z = 1
        return True
    return True


def is_michigan_zip_code(s):
    global state
    global lastword
    global secondtolastword
    global city
    global thirdtolastword
    global zipcode

    if is_number(s) == False:
        return False
    if str.startswith(s,'4') == False:
        return False
    if len(s) != 5:
        return False
    zipcode = s
    city = str.replace(secondtolastword,',','')
    if str.upper(city) == "CITY" or str.upper(city) =='TOWNSHIP' or str.upper(city) =='FALLS' or str.upper(city) =='RAPIDS':
        city = thirdtolastword + " " + city
    city = str.upper(city)
    state = makeState(lastword)
    return True

def makeState(st):
    if len(st) != 2:
        if str.upper(st) == 'MICHIGAN':
            return 'MI'
        else:
            return ''
    return str.upper(st)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False