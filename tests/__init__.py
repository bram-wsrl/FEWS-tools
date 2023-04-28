from pathlib import Path


BASEPATH = Path(__file__).resolve().parent.parent
TESTPATH = BASEPATH / 'tests'
DATAPATH = TESTPATH / 'data'
OUTPUTPATH = DATAPATH / 'output'

PIXML_TIMESERIES_SL = 'pixml_timeseries_sl.xml'
PIXML_TIMESERIES_HL = 'pixml_timeseries_hl.xml'
