import re
import datetime as dt
from pathlib import Path

import pandas as pd

from FEWS_tools import logger


FLAG_MAPPING = {
    'DAMO_pomp': {
        'Bedrijfsstatus': ['BS'],
        'Snelheid': ['SH'],
        'Toerental': ['TT'],
        'Ampere': ['A'],
        'Frequentie': ['FREQ']
        },
    'DAMO_stuw': {
        'onderdoorlaat_NAP': ['Hben', 'Hbov', 'SD'],
        'onderdoorlaat_NAP': ['Hben', 'Hbov', 'MWAR'],
        },
    }


def str_to_datetime(date, fmt='%d-%m-%Y'):
    return dt.datetime.strptime(date, fmt)


def flag_colname(subloc, param, dtres, suffix=''):
    '''build column names as created by convert_pixml2csv'''
    if param in ('Hbov', 'Hben'):
        return f'flag_{param}_H.M.{dtres}{suffix}'
    return f'flag_{subloc}_{param}.{dtres}{suffix}'


def update_flagging(basename: Path, damo_pomp: Path, output_folder: Path=None):
    '''
    Update dischage flagging with flagging of underlying series

    The maximum value flag available in the underlying series is
    used as flag value in the dicharge serie at the corresponding timestep

    basename is a directory that points to the input files
    input files shoud have a specific pattern (see regex)
    damo_pomp is a file that defined periods and rules for discharge calculations.
    output_folder if specified, files are written here and not overwritten
    '''
    # file pattern to match, this is output from convert_pixml2csv
    pattern = r'''.*_(?P<subloc>H|P[0-9]*|VL[0-9]*)_'''\
              r'''(?P<dtres>T[0-9]+)_(?P<slcode>SL[0-9]{6})\.csv'''
    pattern = re.compile(pattern)

    damo_pomp_df = pd.read_csv(damo_pomp, sep=';')
    output_folder = output_folder or basename

    for file in basename.iterdir():
        # select pattern matching files
        match = re.match(pattern, file.name)
        if match:
            logger.debug(f'Update flagging for: {file.name}')
            csv_in = pd.read_csv(file, parse_dates=['date'])

            # parse filepattern, get discharge flag col, select rules
            subloc, dtres, slcode = match.groups()
            flag_discharge_col = flag_colname(subloc, 'Q.B', dtres[1:])
            flag_rules = damo_pomp_df[damo_pomp_df.CODE == slcode]

            if not flag_rules.empty:
                for rule in flag_rules.itertuples():
                    # select columns for specific period
                    params = FLAG_MAPPING['DAMO_pomp'][rule.TYPEFORMULE]
                    flag_underlying_cols = [
                        flag_colname(subloc, param, dtres[1:]) for param in params]

                    # The discharge flag itself is used in comparison
                    flag_underlying_cols += [flag_discharge_col]

                    # select specific period to update
                    start_period = str_to_datetime(rule.OBJECTBEGI)
                    end_period = str_to_datetime(rule.OBJECTEIND)
                    indexer = (start_period <= csv_in.date) & (csv_in.date < end_period)

                    # abort update if any column not present
                    column_not_found = set(flag_underlying_cols) - set(csv_in.columns)
                    if column_not_found:
                        logger.warning(
                            f'''{column_not_found} not found, skipping {indexer.sum()} '''
                            f'''rows between {start_period} & {end_period}''')
                        continue

                    # update flagging for specific period w.r.t. underlying series
                    # the existing discharge flag is updated inplace
                    csv_in.loc[indexer, flag_discharge_col] = csv_in.loc[
                        indexer, flag_underlying_cols].max(axis=1)

                outputfilepath = output_folder / f'{file.name}'
                csv_in.to_csv(outputfilepath, index=False, na_rep='NaN')
                logger.info(f'Updated {outputfilepath}')
            else:
                logger.warning(f'{slcode} not found in {damo_pomp} for {file}')
