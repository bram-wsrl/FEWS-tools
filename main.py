
if __name__ == '__main__':
    import logging
    import argparse
    from pathlib import Path

    from FEWS_tools import logger
    from FEWS_tools.lib.utils import add_loghandler
    from FEWS_tools.scripts.pixml2csv import convert_pixml2csv


    # init parsers - extend with subparser for new function
    parser = argparse.ArgumentParser('FEWS Tools', description='Global options')

    loglevels = ['DEBUG', 'INFO', 'WARNING']
    parser.add_argument('-v', '--loglevel', choices=loglevels, default=loglevels[1])
    parser.add_argument('-l', '--logfile', type=Path)

    # subparsers
    subparsers = parser.add_subparsers(dest='command')

    pixml2csv_parser = subparsers.add_parser('pixml2csv', description='pixml2csv options')
    pixml2csv_parser.add_argument('-b', '--basename', required=True, type=Path)
    pixml2csv_parser.add_argument('-f', '--filename', required=True, type=str)
    pixml2csv_parser.add_argument('-o', '--output_folder', type=Path)
    pixml2csv_parser.add_argument('-s', '--separate_events', action='store_false')
    args = parser.parse_args()

    logger.setLevel(args.loglevel)

    if args.logfile is not None:
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        add_loghandler(logger, logging.FileHandler, logging.DEBUG, fmt,
                       filename=args.logfile, mode='w')

        logger.debug('Logger Initialized')

    if args.command == 'pixml2csv':
        convert_pixml2csv(
            args.basename, args.filename, args.output_folder, args.separate_events)

        logger.info('Conversion completed!')
