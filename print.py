from selenium import webdriver
import  selenium.webdriver.support.ui as UI
import time
import csv
import pandas as pd

# 02.05.2019
# This script intends to scrape data from CHP elections web page, its address is
# given below. After cloning the repo to your local, change chromedriver path parameter
# in "driver" variable below. If you are on Windows, don't forget to add ".exe"
# extension to chromedriver path.


# TODO!: Write a function that scrapes all the details info of a ballot box, on
# the page directed to after successful filling of the form with province, district
# and ballot selection.
# WARNING!: ballots.csv has not yet been completed, its only done until Mardin province.
# Run this iteration to collect full connection info for ballot boxes.
# TODO!: Make a variable for time.sleep stops while making selection between dropdowns.
# Also, find the ideal duration for the browser to wait, and update 2 second parameter
# of time.sleep to this ideal value. Selenium normally returns the error of
# "Stale Element Reference Exception" when function ran without any wait.
# TODO!: Makes functions of save_to_csv of district, province etc. data
driver = webdriver.Chrome(executable_path="/Users/umutirmaksever/Documents/python_work_mac/chp_sts_scrape/chromedriver")
chp_site = "https://sts.chp.org.tr/"

# Radio button in UI to switch to "Yurtiçi Sandık" option
radio_box_xpath = ('//*[@id="rdveriKaynagi_1"]')
provinces_xpath = ('')

# HTML name properties of select dropdowns, these include necessary id and name
# info of provinces, districts and ballot boxes.
provinces_tag_name = "ddlIller"
districts_tag_name = "ddlIlceler"
ballots_tag_name = "ddlSandiklar"
driver.get(chp_site)

# Clicking "Yurtiçi Sandık" radio_box
radio_box = driver.find_elements_by_xpath(radio_box_xpath)[0]
radio_box.click()

# Gets all the provinces
provinces = driver.find_element_by_name(provinces_tag_name)
provinces = provinces.find_elements_by_tag_name("option")
provinces[0].get_attribute("value")

# Creates a dictionary of provinces. Format is {province_id: province_name}
provinces_dict = {}
for option in provinces[1:]:
    option_value = option.get_attribute("value")
    province_name = option.text
    provinces_dict[option_value] = province_name

# Saves provinces list to "provinces.csv"
with open("provinces.csv", "w+", encoding="utf-8") as provinces_csv:
    provinces_csv.write("province_id, province_name\n")
    for key in provinces_dict.keys():
        provinces_csv.write("{}, {}\n".format(key, provinces_dict[key]))


# Collects the districts information into a list.
# See relevant csv file for the structure.
districts_list = []
for province in provinces_dict.items():
    province_options = driver.find_element_by_name(provinces_tag_name)
    select_provinces = UI.Select(province_options)
    select_provinces.select_by_value(province[0])
    time.sleep(2)

    district_select_tag = driver.find_element_by_name(districts_tag_name)
    district_options = district_select_tag.find_elements_by_tag_name("option")
    for district in district_options[1:]:
        district_id = district.get_attribute("value")
        district_name = district.text
        district_info = {
            "related_province_id": province[0],
            "related_province_name": province[1],
            "district_id": district_id,
            "district_name": district_name
        }
        districts_list.append(district_info)
    print("At province: {}".format(province[0]))
print(districts_list)

# Converts districts list to pandas DataFrame and exports as "districts.csv"
districts_pd = pd.DataFrame(districts_list)
districts_pd.to_csv("districts.csv")

# This function collects the list of ballot boxes per district. Returns a list of
# ballot box info, including related district and province ids and names.
def get_ballot_info(province_id, district_id):
    province_options = driver.find_element_by_name(provinces_tag_name)
    select_provinces = UI.Select(province_options)
    select_provinces.select_by_value(str(province_id))
    province_name = provinces_dict[str(province_id)]

    time.sleep(2)

    district_options = driver.find_element_by_name(districts_tag_name)
    select_districts = UI.Select(district_options)
    select_districts.select_by_value(str(district_id))
    district_name = districts_pd[districts_pd["district_id"] == str(district_id)].iloc[0]["district_name"]
    time.sleep(2)

    ballot_select_tag = driver.find_element_by_name(ballots_tag_name)
    ballot_options = ballot_select_tag.find_elements_by_tag_name("option")

    ballots = []
    for ballot in ballot_options:
        ballot_id = ballot.get_attribute("value")
        ballot_number = ballot.text
        ballot_info = {
            "related_province_id": province_id,
            "related_province_name": province_name,
            "related_district_id": district_id,
            "related_district_name": district_name,
            "ballot_id": ballot_id,
            "ballot_number": ballot_number
        }

        ballots.append(ballot_info)
    return ballots

# for province_id in provinces_dict.keys():
#     districts_of_province = districts_pd[districts_pd["related_province_id"] == province_id]
#     for district_id in districts_of_province["district_id"]:
#         ballots_of_district = get_ballot_info(str(province_id), district_id)
#         print("Getting ballots of : {} - {}province_id, district_id)
#         # print(district_id)
#         # ballots_of_district = get_ballot_info(province_id, district_id)
#         for ballot in ballots_of_district:
#             ballots_list.append(ballot)

ballots_list = []
districts_pd[["district_id", "related_province_id"]]

# Iterates over each district, and collects ballot box id and name.
# WARNING!: Full iteration of this loop ideally takes 75 minutes. Called function
# waits for two seconds between each dropbox and one iteration normalls takes 4-7 seconds.
# @Onur Mat bunun hakkında konuşalım mı bi telefonda?
for district in districts_pd[["district_id", "related_province_id"]].iterrows():
    province_id = district[1]["related_province_id"]
    district_id = district[1]["district_id"]
    ballots_of_district = get_ballot_info(str(province_id), str(district_id))
    print("Getting ballots - Province: {}, District: {}".format(province_id, district_id))
    for ballot in ballots_of_district:
        ballots_list.append(ballot)

# Converts ballots list to pandas DataFrame and exports it to "ballots.csv"
ballots_pd = pd.DataFrame(ballots_list)
ballots_pd.to_csv("ballots.csv")

# This function makes selection on the form and clicks the sumbit button. Directed
# page consists all the details about respective ballot.
def get_details_page(ballot_id, related_district_id, related_province_id):
    province_options = driver.find_element_by_name(provinces_tag_name)
    select_provinces = UI.Select(province_options)
    select_provinces.select_by_value(str(related_province_id))
    time.sleep(2)

    district_options = driver.find_element_by_name(districts_tag_name)
    select_districts = UI.Select(district_options)
    select_districts.select_by_value(str(related_district_id))
    time.sleep(2)

    ballot_options = driver.find_element_by_name(ballots_tag_name)
    select_ballots = UI.Select(ballot_options)
    select_ballots.select_by_value(str(ballot_id))

    time.sleep(2)
    submit_button = driver.find_element_by_name("btnSorgula")
    submit_button.click()

get_details_page(3234196, 650, 1)
