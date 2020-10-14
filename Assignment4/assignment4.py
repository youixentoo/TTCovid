# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:39:52 2020

@author: gebruiker
"""
import matplotlib.pyplot as plt

from json import load
from os import mkdir, path
from scipy.optimize import curve_fit
from scipy.stats import linregress
from scipy.cluster import hierarchy
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
    
    dn = cluster(df, "population_density", "growth_rate", True)

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
Clustering of the data, based on which columns are specified.
Allows for removal of datapoints in the form of a list, specific by the country name.
'remove = ["Monaco", "Singapore"]'
"""
def cluster(df, col1, col2, save=False, remove=None):
    df = df.fillna(0.0)
    
    if remove:
        df = df.drop(remove)
    
    x = df[col1]
    y = df[col2]
    xy = df[[col1, col2]]
    
    plot_title = "Scatterplot and Dendogram for {} vs {}".format(col1, col2)
    
    fig, (ax1, ax2) = plt.subplots(1,2, figsize=(36,24), gridspec_kw={'width_ratios': [3, 1]}) # Width, Height
    
    link = hierarchy.linkage(xy, "ward")
    dn = hierarchy.dendrogram(link, labels=xy.index, orientation="left")
    slope, intercept, r_value, p_value, std_err = linregress(x,y)
    
    fig.suptitle(plot_title)
    
    ax2.set(xlabel="Location", ylabel="distances", title="Dendrogram")

    ax1.scatter(x, y)
    ax1.set(xlabel=col1, ylabel=col2, title="Scatter plot, Corr: {:.4}, p-value: {:.4}".format(r_value, p_value))
    for i, txt in enumerate(xy.index):
        ax1.annotate(txt, (x.iloc[i], y.iloc[i]))
    
    
    if save:
        save_location = "Clustering"
        try:
            mkdir(save_location)
        except Exception:
            pass
        
        fig.savefig("{}/{}.png".format(save_location, plot_title), bbox_inches="tight", dpi=200)
    
    
    return dn
    
    
    
    
    
    
    
    
    
    
if __name__ == "__main__":
    main()
    
    