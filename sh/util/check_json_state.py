import sys
import json


if __name__ == '__main__':
    try:
        # implicit == True
        if json.load(sys.stdin)['state']:
            sys.exit(0)
        else:
            sys.exit(1)
    except json.JSONDecodeError:
        sys.stderr.write("decode error\n")
        exit(2)
    except KeyError:
        sys.stderr.write("key error\n")
        exit(3)
