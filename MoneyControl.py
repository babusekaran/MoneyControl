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


class Company(object):
    """docstring for Company"""

    def __init__(self, sector, money_url, name, last_price, p_change, y_low, y_high, market_cap):
        super(Company, self).__init__()
        self.sector = sector
        self.money_url = money_url
        self.name = name
        self.last_price = float(last_price.replace(",",""))
        self.p_change = float(p_change.replace(",",""))
        self.y_low = float(y_low.replace(",",""))
        self.y_high = float(y_high.replace(",",""))
        self.market_cap = float(market_cap.replace(",",""))
        self.ltp_to_low = self.ltp_change_from_low_percent()
        self.ltp_to_high = self.ltp_change_from_high_percent()
        self.high_to_low = self.low_change_from_high_percent()

    def __str__(self):
    	divider = "\n**************************************************************"
        return divider+"\nName      : " + self.name + \
        	 "\nSector     : " + self.sector + \
        	 "\nUrl        : " + self.money_url + \
        	 "\nLTP        : " + str(self.last_price) + \
        	 "\n% Change   : " + str(self.p_change)+\
        	 "\n52wk Low   : " + str(self.y_low)+\
        	 "\n52wk High  : " + str(self.y_high)+\
        	 "\nMarket Cap : " + str(self.market_cap)+\
        	 "\nLTP to Low : " + str(self.ltp_to_low)+" %"\
        	 "\nLTP to High: " + str(self.ltp_to_high)+" %"\
        	 "\nHigh to Low: " + str(self.high_to_low)+" %"+divider

    def ltp_change_from_low_percent(self):
    	return float(float(float(self.last_price-self.y_low)/self.last_price)*100)

    def ltp_change_from_high_percent(self):
    	return float(float(float(self.last_price-self.y_high)/self.last_price)*100)

    def low_change_from_high_percent(self):
    	return float(float(float(self.y_high-self.y_low)/self.y_high)*100)


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

    def __init__(self,exchange):
        super(MoneyControl, self).__init__()
        self.host_url = "https://www.moneycontrol.com"
        self.home_path = "/stocks/marketinfo/marketcap/"
        self.exchange = exchange
        self.sectors = []
        self.sectors_details = {}
        self.get_sectors()
        self.sector_wise_data = {}
        self.all_data = []
        self.current_filter_data = []
        self.collect_data()

    def load_market_cap_page(self, page_path):
        print "Scraping data from -> " + self.host_url + page_path
        return WebScraper.load_page(self.host_url + page_path)

    def get_sectors(self):
        #sector_xpath = "//select[@id='sel_code']/option"
        sector_xpath = "//a[@class='opt_notselected']"
        if self.exchange == 'nse' or self.exchange == 'NSE':
        	self.exchange = 'nse'
        elif self.exchange == 'bse' or self.exchange == 'BSE':
        	self.exchange = 'bse'
        else: self.exchange = 'nse'
        page_data = self.load_market_cap_page(self.home_path+'/'+self.exchange+"/index.html")
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
                y_high = row_data[3].text
                y_low = row_data[4].text
                market_cap = row_data[5].text
                comp_obj = None
                comp_obj = Company(
                    sector, money_url, name, last_price, p_change, y_low, y_high, market_cap)
                if comp_obj != None:
                    self.sector_wise_data[sector].append(comp_obj)
                    self.all_data.append(comp_obj)
        print "Loaded %d portfolio from %d in %s"%(len(self.all_data),len(self.sectors),self.exchange)

if __name__ == '__main__':
	exchange = raw_input("nse or bse ?\n")
	mc = MoneyControl(exchange)



