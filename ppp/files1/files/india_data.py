"""India-wide geography and environmental measurement storage.

Geographic boundaries come from the Government of India's BharatMap service.
Water measurements are imported from CPCB/NWDP; weather observations are
retrieved from Open-Meteo and stored with their source and location metadata.
"""

import json
import csv
from contextlib import closing
import io
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from datetime import datetime, timezone
from pathlib import Path

from geo_hierarchy import INDIA_GEO_DATABASE

DB_PATH = Path("data/india_water_quality.sqlite3")
DISTRICT_API = (
    "https://mapservice.gov.in/gismapservice/rest/services/"
    "BharatMapService/Admin_Boundary_District/MapServer/1/query"
)
DISTRICT_CACHE = {"expires": 0, "items": []}
COLLECTOR_STATUS = {"running": False, "last_run": None, "records": 0, "error": None}
COLLECTOR_LOCK = threading.Lock()
WEATHER_STATUS = {"last_run": None, "records": 0, "error": None}
_DAILY_THREAD = None
NWDP_DATASET_URL = "https://www.nwdp.nwic.gov.in/dataset/surface-water-quality-manual-chemical-parameters-cpcb"


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._active = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            self._active = [attrs.get("href", ""), ""]

    def handle_data(self, data):
        if self._active is not None:
            self._active[1] += data.strip() + " "

    def handle_endtag(self, tag):
        if tag == "a" and self._active is not None:
            self.links.append((self._active[0], self._active[1].strip()))
            self._active = None


def _fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "AquaVision/1.0 (CPCB open-data collector)"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read(), response.geturl()


def _key(value):
    return "".join(ch.lower() for ch in str(value) if ch.isalnum())


def _pick(row, aliases):
    keyed = {_key(k): v for k, v in row.items()}
    for alias in aliases:
        if keyed.get(alias):
            return str(keyed[alias]).strip()
    return ""


def _records_from_csv(data, state, source_url):
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return []
    fields = {_key(name): name for name in reader.fieldnames}
    state_col = next((fields[k] for k in ("state", "statename", "stateut") if k in fields), None)
    district_col = next((fields[k] for k in ("district", "districtname", "districtut") if k in fields), None)
    station_col = next((fields[k] for k in ("station", "stationname", "monitoringstation", "monitoringlocation", "sitename", "location") if k in fields), None)
    date_col = next((fields[k] for k in ("date", "sampledate", "samplingdate", "collectiondate", "monitoringdate", "observationdate") if k in fields), None)
    parameter_col = next((fields[k] for k in ("parameter", "parametername", "indicator") if k in fields), None)
    value_col = next((fields[k] for k in ("value", "result", "reading", "concentration") if k in fields), None)
    unit_col = next((fields[k] for k in ("unit", "units") if k in fields), None)
    meta_cols = {x for x in (state_col, district_col, station_col, date_col, parameter_col, value_col, unit_col) if x}
    numeric_cols = [name for name in reader.fieldnames if name not in meta_cols and any(word in _key(name) for word in (
        "ph", "oxygen", "bod", "cod", "ammonia", "nitrate", "chloride", "fluoride", "sulphate", "sulfate",
        "arsenic", "lead", "mercury", "cadmium", "boron", "calcium", "turbidity", "tds", "conductivity", "coliform", "iron", "zinc", "copper", "chromium", "temperature"
    ))]
    records = []
    for row_number, row in enumerate(reader, start=2):
        row_state = _pick(row, ["state", "statename", "stateut"]) or state
        station = _pick(row, ["station", "stationname", "monitoringstation", "monitoringlocation", "sitename", "location"])
        measured_at = _pick(row, ["date", "sampledate", "samplingdate", "collectiondate", "monitoringdate", "observationdate"])
        if not (station and measured_at):
            continue
        common = {"state": row_state, "district": _pick(row, ["district", "districtname", "districtut"]) or None,
                  "station": station, "measured_at": measured_at, "source": "CPCB/NWDP",
                  "source_url": source_url, "metadata": {"source_row": row_number}}
        if parameter_col and value_col:
            raw_value = row.get(value_col, "")
            try:
                value = float(str(raw_value).replace(",", "").strip())
            except (ValueError, TypeError):
                continue
            records.append({**common, "parameter": str(row.get(parameter_col, "")).strip(), "value": value,
                            "unit": row.get(unit_col) if unit_col else None})
        else:
            for column in numeric_cols:
                try:
                    value = float(str(row.get(column, "")).replace(",", "").strip())
                except (ValueError, TypeError):
                    continue
                records.append({**common, "parameter": column, "value": value})
    return records


def collect_nwdp_measurements(state=None):
    """Discover and import CPCB state CSV resources published by NWDP."""
    if not COLLECTOR_LOCK.acquire(blocking=False):
        return {"status": "running", **COLLECTOR_STATUS}
    COLLECTOR_STATUS.update(running=True, error=None)
    imported, errors, seen = 0, [], set()
    try:
        html, catalog_url = _fetch(NWDP_DATASET_URL)
        parser = _Links()
        parser.feed(html.decode("utf-8", errors="replace"))
        wanted_state = state.casefold() if state else None
        resources = []
        for href, label in parser.links:
            if "/resource/" not in href:
                continue
            title = urllib.parse.unquote(label)
            if not any(period in title for period in ("2021", "2026", "1961")):
                continue
            if wanted_state and wanted_state not in title.casefold():
                continue
            resource_url = urllib.parse.urljoin(catalog_url, href)
            if resource_url not in seen:
                resources.append((resource_url, title))
                seen.add(resource_url)
        for resource_url, title in resources:
            try:
                page, final_page = _fetch(resource_url)
                download_parser = _Links()
                download_parser.feed(page.decode("utf-8", errors="replace"))
                downloads = [(urllib.parse.urljoin(final_page, href), label) for href, label in download_parser.links
                             if href and ("download" in href.casefold() or ".csv" in href.casefold())]
                if not downloads:
                    errors.append(f"No CSV download link found for {title}")
                    continue
                csv_url, _ = downloads[0]
                csv_data, final_url = _fetch(csv_url)
                state_name = title.split("CPCB", 1)[-1].strip().split("(", 1)[0].strip()
                records = _records_from_csv(csv_data, state_name, final_url)
                if records:
                    imported += save_measurements(records)
                else:
                    errors.append(f"No recognizable observation rows in {title}")
            except Exception as exc:
                errors.append(f"{title}: {exc}")
        if not resources:
            raise RuntimeError("No CPCB state resources found on the NWDP catalog page")
        COLLECTOR_STATUS.update(records=imported, last_run=datetime.now(timezone.utc).isoformat(),
                                error="; ".join(errors[:10]) if errors else None)
        return {"status": "complete", "resources": len(resources), "records_imported": imported,
                "errors": errors[:20], "last_run": COLLECTOR_STATUS["last_run"]}
    except Exception as exc:
        COLLECTOR_STATUS.update(error=str(exc), last_run=datetime.now(timezone.utc).isoformat())
        return {"status": "error", "resources": len(seen), "records_imported": imported, "error": str(exc)}
    finally:
        COLLECTOR_STATUS["running"] = False
        COLLECTOR_LOCK.release()


def collect_weather(latitude=None, longitude=None, roi=None):
    """Fetch and store a current Open-Meteo observation for a location."""
    try:
        from config import ROI as DEFAULT_ROI
        from data_sources import get_open_meteo_weather
        roi = roi or DEFAULT_ROI
        latitude = float(latitude if latitude is not None else (float(roi["lat_min"]) + float(roi["lat_max"])) / 2)
        longitude = float(longitude if longitude is not None else (float(roi["lon_min"]) + float(roi["lon_max"])) / 2)
        weather = get_open_meteo_weather(latitude, longitude)
        current, units = weather.get("current", {}), weather.get("units", {})
        measured_at = current.get("time") or datetime.now(timezone.utc).isoformat()
        values = {
            "temperature_2m": current.get("temperature_2m"),
            "relative_humidity_2m": current.get("relative_humidity_2m"),
            "precipitation": current.get("precipitation"),
            "wind_speed_10m": current.get("wind_speed_10m"),
        }
        records = [{
            "state": roi.get("state", ""), "district": None,
            "station": f"{roi.get('water_body', 'monitoring site')} weather",
            "measured_at": measured_at, "parameter": name, "value": value,
            "unit": units.get(name), "source": "Open-Meteo",
            "source_url": "https://api.open-meteo.com/v1/forecast",
            "metadata": {"latitude": latitude, "longitude": longitude,
                         "timezone": weather.get("timezone")},
        } for name, value in values.items() if value is not None]
        count = save_measurements(records) if records else 0
        WEATHER_STATUS.update(last_run=datetime.now(timezone.utc).isoformat(), records=count, error=None)
        return {"status": "complete", "records_imported": count, "latitude": latitude, "longitude": longitude}
    except Exception as exc:
        WEATHER_STATUS.update(last_run=datetime.now(timezone.utc).isoformat(), error=str(exc))
        return {"status": "error", "error": str(exc)}


def _daily_collector():
    while True:
        collect_nwdp_measurements()
        collect_weather()
        time.sleep(86400)


def start_daily_collector():
    global _DAILY_THREAD
    if _DAILY_THREAD is None or not _DAILY_THREAD.is_alive():
        _DAILY_THREAD = threading.Thread(target=_daily_collector, name="environment-daily-collector", daemon=True)
        _DAILY_THREAD.start()


def list_states():
    return sorted(INDIA_GEO_DATABASE)


def _districts_from_bharatmap():
    now = datetime.now(timezone.utc).timestamp()
    if DISTRICT_CACHE["expires"] > now:
        return DISTRICT_CACHE["items"]
    params = urllib.parse.urlencode({
        "where": "1=1", "outFields": "*", "returnGeometry": "false", "f": "json"
    })
    request = urllib.request.Request(
        f"{DISTRICT_API}?{params}", headers={"User-Agent": "AquaVision/1.0"}
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("error"):
        raise RuntimeError(payload["error"].get("message", "BharatMap service error"))

    districts = []
    for feature in payload.get("features", []):
        attrs = feature.get("attributes", {})
        normalized = {str(key).lower(): value for key, value in attrs.items()}
        state = next((normalized[k] for k in ("state_name", "statename", "state", "stname") if normalized.get(k)), None)
        district = next((normalized[k] for k in ("district_name", "districtname", "district", "dtname", "dist_name") if normalized.get(k)), None)
        if state and district:
            districts.append({"state": str(state).strip(), "district": str(district).strip()})
    if not districts:
        raise RuntimeError("BharatMap service returned no recognizable district records")
    districts = sorted({(x["state"], x["district"]) for x in districts})
    result = [{"state": state, "district": district} for state, district in districts]
    DISTRICT_CACHE.update(expires=now + 86400, items=result)
    return result


def districts(state=None, refresh=False):
    if refresh:
        DISTRICT_CACHE["expires"] = 0
    items = _districts_from_bharatmap()
    if state:
        items = [row for row in items if row["state"].casefold() == state.casefold()]
    return items


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("""CREATE TABLE IF NOT EXISTS measurements (
        id TEXT PRIMARY KEY,
        state TEXT NOT NULL,
        district TEXT,
        station TEXT NOT NULL,
        measured_at TEXT NOT NULL,
        parameter TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT,
        source TEXT NOT NULL,
        source_url TEXT,
        metadata TEXT NOT NULL DEFAULT '{}'
    )""")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_measurement_location_date ON measurements(state, district, measured_at)")
    return connection


def save_measurements(records):
    saved = 0
    with closing(_connect()) as db:
        with db:
            for record in records:
                state = str(record.get("state", "")).strip()
                station = str(record.get("station", "")).strip()
                parameter = str(record.get("parameter", "")).strip()
                measured_at = str(record.get("measured_at", "")).strip()
                if not (state and station and parameter and measured_at):
                    raise ValueError("Each record requires state, station, parameter, and measured_at")
                try:
                    value = float(record["value"])
                except (KeyError, TypeError, ValueError):
                    raise ValueError("Each record requires a numeric value")
                source = str(record.get("source") or "CPCB/NWDP").strip()
                identity = str(record.get("id") or "|".join((state, str(record.get("district", "")), station, measured_at, parameter, source)))
                db.execute("""INSERT OR REPLACE INTO measurements
                    (id,state,district,station,measured_at,parameter,value,unit,source,source_url,metadata)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
                        identity, state, record.get("district"), station, measured_at,
                        parameter, value, record.get("unit"), source,
                        record.get("source_url"), json.dumps(record.get("metadata", {})),
                    ))
                saved += 1
    return saved


def get_measurements(state=None, district=None, station=None, parameter=None,
                     date_from=None, date_to=None, limit=500, offset=0, source=None):
    clauses, args = [], []
    for column, value in (("state", state), ("district", district), ("station", station), ("parameter", parameter)):
        if value:
            clauses.append(f"lower({column}) = lower(?)")
            args.append(value)
    if source:
        clauses.append("lower(source) = lower(?)")
        args.append(source)
    if date_from:
        clauses.append("measured_at >= ?")
        args.append(date_from)
    if date_to:
        clauses.append("measured_at <= ?")
        args.append(date_to)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    with closing(_connect()) as db:
        total = db.execute("SELECT COUNT(*) FROM measurements" + where, args).fetchone()[0]
        rows = db.execute("SELECT * FROM measurements" + where + " ORDER BY measured_at DESC LIMIT ? OFFSET ?", [*args, limit, offset]).fetchall()
    return {"total": total, "limit": limit, "offset": offset, "source": "CPCB/NWDP and imported datasets", "items": [
        {**dict(row), "metadata": json.loads(row["metadata"])} for row in rows
    ]}
