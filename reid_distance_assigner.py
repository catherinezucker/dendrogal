"""
Some python code to interface with Mark Reid's fortran tool.

Hopefully I can figure out how to do this in a non-boneheaded way.

"""

from __future__ import division

import subprocess
from subprocess import Popen, PIPE, STDOUT

import numpy as np

import astropy.table
from astropy.coordinates import Galactic
import astropy.units as u
import astropy.constants as c


def test_reid_distances():

    test_string = "test    010203.04 121314.5 -10 1"

    f = open('source_file.dat', 'w')
    f.write(test_string)
    f.close()

    p = Popen(
        ['/Users/tsrice/Documents/Code/mark_reid_kdist/revised_kinematic_distance'],
        shell = False, stdin=PIPE, stdout=PIPE)

    output, error = p.communicate()

    print output
    print error

    lines_of_data = [x for x in output.split('\n') if '!' not in x]

    kd_output = astropy.table.Table.read(lines_of_data, format='ascii')
    
    kd_output.rename_column('col1', 'Source')
    kd_output.rename_column('col2', 'gal_long')
    kd_output.rename_column('col3', 'gal_lat')
    kd_output.rename_column('col4', 'V_lsr')
    kd_output.rename_column('col5', 'V_rev')
    kd_output.rename_column('col6', 'D_k')
    kd_output.rename_column('col7', 'error_D_k_plus')
    kd_output.rename_column('col8', 'error_D_k_minus')
    
    print kd_output
    

def make_reid_distance_column(catalog, nearfar='near'):
    """ Makes a reid distance column. 

    Input: ppv_catalog output. """

    nearfar_dict = {'near': 0,
                    'far': 1}

    source_file_string = ''
    
    for row in catalog:

        name = str(row["_idx"])
        
        galactic_coord = Galactic(
            l=row['x_cen'], b=row['y_cen'], unit=(u.deg, u.deg))

        rhh, rmm, rss = galactic_coord.fk5.ra.hms
        ddd, dmm, dss = galactic_coord.fk5.dec.dms

        rastring = "%02i%02i%5.2f" % (rhh, rmm, rss)
        destring = "%+03i%02i%5.2f" % (ddd, np.abs(dmm), np.abs(dss))
        vstring = "%7.1f" % row['v_cen']
        fstring = str(nearfar_dict[nearfar])

        row_string = name+" "+rastring+" "+destring+" "+vstring+" "+fstring+"\n"

        source_file_string += row_string

    f = open('source_file.dat', 'w')
    f.write(source_file_string)
    f.close()

    p = Popen(
        ['/Users/tsrice/Documents/Code/mark_reid_kdist/revised_kinematic_distance'],
        shell = False, stdin=PIPE, stdout=PIPE)
        
    output, error = p.communicate()

    print output
    print error


    lines_of_data = [x for x in output.split('\n') if '!' not in x]

    kd_output = astropy.table.Table.read(lines_of_data, format='ascii')
    
    kd_output.rename_column('col1', 'Source')
    kd_output.rename_column('col2', 'gal_long')
    kd_output.rename_column('col3', 'gal_lat')
    kd_output.rename_column('col4', 'V_lsr')
    kd_output.rename_column('col5', 'V_rev')
    kd_output.rename_column('col6', 'D_k')
    kd_output.rename_column('col7', 'error_D_k_plus')
    kd_output.rename_column('col8', 'error_D_k_minus')
    
    kd_output['gal_long'].unit = u.deg
    kd_output['gal_lat'].unit = u.deg
    kd_output['V_lsr'].unit = u.km/u.s
    kd_output['V_rev'].unit = u.km/u.s
    kd_output['D_k'].unit = u.kpc
    kd_output['error_D_k_plus'].unit = u.kpc
    kd_output['error_D_k_minus'].unit = u.kpc

    #    print kd_output

    return kd_output

    

"""
! Source     Gal Long  Gal Lat    V_lsr     V_rev    Rev. D_k     +/-
!              (deg)    (deg)    (km/s)    (km/s)     (kpc)      (kpc)
"""

