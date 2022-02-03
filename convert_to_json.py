import argparse
import camelot
import logging
import PyPDF2
import tqdm
import pandas
import json
import pickle
import os
from tqdm.contrib.logging import tqdm_logging_redirect
import hashlib

def hash_file(filename):
   """"This function returns the SHA-1 hash
   of the file passed into it"""

   # make a hash object
   h = hashlib.sha1()

   # open file for reading in binary mode
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return str(h.hexdigest())


logger = logging.getLogger(__name__)

def strategy1(args):
    logger.info("Getting the number of pages for the input file")
    pdf_reader = PyPDF2.PdfFileReader(args.input)
    pages = pdf_reader.getNumPages()
    logger.debug("Number of pages: {}".format(pages))

    data = {}
    logger.info("Started inspecting input file... This will take a while")
    for i in tqdm.tqdm(range(pages), desc="Pages", unit="pages"):
        filename = "temp/{}-{}.pickle".format(hash_file(args.input), str(i))
        try:
            tables = pickle.loads(open(filename, "rb").read())
        except:
            tables = camelot.read_pdf(args.input, flavor='stream', pages=str(i+1))
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    raise exc
            open(filename, "wb").write(pickle.dumps(tables))
        for table in tables:
            df: pandas.DataFrame = table.df
            columnstosum = [args.scorecolumn]
            if args.sum:
                columnstosum = args.sum
            
            for index, row in df.iterrows():
                if index < args.skiplines:
                    continue
                if index == args.skiplines:
                    logger.debug(row)
                score = 0
                for column in columnstosum:
                    if column < 0:
                        column = len(df.columns)+args.scorecolumn
                    asd: str = row[column]
                    asd = asd.strip('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
                    try:
                        score += float(asd)
                    except:
                        pass
                data[row[args.namecolumn]] = score
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file", required=True)
    parser.add_argument('--debug', action=argparse.BooleanOptionalAction, dest="debug",
                        help='enable debug mode (default: false)')
    parser.add_argument("--skiplines", help="Skip first x lines", default=0, type=int)
    parser.add_argument("-n", "--namecolumn", help="The column that contains the name", default=0, type=int)
    parser.add_argument("-s", "--scorecolumn", help="The column that contains the score", default=1, type=int)
    parser.add_argument("--sum", help="The columns that need to be summed", default=[], type=int, nargs='+')
    parser.add_argument("-o", "--output", help="Output file", required=True)
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    data = strategy1(args)

    with open(args.output, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

if __name__ == "__main__":
    with tqdm_logging_redirect():
        main()