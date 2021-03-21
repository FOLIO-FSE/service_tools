from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
from pathlib import Path
from collections import defaultdict
import csv
import pandas as pd

class MFHDBuilder(ServiceTaskBase):
    def __init__(self, args):
        self.infile = args.infile
        self.bibField = args.bibID
        self.holdField = args.holdID
        self.locField = args.location
        self.callField = args.callno
        self.filetype = Path(args.infile).suffix 
        self.outfile = self.infile[:-len(self.filetype)] + ".mrk"

    def do_work(self):

        if (self.filetype == ".tsv"):
            df = pd.read_csv(self.infile, dtype=str, sep='\t')  
        else:
            df = pd.read_csv(self.infile, dtype=str)  

        f = open(self.outfile, "w")

        LDR = '=LDR  00166cx  a22000853  4500\n'
        marc008 = '=008  9810090p\\\\\\\\8\\\\\\4001aueng0000000\n'

        counter = 0
        multirecords = 0
        repeatCounter = 0 
        recordsWritten = 0 
        repeatRecords = defaultdict(int)
        
        for row in df.index:
            bibID = df[self.bibField][row] 
            marc001 = '=001    ' + df[self.holdField][row] + "\n"
            marc004 = '=004    ' + bibID + "\n"

            location = df[self.locField][row]
            callno = str(df[self.callField][row])
            callno = callno.replace(" ", "$i", 1)

            marc852 = '=852 0\\$b' + location + '$h' + callno + "\n"
            ## make sure record was not already processed
            if (repeatRecords[bibID] != 1): 
                f.write(LDR)
                f.write(marc001)
                f.write(marc004)
                f.write(marc008)
                f.write(marc852)
                f.write("\n")
                repeatRecords[bibID] = 1
                recordsWritten += 1
            else:
                repeatCounter +=1

            counter += 1
        print(f"Process complete. {counter} items were processed. {recordsWritten} MFHD records were created and written to {self.outfile} and {repeatCounter} MHFDs will be associated with more than one item record")

            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "infile", "Tab or comma delimited input file (csv/tsv extension required)", "FileChooser")
        ServiceTaskBase.add_argument(parser, "holdID", "Field containing holdings ID", "")
        ServiceTaskBase.add_argument(parser, "bibID", "Field containing bib ID", "")
        ServiceTaskBase.add_argument(parser, "location", "Field containing location code", "")
        ServiceTaskBase.add_argument(parser, "callno", "Field containing call number", "")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "infile", "Tab or comma delimited input file (csv/tsv extension required)", "FileChooser")
        ServiceTaskBase.add_argument(parser, "holdID", "Field containing holdings ID", "")
        ServiceTaskBase.add_argument(parser, "bibID", "Field containing bib ID", "")
        ServiceTaskBase.add_argument(parser, "location", "Field containing location code", "")
        ServiceTaskBase.add_argument(parser, "callno", "Field containing call number", "")
