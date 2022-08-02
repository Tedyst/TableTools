import json
import logging
import argparse
import plotly.express as px
import re

logging.basicConfig()

logger = logging.getLogger()


def stripname(name):
    return re.sub(' (.*\.)* ', ' ', name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input files",
                        required=True, default=[], type=str, nargs='+')
    parser.add_argument('--debug', action=argparse.BooleanOptionalAction, dest="debug",
                        help='enable debug mode (default: false)')
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument('--plot', action=argparse.BooleanOptionalAction, dest="plot",
                        help='enable debug mode (default: false)')
    parser.add_argument('--format', dest="format",
                        default='json', choices=['json', 'csv'])
    parser.add_argument('--stripname', action=argparse.BooleanOptionalAction, dest="stripname",
                        help='enable debug mode (default: false)')
    parser.add_argument(
        "--gauss", help="Apply gauss distribution", default=[], type=int, nargs='+')
    parser.add_argument(
        "--minimum", help="Mininum score to pass and to apply gauss distribution", type=int)
    parser.add_argument(
        "--replacescore", help="Replace score from the first files with the score in the next files", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args.gauss:
        if len(args.gauss) != 10 - args.minimum + 1:
            raise Exception(
                "You need to provide 10-minimum values for the gauss distribution")
        if sum(args.gauss) != 100:
            raise Exception("The sum of the values needs to be 100")

    data = {}
    for inputfile in args.input:
        with open(inputfile, 'r') as f:
            for key, value in json.load(f).items():
                if args.stripname:
                    key = stripname(str(key))
                if not key in data or (args.replacescore and value != 0):
                    data[key.upper()] = float(value)
                else:
                    data[key.upper()] += float(value)
    if args.gauss:
        result = {}
        asd = []
        indexes = []
        failed = []
        for key, value in data.items():
            if not int(value) in result:
                result[int(value)] = []
            result[int(value)].append(key)
        for index in result:
            indexes.append(index)
        indexes.sort()
        for index in indexes:
            if index < args.minimum:
                failed.extend(result[index])
                continue
            asd.extend(result[index])
        result = {}
        for i in range(len(args.gauss)):
            begin = len(asd) * sum(args.gauss[:i]) // 100
            end = len(asd) * sum(args.gauss[:i+1]) // 100
            result[i+args.minimum] = asd[begin:end]
        for nota, value in result.items():
            logger.info(
                f"Extracted {len(value)} values for {nota} with gauss distribution")
        if args.output:
            if args.format == "json":
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=4, sort_keys=True)
            if args.format == "csv":
                with open(args.output, "w") as f:
                    for nota, value in result.items():
                        for persoana in value:
                            f.write("{},{}\n".format(persoana, nota))
        data = result
    else:
        if args.output:
            if args.format == "json":
                with open(args.output, 'w') as f:
                    json.dump(data, f, indent=4, sort_keys=True)
            if args.format == "csv":
                with open(args.output, "w") as f:
                    for key, value in data.items():
                        f.write("{},{}\n".format(key, value))
    if args.plot:
        x = []
        y = {}
        for key, value in data.items():
            if type(value) == list:
                y[int(key)] = len(value)
            else:
                if int(value) not in y:
                    y[int(value)] = 0

                y[int(value)] += 1
        for key, value in y.items():
            x.append(key)
        fig = px.bar(x=x, y=y)
        fig.show()


if __name__ == "__main__":
    main()
