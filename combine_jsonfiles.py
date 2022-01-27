import json
import logging
import argparse
import plotly.express as px

logger = logging.getLogger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input files", required=True, default=[], type=str, nargs='+')
    parser.add_argument('--debug', action=argparse.BooleanOptionalAction, dest="debug",
                        help='enable debug mode (default: false)')
    parser.add_argument("-o", "--output", help="Output file", required=True)
    parser.add_argument('--plot', action=argparse.BooleanOptionalAction, dest="plot",
                        help='enable debug mode (default: false)')
    parser.add_argument("--gauss", help="Apply gauss distribution", default=[], type=int, nargs='+')
    parser.add_argument("--minimum", help="Mininum score to pass and to apply gauss distribution", type=int)
    args = parser.parse_args()
    
    if args.gauss:
        if len(args.gauss) != 10 - args.minimum + 1:
            raise Exception("You need to provide 10-minimum values for the gauss distribution")
        if sum(args.gauss) != 100:
            raise Exception("The sum of the values needs to be 100")

    data = {}
    for inputfile in args.input:
        with open(inputfile, 'r') as f:
            for key, value in json.load(f).items():
                if not key in data:
                    data[key] = float(value)
                else:
                    data[key] += float(value)
    if args.gauss:
        result = {}
        asd = []
        indexes = []
        failed = []
        for key, value in data.items():
            if not float(value) in result:
                result[float(value)] = []
            result[float(value)].append(key)
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
            l = len(asd)
            result[i+args.minimum] = asd[l * sum(args.gauss[:i]) // 100:l * sum(args.gauss[:i+1]) // 100]
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=4, sort_keys=True)
        data = result
    else:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
    if args.plot:
        x = []
        y = {}
        for key, value in data.items():
            if type(value) == list:
                y[int(key)] = len(value)
            else:
                if int(value) not in y:
                    y[int(value)] = 0
                    
                y[int(value)]+=1
        for key,value in y.items():
            x.append(key)
        fig = px.bar(x=x, y=y)
        fig.show()

if __name__ == "__main__":
    main()