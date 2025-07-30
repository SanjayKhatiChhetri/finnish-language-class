import argparse
import os
from .utils import process_file, batch_process

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Google Classroom Parser')
    parser.add_argument('--input', help='Input HTML file or directory')
    parser.add_argument('--output', help='Output TS file or directory')
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        batch_process(args.input, args.output)
    else:
        process_file(args.input, args.output)