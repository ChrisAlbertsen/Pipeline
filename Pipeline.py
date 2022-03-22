from AzureLoader import AzureLoader 
import os

class Pipeline:
    """
    The class creates a data pipeline using the supplied functions, and allows for further functionality using the optional args.
    The instance of Pipeline is supplied to the Node class which then runs the run method (or optionally run_func), if the 
    trigger_func returns a value than can be evaluated as True (True, non-empty list or likewise).

    The default run method goes: extract -> transform -> load -> check -> clean

    Args:
        trigger_func:  Function taking no args and returning a destination (e.g. absolute path or https) for the extract_func or alternatively nothing.
                       Function is prompted by Node, and if anything evaluated as True is returned, the self.run method will run with the trigger_func return as arg.
                       Condition can be used to conditionally select files, set timer for running etc.
        
        extractor_func:  Function taking trigger_func's return as arg. Should return a pandas dataframe or series containing data.

        load_destination:  Dictionary containing 'server','database' and 'table' keys with values referencing the load destination.

        transformer_func (optional):  Function taking a pandas dataframe or series as arg. Transforms the arg input as specified.

        check_func (optional):  Function running any checks defined in the check_func.

        run_func (optional):  Function changing the default run workflow.

        loaderObj (optional):  A class used to load the Pipeline's data a specified destination. Default is a class used to load to Azure, but can be changed,
                               if one wishes to load the AWS or any alternative specification. See code for context.
    
    Returns:
        An instance of the Pipeline object.
    """


    def __init__(self, trigger_func, extractor_func, load_destination: dict, transformer_func = lambda x: x, check_func = lambda: None, 
        run_func = None, loaderObj = AzureLoader):
        self._trigger_func = trigger_func
        self._extractor_func = extractor_func
        self._load_destination = load_destination
        self._transformer_func = transformer_func
        self._run_func = run_func
        self._loaderObj = AzureLoader
        self._check_func = check_func


    def trigger(self):
        """
        Runs _trigger_func

        Returns:
            Reference to target extraction point for data e.g. absolute path, https or other extraction target.
            Returned val(s) is used by self.extract for extraction targets.
        """
        return self._trigger_func()


    def extract(self,trigger_result):
        """
        Runs _extract_func

        Args:
            trigger_result:  Reference to target extraction point for data i.e. absolute path, https or other extraction target.
                             Arg depends on the trigger_func and extractor_func used to initialize the instance of Pipeline
        """
        self.data = self._extractor_func(trigger_result)
        return
    

    def transform(self):
        """
        Applies any specified transformations to self.data.
        If no transformer_func is specified when initializing the instance of Pipeline, the function will return self.data unchanged.

        Returns:
            Pandas dataframe
        """
        self.data = self._transformer_func(self.data)
        return
    

    def load(self):
        """
        Loads data to target using the self._loaderObj (default is Azure SQL Database).
        Target Azure server, database and table is specified in the dict _load_destination.
        """
        cnxion = self._loaderObj(self._load_destination)
        cnxion.insert(self.data,self._load_destination["table"])
        return


    def check(self):
        """
        Run function to check the data uploaded from the Pipeline.
        If not _check_func is supplied when initializing the Pipeline instance the check simply passes.
        """
        self._check_func()
        return
    

    def clean(self, trigger_result):
        """
        Cleans the pipeline making it ready for a new run workflow.

        Args:
            trigger_result:  Reference to target extraction point for data i.e. absolute path, https or other extraction target.
                             Arg depends on the trigger_func and extractor_func used to initialize the instance of Pipeline
        """
        #delete local file if it exists at the destination
        for destination in trigger_result:
            if os.path.exists(destination):
                os.remove(destination)
        
        #delete self.data if it exists
        if "data" in dir(self):
            del self.data
        return


    def run(self,trigger_result):
        """
        Runs the default workflow (or _run_func workflow if specified) extract, transform, load, check, clean.

        Args:
            trigger_result:  Reference to target extraction point for data i.e. absolute path, https or other extraction target.
                             Arg depends on the trigger_func and extractor_func used to initialize the instance of Pipeline
        """
        #if user defined function exists run it
        if self._run_func:
            self._run_func(trigger_result)
        else:
            self.extract(trigger_result)
            self.transform()
            self.load()
            self.check()
            self.clean(trigger_result)
        return
