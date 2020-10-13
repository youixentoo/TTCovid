# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 11:31:07 2020

@author: gebruiker
"""
import matplotlib.pyplot as plt

from json import load
from os import mkdir, path
from scipy.optimize import curve_fit
from scipy.stats import linregress
from numpy import median, exp, linspace
from pandas import DataFrame


def main():
    max_days = 150
    script_cwd = path.dirname(__file__)
    filepath = path.abspath(path.join(script_cwd, "..", "owid-covid-data.json"))

    covid_data = get_data(filepath)
    
    metadata_columns =  ["population_density",
                         "median_age", "aged_65_older", "aged_70_older","gdp_per_capita","life_expectancy",
                         "human_development_index", "growth_rate", "death_rate"
                        ]
    
    metadata, names = get_metadata(covid_data, metadata_columns, max_days)
    
    df = create_dataframe(metadata, names, metadata_columns)
    
    for item in metadata_columns:
        plot_both(df, item, True)
        
    # t = df.corr("human_development_index", "death_rate")
    # print(t)
    
    # plot_data_sc(df, "human_development_index", "death_rate", "death_rate vs human_development_index")
    
    # for item in metadata_columns:
    #     if not item == "growth_rate" or not item == "death_rate":
    #         plot_data_sc(df, item, "growth_rate", "growth_rate vs {}".format(item), "Growth_Rate")
    #         plot_data_sc(df, item, "death_rate", "death_rate vs {}".format(item), "Death_Rate")
    
    
""" 
Create the dataframe
"""
def create_dataframe(metadata, names, columns):
    df = DataFrame(metadata)
    df.columns = columns
    df.index = names
    
    return df
    
"""
Loads the data from the json file
"""
def get_data(filename):
    covid_data = load(open(filename))
    return covid_data



"""
Get the metadata
"""
def get_metadata(covid_data, metadata_columns, max_days):
    metadata = []
    names = []

    for key, value in covid_data.items():
        total_cases = extract_data(value, max_days, "total_cases")
        total_deaths = extract_data(value, max_days, "total_deaths")
    
        growth_rate = get_rate(total_cases)
        
        if growth_rate != -1.0 and not None:
            death_rate = get_rate(total_deaths)
            names.append(value.get("location"))

            metadata_entries = [value.get(item) for item in metadata_columns[0:len(metadata_columns)-2]]
            metadata_entries.append(growth_rate)
            metadata_entries.append(death_rate)

            metadata.append(metadata_entries)

    return (metadata, names)


# https://stackoverflow.com/questions/55725139/fit-sigmoid-function-s-shape-curve-to-data-using-python
# k = growth rate
def sigmoid(x, L, x0, k, b):
    y = L / (1 + exp(-k*(x-x0)))+b
    return (y)

"""
Calculates the growth rate of the dataset.

Used for the 'growth_rate' and 'death_rate' in this script.

Returns None if there is any error when trying to calculate the curve.
"""
def get_rate(data):
    days = len(data)
    try:
        p0 = [max(data), median(days),1,min(data)]
        popt, pcov = curve_fit(sigmoid, days, data, p0)
        
        return popt[2]
    except Exception as exc:
        print(exc.with_traceback(exc.__traceback__))
        return None


"""
Gets the 'total_cases' or 'total_deaths' data based on the specific datatype.
None values are changed to the previous non-None value.
"""
def extract_data(value, max_days, datatype):
    cases = []
        
    for i, data in enumerate(value.get("data")):
        if i >= max_days:
            break
        
        tc = data.get(datatype)
        if not tc == None:
            cases.append(tc)
        else:
            # First value can also be 'None', sets it to 0.0
            try:
                cases.append(cases[-1])
            except IndexError:
                cases.append(0.0)
    
    return cases


"""
For plotting 1 scatterplot.
"""
def plot_data_sc(df, col1, col2, plot_title, location=None):
    without_nan_df = df.dropna()
    
    sc_plot = df.plot(col1, col2, label="Data points", kind="scatter")
    sc_plot.set_title(plot_title)
    
    # Linear regression from scipy. 'r_value' is the Correlation coefficient.
    slope, intercept, r_value, p_value, std_err = linregress(without_nan_df[col1], without_nan_df[col2])

    min_x, max_x = sc_plot.get_xlim()

    x = linspace(min_x, max_x)
    sc_plot.plot(x, intercept + slope*x, 'r', label='Regression line\nCor. Coef: {:.4}'.format(r_value))
    sc_plot.legend(bbox_to_anchor=(1.05, 1), loc=2)
    
    if location:
        try:
            mkdir(location)
        except Exception:
            pass
        
        fig = plt.gcf() # Gets the current figure, needed to save them.
        
        fig.savefig("{}/{}.png".format(location, plot_title), bbox_inches="tight", dpi=100)


"""
Plots the death_rate and growth_rates in the same plot, on different axis. Allows for easier comparisons.

Uses scipy's linregress function to calculate the linear regression and the correlation coefficient (r_value).
"""
def plot_both(df, compare_col, save=False):
    without_nan_df = df.dropna()  
    plot_title = "Growth and Death rate vs {}".format(compare_col)
    
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(8,8))
    
    fig.suptitle(plot_title)
    
    ### Growth Rate ###
    ax1.scatter(df[compare_col], df["growth_rate"], color="tab:blue", label="Data points growth rate")
    
    slope, intercept, r_value, p_value, std_err = linregress(without_nan_df[compare_col], without_nan_df["growth_rate"])
    min_x, max_x = ax1.get_xlim()
    x = linspace(min_x, max_x)
    
    ax1.plot(x, intercept + slope*x, color="tab:orange", label='GR Regression line\nCor. Coef: {:.4}, P-value: {:.4}'.format(r_value, p_value))
    ax1.legend(bbox_to_anchor=(1.05, 1), loc=2)
    ax1.set(xlabel=compare_col, ylabel="growth_rate")
    
    ### Death Rate ###
    ax2.scatter(df[compare_col], df["death_rate"], color="tab:gray", label="Data points death rate")
    
    slope, intercept, r_value, p_value, std_err = linregress(without_nan_df[compare_col], without_nan_df["death_rate"])
    min_x, max_x = ax1.get_xlim()
    x = linspace(min_x, max_x)
    
    ax2.plot(x, intercept + slope*x, color="tab:red", label='DR Regression line\nCor. Coef: {:.4}, P-value: {:.4}'.format(r_value, p_value))
    ax2.legend(bbox_to_anchor=(1.05, 1), loc=2)
    ax2.set(xlabel=compare_col, ylabel="death_rate")
    
    if save:
        save_location = "GRDR"
        try:
            mkdir(save_location)
        except Exception:
            pass
        
        fig.savefig("{}/{}.png".format(save_location, plot_title), bbox_inches="tight", dpi=100)



if __name__ == "__main__":
    main()