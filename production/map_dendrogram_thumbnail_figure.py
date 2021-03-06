"""
Makes a thumbnail showing a cloud in data-space and dendro-space.

"""

from __future__ import division
import os.path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

import astropy.units as u

from dendrogal.production.integrated_map_figure import integrated_map_axes_lb, integrated_map_axes_lv

path = os.path.expanduser("~/Dropbox/Grad School/Research/Milkyway/paper/")

colorbrewer_red = '#e41a1c' 
colorbrewer_blue = '#377eb8'
colorbrewer_green = '#4daf4a'


def single_cloud_lb_thumbnail(fig, ax_limits, dendrogram, catalog, cloud_idx, panel_width=7*u.deg):
    """
    Makes an l, b thumbnail of a single cloud.

    Shows a contour of the emission region used, and a representative ellipse.

    Integrates only over the relevant velocities (twice the RMS in each direction).

    """

    d = dendrogram

    cloud_row = catalog[catalog['_idx'] == cloud_idx]

    velocity_integration = [(cloud_row['v_cen']-3*cloud_row['v_rms']).data[0],
                            (cloud_row['v_cen']+3*cloud_row['v_rms']).data[0]]

    print "Velocity integration limits: {0} km/s".format(velocity_integration)

    ax_lb = integrated_map_axes_lb(fig, ax_limits, d.data, d.wcs, integration_limits=velocity_integration)

    # draw ellipse

    world_coordinates = np.vstack([cloud_row['x_cen'], cloud_row['y_cen'], cloud_row['v_cen']]).T
    lbv_pixels = d.wcs.wcs_world2pix(world_coordinates, 0)

    l_lbv_pixels = lbv_pixels[:,0]
    b_lbv_pixels = lbv_pixels[:,1]
    v_lbv_pixels = lbv_pixels[:,2]

    l_scale_lbv = ax_lb.spatial_scale.value
    b_scale_lbv = ax_lb.spatial_scale.value
    v_scale_lbv = ax_lb.velocity_scale.value

    lb_ell = [Ellipse(xy=zip(l_lbv_pixels, b_lbv_pixels)[i], 
                          angle=cloud_row['position_angle'][i],
                          width=2*cloud_row['major_sigma'][i]/l_scale_lbv, 
                          height=2*cloud_row['minor_sigma'][i]/b_scale_lbv) 
                  for i in range(len(cloud_row))]

    lb_ell2 = [Ellipse(xy=zip(l_lbv_pixels, b_lbv_pixels)[i], 
                          angle=cloud_row['position_angle'][i],
                          width=2*cloud_row['major_sigma'][i]/l_scale_lbv, 
                          height=2*cloud_row['minor_sigma'][i]/b_scale_lbv) 
                  for i in range(len(cloud_row))]

    for e in lb_ell:
        ax_lb.add_artist(e)
        e.set_facecolor('none')
        e.set_edgecolor(colorbrewer_red)
        e.set_linewidth(1.5)
        e.set_zorder(0.95)

    for e in lb_ell2:
        ax_lb.add_artist(e)
        e.set_facecolor('none')
        e.set_edgecolor('white')
        e.set_linewidth(5)
        e.set_alpha(0.8)
        e.set_zorder(0.9)

    cloud_mask = d[cloud_idx].get_mask()
    mask_lb = np.sum(cloud_mask, axis=0).astype('bool')

    ax_lb.contour(mask_lb, levels=[0.5], colors=colorbrewer_blue, linewidths=2, zorder=0.85)
    ax_lb.contour(mask_lb, levels=[0.5], colors='white', linewidths=3, zorder=0.8)

    half_width = (panel_width/2).to(u.deg).value

    ax_lb.set_xlim(l_lbv_pixels-half_width/l_scale_lbv, l_lbv_pixels+half_width/l_scale_lbv)
    ax_lb.set_ylim(b_lbv_pixels-half_width/b_scale_lbv, b_lbv_pixels+half_width/b_scale_lbv)

    return ax_lb


def single_cloud_lv_thumbnail(fig, ax_limits, dendrogram, catalog, cloud_idx, panel_width=7*u.deg, latitude_px_override=None):
    """
    Makes an l, v thumbnail of a single cloud.

    Shows a contour of the emission region used, and a representative ellipse.

    Integrates only over the relevant latitudes (twice the sigma_r in each direction).

    """    

    d = dendrogram

    cloud_row = catalog[catalog['_idx'] == cloud_idx]

    latitude_integration = [(cloud_row['y_cen']-3*cloud_row['radius']).data[0],
                            (cloud_row['y_cen']+3*cloud_row['radius']).data[0]]

    print "Latitude integration limits: {0} deg".format(latitude_integration)

    ax_lv = integrated_map_axes_lv(fig, ax_limits, d.data, d.wcs, integration_limits=latitude_integration, latitude_px_override=latitude_px_override)

    # draw ellipse

    world_coordinates = np.vstack([cloud_row['x_cen'], cloud_row['y_cen'], cloud_row['v_cen']]).T
    lbv_pixels = d.wcs.wcs_world2pix(world_coordinates, 0)

    l_lbv_pixels = lbv_pixels[:,0]
    b_lbv_pixels = lbv_pixels[:,1]
    v_lbv_pixels = lbv_pixels[:,2]

    l_scale_lbv = ax_lv.spatial_scale.value
    b_scale_lbv = ax_lv.spatial_scale.value
    v_scale_lbv = ax_lv.velocity_scale.value

    lv_ells = [Ellipse(xy=zip(l_lbv_pixels, v_lbv_pixels)[i], 
                       width=2*cloud_row['major_sigma'][i]/l_scale_lbv, 
                       height=2*cloud_row['v_rms'][i]/v_scale_lbv) for i in range(len(cloud_row))]

    lv_ells2 = [Ellipse(xy=zip(l_lbv_pixels, v_lbv_pixels)[i], 
                       width=2*cloud_row['major_sigma'][i]/l_scale_lbv, 
                       height=2*cloud_row['v_rms'][i]/v_scale_lbv) for i in range(len(cloud_row))]

    for e in lv_ells:
        ax_lv.add_artist(e)
        e.set_facecolor('none')
        e.set_edgecolor(colorbrewer_red)
        e.set_linewidth(1.5)
        e.set_zorder(0.95)

    for e in lv_ells2:
        ax_lv.add_artist(e)
        e.set_facecolor('none')
        e.set_edgecolor('white')
        e.set_linewidth(5)
        e.set_alpha(0.8)
        e.set_zorder(0.9)    

    cloud_mask = d[cloud_idx].get_mask()
    mask_lv = np.sum(cloud_mask, axis=1).astype('bool')

    ax_lv.contour(mask_lv, levels=[0.5], colors=colorbrewer_blue, linewidths=2, zorder=0.85)
    ax_lv.contour(mask_lv, levels=[0.5], colors='white', linewidths=3, zorder=0.8)

    half_width = (panel_width/2).to(u.deg).value
    velocity_half_width = 17.5/3.5 * half_width

    # set x & y limits
    ax_lv.set_xlim(l_lbv_pixels-half_width/l_scale_lbv, l_lbv_pixels+half_width/l_scale_lbv)
    ax_lv.set_ylim(v_lbv_pixels-velocity_half_width/v_scale_lbv, v_lbv_pixels+velocity_half_width/v_scale_lbv)

    return ax_lv


def single_cloud_dendro_thumbnail(ax, dendrogram, cloud_idx):
    """
    Makes a dendrogram thumbnail for a single cloud.

    Highlights the appropriate branches (and substructure of course).

    Zooms the dendrogram to the right location.

    """

    d = dendrogram

    p = d.plotter()

    p.plot_tree(ax, color='black')

    p.plot_tree(ax, structure=[d[cloud_idx]], color=colorbrewer_blue, lw=2)

    # everything below is machinery to zoom the figure reasonably
    structures = d[cloud_idx].descendants + [d[cloud_idx]]
    structure_positions = [p._cached_positions[x] for x in structures]
    min_position = min(structure_positions)
    max_position = max(structure_positions)
    range_positions = max(max_position - min_position, 10)

    ax.set_xlim(min_position - range_positions/2, max_position + range_positions/2)

    vmin_list = [x.vmin for x in structures]
    vmax_list = [x.vmax for x in structures]

    min_vmin = min(vmin_list)
    max_vmax = max(max(vmax_list),1)
    v_range = max_vmax - min_vmin

    ax.set_ylim(min_vmin - v_range/10, max_vmax + v_range/10)
    plt.setp(ax.get_xticklabels(), visible=False)

    return p



def make_thumbnail_dendro_figure(dendrogram, catalog, cloud_idx, panel_width=7*u.deg, latitude_px_override=None):

    d = dendrogram
    cloud_row = catalog[catalog['_idx'] == cloud_idx]    

    fig = plt.figure()

    # draw a dendrogram on ax_dendro
    ax_dendro = fig.add_subplot(122)
    p = single_cloud_dendro_thumbnail(ax_dendro, d, cloud_idx)

    ax_dendro.set_ylabel("Intensity (K)")
    # ax_dendro.set_title('cloud structure IDx: {0}'.format(cloud_idx))

    # draw maps on ax_lb & ax_lv
    ax_lb_limits = [0.1, 0.55, 0.35, 0.35]
    ax_lb = single_cloud_lb_thumbnail(fig, ax_lb_limits, d, catalog, cloud_idx, panel_width=panel_width)

    lb_lon = ax_lb.coords['glon']
    lb_lon.set_ticks(spacing=2*u.deg, color='white', exclude_overlapping=True)
    lb_lon.display_minor_ticks(True)
    lb_lon.set_axislabel(r"$l$ (deg)", minpad=1.5)

    lb_lat = ax_lb.coords['glat']
    lb_lat.set_ticks(spacing=2*u.deg, color='white', exclude_overlapping=True)
    lb_lat.display_minor_ticks(True)
    lb_lat.set_axislabel(r"$b$ (deg)", minpad=1.5)


    ax_lv_limits =  [0.1, 0.1, 0.35, 0.35]  
    ax_lv = single_cloud_lv_thumbnail(fig, ax_lv_limits, d, catalog, cloud_idx, panel_width=panel_width, latitude_px_override=latitude_px_override)

    lv_lon = ax_lv.coords['glon']
    lv_lon.set_ticks(spacing=2*u.deg, color='white', exclude_overlapping=True)
    lv_lon.display_minor_ticks(True)
    lv_lon.set_axislabel(r"$l$ (deg)", minpad=1.5)

    vlsr = ax_lv.coords['vopt']
    vlsr.set_ticks(spacing=10*u.m/u.s, color='white', exclude_overlapping=True) # erroneous units - why!?
    vlsr.display_minor_ticks(True)
    vlsr.set_axislabel(r"$v_{LSR}$ (km s$^{-1}$)")
    vlsr.set_ticklabel_position('lr')

    fig.ax_dendro = ax_dendro
    fig.ax_lb = ax_lb
    fig.ax_lv = ax_lv

    return fig
