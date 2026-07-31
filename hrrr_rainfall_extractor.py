import numpy as np
import os

class HRRRRainfallExtractor:
    def __init__(self, folder_path, lats, lons,from_npy=True):
        """
        Initializes with the folder containing HRRR files
        and the target coordinates.
        """
        self.folder_path = folder_path
        self.lats = np.array(lats)
        self.lons = np.array(lons)
        self.num_points = len(self.lats)
        
        if from_npy==False:
            pass

def fetch_from_npy(self, issue_time,start_time, end_time):
    """
    Finds the 24 hourly files for the given day using the exact naming convention,
    extracts the values, and returns a matrix of shape (num_points, 24).
    """
    # Convert year and Day of Year to a string date (e.g., "20240101")
    
    nt = int((end_time - start_time) / 3600) + 1  # Number of time steps (hours)
    # Pre-allocate the output matrix: (1 million points, 24 hours)
    output = np.zeros((self.num_points, nt), dtype=np.float32)
    
    counter = 0
    for i in range(start_time, end_time, 3600):
        # 1. Build the two potential exact paths
        filename = f"{issue_time}_{i}.py"
        path_f = os.path.join(self.folder_path, filename)
        if os.path.exists(path_f):    
            try:
                data = np.load(path_f)
                output[:, counter] = data
                counter += 1
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
        else:
            print(f"File {path_f} not found")
            counter +=1
            
    return output

# --- Usage Example ---
if __name__ == '__main__':
    lats = np.random.uniform(25, 49, 1000000)
    lons = np.random.uniform(-125, -67, 1000000)
    
    hrrr_folder = "/nfsscratch/IFC/rush)argon/hrrr/"
    extractor = HRRRRainfallExtractor(hrrr_folder, lats, lons)
    rainfall_matrix = extractor.fetch_day(2020, 1)  # Returns shape (1000000, 24)