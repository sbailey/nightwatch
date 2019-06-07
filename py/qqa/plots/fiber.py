import numpy as np
import jinja2
import desimodel.io

import bokeh
import bokeh.plotting as bk
import bokeh.models
from bokeh.embed import components

from astropy.table import Table, join
# from bokeh.models.tickers import FixedTicker
# from bokeh.models.ranges import FactorRange
from bokeh.models import LinearColorMapper, ColorBar, HoverTool #, CustomJS, HTMLTemplateFormatter, NumeralTickFormatter
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter
from bokeh.transform import transform
from bokeh.transform import linear_cmap
import bokeh.palettes as palettes
from ..plots.core import get_colors, plot_histogram


def plot_fibers(source, name, cam=None, width=250, height=270, zmin=None, 
                zmax=None, percentile=None, title=None, hist_x_range=None,
                plate_x_range=None, plate_y_range=None,
                tools='box_select,reset', tooltips=None):
    '''
    ARGS:
        source :  ColumnDataSource object
        name : a string data column in qadata

    Options:
        cam : string ('B', 'R', 'Z') to specify which camera wavelength
        (zmin,zmax) : hardcoded (min,max) to clip data
        percentile : (min,max) percentiles to clip data
        width, height : width and height of graph in pixels
        title : title for the plot
        tools : string of supported features for the plot
        tooltips : hovertool info
        hist_x_range, plate_x_range, plate_y_range : figure ranges to support linking


    Generates a focal plane plot with data per fiber color-coded based on its value
    Generates a histogram of NAME values per fiber
    '''
    #- Focal plane colored scatter plot
    fig = bk.figure(width=width, height=height, title=title, tools=tools, 
                    x_range=plate_x_range, y_range=plate_y_range)

    full_metric = np.array(source.data[name])
    #- Filter data to just this camera
    cameras = np.array(source.data['CAM']).astype(str)
    booleans_metric = np.char.upper(cameras) == cam.upper()
    metric = full_metric[booleans_metric]

    if any(booleans_metric):
        if percentile:
            pmin, pmax = np.percentile(metric, percentile)
            metric = np.clip(metric, pmin, pmax)
        if zmin or zmax:
            metric = np.clip(metric, zmin, zmax)

    #- Generate colors
    mapper = linear_cmap(name, palette, low=min(full_metric), high=max(full_metric),
                         nan_color='gray')
    palette = mapper['transform'].palette
    
    #- Plot only the fibers which measured the metric
    view_metric = CDSView(source=source, filters=[BooleanFilter(booleans_metric)])
        #- TODO: switch to group filter
    s = fig.scatter('X', 'Y', source=source, view=view_metric, color=mapper, 
                    radius=5, alpha=0.7)#, hover_color='firebrick')

    #- Plot the rest of the fibers
    fibers_measured = source.data['FIBER'][booleans_metric]
    ii = ~np.in1d(source.data['FIBER'], fibers_measured)
    booleans_empty = [fiber in ii for fiber in range(len(source.data))]
    view_empty = CDSView(source=source, filters=[BooleanFilter(booleans_empty)])    
    fig.scatter('X', 'Y', source=source, view=view_empty, fill_color='#DDDDDD', radius=2)

    #- Aesthetics: outline the focal plates by camera color, label cameras,
    #- style visual attributes of the figure
    camcolors = dict(B='steelblue', R='firebrick', Z='gray')

    if cam:
        color = camcolors[cam.upper()]
        fig.ellipse(x=[0,], y=[0,], width=830, height=830, fill_color=None,
                    line_color=color, line_alpha=0.5, line_width=2)
        fig.text([-350,], [350,], [cam.upper(),],
            text_color=camcolors[cam.upper()],
            text_align='center', text_baseline='middle')

    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    fig.xaxis.major_tick_line_color = None
    fig.xaxis.minor_tick_line_color = None
    fig.yaxis.major_tick_line_color = None
    fig.yaxis.minor_tick_line_color = None
    fig.outline_line_color = None
    fig.xaxis.axis_line_color = None
    fig.yaxis.axis_line_color = None
    fig.xaxis.major_label_text_font_size = '0pt'
    fig.yaxis.major_label_text_font_size = '0pt'
    
    #- Histogram of values
    hfig = plot_histogram(metric, palette=palette, title=name, width=width,
                          x_range=hist_x_range, num_bins=50)
    
    return fig, hfig
