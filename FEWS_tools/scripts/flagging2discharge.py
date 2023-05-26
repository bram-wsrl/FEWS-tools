# load DAMO_pomp
# point to discharge csv
# find sublocation in DAMO_pomp
# loop over rows in DAMO_pomp
# transfer flagging to discharge series for selected period using mapping

# Only DAMO_pomp functionality implemented
# add unittests
# add comments
# remove large files from test dir



import re
import datetime as dt
from pathlib import Path

import pandas as pd

from FEWS_tools import logger


FLAG_MAPPING = {
    'DAMO_pomp': {
        'Bedrijfsstatus': ['BS', 'Q.B'],
        'Snelheid': ['SH', 'Q.B'],
        'Toerental': ['TT', 'Q.B'],
        'Ampere': ['A', 'Q.B'],
        'Frequentie': ['FREQ', 'Q.B']
        },
    'DAMO_stuw': {
        'onderdoorlaat_NAP': ['Hben', 'Hbov', 'SD', 'Q.B'],
        'onderdoorlaat_NAP': ['Hben', 'Hbov', 'MWAR', 'Q.B'],
        },
    }


def str_to_datetime(date, fmt='%d-%m-%Y'):
    return dt.datetime.strptime(date, fmt)


def flag_colname(subloc, param, dtres, suffix=''):
    if param in ('Hbov', 'Hben'):
        return f'flag_{param}_H.M.{dtres}{suffix}'
    return f'flag_{subloc}_{param}.{dtres}{suffix}'


def update_flagging(basename, damo_pomp, output_folder=None):

    damo_pomp_df = pd.read_csv(damo_pomp, sep=';')

    pattern = r'''.*_(?P<subloc>H|P[0-9]*|VL[0-9]*)_'''\
              r'''(?P<dtres>T[0-9]+)_(?P<slcode>SL[0-9]{6})\.csv'''
    pattern = re.compile(pattern)

    for file in basename.iterdir():
        match = re.match(pattern, file.name)
        if match:
            subloc, dtres, slcode = match.groups()
            csv_in = pd.read_csv(file, parse_dates=['date'])

            logger.debug(f'Update flagging for: {file.name}')

            flag_column_out = flag_colname(subloc, 'Q.B', dtres[1:], '_updated')
            csv_in[flag_column_out] = csv_in[flag_colname(subloc, 'Q.B', dtres[1:])]

            update_cnt = 0
            for row in damo_pomp_df[damo_pomp_df.CODE == slcode].itertuples():

                params = FLAG_MAPPING['DAMO_pomp'][row.TYPEFORMULE]
                flag_columns_in = [flag_colname(subloc, param, dtres[1:]) for param in params]

                start_period = str_to_datetime(row.OBJECTBEGI)
                end_period = str_to_datetime(row.OBJECTEIND)
                indexer = (start_period <= csv_in.date) & (csv_in.date < end_period)

                column_not_found = set(flag_columns_in) - set(csv_in.columns)
                if column_not_found:
                    logger.warning(
                        f'''{column_not_found} not found, skipping {indexer.sum()} '''
                        f'''rows between {start_period} & {end_period}''')
                    continue

                csv_in.loc[indexer, flag_column_out] = csv_in.loc[indexer, flag_columns_in].max(axis=1)
                csv_in[flag_column_out] = csv_in[flag_column_out]

                update_cnt += indexer.sum()
                logger.debug(
                    f'''{row.TYPEFORMULE}, {row.OBJECTBEGI}, '''
                    f'''{row.OBJECTEIND}, nrows={indexer.sum()}''')

            changes = csv_in[csv_in[flag_column_out.strip('_updated')] != csv_in[flag_column_out]]
            if not changes.empty:
                logger.debug(f'\n{changes.to_string()}')

            # csv_in.to_csv(output_folder or basename / f'{file.stem}_upd.csv')
            logger.info(f'Updated {file} ({update_cnt}/{len(csv_in)} rows)')


if __name__ == '__main__':
    basename = Path(r'./tests/data/flagging/csv/')
    damo_pomp = Path(r'./tests/data/flagging/DAMO_pomp.csv')
    update_flagging(basename, damo_pomp)
