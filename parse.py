#!/usr/bin/python

from itertools import islice
import time
import subprocess
import os
import re

from datetime import datetime


def parse(printout):
    parsed_list = []
    parsed = []
    for l in printout.strip().splitlines():
        parsed = []

        cluttered = [e.strip() for e in l.split(' ')]

        for p in cluttered:
            if p:
                parsed.append(p)
        if len(parsed):
            parsed_list.append(parsed)
    return parsed if len(parsed_list) == 1 else parsed_list


def exec_cmd(cmd, check=False):
    nul_f = open(os.devnull, 'w')
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=nul_f,
                               shell=True)
    nul_f.close()
    response = process.communicate()[0].strip()
    return response


COMPUTE_LOG = "memory-monitor-cic-2.log"
MEMSTAT_CSV = "memmonitor.csv"

SRCH_LIST = ["horizon  26786", "horizon  26787"]

RSS_IDX = 6

def datacrunch():

    date_start = "CURRENT TIME AND SYSTEM INFO"

    ps_start = "LARGEST MEM PROCESSES"
    ps_end = "FREE MEMORY"

    date_rec_started = False
    date_lineno = 0
    date_maxline = 2

    rss_list = []
    rss_usage_list = []
 
    srch_dict = {}

    ps_rec_started = False

    date = ""

    with open(COMPUTE_LOG, 'r') as f:

        while True:

            line = f.readline()
            if line:

                if date_start in line:
                    date = ""
                    date_rec_started = True
                
                if date_rec_started:
                    date_lineno += 1

                    if date_lineno == date_maxline:
	                date = ' '.join(line.rstrip('\n').split(' ')[:-2])
                        date = datetime.strptime(date, '%a %b %d %H:%M:%S').strftime("%m%d%H%M%S")
                        date_rec_started = False
                        date_lineno = 0
                        rss_usage_list = [date]

                if date:

                    if (ps_rec_started and (ps_end in line)):

                        for srch in SRCH_LIST:
                            if srch in srch_dict:
                                rss_usage_list.append(srch_dict[srch])
                            else:
                                rss_usage_list.append('0')

                        ps_rec_started = False
                        date = ""
                        rss_list.append(rss_usage_list)
                        rss_usage_list = []
                        srch_dict = {}




                    if ps_rec_started:
                    
                       for srch in SRCH_LIST:
         
                           if srch in line:

                              ps_line = parse(line.rstrip('\n'))
                              print("PS LINE: %s\n" % ps_line)
                              rss = ps_line[RSS_IDX-1]
                              print("RSS: %s\n" % rss)
                              srch_dict[srch] = rss


                    if ps_start in line:
                        ps_rec_started = True



            else:
                break


    with open(MEMSTAT_CSV, 'w') as f:
        for rss_usage_list in rss_list:
            f.write("%s\n" % ','.join(
                                      rss_usage_list
                                     ))
 



def main():
    datacrunch()


if __name__ == '__main__':
    main()



