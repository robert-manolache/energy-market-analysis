import os
import pandas as pd
from nemtel.extractor import NEM_extractor

def read_NEM_csv(path):
    """
    """
    df_list = []
    row_labels = pd.read_csv(path, usecols=[0], header=None)
    I0 = row_labels[row_labels[0]=='I'].index.tolist()
    I1 = I0[1:] + row_labels.tail(1).index.tolist()
    for i0, i1 in zip(I0, I1):
        skiprows = i0
        nrows = i1-i0-1
        df = pd.read_csv(path, skiprows=skiprows, nrows=nrows)
        df_list.append(df.iloc[:,1:])
    return df_list

class NEM_loader(NEM_extractor):
    """
    """

    def __init__(self, data_dir, base_url="http://nemweb.com.au"):
        """
        """
        NEM_extractor.__init__(self, data_dir, base_url)
        self.available_file_df = None
        self.available_files = None
        self.files_to_read = None
    
    def get_available_files(self):
        """
        """
        self.load_tracker_df()
        tracker_df = self.current_tracker_df
        df = tracker_df[tracker_df.DOWNLOADED]
        df.loc[:, 'FILE'] = df['URL'].apply(lambda x: 
                            x.split('/')[-1].replace('.zip','.CSV'))
        self.available_file_df = df[['TIMESTAMP', 'FILE']]
        self._set_time_range(df)
        self.available_files = os.listdir(self.resource_dir)
        # note this may be sensitive to file sorting (may have to fix)
        # also won't work with Archive Trackers!
        if df.FILE.tolist() == self.available_files:
            pass
        else:
            print("WARNING: inconsistency detected in file records")

    def set_read_list(self, latest=1, by_time_range=False, 
                      manual_list=None, all_files=False):
        """
        """
        if by_time_range:
            df = self.available_file_df.copy()
            df = df[(df['TIMESTAMP']>=self.time_range[0])&
                    (df['TIMESTAMP']<=self.time_range[1])]
            read_list = df['FILE'].tolist()
        elif manual_list is not None:
            read_list = manual_list
        elif all_files:
            read_list = self.available_files
        else:
            read_list = self.available_files[-latest:]
        self.files_to_read = read_list

    def process_read_list(self):
        """
        """
        return {
            f: read_NEM_csv(os.path.join(self.resource_dir,f))
            for f in self.files_to_read
        }
