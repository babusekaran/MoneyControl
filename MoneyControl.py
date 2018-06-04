import time
import calendar
import requests
import hashlib
import random
import mimetypes
import os
from lxml import html
import xml.etree.ElementTree as ET
from requests import ConnectionError


host_url = "https://www.moneycontrol.com"
market_cap_path = "/stocks/marketinfo/marketcap/nse/"
market_cap_index = market_cap_path + "index.html"


class Company(object):
    """docstring for Company"""

    def __init__(self, sector, money_url, name, last_price, p_change, y_low, y_high, market_cap):
        super(Company, self).__init__()
        self.sector = sector
        self.money_url = money_url
        self.name = name
        self.last_price = last_price
        self.p_change = p_change
        self.y_low = y_low
        self.y_high = y_high
        self.market_cap = market_cap

    def __str__(self):
    	divider = "\n**************************************************************"
        return divider+"\nName      : " + self.name + \
        	 "\nSector    : " + self.sector + \
        	 "\nUrl       : " + self.money_url + \
        	 "\nLTP       : " + self.last_price + \
        	 "\n% Change  : " + self.p_change+\
        	 "\n52wk Low  : " + self.y_low+\
        	 "\n52wk High : " + self.y_high+\
        	 "\nMarket Cap: " + self.market_cap+divider



class WebScraper(object):
    """docstring for WebScraper"""

    def __init__(self, arg):
        super(WebScraper, self).__init__()

    @staticmethod
    def load_page(page_url):
        return requests.get(page_url)

    @staticmethod
    def scrape_page(page_data, xpath_criteria):
        page_to_scrape_tree = html.fromstring(page_data.content)
        return (page_to_scrape_tree.xpath(xpath_criteria))


class MoneyControl(object):
    """docstring for MoneyControl"""

    def __init__(self):
        super(MoneyControl, self).__init__()
        self.sectors = []
        self.sectors_details = {}
        self.get_sectors()
        self.sector_wise_data = {}
        self.all_data = []
        self.collect_data()
        print "Collected %d portfolios from %d sectors" %(len(self.all_data),len(self.sectors))

    def load_market_cap_page(self, page_path):
        print "Scraping data from -> " + host_url + page_path
        return WebScraper.load_page(host_url + page_path)

    def get_sectors(self):
        #sector_xpath = "//select[@id='sel_code']/option"
        sector_xpath = "//a[@class='opt_notselected']"
        page_data = self.load_market_cap_page(market_cap_index)
        sectors = WebScraper.scrape_page(page_data, sector_xpath)
        for sec in sectors:
            self.sectors_details[sec.text] = sec.get("href")
            self.sectors.append(sec.text)
        #self.sectors.append("Top 100")
        #self.sectors_details["Top 100"] = market_cap_index

    def collect_data(self):
        company_xpath = "//tr/td/a[@class='bl_12']/b"
        for sector in self.sectors:
            self.sector_wise_data[sector] = []
            company_list = []
            page_data = self.load_market_cap_page(self.sectors_details[sector])
            companies = WebScraper.scrape_page(page_data, company_xpath)
            for company in companies:
                company_row = company.getparent().getparent().getparent()
                row_data = company_row.getchildren()
                money_url = row_data[0].getchildren()[0].get("href")
                name = company.text
                last_price = row_data[1].text
                p_change = row_data[2].text
                y_low = row_data[3].text
                y_high = row_data[4].text
                market_cap = row_data[5].text
                comp_obj = None
                comp_obj = Company(
                    sector, money_url, name, last_price, p_change, y_low, y_high, market_cap)
                if comp_obj != None:
                    self.sector_wise_data[sector].append(comp_obj)
                    self.all_data.append(comp_obj)


if __name__ == '__main__':
    mc = MoneyControl()


