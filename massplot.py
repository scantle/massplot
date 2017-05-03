# -*- coding: utf-8 -*-
"""
@author: lelands
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from descartes import PolygonPatch

#-----------------------------------------------------------------------------#
# For faster plotting...
class massplot(object):
    """
    Variables:
        fig
        ax
        axinset
        feature_list
        colors
        marks
        legend_loc
        legend_size
        legend_ncol
        colors_used
        legend_mask
        current_loc

    Methods:
        __init__()
        add_features()
        update_feature()
        drop_features()
        create_legend()
        update_legend()
        set_title()
        create_minimap()
        minimap_current_loc()
        add_to_pdf()

    TODO: List current features method
    """


    def __init__(self, xlims, ylims, xlabel, ylabel, xscale, yscale, figwidth, figheight):

        self.feature_list = []
        self.colors = ['#4e79a7','#f28e2b','#e15759','#76b7b2','#59a14f','#edc948','#b07aa1',
                       '#ff9da7','#9c755f','#bab0ac']
        self.color_mask = [False for i in range(0,len(self.colors))]
        self.legend_mask = []

        self.fig = plt.figure(figsize=(figwidth, figheight))
        self.ax = self.fig.add_subplot(111)

        # Axis settings
        self.ax.set_xlabel(xlabel, fontsize=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.tick_params(axis='x', labelsize=12)
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.yaxis.set_ticks_position('left')

        # Handle if xscale is date
        # TODO: Someday, handle if yscale is date
        if xscale.lower() == 'date':
            # TODO: Make these function arguments (oi!)
            years = mdates.YearLocator()
            months = mdates.MonthLocator()
            yearsFmt = mdates.DateFormatter('%Y')
            self.ax.xaxis.set_major_locator(years)
            self.ax.xaxis.set_major_formatter(yearsFmt)
            self.ax.xaxis.set_minor_locator(months)
            self.ax.set_xlabel('Date', fontsize = 10)
            self.ax.tick_params(axis='x', labelsize = 8)
        else:
            self.ax.set_xscale(xscale)
        self.ax.set_yscale(yscale)
        self.ax.tick_params(axis='x')
        self.ax.xaxis.grid(True, which='minor')
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)


    def add_feature(self, style, color=None, label=None, inlegend=True, empty=False):
        # Add to legend mask list
        self.legend_mask.append(inlegend)
        # Auto assign a color if none given
        if color is None:
            color = self._checkout_color()
        if label is None:
            label = 'New Feature'
        # Add to list, add to plot (in legendable, otherwise)
        feature_index = len(self.feature_list)
        if not empty:
            self.feature_list.append(self.ax.plot([], [], style,
                                                  color=color, label=label)[0])
        if empty:
            # As in, no center
            bg_color = self.ax.get_facecolor()
            self.feature_list.append(self.ax.plot([], [], style,
                                              mec=color, mfc=bg_color,
                                              label=label)[0])
        # Report index for user
        print "New Feature Index: ", feature_index


    def add_features_same_color(self, num_features, style, color=None, inlegend=True):
        # Auto assign a color if none given
        if color is None:
            color = self._checkout_color()
        for i in range(num_features):
            self.add_feature(style, color=color, inlegend=inlegend)


    def add_features(self, num_features, style, inlegend=True):
        for i in range(num_features):
            self.add_feature(style, inlegend=inlegend)


    # For chemheads
    def add_ND_pair_feature(self, style, color=None):
        if color is None:
            color = self._checkout_color()
        # One in the legend
        self.add_feature(style, color, inlegend=True)
        # The assumption is the user will not want ND value in the legend
        # They will instead use the add_legend_ND_feature method
        self.add_feature(style, color, inlegend=False, empty=True)


    # Even crazier
    def mass_add_chem(self, num_locs, num_analytes, symbols, nd=True):
        # Get colors
        color_list = []
        for i in range(num_analytes):
            color_list.append(self._checkout_color())
        for i in range(num_locs):
            print "--------------------Location", i
            for j in range(num_analytes):
                print "----------Analyte", j
                self.add_feature(symbols[i], color_list[j], inlegend=True)
                if nd:
                    self.add_feature(symbols[i], color_list[j],
                                     inlegend=False, empty=True)
        print "All done!"

    def add_legend_ND_feature(self, color=None):
        # TODO: Auto move to end of feature_list when legend is updated
        # TODO: Even better make this a proxy artist:
        # http://matplotlib.org/users/legend_guide.html
        if color is None:
            color = '#666666'
        self.legend_mask.append(True)
        bg_color = self.ax.get_facecolor()
        feature_index = len(self.feature_list)
        self.feature_list.append(self.ax.plot([], [],
                                'o', mec=color, mfc=bg_color,
                                label="Non-Detects")[0])
        print "ND Feature Index: ", feature_index


    def update_feature(self, feature_num, x, y, label=None, inlegend=True):
        x, y = self._strip_to_data([x, y])
        self.feature_list[feature_num].set_data(x, y)
        self.legend_mask[feature_num] = inlegend
        if label is not None:
            self.feature_list[feature_num].set_label(label)


    def mask_feature(self, feature_nums):
        if isinstance(feature_nums, list):
            for i in feature_nums:
                self.update_feature(i, [], [])
                self.legend_mask[i] = False
        if isinstance(feature_nums, int):
            self.update_feature(feature_nums, [], [])
            self.legend_mask[feature_nums] = False


    def remove_feature(self, feature_nums):
        if isinstance(feature_nums, list):
            for i in feature_nums:
                self._checkin_color(self.feature_list[i].get_color())
                del(self.feature_list[i])
                del(self.legend_mask[i])
        if isinstance(feature_nums, int):
            self._checkin_color(self.feature_list[feature_nums].get_color())
            del(self.feature_list[feature_nums])
            del(self.legend_mask[feature_nums])


    def create_legend(self, loc, size, ncol):
        self.legend_loc = loc
        self.legend_size = size
        self.legend_ncol = ncol
        self.update_legend()


    def update_legend(self, ncol=None):
        if ncol is None:
            ncol = self.legend_ncol
        else:
            self.legend_ncol = ncol
        legend_list = [self.feature_list[i] for i, val in enumerate(self.legend_mask) if val]
        labs = [feat.get_label() for feat in legend_list]
        self.ax.legend(legend_list, labs,
                       loc = self.legend_loc,
                       prop={'size':self.legend_size},
                       ncol = self.legend_ncol)

    def set_title(self, title):
        # A very light wrapper
        self.ax.set_title(title)


    def create_minimap(self, map_right, map_bottom, map_w, map_h, x, y, xbuffer,
                       ybuffer, xy_color, xy_size, shapelist=None, shapecolors=None):
        x, y = self._strip_to_data([x, y])
        # right, bottom, w x h
        self.axinset = plt.axes([map_right, map_bottom, map_w, map_h])
        self.axinset.grid(b=None)
        self.axinset.set_facecolor('white')
        if shapelist is not None:
            # Plot Shapefile(s)
            self.add_shapefiles(self.axinset, shapelist, shapecolors)
        # Add coords
        self.axinset.plot(x, y, 'o', color = xy_color, ms = xy_size)
        self.axinset.set_ylim([min(y) - ybuffer, max(y) + ybuffer])
        self.axinset.set_xlim([min(x) - xbuffer, max(x) + xbuffer])
        # Add blank feature for current location
        self.current_loc = self.axinset.plot([], [], 'o')[0]
        # Remove all axes junk
        self._blankify_plot(self.axinset)


    def minimap_current_loc(self, x, y, xy_color, xy_size):
        x, y = self._strip_to_data([x, y])
        self.current_loc.set_data(x, y)
        self.current_loc.set_markerfacecolor(xy_color)
        self.current_loc.set_markeredgecolor(xy_color)
        self.current_loc.set_markersize(xy_size)


    def add_to_pdf(self, pdf_object):
        pdf_object.savefig()


    # Helper "Private" Functions
    def _checkout_color(self):
        color_index = self.color_mask.index(False)
        color = self.colors[color_index]
        self.color_mask[color_index] = True
        return color

    def _checkin_color(self, returned_color):
        # Is it even one of our colors?
        if returned_color in self.colors:
            color_index = self.colors.index(returned_color)
            self.color_mask[color_index] = False

    def _strip_to_data(self, items):
        for i, obj in enumerate(items):
            if isinstance(obj, pd.Series):
                items[i] = obj.values
        return items


    def _blankify_plot(self, axis_object):
        axis_object.tick_params(axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labeltop='off',
            labelbottom='off') # labels along the bottom edge are off
        axis_object.tick_params(axis='y',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            left='off',      # ticks along the bottom edge are off
            right='off',         # ticks along the top edge are off
            labelright='off',
            labelleft='off') # labels along the bottom edge are off
        axis_object.xaxis.set_ticklabels([])
        axis_object.yaxis.set_ticklabels([])


    # Less "private" shapefile functions

    def getShapeType(self, shapeobj):
        # Source: pg4 of
        #https://www.esri.com/library/whitepapers/pdfs/shapefile.pdf
        if shapeobj.shapeType in [1,11,21]:
            return 'point'
        if shapeobj.shapeType in [3,13,23]:
            return 'line'
        if shapeobj.shapeType in [5,15,25]:
            return 'polygon'
        if shapeobj.shapeType in [8,18,28]:
            return 'multipoint'
        if shapeobj.shapeType in [31]:
            return 'multipatch'


    def add_shapefiles(self, axis_object, shapelist, shapecolors):
        for i, item in enumerate(shapelist):
            item_type = self.getShapeType(item)
            if item_type=='polygon':
                for shape in item.iterShapes():
                    axis_object.add_patch(PolygonPatch(shape,
                                        fc=shapecolors[i], ec=shapecolors[i]))
            if item_type=='line':
                for shape in item.iterShapes():
                    x = [j[0] for j in shape.points[:]]
                    y = [j[1] for j in shape.points[:]]
                    axis_object.plot(x,y, color=shapecolors[i])

#--------------------------------------------------------------------------------------------------#