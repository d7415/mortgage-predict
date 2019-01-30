#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import datetime
import re

loan = 40000000 # pence
rate = 3.00 # percent
start = datetime.datetime.today()
payments = []
ratechanges = []
verbosity = "m" # d, m or s - day, month or summary

def parsedate(pdate):
    if len(pdate) == 6:
        return datetime.datetime.strptime(pdate, "%y%m%d")
    elif len(pdate) == 8:
        return datetime.datetime.strptime(pdate, "%Y%m%d")
    else:
        raise ValueError("Invalid length: %s (%d)" % (pdate, len(pdate)))

for param in sys.argv[1:]:
    if "," in param: # Pair of date,paid or date,aer
        [p1, p2] = param.split(",")
        if p1[0] == "/":
            if p1[-1] != "/":
                pdate = p1[1:]
            else:
                pdate = p1[1:-1]
            amount = p2
        else:
            try:
                parsedate(p1)
                pdate = p1
                amount = p2
            except ValueError:
                try:
                    parsedate(p2)
                    pdate = p2
                    amount = p1
                except:
                    raise ValueError("Unable to find date in '%s'" % (param))
        if amount[-1] == "%":
            ratechanges.append([re.compile(pdate+"$"), amount[:-1]])
        else:
            if amount[0] in "£$":
                amount = amount[1:]
            payments.append([re.compile(pdate+"$"), int(float(amount)*100)])
    elif param[0] in "£$":
        loan = int(float(param[1:])*100)
    elif param[-1] == "%":
        rate = float(param[:-1])
    else:
        start = parsedate(param)

balance = loan
day = start
monthly = start.day
maxlength = start + datetime.timedelta(days=365*50) # 50 year loan
oneday = datetime.timedelta(days=1)
paid = 0
interest = 0
print("%8s %12s %12s %12s %8s" % ("Date", "Balance", "Interest", "Payments", "Rate"))
print("-"*56)
while balance > 0:
    day += oneday
    if day > maxlength:
        print("50 year limit reached")
        break

    daystr = day.strftime("%Y%m%d")
    for rc in ratechanges:
        if rc[0].search(daystr) is not None:
            rate = rc[1]

    balance += balance * rate / 36500
    interest += balance * rate / 36500

    for p in payments:
        if p[0].search(daystr) is not None:
            balance -= p[1]
            paid += p[1]

    if verbosity == "d" or (verbosity == "m" and (day.day == monthly or (day.day < monthly and (day+oneday).month > day.month))):
        print("%8s %12.2f %12.2f %12.2f %7.2f%%" % (daystr, balance/100, interest/100, paid/100, rate))
        paid = 0
        interest = 0

print("-"*56)
print("%8s %12.2f %12.2f %12.2f %7.2f%%" % (day.strftime("%Y%m%d"), balance/100, interest/100, paid/100, rate))
