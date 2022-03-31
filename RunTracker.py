import datetime
import os
import pickle

class RunTracker:

    _tracking_file_path = os.path.join(os.path.dirname(__file__),"Tracking data.pickle")

    _template_subdict = {
        "last trigger": datetime.datetime(1,1,1),
        "last error": datetime.datetime(1,1,1),
        "interval": None,
        "schedule": None,
    }

    def __init__(self,pipeline_data):
        self.tracking_data = self._load_tracking_data(pipeline_data)


    def _load_tracking_data(self,pipeline_data):
        try:
            with open(self._tracking_file_path, "rb") as f:
                self.tracking_data = pickle.load(f)
            self._check_loaded_data(pipeline_data)
            return self.tracking_data
        #if file not found create file and re-run method
        except FileNotFoundError: 
            with open(self._tracking_file_path, "wb") as f:
                pickle.dump({"pickle_cant_be_empty":self._template_subdict},f)
                print("Created new file for RunTracker")
            return self._load_tracking_data(pipeline_data)
                 
    def _check_loaded_data(self,pipeline_data):
        keys = self.tracking_data.keys()
        subkeys = self._template_subdict.keys()
        made_a_change = False

        for pipeline_name in pipeline_data:
            #If pipeline not in first level of dict add it using template
            if pipeline_name not in keys:
                new_pipeline = {pipeline_name: self._template_subdict}
                self.tracking_data |= new_pipeline
                #No reason to check subkeys if its a new added pipeline
                continue
            #Check if all subkeys are available for loaded pipelines
            for subkey in subkeys:
                if subkey not in self.tracking_data[pipeline_name].keys():
                    self.tracking_data[pipeline_name][subkey] = self._template_subdict[subkey]
        

        for key,val in pipeline_data.items():
            if val:
                for subkey in val:
                    if not self.tracking_data[key][subkey]:
                        self.tracking_data[key][subkey] = pipeline_data[key][subkey] 

        #overwrite old data
        with open(self._tracking_file_path, "wb") as f:
            pickle.dump(self.tracking_data,f)

        return self.tracking_data


    def update(self,pipeline_name: str, field: str):
        if field == "last trigger" and self.tracking_data[pipeline_name]["schedule"]:
            data = self.tracking_data[pipeline_name]
            time_passed = datetime.datetime.now() - data["last trigger"]
            floored_time = time_passed // data["interval"] * data["interval"] + data["last trigger"]
            self.tracking_data[pipeline_name]["last trigger"] = floored_time
        else:
            self.tracking_data[pipeline_name][field] = datetime.datetime.now()
        with open(self._tracking_file_path, "wb") as f:
            pickle.dump(self.tracking_data,f)