from service_tasks.service_task_base import ServiceTaskBase, abstractmethod
import sys, csv, pandas as pd

class IiiBoundWithCsvProcessor(ServiceTaskBase):
    def __init__(self, args):
        self.csv_file = args.csv_file

    def do_work(self):

        outfilename = self.csv_file + ".modified"
        outfile = open(outfilename, "w")

        with open(self.csv_file) as f:
            csv_reader = csv.reader(f)
            header = next(csv_reader)
            joined = '","'.join(header)
            # each boundwith has a .b number and call number, subtract 2 from length of the header to
            # find number of fixed fields and then divide by 2 to find number of boundwidths
            num_fields = len(header) - 2
            rec = 1
            outfile.write(f'"{joined}"')
            print("Processing file. Please wait....")

            for row in csv_reader:
                lrow = list(row)
                num_boundwiths = int((len(lrow) - num_fields)/2)
                boundwiths = lrow[:num_boundwiths]
                itemno = lrow[num_boundwiths]
                itemcalls = lrow[num_boundwiths + 1:(num_boundwiths + 1)*2 - 1]
                rest_of_row = lrow[(num_boundwiths + 1)*2:]

                # reformat the rows for output
                boundwiths = "{{'" + "' '".join(boundwiths) + "'}},"
                itemcalls = "{{'" + "' '".join(itemcalls) + "'}},"
                #
                rest_of_row = ''","''.join(rest_of_row)
                rec += 1
                outfile.write(f'{boundwiths}","{itemno}","{itemcalls}","{rest_of_row}"\n')

            outfile.close()
            total_records = str(rec)
            print(f"{total_records} records written into {outfilename}")
            
    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_argument(parser, "csv_file", "Delimited file containing field to analyze", "FileChooser")

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_cli_argument(parser, "csv_file", "Delimited file containing field to analyze")
