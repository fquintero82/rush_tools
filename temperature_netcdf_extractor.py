import xarray as xr
import numpy as np
import pandas as pd


class NetCDFTemperatureExtractor:
    def __init__(self, nc_path, lats, lons):
        self.nc_path = nc_path
        self.lats = np.array(lats)
        self.lons = np.array(lons)
        
        # Open dataset to get coordinate vectors
        with xr.open_dataset(nc_path,engine="h5netcdf") as ds:
            self.grid_lats = ds.latitude.values    # [40, 40.25, ..., 45]
            self.grid_lons = ds.longitude.values   # [-98, -97.75, ..., -90]
            self.times = ds.valid_time.values
            
        # Precalculate the index positions
        self.lat_idxs, self.lon_idxs = self._precalculate_indices()

    def _precalculate_indices(self):
        """
        Maps 1M Lat/Lons to integer indices of the 0.25 degree grid.
        """
        print("Precalculating NetCDF grid indices...")
        
        # Calculate indices based on grid resolution (0.25) and start point
        # Formula: (Point - Start) / Resolution
        # We use np.rint().astype(int) to find the 'nearest' index
        lat_idxs = np.rint((self.lats - self.grid_lats[0]) / 0.25).astype(int)
        lon_idxs = np.rint((self.lons - self.grid_lons[0]) / 0.25).astype(int)
        
        # Safety clip to ensure indices stay within the NetCDF grid dimensions
        lat_idxs = np.clip(lat_idxs, 0, len(self.grid_lats) - 1)
        lon_idxs = np.clip(lon_idxs, 0, len(self.grid_lons) - 1)
        
        return lat_idxs, lon_idxs

    def extract_year(self, year):
            """
            Subsets the data for a specific year and extracts all points.
            """
            # 1. Calculate time boundaries in Unix Timestamps
            start_ts = pd.Timestamp(year=year, month=1, day=1).to_datetime64()
            end_ts = pd.Timestamp(year=year, month=12, day=31, hour=23).to_datetime64()
            
            # 2. Find indices where validtime is within the year
            time_mask = (self.times >= start_ts) & (self.times <= end_ts)
            print(self.times[time_mask])
            if not np.any(time_mask):
                raise ValueError(f"No data found in NetCDF for year {year}")

            # 3. Read only the necessary slice from disk
            with xr.open_dataset(self.nc_path,engine="h5netcdf") as ds:
                # Note: We use .isel() to get the specific time slice before .values
                # This prevents loading the entire multi-year file into RAM
                print(f"Loading data for year {year}...")
                # Assuming dims are (longitude, latitude, validtime)
                yearly_cube = ds.t2m.isel(valid_time=time_mask).values
                yearly_cube = yearly_cube - 273.15

            #print(f"Subsetting {self.num_points} points...")
            # Indexing: [longitudes, latitudes, filtered_time]
            out = yearly_cube[:,self.lat_idxs,self.lon_idxs]
            return out.T

if __name__=='__main__':
# --- Usage ---
    lats = np.random.uniform(25, 49, 1000000)
    lons = np.random.uniform(-125, -67, 1000000)
    path="/home/fquinteroduque/LSS/preclab/era5/temperature/temperature.nc"
    path="V:\\era5\\temperature\\temperature.nc"
    extractor = NetCDFTemperatureExtractor(path, lats, lons)
    temp_matrix = extractor.extract_year(2002) # Result: (1000000, 365)