# rush-tools

## Installation
This configuration runs on a Windows machine using Nvidia RTX 2000

1. Open a terminal in the project folder.
2. Create and activate a Conda environment named `rush-tools` with the required packages:

   ```bash
   conda env remove -y -n rush-tools
   conda create -n rush-tools -c conda-forge python=3.11 cupy numba pandas h5netcdf rasterio pyproj xarray dataretrieval cfgrib spotpy boto3 cuda-version=12.6 -y
   conda activate rush-tools
   conda install -c conda-forge cuda-nvcc -y
   ```


