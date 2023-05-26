from pathlib import Path

DEBUG = False

BASEPATH = Path(__file__).resolve().parent.parent
TESTPATH = BASEPATH / 'tests'
DATAPATH = TESTPATH / 'data'
FLAGDATA = DATAPATH / 'flagging'
OUTPUTPATH = DATAPATH / 'output'

PIXML_TIMESERIES_SL = 'pixml_timeseries_sl.xml'
PIXML_TIMESERIES_HL = 'pixml_timeseries_hl.xml'
PIXML_TIMESERIES_HL_SL = 'pixml_timeseries_hl_sl.xml'
PIXML_TIMESERIES_HL_ORDER = 'pixml_timeseries_hl_order.xml'

DAMO_POMP = FLAGDATA / 'DAMO_pomp.csv'
