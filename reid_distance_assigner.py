"""
Some python code to interface with Mark Reid's fortran tool.

Hopefully I can figure out how to do this in a non-boneheaded way.

"""

from __future__ import division

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT

import numpy as np

import astropy.table
from astropy.coordinates import Galactic
import astropy.units as u
import astropy.constants as c

executable_path = os.path.expanduser('~/Documents/Code/mark_reid_kdist/revised_kinematic_distance')

executable_path_universal = os.path.expanduser('~/Documents/Code/mark_reid_kdist/universal_sersic_kdist')


def test_reid_distances(executable_path=executable_path, verbose=True):

    test_string = "test    010203.04 121314.5 -10 1\n"

    f = open('source_file.dat', 'w')
    f.write(test_string)
    f.close()

    p = Popen(
        [executable_path],
        shell = False, stdin=PIPE, stdout=PIPE)

    output, error = p.communicate()

    if verbose:
        print output
        print error

    lines_of_data = [x for x in output.split('\n') if '!' not in x and x != '']

    kd_output = astropy.table.Table.read(lines_of_data, format='ascii')
    
    kd_output.rename_column('col1', 'Source')
    kd_output.rename_column('col2', 'gal_long')
    kd_output.rename_column('col3', 'gal_lat')
    kd_output.rename_column('col4', 'V_lsr')
    kd_output.rename_column('col5', 'V_rev')
    kd_output.rename_column('col6', 'D_k')
    kd_output.rename_column('col7', 'error_D_k_plus')
    kd_output.rename_column('col8', 'error_D_k_minus')
    
    if verbose:
        print kd_output, lines_of_data

    return kd_output

try:
    reid_test_output = test_reid_distances(verbose=False)

    assert type(reid_test_output) == astropy.table.table.Table
    assert len(reid_test_output) == 1
    assert len(reid_test_output.colnames) == 8
    assert reid_test_output['D_k'][0] == 0.41
except Exception, e:
    print e
    raise ImportError("Reid distances cannot be imported: unit tests failed! (Reid flat)")


def test_universal_distances(executable_path=executable_path_universal, verbose=True):

    test_string = "test    030.00 -01.00 -10 0\n"

    f = open('source_file.dat', 'w')
    f.write(test_string)
    f.close()

    p = Popen(
        [executable_path],
        shell = False, stdin=PIPE, stdout=PIPE)

    output, error = p.communicate()

    if verbose:
        print output
        print error

    lines_of_data = [x for x in output.split('\n') if '!' not in x and x != '']

    kd_output = astropy.table.Table.read(lines_of_data, format='ascii')
    
    kd_output.rename_column('col1', 'Source')
    kd_output.rename_column('col2', 'gal_long')
    kd_output.rename_column('col3', 'gal_lat')
    kd_output.rename_column('col4', 'V_lsr')
    kd_output.rename_column('col5', 'V_rev')
    kd_output.rename_column('col6', 'D_k')
    kd_output.rename_column('col7', 'error_D_k_plus')
    kd_output.rename_column('col8', 'error_D_k_minus')
    
    if verbose:
        print kd_output, lines_of_data

    return kd_output

try:
    universal_test_output = test_universal_distances(verbose=False)

    assert type(universal_test_output) == astropy.table.table.Table
    assert len(universal_test_output) == 1
    assert len(universal_test_output.colnames) == 8
    assert universal_test_output['gal_long'] == 30
    assert universal_test_output['gal_lat'] == -1
    assert universal_test_output['D_k'][0] == 14.92
except Exception, e:
    print e
    raise ImportError("Reid distances cannot be imported: unit tests failed! (Reid Universal)")
    

def make_reid_distance_column(catalog, nearfar='near', executable_path=executable_path):
    """ 
    Makes a reid distance column. 

    Input: ppv_catalog output. 

    """

    nearfar_dict = {'near': 0,
                    'far': 1}

    source_file_string = ''
    
    galactic_coord = Galactic(
        l=catalog['x_cen'], b=catalog['y_cen'], unit=(u.deg, u.deg))

    rhh, rmm, rss = galactic_coord.fk5.ra.hms
    ddd, dmm, dss = galactic_coord.fk5.dec.dms

    fstring = str(nearfar_dict[nearfar])

    for i, row in enumerate(catalog):

        name = str(row["_idx"])
        
        rastring = "%02i%02i%05.2f" % (rhh[i], rmm[i], rss[i])
        destring = "%+03i%02i%05.2f" % (ddd[i], np.abs(dmm)[i], np.abs(dss)[i])
        vstring = "%7.1f" % row['v_cen']

        row_string = name+" "+rastring+" "+destring+" "+vstring+" "+fstring+"\n"

        source_file_string += row_string

        # row_string.abcdasd()

    f = open('source_file.dat', 'w')
    f.write(source_file_string)
    f.close()

    p = Popen(
        [executable_path],
        shell = False, stdin=PIPE, stdout=PIPE)
        
    output, error = p.communicate()

    lines_of_data = [x for x in output.split('\n') if '!' not in x and x != '']


    # Sometimes the output is poorly formatted such that columns run up against each other. Let's sanitize those columns.
    for i in range(len(lines_of_data)):
        line = lines_of_data[i]
        if len(line.split()) != 8:
            tuple_split = tuple(line.split()[0:5])
            lines_of_data[i] = "  {0} {1} {2}  {3} {4}    0.00   0.00  0.00".format(*tuple_split)

    kd_output = astropy.table.Table.read(lines_of_data, format='ascii.no_header')
    
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


def make_universal_distance_column(catalog, nearfar='near', executable_path=executable_path_universal):
    """ 
    Makes a universal distance column. 

    Input: ppv_catalog output. 

    """

    nearfar_dict = {'near': 0,
                    'far': 1}

    source_file_string = ''

    lon_column = catalog['x_cen']
    lat_column = catalog['y_cen']
    
    fstring = str(nearfar_dict[nearfar])

    for i, row in enumerate(catalog):

        name = str(row["_idx"])
        
        lon_string = "{0:07.3f}".format(lon_column[i])
        lat_string = "{0:+07.3f}".format(lat_column[i])
        # lat_string = "%+03i%02i%05.2f" % (ddd[i], np.abs(dmm)[i], np.abs(dss)[i])
        vstring = "%7.1f" % row['v_cen']

        row_string = name+" "+lon_string+" "+lat_string+" "+vstring+" "+fstring+"\n"

        source_file_string += row_string

        # row_string.abcdasd()

    f = open('source_file.dat', 'w')
    f.write(source_file_string)
    f.close()

    p = Popen(
        [executable_path],
        shell = False, stdin=PIPE, stdout=PIPE)
        
    output, error = p.communicate()

    lines_of_data = [x for x in output.split('\n') if '!' not in x and x != '']


    # Sometimes the output is poorly formatted such that columns run up against each other. Let's sanitize those columns.
    for i in range(len(lines_of_data)):
        line = lines_of_data[i]
        if len(line.split()) != 8:
            tuple_split = tuple(line.split()[0:5])
            lines_of_data[i] = "  {0} {1} {2}  {3} {4}    0.00   0.00  0.00".format(*tuple_split)

    kd_output = astropy.table.Table.read(lines_of_data, format='ascii.no_header')
    
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

    # print kd_output

    return kd_output


def distance_assigner_with_plusminus_errors(structure_catalog, kdist_catalog, distance_column_name='distance'):

    structure_catalog[distance_column_name] = kdist_catalog['D_k']
    structure_catalog['error_'+distance_column_name+'_plus'] = np.abs(kdist_catalog['error_D_k_plus'])
    structure_catalog['error_'+distance_column_name+'_minus'] = np.abs(kdist_catalog['error_D_k_minus'])


def choose_nearfar_distance(structure_catalog, nearfar, bool_array, unambiguous_tag=False):

    if nearfar not in ['near', 'far']:
        raise ValueError("`nearfar` must be 'near' or 'far'.")

    tag_dict = {'near': 'N', 'far': 'F'}
    if unambiguous_tag:
        tag = 'U'
    else:
        tag = tag_dict[nearfar]

    structure_catalog['distance'][bool_array] = structure_catalog[nearfar+'_distance'][bool_array]
    structure_catalog['error_distance_plus'][bool_array] = structure_catalog['error_'+nearfar+'_distance_plus'][bool_array]
    structure_catalog['error_distance_minus'][bool_array] = structure_catalog['error_'+nearfar+'_distance_minus'][bool_array]
    structure_catalog['KDA_resolution'][bool_array] = tag


"""
! Source     Gal Long  Gal Lat    V_lsr     V_rev    Rev. D_k     +/-
!              (deg)    (deg)    (km/s)    (km/s)     (kpc)      (kpc)
"""

