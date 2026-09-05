"""Builds the two JSON files the NoobsNepse iOS app reads.

    app/current.json   latest daily bar per symbol (+ company name, market cap)
    app/monthly.json   full monthly OHLCV candles per symbol

Both are keyed by trading symbol so the app decodes straight into a dictionary
and looks holdings up by ticker without scanning.

Run it from main.py BEFORE clean_dir() -- company names and market caps only
exist in symbols/symbols.csv, which clean_dir() deletes. When that file is gone
(standalone runs) the previous app/current.json is reused for the metadata, so
regenerating never silently drops company names.

Monthly candles are emitted raw. The buy signal is deliberately NOT precomputed
here: a stored flag drifts from its own definition the moment the rule changes,
and the app can compare close > open itself.
"""

import csv
import json
import os
from datetime import datetime, timezone

DATA_DIR = 'data'
APP_DIR = 'app'
SYMBOLS_CSV = 'symbols/symbols.csv'


def _read_rows(path):
    """Daily bars from one scraped CSV, oldest first. Bad rows are skipped."""
    rows = []
    with open(path, 'r') as f:
        for r in csv.DictReader(f):
            try:
                rows.append((
                    r['timestamp'][:10],
                    float(r['open']), float(r['high']),
                    float(r['low']), float(r['close']),
                    float(r['volume'] or 0),
                ))
            except (ValueError, TypeError, KeyError):
                continue
    return rows


def _monthly(rows):
    """Collapse daily bars into monthly candles: first open, max high, min low,
    last close, summed volume. Returns [[YYYY-MM, o, h, l, c, v], ...]."""
    out = []
    for date, o, h, l, c, v in rows:
        month = date[:7]
        if out and out[-1][0] == month:
            candle = out[-1]
            candle[2] = max(candle[2], h)
            candle[3] = min(candle[3], l)
            candle[4] = c
            candle[5] += v
        else:
            out.append([month, o, h, l, c, v])
    return [[m, round(o, 2), round(h, 2), round(l, 2), round(c, 2), int(v)]
            for m, o, h, l, c, v in out]


def _load_meta():
    """symbol -> {name, marketcap, weight}. Falls back to the previous
    current.json when symbols.csv has already been cleaned away."""
    meta = {}
    if os.path.exists(SYMBOLS_CSV):
        with open(SYMBOLS_CSV, 'r') as f:
            for r in csv.DictReader(f):
                symbol = (r.get('Symbol') or '').strip()
                if not symbol:
                    continue
                meta[symbol] = {
                    'n': (r.get('Company_Name') or '').strip(),
                    'mc': _num(r.get('Marketcap')),
                    'w': _num(r.get('Nepse_Weight')),
                }
        print(f'_load_meta() -> {len(meta)} symbols from {SYMBOLS_CSV}')
        return meta

    previous = os.path.join(APP_DIR, 'current.json')
    if os.path.exists(previous):
        with open(previous, 'r') as f:
            for symbol, row in json.load(f).get('symbols', {}).items():
                meta[symbol] = {'n': row.get('n', ''), 'mc': row.get('mc'), 'w': row.get('w')}
        print(f'_load_meta() -> symbols.csv missing, reused {len(meta)} names from {previous}')
    else:
        print('_load_meta() -> no symbol metadata available; names will be blank')
    return meta


def _num(value):
    try:
        return float(str(value).replace(',', ''))
    except (ValueError, TypeError, AttributeError):
        return None


def build():
    if not os.path.isdir(DATA_DIR):
        print(f'build() -> {DATA_DIR}/ not found, nothing to build')
        return

    os.makedirs(APP_DIR, exist_ok=True)
    meta = _load_meta()
    generated = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    current, monthly, as_of = {}, {}, ''

    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.endswith('.csv'):
            continue
        symbol = filename[:-4]
        rows = _read_rows(os.path.join(DATA_DIR, filename))
        if not rows:
            print(f'build() -> {symbol}: no usable rows, skipped')
            continue

        monthly[symbol] = _monthly(rows)

        date, o, h, l, c, v = rows[-1]
        previous_close = rows[-2][4] if len(rows) > 1 else c
        info = meta.get(symbol, {})
        current[symbol] = {
            'n': info.get('n', ''),
            'd': date,
            'o': round(o, 2), 'h': round(h, 2), 'l': round(l, 2), 'c': round(c, 2),
            'p': round(previous_close, 2),
            'ch': round((c - previous_close) / previous_close * 100, 2) if previous_close else 0.0,
            'v': int(v),
            'mc': info.get('mc'),
            'w': info.get('w'),
        }
        as_of = max(as_of, date)

    _write('current.json', {'generated': generated, 'asOf': as_of, 'symbols': current})
    _write('monthly.json', {'generated': generated, 'asOf': as_of, 'symbols': monthly})

    candles = sum(len(v) for v in monthly.values())
    print(f'build() -> {len(current)} symbols, {candles} monthly candles, as of {as_of}')


def _write(name, payload):
    path = os.path.join(APP_DIR, name)
    with open(path, 'w') as f:
        json.dump(payload, f, separators=(',', ':'))
    print(f'_write() -> {path} ({os.path.getsize(path) / 1024:.0f} KB)')


if __name__ == '__main__':
    build()
