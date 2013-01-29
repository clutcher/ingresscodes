#-*- coding: utf-8 -*-

import re
import datetime
import time
import requests

# ACSID cookie
acsid = ''
# csrftoken cookie
csrftoken = ''
# Google Key API with G+ ON
keyAPI = ''

cookie = 'ACSID=' + acsid + ';' + 'csrftoken=' + csrftoken


def checkInputData():
    response = postToIntel('test')
    if response.find('gameBasket'):
        return 1
    else:
        return 0


def convertTime(val):
    if '.' not in val:
        return datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")

    nofrag, frag = val.split(".")
    date = datetime.datetime.strptime(nofrag, "%Y-%m-%dT%H:%M:%S")

    return date


def collect(htmlSource):
    "Collect passcodes"

    passcode = []
    # 4 patterns of passcodes
    passFTypePattern = re.compile(
        "[0-9][A-Za-z][A-Za-z][0-9][A-Za-z]*[0-9][A-Za-z][0-9][A-Za-z]")
    passSTypePattern = re.compile("[A-Za-z]*[0-9][0-9][A-Za-z]")
    passTTypePattern = re.compile("82666[0-9]{5,6}")
    passJTypePattern = re.compile("[A-Z0-9]{10}")

    passcode.extend(re.findall(passFTypePattern, htmlSource))
    passcode.extend(re.findall(passSTypePattern, htmlSource))
    passcode.extend(re.findall(passTTypePattern, htmlSource))
    passcode.extend(re.findall(passJTypePattern, htmlSource))

    # Remove passcode with length < 7
    for passOne in passcode:
        if len(passOne) < 7:
            passcode = filter(lambda a: a != passOne, passcode)

    return passcode


def parseGooglePlus():
    "Parse Google+ for heshtags #ingresspasscode and #passcode"
    www = 'https://www.googleapis.com/plus/v1/activities'
    fields = 'items(object/content,updated)'

    searchIPS = {'query': '#ingresspasscode', 'orderBy': 'recent', 'maxResults': '20', 'fields': fields, 'key': keyAPI}
    searchPS = {'query': '#passcode', 'orderBy': 'recent', 'maxResults': '20', 'fields': fields, 'key': keyAPI}

    rIPS = requests.get(www, params=searchIPS)
    rPS = requests.get(www, params=searchPS)

    data = rIPS.json()['items']
    data.extend(rPS.json()['items'])

    # Because of strange working of Google+ API Search
    # We will also fetch data from DeCode Ingress Group and Page
    wwwG = 'https://www.googleapis.com/plus/v1/people/114606795989653285746/activities/public'
    wwwP = 'https://www.googleapis.com/plus/v1/people/111701852247617430859/activities/public'
    parameters = {'maxResults': '20', 'fields': fields, 'key': keyAPI}

    rG = requests.get(wwwG, params=parameters)
    rP = requests.get(wwwP, params=parameters)

    data.extend(rP.json()['items'])
    data.extend(rG.json()['items'])

    return data


def postToIntel(passcode):
    "Post passcode to ingress intel"

    www = 'http://www.ingress.com/rpc/dashboard.redeemReward'

    r = requests.post(www, data='{"passcode": "%s", "method":"dashboard.redeemReward"}' % passcode,
                      headers={
                      'Cookie': cookie,
                      'X-Requested-With': 'XMLHttpRequest',
                      'X-CSRFToken': csrftoken,
                      })

    return r.text

if __name__ == '__main__':

    if checkInputData():

        print 'Run time UTC0 - ' + str(datetime.datetime.now())
        print 'Waiting for new passcodes...'

        deltaTimeRegion = datetime.timedelta(hours=2)
        deltaTimePost = datetime.timedelta(minutes=15)

        accquired = []

        while True:

            try:
                data = parseGooglePlus()
            except:
                print 'Some magic in retrieving. Don`t worry.'
                data = []
            codes = []

            for article in data:
                date, content = article.values()
                date = convertTime(date)
                if (datetime.datetime.now() - date - deltaTimeRegion) < deltaTimePost:
                    codes = collect(content.values()[0])

                    if len(codes) > 0:
                        for code in codes:
                            if code not in accquired:
                                print 'Time now: ' + str(datetime.datetime.now())
                                print 'Accquired passcode on: ' + str(code)
                                print 'Passcode posted on: ' + str(date)
                                try:
                                    print postToIntel(code)
                                    accquired.append(code)
                                except:
                                    print 'Malfunction. We`ll try again after one minute.'
            time.sleep(60)
    else:
        print "Invalid cookies."
