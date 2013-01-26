#-*- coding: utf-8 -*-

import re
import datetime
import time
import requests

#ACSID cookie
acsid = ''
#csrftoken cookie
csrftoken = ''
#Google Key API with G+ ON
keyAPI = ''

cookie = 'ACSID=' + acsid + ';' + 'csrftoken=' + csrftoken


def convertTime(val):
    if '.' not in val:
        return datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S")

    nofrag, frag = val.split(".")
    date = datetime.datetime.strptime(nofrag, "%Y-%m-%dT%H:%M:%S")

    return date


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
        if len(passOne) < 7:
            passcode = filter(lambda a: a != passOne, passcode)

    return passcode


def parseGooglePlus():
    "Parse Google+ for heshtags #ingresspasscode and #passcode"
    www = 'https://www.googleapis.com/plus/v1/activities'
    fields = 'items(object/content,updated)'

    searchIPS = {'query': '#ingresspasscode', 'fields': fields, 'key': keyAPI}
    searchPS = {'query': '#passcode', 'fields': fields, 'key': keyAPI}

    rIPS = requests.get(www, params=searchIPS)
    rPS = requests.get(www, params=searchPS)

    data = rIPS.json()['items']
    data.extend(rPS.json()['items'])

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

    print 'Run time UTC0 - ' + str(datetime.datetime.now())
    print 'Waiting for new passcodes...'

    deltaTimeRegion = datetime.timedelta(hours=2)
    deltaTimePost = datetime.timedelta(minutes=10)

    while True:
        data = parseGooglePlus()
        codes = []

        for article in data:
            date, content = article.values()
            date = convertTime(date)
            if (datetime.datetime.now() - date + deltaTimeRegion) < deltaTimePost:
                codes = collect(content.values()[0])
                if len(codes) > 0:
                    for code in codes:
                        print 'Accquired new passcode: ' + str(code)
                        print postToIntel(code)
        time.sleep(60)