#reads stage4 tar files and extracts the data for a given day and a set of lat/lon points
import tarfile
import rasterio
import numpy as np
import io
import pyproj
from datetime import datetime, timedelta
CRS_WKT = """PROJCRS["unnamed",BASEGEOGCRS["Coordinate System imported from GRIB file",DATUM["unnamed",ELLIPSOID["Sphere",6371200,0,LENGTHUNIT["metre",1,ID["EPSG",9001]]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]]],CONVERSION["Polar Stereographic (variant B)",METHOD["Polar Stereographic (variant B)",ID["EPSG",9829]],PARAMETER["Latitude of standard parallel",60,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8832]],PARAMETER["Longitude of origin",-105,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8833]],PARAMETER["False easting",0,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",south,MERIDIAN[90,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],ORDER[1],LENGTHUNIT["Metre",1]],AXIS["(N)",south,MERIDIAN[180,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]],ORDER[2],LENGTHUNIT["Metre",1]]]"""
class TarTiffExtractor:

    def __init__(self, tar_path, lats, lons):
        """
        Initializes with Tar path, raw Lat/Lons, and the specific Grid CRS.
        """
        self.tar_path = tar_path
        self.lats = np.array(lats)
        self.lons = np.array(lons)
        self.crs_wkt = CRS_WKT

        self.num_points = len(self.lats)
        
        # We will calculate these indices once we open the first file
        self.rows = None
        self.cols = None
        self.transform = None

    def _initialize_indices(self, src):
        """
        Direct NumPy implementation of the Inverse Affine Transform.
        Maps Map Coordinates (meters) -> Pixel Indices (row, col).
        """
        print("Initializing coordinate transformation with NumPy...")
        
        # 1. Transform Lat/Lon to Meters
        transformer = pyproj.Transformer.from_crs("EPSG:4326", self.crs_wkt, always_xy=True)
        x_meters, y_meters = transformer.transform(self.lons, self.lats)
        
        # 2. Get the Affine Transform components from the file
        # A transform looks like: [x_scale, x_rot, x_offset, y_rot, y_scale, y_offset]
        t = src.transform
        
        # 3. Perform the Inverse Transform manually using NumPy
        # Formula for pixels from coordinates:
        # col = (x - x_offset) / x_scale
        # row = (y - y_offset) / y_scale
        # Note: This assumes 0 rotation, which is standard for MRMS/HRAP Tiffs
        
        self.cols = (x_meters - t.c) / t.a
        self.rows = (y_meters - t.f) / t.e
        
        # 4. Round and cast to Integer
        self.rows = np.floor(self.rows).astype(int)
        self.cols = np.floor(self.cols).astype(int)
        
        # 5. Clip to ensure we stay within the grid (0 to height-1, 0 to width-1)
        self.rows = np.clip(self.rows, 0, src.height - 1)
        self.cols = np.clip(self.cols, 0, src.width - 1)
        
        self.transform = t
        print(f"Successfully mapped {self.num_points:,} points.")

    def fetch_day(self, year, doy):
        """
        Extracts 24 hours for a specific DOY.
        """
        date_obj = datetime(year, 1, 1) + timedelta(days=doy - 1)
        date_prefix = date_obj.strftime("%Y%m%d")
        daily_output = np.zeros(( self.num_points,24), dtype=np.float32)
        
        #print(f"--- Processing {date_prefix} (DOY {doy}) ---")
        
        with tarfile.open(self.tar_path, 'r') as tar:
            for hour in range(24):
                filename = f"{date_prefix}{hour:02d}.tif"
                
                try:
                    # Search for the hourly file member
                    member = next(m for m in tar.getmembers() if filename in m.name)
                    f = tar.extractfile(member)
                    
                    if f is not None:
                        with io.BytesIO(f.read()) as memfile:
                            with rasterio.open(memfile) as src:
                                # Initialize indices only on the very first file encountered
                                if self.rows is None:
                                    self._initialize_indices(src)
                                
                                # Fast read of the million points
                                data_2d = src.read(1)
                                daily_output[:, hour] = data_2d[self.rows, self.cols]
                                
                        #print(f"  Hour {hour:02d} processed.")
                        
                except StopIteration:
                    continue 
                except Exception as e:
                    print(f"  Error on {filename}: {e}")

        return daily_output
if __name__=='__main__':
    # --- Setup and Execution ---

    # 1. Dummy lats/lons (Replace with your 1M coordinates)
    lats = np.random.uniform(25, 49, 1000000)
    lons = np.random.uniform(-125, -67, 1000000)

    # 2. Initialize
    path = "/home/fquinteroduque/LSS/preclab/stage4/tif/2002.tar"
    path = "V:\\stage4\\tif\\2002.tar"
    path = "/Dedicated/preclab/stage4/tif/2002.tar"
    extractor = TarTiffExtractor(path, lats, lons)

    # 3. Fetch Jan 1st
    # Output shape: (24, 1000000)
    data = extractor.fetch_day(2002, 1)