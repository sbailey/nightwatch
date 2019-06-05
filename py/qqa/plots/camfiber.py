"""
Placeholder: per-camera per-fiber plots
"""
import numpy as np

import jinja2

import bokeh
import bokeh.plotting as bk
from bokeh.embed import components

from ..plots.fiber import plot_fibers


def plot_per_camfiber(data, attribute, cameras, components_dict, percentiles={}, 
                      zmaxs={}, zmins={}):
    '''
    ARGS:
        data : 
        attribute : string corresponding to column name in DATA
        cameras : list of string representing unique camera values
        components_dict : dictionary of html components for rendering
    
    Options:
        percentiles : dictionary of cameras corresponding to (min,max) 
            percentiles to clip data
        zmaxs : dictionary of cameras corresponding to hardcoded max values
            to clip data
        zmins : dictionary of cameras corresponding to hardcoded min values
            to clip data
    
    ***MUTATES ARGUMENT
    Updates components_dict to include key-value pairs to the html components
    for the per camera per fiber plot
        keys are the type of plot (represented as NAME)
        values are a bokeh gridplot object of focal plane figures and histograms
    '''
    data = Table(data)
    if attribute not in data.columns:
        return

	figs_list, hfigs_list = [], []
	for c in cameras:
		fig, hfig = plot_fibers(data, attribute, cam=c, percentile=percentiles.get(c, None),
            zmin=zmins.get(c), zmax=zmaxs.get(c))
		figs_list.append(fig)
		hfigs_list.append(hfig)
	figs = bk.gridplot([figs_list, hfigs_list], toolbar_location='right')
	script, div = components(figs)

	components_dict[attribute] = dict(script=script, div=div)
