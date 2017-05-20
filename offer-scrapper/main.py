#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import ceil
from bs4 import BeautifulSoup
import urllib
import sys, os
import subprocess as sp
import difflib
import shutil
import re
import random
import pickle

from utils import Colors
from args import Args

page=1
URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165_111/niveaux-3_2_9/page-" + str(page) + ".html"
result_file="/home/marrakchino/github/letudiant-offers-scrapper/.results.txt"
tmp_result_file="/home/marrakchino/github/letudiant-offers-scrapper/.results.txt.tmp"
args = Args()

def next_page():
    global URL
    global page
    URL=URL.replace("page-" + str(page), "page-" + str(page+1))
    page += 1

if args.number_of_pages != None and args.number_of_days != None:
    print("You can only specify a number of pages or a number of days, incompatible arguments.")
    exit(1)

def parse_pages(n, filter=[], new=False, interactive=False):

    global page
    global URL

    offers_ready_to_be_dumped=[[] for _ in range(n * 10)]
    offer_i = 0
    offer_url_list=[]
    while page <= n:
        r=urllib.urlopen(URL)
        soup=BeautifulSoup(r)

        offer_titles=soup.find_all("a", class_="c-search-result__title")
        offer_url_list.extend([offer_titles[j]['href'] for j in range(len(offer_titles))])
        offer_companies=soup.find_all("span", class_="  ")
        offer_locations=soup.find_all("span", class_="  u-typo-italic ")
        
        if len(offer_titles) != len(offer_companies):
            print("The number of offers doesn't correspond to the number of companies")
            exit(1)

        k=0
        while k < len(offer_titles):
            title=offer_titles[k].text
            company=offer_companies[k].text
            location=offer_locations[k].text
            k+=1

            # silence 'not-so-exciting' offers' locations
            if len(location) > 35:
                location=location.split(",", 1)[0] + " ..."

            # no need for the publication date
            if title.find("Publi") != -1:
                title=title[:title.find("Publi") - 1]

            def replace_accents(s):
                s.replace(u"é", "e")
                s.replace(u"è", "e")
                s.replace(u"ê", "e")
                s.replace(u"â", "a")
                s.replace(u"à", "a")
                s.replace(u"û", "u")
                s.replace(u"î", "offer_i")
                s.replace(u"ô", "o")
                return s

            # offers are appended in their order of display
            offers_ready_to_be_dumped[offer_i].append(replace_accents(company))
            offers_ready_to_be_dumped[offer_i].append(replace_accents(title))
            offers_ready_to_be_dumped[offer_i].append(replace_accents(location))


            def dump_results():
                pickle.dump(offers_ready_to_be_dumped, open(tmp_result_file, "wb"))

            def show_results():
                #TODO: FIX
                if new:
                    previous_content = pickle.load(open(result_file, "rb"))
                    fresh_content = pickle.load(open(tmp_result_file, "rb"))
                    for offer in [off for off in previous_content+fresh_content if (off not in fresh_content) or (off not in previous_content)]:
                        tmp_result=Colors.GREEN + "[" +  "]" + Colors.BOLD + offer[0] + Colors.ENDC + Colors.GREEN + offer[1] + Colors.BLUE + offer[2] + Colors.ENDC
                        print(tmp_result)
                            
                else:
                    dumped_content=pickle.load(open(tmp_result_file, "rb"))
                    os.rename(tmp_result_file, result_file)

                    if filter == None:
                        for offer_i in range(len(dumped_content)):
                            if offer_i % 10 == 0:
                                print(Colors.HEADER + "Page" + str(offer_i / 10 + 1))

                            tmp_result=Colors.GREEN + "[" + str(offer_i) + "]" + Colors.BOLD + dumped_content[offer_i][0] + Colors.ENDC + Colors.GREEN + dumped_content[offer_i][1] + Colors.BLUE + dumped_content[offer_i][2] + Colors.ENDC
                            print(tmp_result)

                    else:
                        for offer_i in range(len(dumped_content)):
                            if offer_i % 10 == 0:
                                print(Colors.HEADER + "Page" + str(offer_i / 10 + 1))
                            for f in filter:
                                if f in dumped_content[offer_i][1].lower() or f in dumped_content[offer_i][2].lower():
                                    tmp_result=Colors.GREEN + "[" + str(offer_i) + "]" + Colors.BOLD + dumped_content[offer_i][0] + Colors.ENDC + Colors.GREEN + dumped_content[offer_i][1] + Colors.BLUE + dumped_content[offer_i][2] + Colors.ENDC
                                    print(tmp_result)
                                
            offer_i += 1

        next_page()

    dump_results()
    show_results()

    if interactive:
        def select_offer(query):
            offer_url=re.sub(r"\/stages-etudiants.*", offer_url_list[int(query)], URL)
            r_offer=urllib.urlopen(offer_url)
            r_soup=BeautifulSoup(r_offer)
            
            # Unused
            # paragraphs=r_soup.find_all('h5', text=False)

            print("=" * 150)
            for l in range(len(r_soup.find_all('p'))):
                print(Colors.YELLOW + (r_soup.find_all('p')[l].text) + Colors.ENDC)
            print("=" * 150)

            
        while (True):
            query=raw_input(Colors.UNDERLINE + "Enter your query (q to quit):" + Colors.ENDC + " ")
            if (query.lower() == "q"):
                break
            else:
                if (int(query) < 10 * n):
                    select_offer(query)
                else:
                    print("Wrong number, try again.")

    # clear temporary file
    if os.path.exists(tmp_result_file):
        os.remove(tmp_result_file)


def parse_days(n, filter=[]):
    print("Not yet implemented")

def parse_new():
    print("Not yet implemented")


def parse_company(company_name):
    print("Not yet implemented")

def main():
    if args.number_of_pages:
        parse_pages(args.number_of_pages, args.filter_search, args.new, args.interactive_mode)

    elif args.number_of_days:
        parse_days(args.number_of_days, args.filter_search)

    else: # Default
        parse_pages(args.number_of_pages, args.filter_search, args.new, args.interactive_mode)

if __name__ == "__main__":
    main()
