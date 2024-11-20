"""
Preprocessing steps recommended by ICEYE for their GRD datasets.
See 'ICEYE GRD data pre-processing' in https://www.iceye.com/sar-data/snap
"""

import sys, os
sys.path.append(os.path.expanduser('~/.snap/snap-python'))
import esa_snappy
from esa_snappy import ProductIO, GPF, HashMap
from datetime import datetime, timezone
import jpy

def speckle_filtering(product):
    """Apply Speckle filtering via ESA SNAP

    See Java implementation for parameters reference:
    https://github.com/senbox-org/s1tbx/blob/master/s1tbx-op-sar-processing/src/main/java/org/esa/s1tbx/sar/gpf/filtering/SpeckleFilterOp.java
    """

    parameters = HashMap()
    parameters.put('sourceBandNames', 'Amplitude_VV')
    parameters.put('filter', 'Lee Sigma')
    parameters.put('windowSize', '5x5')

    return GPF.createProduct('Speckle-Filter', parameters, product)

def add_elevation_band(product):
    """Add elevation band via ESA SNAP

    See Java implementation for parameters reference:
    https://github.com/senbox-org/snap-engine/blob/master/snap-dem/src/main/java/org/esa/snap/dem/gpf/AddElevationOp.java
    """

    parameters = HashMap()
    parameters.put('bandName', 'elevation')
    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')

    return GPF.createProduct('AddElevation', parameters, product)

def remove_land_pixels(product):
    """Filter out land pixels (elevation > 0) via ESA SNAP

    See Java implementation for parameters reference:
    https://github.com/senbox-org/snap-engine/blob/master/snap-gpf/src/main/java/org/esa/snap/core/gpf/common/BandMathsOp.java
    """

    product_with_elevation = add_elevation_band(product)

    parameters = HashMap()

    BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    targetBand1 = BandDescriptor()
    targetBand1.name = 'Amplitude_VV'
    targetBand1.type = 'float32'
    targetBand1.expression = 'elevation <= 0 ? Amplitude_VV : 0'
    targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    targetBands[0] = targetBand1
    parameters.put('targetBands', targetBands)

    return GPF.createProduct('BandMaths', parameters, product_with_elevation)

def terrain_correction(product):
    """Apply terrain correction via ESA SNAP

    See Java implementation for parameters reference:
    https://github.com/senbox-org/s1tbx/blob/master/s1tbx-op-sar-processing/src/main/java/org/esa/s1tbx/sar/gpf/geometric/RangeDopplerGeocodingOp.java
    """

    parameters = HashMap()
    parameters.put('sourceBandNames', 'Amplitude_VV')
    parameters.put('nodataValueAtSea', False)

    return GPF.createProduct('Terrain-Correction', parameters, product)

# def crop(product):
#     parameters = HashMap()
#     parameters.put('region', '8446,13427,2000,2000') # x,y,width,height
#     parameters.put('copyMetadata', True)

#     return GPF.createProduct('Subset', parameters, product)

if len(sys.argv) < 2:
    print('Provide path to a ICEYE GRD file (.tif) as an argument.')
    sys.exit(1)

input_path = sys.argv[1]
input = ProductIO.readProduct(input_path)

band_names = input.getBandNames()
if not 'Amplitude_VV' in band_names:
    print('Amplitude_VV band not found in dataset.')
    sys.exit(1)

output = terrain_correction(remove_land_pixels(speckle_filtering(input)))

timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")
directory, filename = os.path.split(input_path)
output_path = os.path.join(directory, f'pp_{timestamp}_{filename}')
ProductIO.writeProduct(output, str(output_path), 'GeoTIFF')
