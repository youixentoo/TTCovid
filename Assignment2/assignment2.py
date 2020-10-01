# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 11:47:34 2020

@author: Thijs Weenink

Plots the total_cases or total_deaths (though not tested) of a single country, multiple countries
or all countries. With the sigmoid fitted line added.
To also plot the growth rates as a barplot, enable it in multiple_countries(). This function 
is not relevant for single_country(). 

There is currently no check for a 'second wave', so if a country has one, the fitted line/growth rate
for that country isn't 100% reliable.
"""
import matplotlib.pyplot as plt

from json import load
from random import randint
from os import mkdir, path
from scipy.optimize import curve_fit
from numpy import median, exp, asarray, linspace

from datetime import datetime

def main():
    # https://github.com/owid/covid-19-data/tree/master/public/data
    script_cwd = path.dirname(__file__)
    filepath = path.abspath(path.join(script_cwd, "..", "owid-covid-data.json"))
    
    covid_data = get_data(filepath)
    start_date = get_start_date(covid_data)

    # Select a country based on country code, only used for single country plotting,
    # leave as an empty string to plot a random country from the list.
    country_code = "ESP"
    comparison = "total_cases"

    countries_list = list(covid_data.keys())
    
    # This country had a growth rate of around 40, making the entire barplot unreadable.
    # countries_list.remove("AIA") # = Anguilla
    # This country had the second highest growth rate.
    # countries_list.remove("HKG") # = Hong Kong

    
    # Check if the selected country code exists, otherwise plot a random one.
    if country_code in countries_list:
        country_data = covid_data.get(country_code)
    else:
        country_index = randint(0, len(countries_list)-1)
        country_data = covid_data.get(countries_list[country_index])


    # single_country(country_data, comparison, start_date)

    selected_countries = ["AFG", "HTI", "CHN", "SDN", "NLD"]

    # selected_countries = countries_list # if you want to do all countries.
    # Not recommended. Remember to also add ', True' to the function call.
    multiple_countries(covid_data, comparison, start_date, selected_countries)


"""
Loads the data from the json file
"""
def get_data(filename):
    covid_data = load(open(filename))
    return covid_data


"""
Gets the earliest date from the data, datetime object
"""
def get_start_date(covid_data):
    min_date = []
    for key, value in covid_data.items():
        min_date.append(datetime.strptime(value.get("data")[0].get("date"), "%Y-%m-%d"))

    return min(min_date)


"""
Main function calls for a single country
"""
def single_country(country_data, comparison, start_date):
    full_name = country_data.get("location")
    population = country_data.get("population")
    data = country_data.get("data")

    days, compared = date_compared_to(data, comparison, start_date)

    compared = (compared / population)*10000

    # Same format as the one used for multiple countries
    data = {full_name:(days, compared)}

    plot_data(data, comparison, 8, 6)

    print(full_name, population)


"""
Main function calls for a multiple or all countries

Add 'True' to the plot_data() call to plot growth rates per country as a barplot.
"""
def multiple_countries(covid_data, comparison, start_date, selected_countries=None, all_countries=False):
    # print(selected_countries)

    # Dictionary to store the data in per country, used to make the plot.
    data_points = {}
    # For-loop to get all the data from the selected data or all countries if selected.
    for country in selected_countries:
        country_data = covid_data.get(country)

        full_name = country_data.get("location")
        population = country_data.get("population")
        data = country_data.get("data")

        days, compared = date_compared_to(data, comparison, start_date)

        compared = (compared / population)*10000

        data_points[country] = (days, compared)

    # Add True at the end to plot growth rates.
    plot_data(data_points, comparison, 20, 15, all_countries)


"""
Compares the data on date versus whatever is specified
Some entries are 'None', if the entry is 'None' for total_, it copies the data
from the day before. If the entry is of type new_, it sets it to 0.0.
The date gets converted to the amount of days since the the start of measuring.
This is global, meaning some countries start at x=0 and others at x=75, etc.
Makes plotting much easier.
"""
def date_compared_to(country_data, to_compare_to, start_date):
    data_type = to_compare_to.split("_")[0]

    # Converting of dates to days since start.
    days = [(datetime.strptime(list_item.get("date"), "%Y-%m-%d")-start_date).days for list_item in country_data]
    compare_data = []
    for list_item in country_data:
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

    # Return as np arrays
    return asarray(days), asarray(compare_data)


# Old sigmoid, I had issues with this one
# def sigmoid(x_time, r, L):
#     y_cases = L / (1 + (L-1)*np.exp(-r*x_time))
#     return y_cases

# https://stackoverflow.com/questions/55725139/fit-sigmoid-function-s-shape-curve-to-data-using-python
# k = growth rate
def sigmoid(x, L, x0, k, b):
    y = L / (1 + exp(-k*(x-x0)))+b
    return (y)

"""
Plots the data
"""
def plot_data(data, comparison, f_x=6, f_y=4, all_countries=False, plot_growth_rate=False):
    
    comparison_e = comparison.replace("_", " ")

    fig, ax = plt.subplots(figsize=(f_x,f_y)) # *72 = pixels

    countries = list(data.keys())
    num_colors = len(countries)*2
    max_fev = 2500*num_colors

    if all_countries:
        plot_title = "{}{} in all countries".format(comparison_e[0].upper(), comparison_e[1::])
    else:
        plot_title = "{}{} in {}".format(comparison_e[0].upper(), comparison_e[1::], ", ".join(countries))

    # Selects a colormap
    cm = plt.get_cmap('tab20')
    ax.set_prop_cycle('color', [cm(1.*i/num_colors) for i in range(num_colors)])

    # Extra, to store the growth rates per country
    growth_rate_per_country = {}

    # Plots all the data and the fitting lines
    for country in countries:
        days, compared = data.get(country)
        p0 = [max(compared), median(days),1,min(compared)]

        popt, pcov = curve_fit(sigmoid, days, compared, p0, maxfev=max_fev)
        
        # Saves the growth rate per country to the dictionary
        growth_rate_per_country[country] = popt[2]
        # print("L: {}, x0: {}, k: {}, b: {}".format(*popt))

        fitted = sigmoid(days, *popt)

        plt.plot(days, compared, ".", label="{}_raw".format(country))
        plt.plot(days, fitted, label="{}_fitted".format(country))

    # 'Opmaak'
    plt.xticks(rotation=90)
    plt.title(plot_title)
    plt.ylabel("Amount of {} per 10000".format(comparison_e))
    plt.xlabel("Days")

    # Determines the amount of columns in the legend
    if num_colors >= (f_y*3):
        columns = num_colors//(f_y*3)
    else:
        columns = 1

    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, ncol=columns)

    # Determines the name of the folder to store the plots in.
    if all_countries:
        dir_name = "All_countries"
    else:
        if len(countries) > 5:
            dir_name = "{}_etc".format("_".join(countries[0:5]))
        else:
            dir_name = "_".join(countries)

    # Makes a folder to store the images in if making multiple pictures.
    try:
        mkdir(dir_name)
    except Exception:
        pass

    # Save the plot in the specific folder.
    plt.savefig("{}/{}.png".format(dir_name, plot_title), bbox_inches="tight", dpi=100)

    # Entirely manual, for showing growth rates as a bar plot.
    if plot_growth_rate:
        plt.close()

        fig, ax = plt.subplots(figsize=(30,8)) # *72 = pixels

        x_values = growth_rate_per_country.keys()
        num_colors = len(x_values)

        bar_plot = plt.bar(x_values, growth_rate_per_country.values())
        plt.xticks(fontsize=8, rotation=90)
        plt.title("Growth rate per country")
        plt.xlabel("Country code")
        plt.ylabel("Growth rate")

        # Coloring of the bars in the bar plot.
        colors = iter(plt.cm.viridis(linspace(0,1,num_colors)))
        for i, bar in enumerate(bar_plot):
            bar.set_color(next(colors))

        plt.savefig("{}/{}.png".format(dir_name, "Growth rate per country"), bbox_inches="tight", dpi=100)



if __name__ == "__main__":
    main()
