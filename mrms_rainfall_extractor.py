import os
import glob
import xarray as xr
import numpy as np
from datetime import datetime, timedelta

class MRMSRainfallExtractor:
    def __init__(self, folder_path, lats, lons):
        """
        Initializes with the folder containing hourly MRMS NetCDF files
        and the target coordinates.
        """
        self.folder_path = folder_path
        self.lats = np.array(lats)
        self.lons = np.array(lons)
        self.num_points = len(self.lats)
        
        # 1. Open a sample file safely using h5netcdf to get the spatial grid vectors
        sample_file = self._get_sample_file()
        with xr.open_dataset(sample_file, engine="h5netcdf") as ds:
            self.grid_lats = ds.Lat.values
            self.grid_lons = ds.Lon.values
            
        # Calculate the cell resolution dynamically
        self.lat_res = abs(self.grid_lats[1] - self.grid_lats[0])
        self.lon_res = abs(self.grid_lons[1] - self.grid_lons[0])
            
        # 2. Precalculate spatial integer indices
        self.lat_idxs, self.lon_idxs = self._precalculate_spatial_indices()

    def _get_sample_file(self):
        """Finds the first NetCDF file in the directory to use as a template."""
        files = glob.glob(os.path.join(self.folder_path, "*.nc"))
        if not files:
            raise FileNotFoundError(f"No NetCDF (.nc) files found in {self.folder_path}")
        return files[0]

    def _precalculate_spatial_indices(self):
        """
        Maps 1M Lat/Lons to the integer row/col positions of the MRMS grid.
        Formula: (Target_Coordinate - Grid_Origin) / Grid_Resolution
        """
        print("Precalculating MRMS grid indices...")
        
        lat_idxs = np.rint((self.lats - self.grid_lats[0]) / (self.grid_lats[1] - self.grid_lats[0])).astype(int)
        lon_idxs = np.rint((self.lons - self.grid_lons[0]) / (self.grid_lons[1] - self.grid_lons[0])).astype(int)
        
        # Clip indices to ensure they never exceed grid boundaries
        lat_idxs = np.clip(lat_idxs, 0, len(self.grid_lats) - 1)
        lon_idxs = np.clip(lon_idxs, 0, len(self.grid_lons) - 1)
        
        return lat_idxs, lon_idxs
    
    def fetch_day(self, year, doy):
        """
        Finds the 24 hourly files for the given day using the exact naming convention,
        extracts the values, and returns a matrix of shape (num_points, 24).
        """
        # Convert year and Day of Year to a string date (e.g., "20240101")
        date_obj = datetime(year, 1, 1) + timedelta(days=doy - 1)
        date_str = date_obj.strftime("%Y%m%d")
        
        # Pre-allocate the output matrix: (1 million points, 24 hours)
        daily_output = np.zeros((self.num_points, 24), dtype=np.float32)
        
        print(f"Processing MRMS data for {date_str}...")
        
        for hour in range(24):
            # 1. Build the two potential exact paths
            filename_ms = f"MultiSensor_{date_str}-{hour:02d}0000.nc"
            filename_gc = f"GaugeCorr_{date_str}-{hour:02d}0000.nc"
            
            path_ms = os.path.join(self.folder_path, filename_ms)
            path_gc = os.path.join(self.folder_path, filename_gc)
            
            # 2. Determine which product exists
            if os.path.exists(path_ms):
                nc_file = path_ms
            elif os.path.exists(path_gc):
                nc_file = path_gc
            else:
                # Missing hour: silently skip to preserve matrix shape, fills with NaN
                continue
                
            try:
                # Open safely with h5netcdf within a context manager
                with xr.open_dataset(nc_file, engine="h5netcdf") as ds:
                    # Load 2D slice into memory
                    grid_data = ds.MRMS.values
                    
                    # Extract the 1M points via fancy indexing using precalculated locations
                    # Check dimension ordering! Swap to [lon, lat] if MRMS is ordered (Lon, Lat)
                    daily_output[:, hour] = grid_data[self.lat_idxs, self.lon_idxs]
                    
            except Exception as e:
                print(f"Error reading hour {hour:02d} ({os.path.basename(nc_file)}): {e}")
                
        return daily_output

# --- Usage Example ---
if __name__ == '__main__':
    lats = np.random.uniform(25, 49, 1000000)
    lons = np.random.uniform(-125, -67, 1000000)
    mrms_folder = "Y:\\mrms_netcdf_archive\\mrms\\2020\\"
    #mrms_folder = "/Dedicated/IFC/mrms_netcdf_archive/mrms/2020/"
    extractor = MRMSRainfallExtractor(mrms_folder, lats, lons)
    rainfall_matrix = extractor.fetch_day(2020, 1)  # Returns shape (1000000, 24)