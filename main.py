
if __name__ == '__main__':
    import logging
    import argparse
    from pathlib import Path

    from FEWS_tools import logger
    from FEWS_tools.lib.utils import add_loghandler
    from FEWS_tools.scripts.pixml2csv import convert_pixml2csv
    from FEWS_tools.scripts.flagging2discharge import update_flagging


    # init parsers - extend with subparser for new function
    parser = argparse.ArgumentParser('FEWS Tools', description='Global options')

    loglevels = ['DEBUG', 'INFO', 'WARNING']
    parser.add_argument('-v', '--loglevel', choices=loglevels, default=loglevels[1])
    parser.add_argument('-l', '--logfile', type=Path)

    # subparsers
    subparsers = parser.add_subparsers(dest='command')

    pixml2csv_parser = subparsers.add_parser(
        'pixml2csv', description='pixml2csv options')
    pixml2csv_parser.add_argument('-b', '--basename', required=True, type=Path)
    pixml2csv_parser.add_argument('-f', '--filename', required=True, type=str)
    pixml2csv_parser.add_argument('-o', '--output_folder', type=Path)
    pixml2csv_parser.add_argument('-s', '--separate_events', action='store_false')
    pixml2csv_parser.add_argument('-j', '--join_h_to_sl', action='store_true')

    flagging2discharge_parser = subparsers.add_parser(
        'flagging2discharge', description='update flagging options')
    flagging2discharge_parser.add_argument('-b', '--basename', required=True, type=Path)
    flagging2discharge_parser.add_argument('-p', '--damo_pomp', required=True, type=str)
    flagging2discharge_parser.add_argument('-o', '--output_folder', type=Path)

    args = parser.parse_args()

    logger.setLevel(args.loglevel)

    if args.logfile is not None:
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        add_loghandler(logger, logging.FileHandler, logging.DEBUG, fmt,
                       filename=args.logfile, mode='a')

        logger.debug('Logger Initialized')

    if args.command == 'pixml2csv':
        convert_pixml2csv(
            args.basename, args.filename, args.output_folder, args.separate_events, args.join_h_to_sl)

        logger.info('Conversion completed!')

    elif args.command == 'flagging2discharge':
        update_flagging(args.basename, args.damo_pomp, args.output_folder)

        logger.info('Update completed!')
