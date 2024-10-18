"""
Preprocessing steps recommended by ICEYE for their GRD datasets.
See 'ICEYE GRD data pre-processing' in https://www.iceye.com/sar-data/snap
"""

import sys, os
sys.path.append(os.path.expanduser('~/.snap/snap-python'))
import esa_snappy
from esa_snappy import ProductIO, GPF, HashMap
from datetime import datetime, timezone

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

def terrain_correction(product):
    """Apply terrain correction via ESA SNAP

    See Java implementation for parameters reference:
    https://github.com/senbox-org/s1tbx/blob/master/s1tbx-op-sar-processing/src/main/java/org/esa/s1tbx/sar/gpf/geometric/RangeDopplerGeocodingOp.java
    """

    parameters = HashMap()
    parameters.put('sourceBandNames', 'Amplitude_VV')
    parameters.put('nodataValueAtSea', False)

    return GPF.createProduct('Terrain-Correction', parameters, product)

if len(sys.argv) < 2:
    print('Provide path to a ICEYE GRD file (.tif) as an argument.')
    sys.exit(1)

input_path = sys.argv[1]
input = ProductIO.readProduct(input_path)

band_names = input.getBandNames()
if not 'Amplitude_VV' in band_names:
    print('Amplitude_VV band not found in dataset.')
    sys.exit(1)

output = terrain_correction(speckle_filtering(input))

timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")
directory, filename = os.path.split(input_path)
output_path = os.path.join(directory, f'pp_{timestamp}_{filename}')
ProductIO.writeProduct(output, str(output_path), 'GeoTIFF')
