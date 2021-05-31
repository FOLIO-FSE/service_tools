from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
from pathlib import Path
from collections import defaultdict
import csv
import pandas as pd


class MFHDBuilder(ServiceTaskBase):
    def __init__(self, args):
        super().__init__()
        self.infile = args.infile
        self.bibField = args.bibID
        self.holdField = args.holdID
        self.library = args.library
        self.locField = args.location
        self.callField = args.callno
        self.holdings = args.holdings
        self.filetype = Path(args.infile).suffix
        self.outfile = self.infile[:-len(self.filetype)] + ".mrk"

    def do_work(self):

        if (self.filetype == ".tsv"):
            df = pd.read_csv(self.infile, dtype=str, sep='\t')
        else:
            df = pd.read_csv(self.infile, dtype=str)

        f = open(self.outfile, "w", encoding='utf-8')

        LDR = '=LDR  00166cx  a22000853  4500\n'
        marc008 = '=008  9810090p\\\\\\\\8\\\\\\4001aueng0000000\n'

        counter = 0
        multirecords = 0
        repeatCounter = 0
        recordsWritten = 0
        repeatRecords = defaultdict(int)

        for row in df.index:
            bibID = str(df[self.bibField][row])
            holdID = str(df[self.holdField][row])
            library = str(df[self.locField][row])
            location = str(df[self.locField][row])
            callno = str(df[self.callField][row])
            callno = callno.replace(" ", "$i", 1)

            if (self.library != 'NA'):
                holdID = holdID + library 
                marc852 = '=852 0\\$a' + library + '$c' + location + '$h' + callno + "\n" 
            else:
                marc852 = '=852 0\\$c' + location + '$h' + callno + "\n"

            marc001 = '=001    ' + holdID + "\n"
            marc004 = '=004    ' + bibID + "\n"


            ## make sure record was not already processed
            if (repeatRecords[bibID] != 1):
                f.write(LDR)
                f.write(marc001)
                f.write(marc004)
                f.write(marc008)
                f.write(marc852)

                if (self.holdings != 'NA'):
                    holdID = holdID + library 
                    marc866 = '=866  \\$a' + self.holdings + "\n" 
                    f.write(marc866) 

                f.write("\n")
                repeatRecords[bibID] = 1
                recordsWritten += 1
            else:
                repeatCounter += 1

            counter += 1
        print(
            f"Process complete. {counter} items were processed. {recordsWritten} MFHD records were created and written to {self.outfile} and {repeatCounter} MHFDs will be associated with more than one item record")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "infile", "Tab or comma delimited input file (csv/tsv extension required)",
                                     "FileChooser")
        ServiceTaskBase.add_argument(parser, "holdID", "Field containing holdings ID", "")
        ServiceTaskBase.add_argument(parser, "bibID", "Field containing bib ID", "")
        ServiceTaskBase.add_argument(parser, "library", "Type NA if not applicable. Field containing library code", "")
        ServiceTaskBase.add_argument(parser, "location", "Field containing location code", "")
        ServiceTaskBase.add_argument(parser, "callno", "Field containing call number", "")
        ServiceTaskBase.add_argument(parser, "holdings", "Type NA if not applicable. Field containing holdings statement", "")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "infile",
                                         "Tab or comma delimited input file (csv/tsv extension required)")
        ServiceTaskBase.add_cli_argument(parser, "holdID", "Field containing holdings ID")
        ServiceTaskBase.add_cli_argument(parser, "bibID", "Field containing bib ID")
        ServiceTaskBase.add_cli_argument(parser, "library", "Type NA if not applicable. Field containing library code")
        ServiceTaskBase.add_cli_argument(parser, "location", "Field containing location code")
        ServiceTaskBase.add_cli_argument(parser, "callno", "Field containing call number")
        ServiceTaskBase.add_cli_argument(parser, "holdings", "Type NA if not applicable. Field containing holdings statement")
