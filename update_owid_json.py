# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 17:04:29 2020

@author: Thijs Weenink

Checks the current owid-covid-data.json file with the one on GitHub.
Downloads a new version if available or if the file doesn't exist.
"""
from update_check import checkForUpdates

def check_data():
    filename = "owid-covid-data.json"
    github_source = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.json"

    try:
        downloaded_new = checkForUpdates(filename, github_source)
    except FileNotFoundError:
        with open("owid-covid-data.json", "w") as new_file:
            new_file.close()
        downloaded_new = checkForUpdates(filename, github_source)

    if downloaded_new == False:
        print("File up to date.")

    return downloaded_new


if __name__ == "__main__":
    check_data()
