#-*- coding: utf-8 -*-
import urllib
import urllib2
import re
import time
from splinter import Browser

email = ''
password = ''


def collect(htmlSource):
    "Collect passcodes"

    passcode = []
    # 3 patterns of passcodes
    passFTypePattern = re.compile(
        "[0-9][A-Za-z][A-Za-z][0-9][A-Za-z]*[0-9][A-Za-z][0-9][A-Za-z]")
    passSTypePattern = re.compile("[A-Za-z]*[0-9][0-9][A-Za-z]")
    passTTypePattern = re.compile("82666[0-9]{5,6}")
    passcode.extend(re.findall(passFTypePattern, htmlSource))
    passcode.extend(re.findall(passSTypePattern, htmlSource))
    passcode.extend(re.findall(passTTypePattern, htmlSource))

    # Remove passcode with length < 4
    for passOne in passcode:
        if len(passOne) < 4:
            passcode = filter(lambda a: a != passOne, passcode)

    return passcode


def parseDecodeIngress():
    "Parse decodeingress.me"

    passcodes = []

    www = "http://decodeingress.me/category/code/"
    try:
        page = urllib2.urlopen(www).read()
    except:
        print 'Can`t open site. Check your internet connection or try later.'

    passcodes = collect(page)
    passcodes = [element.lower() for element in passcodes]
    passcodes = list(set(passcodes))
    return passcodes


def postToIntel(passcode):
    "Post passcode to ingress intel"

    www = 'https://www.ingress.com/intel'

    #Splinter browser
    browser = Browser()
    try:
        browser.visit(www)
        browser.click_link_by_text('Log in')
        browser.fill('Email', email)
        browser.fill('Passwd', password)
        button = browser.find_by_name('signIn')
        button.click()

        idbox = browser.find_by_xpath('''id('passcode')''').first
        browser.execute_script("$('#redeem_reward').addClass('show_box')")
        idbox.fill(passcode)

        button = browser.find_by_value('Input passcode')
        button.click()
    except:
        browser.quit()

    return 1

if __name__ == '__main__':

    print 'First parse.'
    print 'Waiting for new passcodes...'

    if password = '' or email = '':
        print 'Enter password!'
        raise SystemExit()

    old = parseDecodeIngress()

    while 1:
        errorFlag = 0
        new = parseDecodeIngress()
        codes = [x for x in new if x not in old]
        if len(codes) > 0:
            for code in codes:
                print 'Accquired new passcode: ' + code
                try:
                    postToIntel(code)
                except:
                    errorFlag = 1
                    print 'Something go wrong! Wi`ll try again.'

                if errorFlag == 1:
                    try:
                        postToIntel(code)
                    except:
                        print 'It`s a kind of magic)'
                    else:
                        errorFlag = 0
        old = new
        time.sleep(60)