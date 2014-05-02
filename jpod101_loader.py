#
#	Author: Michael Hiebl (http://www.haidozo.de)
#
#
#	Page tree structure
#	
#	|	
#	| - Absolute Beginner
#	| 
#	| - Beginner (category)
#	|		|
#	|		| - Beginner Season 1 (subcategory)
#	|					|	
#	|					| - Self Introduction (lesson)
#	|								|
#	|								| - *.mp3 (lesson documents)
#	|	
#	| - Intermediate
#	|	
#	| - Advanced
#	|	
#

'''Module docstring.

Usage: jpod101_loader.py -u username - p password [-d download_path] [-h] [--help]
'''

######### system packages #########
import sys
import getopt
import os.path

######### utility packages #########
from bs4 import BeautifulSoup
import requests
import re

######### global variables #########
login_page = 'http://www.japanesepod101.com/member/login_new.php'
redirect_page = 'http://www.japanesepod101.com/member/member.php?page=myaccount'
start_page = 'http://www.japanesepod101.com/index.php?cat='
categories = [ 'Beginner', 'Intermediate', 'Advanced', 'Japanese Specific', 'Absolute+Beginner']
credentials = {'amember_login':'', 'amember_pass':''}
path = '.\\'


########################################################################################################################
def download_media(media, path, lesson, lesson_counter):
    mp3_url = media.span['data-url']
    lesson_text = ''.join(c for c in lesson.text if c.isalnum())                   # remove non alphanumeric chars
    file = r'\\' + \
           str(lesson_counter) + '_' + \
           lesson_text + '_' + \
           media.span.text.replace(' ', '_') + \
           '.mp3'

    if not os.path.exists(path+file):
        with open(path+file, 'wb') as handle:
            got_mp3 = False
            while not got_mp3:
                try:
                    r = requests.get(mp3_url, stream=True)
                    got_mp3 = True
                except:
                    print("Couldn't load mp3. I'll try again...")
            for kbuffer in r.iter_content(1024):
                if not kbuffer:
                    print("reading %s blocked.\n" % file)
                    return 1
                    break
                else:
                    handle.write(kbuffer)
            #print(file + ' loaded successfully')
    else:
        print(file + ' exists already')

    return 0


########################################################################################################################
def create_path(cat, subcat, subcat_counter, lesson, lesson_counter):
    subcat_dir = ''.join(c for c in subcat.text if c.isalnum())                   # remove non alphanumeric chars
    lesson_dir = ''.join(c for c in lesson.text if c.isalnum())                   # remove non alphanumeric chars
    p = path + \
            r"\\" + \
            cat + \
            r"\\" + \
            str(subcat_counter) + \
            '_' + \
            subcat_dir + \
            r"\\" + \
            str(lesson_counter) + \
            '_' + \
            lesson_dir
    return p


def create_dir(path):                                      # create folder hierarchy
    if not os.path.exists(path):
        os.makedirs(path)


########################################################################################################################
def get_jpod101():
    try:
        session = requests.session()                                            # cookie handling done by session
        session.post(login_page, credentials)                                   # logon with credentials
        session.get(redirect_page)                                              # follow redirect
        response = session.get(start_page+categories[0])                        # load first category
        category_soup = BeautifulSoup(response.text)                            # get the main soup
    except ConnectionError:
        print("Connecting failed")
        return 1
    except HTTPError:
        print("HTTP error")
        return 1
    except:
        print("Error setting up session object")
        return 1

    for cat in categories:
        pattern = '.*cat=' + cat.replace('+','\+') + '$'                        # escape pluses for regex
        for finding in category_soup.findAll('a',                               # iterate over categories
                                    {'class':'ill-level-title',
                                    'href': re.compile(pattern)}):
            print("downloading category " + cat + "...")

            subcat_counter = 0
            for subcat in finding.parent.findAll('a',                           # iterate over sub categories
                                                {'class':'ill-season-title'}):

                subcat_counter += 1
                got_subcat = False
                while not got_subcat:
                    try:
                        response = session.get(subcat['href'])
                        got_subcat = True
                    except:
                        print("Couldn't get subcategory link. I'll try again...")
                sub_category_soup = BeautifulSoup(response.text)
                lesson_counter = 0
                for lesson in sub_category_soup.findAll('div',
                                                        {'class':'audio-lesson'}):
                    lesson_counter += 1
                    lesson_link = lesson.find('a')
                    current_path = create_path(cat,
                                               subcat,
                                               subcat_counter,
                                               lesson_link,
                                               lesson_counter
                                               )
                    create_dir(current_path)                                     # create folder for the subcategory
                    lesson_headline = None
                    try:
                        lesson_headline = session.get(lesson_link['href']).text
                    except:
                        print("Caught lesson link !!!!!!!" + lesson_link['href'])
                        lesson_headline = session.get(lesson_link['href']).text

                    lesson_soup = BeautifulSoup(lesson_headline)
                    print("downloading " + lesson_link.text + "... ", end=" ")
                    sys.stdout.flush()
                    for media in lesson_soup.findAll('div',
                                                     {'class':'lesson-media'}):
                        download_media(media,
                                       current_path,
                                       lesson_link,
                                       lesson_counter)
                    print("OK")
                    sys.stdout.flush()
    return 0


########################################################################################################################
def process_options(opts):
    user_checked = None
    password_checked = None
    if len(opts) > 0:
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print (__doc__)
                return 0
            elif opt == '-u':
                credentials['amember_login'] = arg
                user_checked = True
            elif opt == '-p':
                credentials['amember_pass'] = arg
                password_checked = True
            elif opt == '-d':
                global path
                path = arg
            else:
                print("Unknown argument: ")
                print(opt)
                return 1
        if user_checked and password_checked:
            return 0
    print("missing arguments.\n")
    print(__doc__)
    return 1


########################################################################################################################
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hu:p:d:',  ['help'])
    except getopt.error as err:
        print (err)
        print ('\n\tfor help use --help')
        return 1
    ret = process_options(opts)                                                     # process options
    if 0 == ret:
        return get_jpod101()                                                        # parse xml and load lessons
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
