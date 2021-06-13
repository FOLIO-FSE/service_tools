import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

from service_tasks.service_task_base import ServiceTaskBase, abstractmethod


class RemapField(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.infile = args.infile
        self.mapfile = args.mapfile
        self.filetype = Path(args.infile).suffix 
        self.outfilebase = self.infile[:-len(self.filetype)] + ".1"

    def do_work(self):

        if (self.filetype == ".tsv"):
            df = pd.read_csv(self.infile, dtype=str, sep='\t')  
            outfile = self.outfilebase + '.tsv'
        else:
            df = pd.read_csv(self.infile, dtype=str)  
            outfile = self.outfilebase + '.csv'

        mapdf = pd.read_csv(self.mapfile, dtype=str, sep='\t')  

        replacehead = mapdf.columns[0]
        print(replacehead)

        foliohead = mapdf.columns[1]
        print(foliohead)

        oldvals = mapdf[replacehead].values.tolist()
        print((json.dumps(oldvals, indent=4)))
        newvals = mapdf[foliohead].values.tolist()
        print((json.dumps(newvals, indent=4)))

        sourcecol = df[replacehead].values.tolist()

        newlist = []
        # create a dictionares to count replacments
        replaceDict = defaultdict(int)
        replaceVals = dict(mapdf.values) 
        inverse_mapper = {v: k for k, v in replaceVals.items()}

        for val in sourcecol:
            maplistlength = len(oldvals)
            counter = 0

            for i in range(maplistlength):
                if (oldvals[i] == val):
                    val = newvals[i]
                    replaceDict[val] += 1
                    i = maplistlength - 1

            newlist.append(val)

        df[replacehead] = newlist

        if (self.filetype == ".tsv"):
            df.to_csv(outfile, sep = '\t', index=False)  
        else:
            df.to_csv(outfile, index=False)  

        print(f"The following values were replaced and written to {outfile}:") 
        for i in replaceDict:
            if (type(i) == str):
                print(f"    {inverse_mapper[i]} was changed to {i} -- {replaceDict[i]} times")
            else:
                print(f"    {inverse_mapper[i]} was replaced with an empty value -- {replaceDict[i]} times")
            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "infile", "Tab or comma delimited input file (csv/tsv extension required)", "FileChooser")
        ServiceTaskBase.add_argument(parser, "mapfile", "TSV mapping file (column headers required)", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "infile", "Tab or comma delimited input file (csv/tsv extension required)")
        ServiceTaskBase.add_cli_argument(parser, "mapfile", "TSV mapping file (column headers required)")
