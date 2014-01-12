#!/usr/bin/python
#
# Copyright (c) 2014, Mendix bv
# All Rights Reserved.
#
# http://www.mendix.com/
#

import cmd
import sys
import pmCommand

from pmCommand import logger


class CLI(cmd.Cmd):

    def __init__(self, yaml_files=None):
        logger.debug('Using pmCommand version %s' % pmCommand.__version__)
        cmd.Cmd.__init__(self)
        self._pmCommand = pmCommand.PMCommand()
        self._sort = True

    def do_login(self, args):
        (username, password) = args.split()
        self._pmCommand.login(username, password)

    def do_sort(self, args):
        self._sort = not self._sort
        logger.info("Sorted output is now %s." %
                    ("on" if self._sort else "off",))

    def do_listipdus(self, args):
        pdus = self._pmCommand.listipdus()
        (fields, headers) = self._pmCommand.listipdus_table_info()
        self._print_table(fields, headers, pdus)

    def do_status(self, args):
        outlets = self._pmCommand.status()
        (fields, headers) = self._pmCommand.status_table_info()
        self._print_table(fields, headers, outlets)

    def outlet_action(self, action, args):
        pdu_outlets = [x.strip() for x in args.split(',')]
        for pdu_outlet in pdu_outlets:
            (pdu_id, outlet_id) = pmCommand.util.parse_outlet(pdu_outlet)
            if pdu_id is not None and outlet_id is not None:
                self._pmCommand.on(pdu_id, outlet_id)

    def do_on(self, args):
        self.outlet_action("on", args)

    def _print_table(self, fields, headers, rows):
        if self._sort:
            rows = sorted(rows)

        output = ['']
        maxlen = {}
        for field in fields:
            maxlen[field] = max(len(headers[field]),
                                max([len(row.label[field]) for row in rows]))
            output.append(headers[field].ljust(maxlen[field]))
        print '  '.join(output)

        output = ['']
        for field in fields:
            output.append('=' * maxlen[field])
        print '  '.join(output)

        for row in rows:
            output = ['']
            for field in fields:
                output.append(row.label[field].ljust(maxlen[field]))
            print '  '.join(output)

    def do_exit(self, args):
        return -1

    def do_quit(self, args):
        return -1

    def do_EOF(self, args):
        print
        return -1

    # if the emptyline function is not defined, Cmd will automagically
    # repeat the previous command given, and that's not what we want
    def emptyline(self):
        pass

    def do_help(self, args):
        print("""pmCommand strikes back!

Available commands:
 login <url> <username> <password>
""")

        print("Hint: use tab autocompletion for commands!")

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        "-c",
        action="append",
        type="string",
        dest="yaml_files"
    )
    parser.add_option(
        "-v",
        "--verbose",
        action="count",
        dest="verbose",
        help="increase verbosity of output (-vv to be even more verbose)"
    )
    parser.add_option(
        "-q",
        "--quiet",
        action="count",
        dest="quiet",
        help="decrease verbosity of output (-qq to be even more quiet)"
    )
    (options, args) = parser.parse_args()

    # how verbose should we be? see
    # http://docs.python.org/release/2.7/library/logging.html#logging-levels
    verbosity = 0
    if options.quiet:
        verbosity = verbosity + options.quiet
    if options.verbose:
        verbosity = verbosity - options.verbose
    verbosity = verbosity * 10 + 20
    if verbosity > 50:
        verbosity = 100
    if verbosity < 5:
        verbosity = 5
    logger.setLevel(verbosity)

    cli = CLI(yaml_files=options.yaml_files)
    if args:
        cli.onecmd(' '.join(args))
    else:
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            print("^C")
            sys.exit(130)  # 128 + SIGINT
