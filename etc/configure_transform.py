#!/usr/bin/env python

import os
import re
import sys
sys.path.append('../libexec/python')

from sutils import (
    get_fullpath,
    read_file,
    write_file
)

from logman import logger
import optparse


def get_parser():

    parser = optparse.OptionParser(description="singularity configuration parsing helper in python")


    # Configuration defaults header
    parser.add_option("--defaults",
                      dest='defaults',
                      help="configuration defaults header file (../src/lib/config_defaults.h)",
                      type=str)

    # input configuration file
    parser.add_option("--infile",
                      dest='infile',
                      help="the configuration input file path (singularity.conf.in)",
                      type=str)

    # Output configuration file
    parser.add_option("--outfile",
                      dest='outfile',
                      help="the configuration output file path (singularity.conf)",
                      type=str)

    return parser


def main():
    '''parse configuration options and produce configuration output file
    '''
    logger.info("\n*** STARTING PYTHON CONFIGURATION HELPER ****")
    parser = get_parser()

    try:
        (args,options) = parser.parse_args()
    except:
        logger.error("Input args to %s improperly set, exiting.", os.path.abspath(__file__))
        parser.print_help()
        sys.exit(1)

    # Check for required args
    [check_required(parser,arg) for arg in [args.defaults,
                                            args.infile,
                                            args.outfile]]

    # Run the configuration
    configure(args)

def check_required(parser,arg):
    '''check_required arg checks that an argument is defined.
    It is a workaround for missing required parameter of argparse
    :param parser: the parser
    :param arg: the argument
    '''
    if not arg:   # if filename is not given
        parser.error('Missing required argument.')
        parser.print_help()
        sys.exit(1)


def configure(args):

    # Get fullpath to each file, and concurrently check that exists
    defaultfile = get_fullpath(args.defaults) # ../src/lib/config_defaults.h
    infile = get_fullpath(args.infile)       # singularity.conf.in

    # Find define statements
    define_re = re.compile("#define ([A-Z_]+) (.*)")

    # Read in input and default files
    defaultfile = read_file(defaultfile)
    data = "".join(read_file(infile))

    # Lookup for values we want replaced
    lookup = {'0':'no',
              '1':'yes'}

    defaults = {}
    # Read in defaults to dictionary
    for line in defaultfile:
        match = define_re.match(line)
        if match:
            key, value = match.groups()

            # Maintain the original default set by user
            defaults[key] = value

            # Use parsed value for final config
            new_value = value.replace('"', '')
            if new_value in lookup:
                new_value = lookup[new_value]
            data = data.replace("@" + key + "@", new_value)

    # Write to output file
    outfile = "%s.tmp" %(args.outfile)
    write_file(outfile,data)
    os.rename(outfile, args.outfile)

    logger.info("*** FINISHED PYTHON CONFIGURATION HELPER ****\n")


if __name__ == '__main__':
    main()
