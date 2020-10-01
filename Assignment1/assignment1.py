# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 13:05:26 2020

@author: Thijs Weenink

Version 2, added support for multiple/all countries
"""

import matplotlib.pyplot as plt

from json import load
from random import randint
from os import mkdir, path


def main():
    # https://github.com/owid/covid-19-data/tree/master/public/data
    script_cwd = path.dirname(__file__)
    filepath = path.abspath(path.join(script_cwd, "..", "owid-covid-data.json"))
    
    covid_data = get_data(filepath)
    
    countries_list = list(covid_data.keys())
    # print(countries_list)
    
    comparisons = ["total_cases", "new_cases", "total_deaths", "new_deaths"]
    
    # one_country(comparisons, countries_list, covid_data, "FRA")
    
    # selected = ["FRA", "NLD"]
    
    multiple_countries(comparisons, countries_list, covid_data, all_countries=True)


"""
For a single country, leave 'country' as an empty string for a random country
"""
def one_country(comparisons, countries_list, covid_data, country=""):
    try:
        country_index = countries_list.index(country)
    except ValueError:
        country_index = randint(0, len(countries_list)-1)

    selected_country = countries_list[country_index]
    print(selected_country, covid_data[selected_country]["location"])
    
    specific_country = covid_data[selected_country]
    
    for comparison in comparisons:
        dates, compare_data = date_compared_to(specific_country, comparison)
        plot_data_single(dates, compare_data, comparison, specific_country["location"])


"""
For multiple or all countries
"""
def multiple_countries(comparisons, countries_list, covid_data, selected_countries=None, all_countries=False):
    if all_countries:
        selected_countries = countries_list
    
    for comparison in comparisons:
        data_points = {}
        for country in selected_countries:
            country_index = countries_list.index(country)
        
            selected_country = countries_list[country_index]
            # print(selected_country, covid_data[selected_country]["location"])
        
            specific_country = covid_data[selected_country]
            dates, compare_data = date_compared_to(specific_country, comparison)
            
            data_points[country] = (dates, compare_data)
        if all_countries:
            plot_data_multiple(data_points, comparison, 20, 10, True)
        else:
            plot_data_multiple(data_points, comparison, 12, 8)
                         

"""
Loads the data from the json file
"""
def get_data(filename):
    covid_data = load(open(filename))
    return covid_data


"""
Compares the data on date versus whatever is specified
Some entries are 'None', if the entry is 'None' for total_, it copies the data
from the day before. If the entry is of type new_, it sets it to 0.0.
"""
def date_compared_to(country_data, to_compare_to):
    data = country_data["data"]
    data_type = to_compare_to.split("_")[0]
    
    dates = [list_item.get("date") for list_item in data]
    compare_data = []
    for list_item in data:
        temp = list_item.get(to_compare_to)
        if not temp == None:
            compare_data.append(temp)
        else:
            if data_type == "total":
                # First value can also be 'None', sets it to 0.0
                try:
                    compare_data.append(compare_data[-1])
                except IndexError:
                    compare_data.append(0.0)
            else:
                compare_data.append(0.0)
    
    return dates, compare_data
  
  
"""
Plots the data for a single country
"""
def plot_data_single(x, y, comparison, country, f_x = 6, f_y = 4):
    comparison_e = comparison.replace("_", " ")
          
    plot_title = "Date versus {} in {}".format(comparison_e, country)
    
    fig, ax = plt.subplots(figsize=(f_x,f_y))
    
    plt.plot(x, y)
    plt.xticks(rotation=90)
    plt.title(plot_title)
    plt.ylabel("Amount of {}".format(comparison_e))
    plt.xlabel("Dates")
    
    # To limit the amount of dates shown,
    # otherwise the plot becomes unreadable.
    every_nth = len(x) // 17
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
            
    try:
        mkdir(country)
    except Exception:
        pass
    
    plt.savefig("{}/{}.png".format(country, plot_title), bbox_inches="tight", dpi=100)
    
    
"""
Plots the data for multiple countries at once
"""
def plot_data_multiple(data_points, comparison, f_x = 6, f_y = 4, all_countries=False):
    comparison_e = comparison.replace("_", " ")
          
    plot_title = "Date versus {}".format(comparison_e)
    
    fig, ax = plt.subplots(figsize=(f_x,f_y)) # *72 = pixels
    
    countries = list(data_points.keys())
    num_colors = len(countries)
    
    # Selects a color
    cm = plt.get_cmap('tab20')
    ax.set_prop_cycle('color', [cm(1.*i/num_colors) for i in range(num_colors)])
    
    # Plots all the data
    for country in countries:
        x, y = data_points.get(country)
        plt.plot(x, y, label=country)
        
    plt.xticks(rotation=90)
    plt.title(plot_title)
    plt.ylabel("Amount of {}".format(comparison_e))
    plt.xlabel("Dates")
    
    # Determines the amount of columns in the legend
    if num_colors >= (f_y*3):
        columns = num_colors//(f_y*3)
    else:
        columns = 1
        
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, ncol=columns)
    
    # To limit the amount of dates shown,
    # otherwise the plot becomes unreadable.
    ratio = f_x // 6
    every_nth = len(x) // (17*ratio)
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    
    if all_countries:
        dir_name = "All_countries"
    else:
        if len(countries) > 5:
            dir_name = "{}_etc".format("_".join(countries[0:5]))
        else:
            dir_name = "_".join(countries)       

    try:        
        mkdir(dir_name)
    except Exception:
        pass
    
    plt.savefig("{}/{}.png".format(dir_name, plot_title), bbox_inches="tight", dpi=100)



if __name__ == "__main__":
    main()