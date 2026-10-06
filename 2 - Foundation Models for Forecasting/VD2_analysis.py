#!/usr/bin/env python3
"""Supported Case 2 calculations. Local CSV inputs only; no AI/model API calls.

python VD2_analysis.py compare --csv data/train.csv --out outputs
python VD2_analysis.py evaluate --csv data/train.csv --out outputs --choice weekday_mean
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

STORES = list(range(1, 16)) + [85, 122, 209, 259, 262]
SUNDAY_STORES = [85, 122, 209, 259, 262]
ORIGINS = ["2015-03-28", "2015-05-09", "2015-06-20"]
HORIZON = 42
CONTEXT = 84
METHODS = ["seasonal_naive", "weekday_mean", "timesfm"]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_inputs(csv, forecasts, source):
    stamp = json.loads(source.read_text())
    if sha256(csv) != stamp["data_sha256"]:
        raise ValueError("Data fingerprint differs from the course extract. Check the downloaded file.")
    if sha256(forecasts) != stamp["prediction_sha256"]:
        raise ValueError("Forecast file differs from the supplied snapshot. Restore the course file.")
    df = pd.read_csv(csv, dtype={"StateHoliday": str}, parse_dates=["Date"], low_memory=False)
    if df.duplicated(["Store", "Date"]).any():
        raise ValueError("Duplicate store/date rows.")
    if df.Sales.isna().any() or (df.Sales < 0).any() or not df.Open.isin([0, 1]).all():
        raise ValueError("Invalid sales or Open values.")
    fc = pd.read_csv(forecasts, parse_dates=["date"])
    if fc.duplicated(["origin", "Store", "date"]).any():
        raise ValueError("Duplicate forecast keys.")
    expected_columns = ["prediction", "q10", "q80", "q90"]
    if not np.isfinite(fc[expected_columns]).all().all() or (fc[expected_columns] < 0).any().any():
        raise ValueError("Forecast values must be finite and nonnegative.")
    if not ((fc.q10 <= fc.q80) & (fc.q80 <= fc.q90)).all():
        raise ValueError("Crossed forecast quantiles.")
    return df, fc, stamp


def build_origin(df, fc, origin_text):
    origin = pd.Timestamp(origin_text)
    dates = pd.date_range(origin, periods=HORIZON)
    history_dates = pd.date_range(origin - pd.Timedelta(days=CONTEXT), periods=CONTEXT)
    rows = []
    for store in STORES:
        data = df.loc[df.Store == store].set_index("Date").sort_index()
        history, test = data.reindex(history_dates), data.reindex(dates)
        if history.Sales.isna().any() or test.Sales.isna().any() or test.Open.isna().any():
            raise ValueError("A required date is missing; do not silently fill it with zero.")
        last56 = history.Sales.iloc[-56:]
        weekday_means = last56.groupby(last56.index.dayofweek).mean()
        tf = fc.loc[(fc.Store == store) & (fc.origin == origin_text)].set_index("date").reindex(dates)
        if tf.prediction.isna().any():
            raise ValueError("Forecast snapshot does not cover the requested dates and stores.")
        candidates = [np.resize(history.Sales.to_numpy()[-7:], HORIZON),
                      np.array([weekday_means[d.dayofweek] for d in dates]), tf.prediction.to_numpy()]
        for method, prediction in zip(METHODS, candidates):
            for k, date in enumerate(dates):
                opened = int(test.Open.iloc[k])
                row = dict(origin=origin_text, Store=store, date=str(date.date()),
                           group="Sunday-trading" if store in SUNDAY_STORES else "Other 15",
                           Open=opened, actual=float(test.Sales.iloc[k]), method=method,
                           raw_prediction=float(prediction[k]), prediction=float(prediction[k]) * opened)
                if method == "timesfm":
                    row.update(q10=float(tf.q10.iloc[k]) * opened,
                               q80=float(tf.q80.iloc[k]) * opened,
                               q90=float(tf.q90.iloc[k]) * opened)
                rows.append(row)
    return pd.DataFrame(rows)


def score(g, prediction="prediction"):
    errors = (g.actual - g[prediction]).abs()
    denominator = float(g.actual.abs().sum())
    return dict(rows=len(g), stores=int(g.Store.nunique()), mae=float(errors.mean()),
                wape=float(errors.sum() / denominator) if denominator else None,
                absolute_error_sum=float(errors.sum()), actual_sum=denominator)


def score_table(pred, by):
    return pd.DataFrame([dict(zip(by, key if isinstance(key, tuple) else (key,)), **score(g))
                         for key, g in pred.groupby(by, sort=False)])


def paired_bootstrap(pred, reps=1000):
    errors = pred.assign(ae=(pred.actual - pred.prediction).abs()).groupby(["Store", "method"]).ae.sum().unstack()[METHODS]
    counts = pred[pred.method == METHODS[0]].groupby("Store").size().reindex(errors.index)
    rng = np.random.default_rng(0)
    picks = rng.integers(0, len(errors), size=(reps, len(errors)))
    boot = errors.to_numpy()[picks].sum(axis=1) / counts.to_numpy()[picks].sum(axis=1)[:, None]
    means = errors.sum() / counts.sum()
    rows = []
    for base in ["seasonal_naive", "weekday_mean"]:
        b = METHODS.index(base)
        for j, method in enumerate(METHODS):
            if method == base:
                continue
            delta = boot[:, j] - boot[:, b]
            rows.append(dict(method=method, baseline=base, delta_mae=float(means[method] - means[base]),
                             low=float(np.quantile(delta, .025)), high=float(np.quantile(delta, .975)),
                             resampling_unit="store", stores=len(errors), resamples=reps))
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["compare", "evaluate"])
    parser.add_argument("--csv", type=Path, default=Path("data/train.csv"))
    parser.add_argument("--forecasts", type=Path, default=Path(__file__).with_name("VD2_foundation_forecasts.csv"))
    parser.add_argument("--source", type=Path, default=Path(__file__).with_name("VD2_forecast_source.json"))
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--choice", choices=METHODS)
    args = parser.parse_args()
    if args.stage == "evaluate" and not args.choice:
        parser.error("evaluate requires --choice after you record your validation decision")
    df, fc, stamp = load_inputs(args.csv, args.forecasts, args.source)
    args.out.mkdir(parents=True, exist_ok=True)
    record = dict(data_sha256=stamp["data_sha256"], forecast_sha256=stamp["prediction_sha256"],
                  code_sha256=sha256(__file__), methods=METHODS, stores=STORES, origins=ORIGINS,
                  horizon=HORIZON, context_days=CONTEXT,
                  calendar_assumption="Recorded Open is treated as the planned schedule known at each origin.",
                  python=platform.python_version(), pandas=pd.__version__, numpy=np.__version__)
    if args.stage == "compare":
        pred = pd.concat([build_origin(df, fc, o) for o in ORIGINS[:2]], ignore_index=True)
        pred.to_csv(args.out / "validation_predictions.csv", index=False)
        table = score_table(pred, ["method"])
        table.to_csv(args.out / "validation.csv", index=False)
        score_table(pred, ["origin", "method"]).to_csv(args.out / "validation_by_origin.csv", index=False)
        (args.out / "compare_record.json").write_text(json.dumps(record, indent=2) + "\n")
        print(table.to_string(index=False))
        print("Record your choice and reason before using evaluate. Lower MAE is better.")
    else:
        comparison_path = args.out / "compare_record.json"
        if not comparison_path.exists():
            raise ValueError("Run compare first, then record your choice.")
        comparison = json.loads(comparison_path.read_text())
        for key in ["data_sha256", "forecast_sha256", "code_sha256"]:
            if comparison[key] != record[key]:
                raise ValueError("Inputs/code changed since compare. Reconcile and repeat compare first.")
        pred = build_origin(df, fc, ORIGINS[-1])
        pred.to_csv(args.out / "final_predictions.csv", index=False)
        table = score_table(pred, ["method"])
        table.to_csv(args.out / "final_scores.csv", index=False)
        score_table(pred, ["group", "method"]).to_csv(args.out / "final_groups.csv", index=False)
        paired_bootstrap(pred).to_csv(args.out / "paired_mae.csv", index=False)
        calendar = []
        for method, g in pred.groupby("method", sort=False):
            for label, column in [("raw", "raw_prediction"), ("known_schedule", "prediction")]:
                calendar.append(dict(method=method, calendar=label, **score(g, column)))
        pd.DataFrame(calendar).to_csv(args.out / "calendar_check.csv", index=False)
        coverage = []
        tf = pred[pred.method == "timesfm"]
        for universe, g in [("all days", tf), ("open days", tf[tf.Open == 1]), ("closed days", tf[tf.Open == 0])]:
            coverage.append(dict(universe=universe, rows=len(g),
                                 covered=int(((g.actual >= g.q10) & (g.actual <= g.q90)).sum()),
                                 coverage80=float(((g.actual >= g.q10) & (g.actual <= g.q90)).mean()),
                                 mean_width=float((g.q90 - g.q10).mean())))
        pd.DataFrame(coverage).to_csv(args.out / "interval_coverage.csv", index=False)
        record["choice"] = args.choice
        (args.out / "evaluate_record.json").write_text(json.dumps(record, indent=2) + "\n")
        print(table.to_string(index=False))
        print("Recorded choice:", args.choice, "Keep it visible if the final ordering changes.")


if __name__ == "__main__":
    main()
