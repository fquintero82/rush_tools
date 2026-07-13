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

    def extract_period(self, start_doy, end_doy):
        """
        Extracts ET values for a range of days.
        Returns shape: (num_points, num_days)
        """
        num_days = end_doy - start_doy + 1
        output = np.zeros((self.num_points, num_days), dtype=np.float32)

        for i, doy in enumerate(range(start_doy, end_doy + 1)):
            file_path = self.get_file_path(doy)
            
            if os.path.exists(file_path):
                with rasterio.open(file_path) as src:
                    # Initialize indices on the first file we successfully open
                    if self.rows is None:
                        self._initialize_indices(file_path)
                    
                    # Read the 2D grid and extract our points
                    data = src.read(1)
                    output[:, i] = data[self.rows, self.cols] / 1000. #mm/day
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
    et = extractor.extract_period( 1, 10)
    print(et.shape)  # Should be (1000000, 10)
    print('here')