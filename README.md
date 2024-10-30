# Ship detection from SAR imagery

## Preprocess ICEYE GRD data

### Setting up ESA SNAP

Install ESA SNAP with default options on your Linux machine (or Windows Subsystem for Linux).
Note that ESA SNAP version 11.0.0 doesn't automatically work with the `esa_snappy` Python module, so install version 10.0.0 instead.
You can download it [here](https://step.esa.int/main/download/snap-download/), choose the "Sentinel Toolboxes" version.
This guide assumes it is installed under `~/esa-snap` (default).

Now configure the ESA SNAP Python module `esa_snappy` by running

```shell
$ cd ~/esa-snap/bin
$ ./snappy-conf /usr/bin/python3
```

You can verify `esa_snappy` was installed correctly by running its tests.

```shell
$ cd ~/.snap/snap-python/esa_snappy/tests
$ python test_snappy_mem.py
$ python test_snappy_perf.py
$ python test_snappy_product.py
```

### Download sample data

Download some sample data from ICEYE [here](https://www.iceye.com/resources/datasets).
For example, the Singapore Strait dataset is relevant for this use case.

Extract the zip and make sure there's a large `.tif` file inside.

### Run the preprocessor

Clone this repository to your machine.
Then inside the repository directory, run the following, replacing the placeholder path with the actual path to the sample dataset (`.tif` file) you've downloaded.

```shell
$ python preprocess-iceye-grd.py [path/to/iceye/dataset.tif]
```

For example, if your dataset is located in `~/Downloads/iceye-singapore/ICEYE_GRD_SM_159816_20211114T024121.tif`, run

```shell
$ python preprocess-iceye-grd.py ~/Downloads/iceye-singapore/ICEYE_GRD_SM_159816_20211114T024121.tif
```

Preprocessing will take some minutes depending on the size of the dataset.
After it's done, the preprocessed dataset is available as a GeoTIFF file (also a `.tif`) next to the source dataset as `pp_[timestamp]_[original_file_name].tif`.
For example, as `~/Downloads/iceye-singapore/pp_20241018T154122_ICEYE_GRD_SM_159816_20211114T024121.tif` in this case.

Now the dataset can be imported to GIS tools (e.g. ESA SNAP, `rasterio` Python module) and further worked on.

## Using preprocessed data

I've added a demo with `rasterio` as an example use-case (requires `rasterio`, `numpy`, and `matplotlib` Python modules).

```shell
$ python demo-rasterio.py [path/to/preprocessed/geotiff.tif]
```

So for example

```shell
$ python demo-rasterio.py ~/Downloads/iceye-singapore/pp_20241018T154122_ICEYE_GRD_SM_159816_20211114T024121.tif
```

It just shows the data as an image after some normalization and clipping of the brightest pixels.
Clipping is required since some pixels, e.g. parts of ships and other metallic structures, can be VERY bright compared to the rest of the pixels, e.g. nature.
Without clipping, the image would appear almost totally dark after normalization, since there are so few of the brightest pixels.
