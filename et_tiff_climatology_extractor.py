import os
import rasterio
import numpy as np
from datetime import datetime

class EtTiffExtractor:
    def __init__(self, folder_path, lats, lons):
        """
        Initializes with the folder containing the SSEBop ET files 
        and the target coordinates.
        """
        self.folder_path = folder_path
        self.lats = np.array(lats)
        self.lons = np.array(lons)
        self.num_points = len(self.lats)
        
        # Row and Column indices (calculated once)
        self.rows = None
        self.cols = None

    def _initialize_indices(self, sample_tif):
        """
        Maps Lat/Lon to Row/Col using the first available file.
        Since CRS matches, we use src.index directly.
        """
        print(f"Mapping coordinates using sample file: {sample_tif}")
        with rasterio.open(sample_tif) as src:
            t = src.transform
            self.cols = (self.lons - t.c) / t.a
            self.rows = (self.lats - t.f) / t.e
            self.rows = np.floor(self.rows).astype(int)
            self.cols = np.floor(self.cols).astype(int)
            self.rows = np.clip(self.rows, 0, src.height - 1)
            self.cols = np.clip(self.cols, 0, src.width - 1)
    def get_file_path(self, doy):
        """
        Constructs the filename: meanDOY.tif
        Example: mean_1.tif
        """
        filename = f"mean_{doy}.tif"
        return os.path.join(self.folder_path, filename)

    def extract_period(self, start_unixtime:int, end_unixtime:int):
        """
        Extracts ET values for a range of hours.
        Returns shape: (num_points, num_hours)
        """
        hours = np.arange(start_unixtime, end_unixtime + 1, 3600)        #create a sequence of the hours in the range
        dt64 = hours.astype('datetime64[s]')

        # 3. Calculate Day of Year: Subtract the start of the year and add 1
        # (We cast to 'datetime64[D]' to get the day string/units)
        year_start = dt64.astype('datetime64[Y]')
        doys = (dt64.astype('datetime64[D]') - year_start).astype(int) + 1
        #find the corresponding filepath for each day of year
        #file_paths = [self.get_file_path(doy) for doy in doys]


        output = np.zeros((self.num_points, len(hours)), dtype=np.float32)

        # Loop through each unique file once, extract the ET values, and fill the matching hours in the output array
        for doy in np.unique(doys):
            file_path = self.get_file_path(int(doy))
            
            if os.path.exists(file_path):
                with rasterio.open(file_path) as src:
                    # Initialize indices on the first file we successfully open
                    if self.rows is None:
                        self._initialize_indices(file_path)
                    
                    # Read the 2D grid and extract our points
                    data = src.read(1)
                    values = data[self.rows, self.cols] / 1000.0  # mm/day
                    hour_indices = np.where(doys == doy)[0]
                    output[:, hour_indices] = values[:, None]
                print(f"Processed Day {doy}")
            else:
                print(f"Warning: File missing for Day {doy}: {file_path}")
        
        return output




 
    
if __name__=="__main__":
    # --- Usage Example ---
    et_folder = "/home/fquinteroduque/LSS/preclab/data/modisSSEBop/et_climatology"
    et_folder = "V:\\data\\modisSSEBop\\daily_climatology\\"
    lats = np.random.uniform(25, 49, 1000000)
    lons = np.random.uniform(-125, -67, 1000000)
    extractor = EtTiffExtractor(et_folder, lats, lons)
    # # Get full year 2002
    et = extractor.extract_period( 1783987200, 1784073600)
    print(et.shape)  # Should be (1000000, 10)
    print('here')