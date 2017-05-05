# massplot
A matplotlib wrapper for rapidly creating simple plots. Takes advantage of reusing plot features and just updating data. Contains some special methods for chemistry-based plots.

## Basic Intended Operation
First, a plot object must be initialized using massplot.create(). The constructor method accepts some basic plot parameters to establish the axes of the plot.

```python
import massplot

plot_obj = massplot.create(xlims = [0.1, 100],
                            ylims = [0, 1000],
                            xlabel = 'X axis',
                            ylabel = 'Y axis',
                            xscale ='log',
                            yscale ='linear',
                            figwidth = 11,
                            figheight = 8.5)
```

We don't want to add data to the plot yet - but we do want to create some features that can be used to hold data later on. Colors will be automatically assigned, or can be passed as an argument, but the symbols/style must be passed. You can specify if a feature should be included in the legend (default is `inlegend = True`) Here is a brief example of some of the feature-adding methods in massplot. Each returns the index (indices) of the added features, for refencing during updates.
```python
plot_obj.add_feature(style = '--^', label = 'Triangle Line', inlegend = True, empty = False)
plot_obj.add_features(num_features = 2, style = '--o', inlegend = True)
plot_obj.add_features_same_color(num_features = 2, style = 'o', inlegend = True)
```
For adding lots of chemistry features - number of locations per plot, and how many chemical analytes will displayed from each well. In the example below, 12 features would be created - three analytes for every well, with an extra non-detect (ND) feature for each (2 * 3 * 2). Non-detect features use a empty marker (e.g. a hollow circle) of the same color.
```python
plot_obj.mass_add_chem(num_locs = 2, num_analytes = 3, symbols, nd=True)

# Similarily, add two features
plot_obj.add_ND_pair_feature(style=='o')
```
Next, the legend and a minimap (for data with spatial relationships) can be added. The minimap creates a smaller scatterplot of locations on top of the first plot, and can accept shapefile `pyshp` objects (in a list) to add to the plot. 
```python
plot_obj.create_legend(loc = 'lower right', size = 7, ncol = 1)

# First arguments are map location in the order: right, bottom, width, height
plot_obj.create_minimap(.125, .11, .185, .18,
                        x = data['X'], y = data['Y'],
                        xbuffer = 100, ybuffer = 100,
                        xy_color = 'grey', xy_size = 1,
                        shapelist=[roads, rails], shapecolors=['silver', 'brown'])
```
### Data update loop
From here, you can loop over the data and update features. This is a somewhat involved process that hopefully will be simplified in future versions. The main crux is deciding how to keep track of how many features have been updated, and how many have been not (and should therefore be masked from the current plot). If every plot has the same number of features (e.g. every plot contains chemistry data from 2 wells) its easier. However, this is not always easy. Below is an example of a data update loop routine.

```python
for locations in plot_list:
    subset_data = data[data['location'].isin(locations)] # Pandas dataframe
    
    # Update plot title
    plot_obj.set_title(', '.join(locations)) # Puts a comma and a space between location names
    
    # Update lines
    for i, loc in enumerate(locations):
        # Update one feature for each location
        plot_obj.update_feature(feature_num = i,
                                subset_data[subset_data['location]==loc, 'Date'],
                                subset_data[subset_data['location]==loc, 'Value'],
                                label = loc)
    # If there's leftover features, you should mask them. An example method for tracking is shown here.
    if (len(plot_obj.feature_list) > len(locations)):
        extra_features = len(plot_obj.feature_list) - len(locations)
        plot_obj.mask_feature(len(locations)+1, len(locations) + extra_features - 1)
    
    # Update the legend
    plot_obj.update_legend()
    
    # Update the minimap location
    locx = subset_data['X'].unique()
    locy = subset_data['Y'].unique()
    plot_obj.minimap_current_loc(locx, locy, 'red', 3)
    
    # Add the plot to an open pdf object:
    plot_obj.add_to_pdf(pdf_object)
```
massplot was written with PDFs in mind, but obviously the matplotlib library can output into a variety of formats.

## massplot Motivation
`matplotlib` creates great looking plots - especially with a good [style sheet](https://tonysyu.github.io/raw_content/matplotlib-style-gallery/gallery.html). But it's not really set up to rapidly create endless plots for output, instead focusing on interactive features. While other more optimized plotting packages exist, a common solution to speeding up `matplotlib` is to avoid re-drawing elements of plots and instead simply updating the data of the plot "artists". However, this can be cumbersome and timely to set up. `massplot` provides some structure for effectively using this method and compressing code length.

## Package requirements
Python 2.7X, 3.5+
- matplotlib
- pandas (barely - checks to see if you're passing a series in a few methods)
- descartes (for shapefiles)