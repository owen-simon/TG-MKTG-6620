#!/usr/bin/env python3
"""Student analysis support for V&D 1, revised September 9, 2026.

Reads a LOCAL course CSV only. No downloads, API calls, or paid services.
Run compare first; record a choice; then run evaluate with that choice.
The fixed models are fitted on the same training rows in either command.
No fitting, selection, or calibration uses final-test outcomes.
"""

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ["tenure", "MonthlyCharges", "TotalCharges"]
CATEGORICAL = ["Contract", "InternetService", "PaperlessBilling", "PaymentMethod"]
METHODS = ["contract", "logistic", "trees"]
CONTACT_SHARE = 0.20
SAVE_RATES = [0.10, 0.15, 0.20]
NET_VALUE = 66.0
CONTACT_COST = 6.20
SEED = 0
BOOTSTRAPS = 1000


def load_data(path):
    """Check the assigned extract, then apply one documented cleaning rule."""
    if not path.is_file():
        raise ValueError("Use the local churn.csv supplied with the assignment.")
    df = pd.read_csv(path)
    required = ["customerID", "Churn"] + NUMERIC + CATEGORICAL
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    if df.shape != (7043, 21) or df["Churn"].value_counts().to_dict() != {"No": 5174, "Yes": 1869}:
        raise ValueError("This is not the assigned 7,043-row, 21-column extract.")
    if df["customerID"].isna().any() or not df["customerID"].is_unique:
        raise ValueError("Customer IDs must be present and unique.")
    total = pd.to_numeric(df["TotalCharges"], errors="coerce")
    blank = df["TotalCharges"].astype(str).str.strip().eq("")
    if blank.sum() != 11 or not total.isna().equals(blank) or not df.loc[blank, "tenure"].eq(0).all():
        raise ValueError("Expected 11 blank TotalCharges values, all at zero tenure.")
    df["TotalCharges"] = total.fillna(0.0)
    if df[NUMERIC + CATEGORICAL].isna().any().any():
        raise ValueError("Unexpected missing value in an analysis input.")
    if not np.isfinite(df[NUMERIC].to_numpy(dtype=float)).all():
        raise ValueError("Numeric inputs must be finite.")
    return df


def split_rows(y):
    """60% training, 20% validation, 20% final test; fixed row positions."""
    train, remainder = train_test_split(
        np.arange(len(y)), test_size=0.40, stratify=y, random_state=SEED)
    validation, test = train_test_split(
        remainder, test_size=0.50, stratify=y[remainder], random_state=SEED)
    assert not (set(train) & set(validation) or set(train) & set(test) or set(validation) & set(test))
    assert len(train) + len(validation) + len(test) == len(y)
    return train, validation, test


def fit_methods(df, y, train):
    """Use training rows only, including the contract rule's group rates."""
    rates = pd.Series(y[train]).groupby(df.iloc[train]["Contract"].reset_index(drop=True)).mean()
    fitted = {"contract": (rates, float(y[train].mean()))}
    estimators = {
        "logistic": LogisticRegression(C=1.0, max_iter=3000, solver="lbfgs", random_state=SEED),
        "trees": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=2, random_state=SEED),
    }
    for name, estimator in estimators.items():
        preprocessing = ColumnTransformer([
            ("numeric", StandardScaler(), NUMERIC),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ])
        pipe = Pipeline([("inputs", preprocessing), ("model", estimator)])
        pipe.fit(df.iloc[train][NUMERIC + CATEGORICAL], y[train])
        fitted[name] = pipe
    return fitted


def predict_methods(fitted, df, rows):
    rates, fallback = fitted["contract"]
    predictions = {"contract": df.iloc[rows]["Contract"].map(rates).fillna(fallback).to_numpy()}
    for name in ["logistic", "trees"]:
        predictions[name] = fitted[name].predict_proba(df.iloc[rows][NUMERIC + CATEGORICAL])[:, 1]
    for p in predictions.values():
        assert np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all()
    return predictions


def top_rows(p, tie_order):
    """At most 20%: round down; ties use a saved random order, never outcomes."""
    n = max(1, int(np.floor(CONTACT_SHARE * len(p))))
    return np.lexsort((tie_order, -np.asarray(p)))[:n]


def metric_table(y, predictions, tie_order):
    rows = []
    for name, p in predictions.items():
        selected = top_rows(p, tie_order)
        rows.append(dict(
            method=name, n=len(y), auc=float(roc_auc_score(y, p)),
            contact_n=len(selected), top20_churn_rate=float(y[selected].mean()),
            top20_mean_prediction=float(p[selected].mean()),
            mean_prediction=float(p.mean()), observed_churn_rate=float(y.mean())))
    return pd.DataFrame(rows)


def paired_intervals(y, predictions, repetitions=BOOTSTRAPS):
    """Percentile AUC intervals; the same sampled rows score every method.

    Fitted predictions stay fixed. This measures evaluation-sample uncertainty,
    not uncertainty from refitting, model selection, future drift, or treatment.
    """
    rng = np.random.RandomState(SEED)
    draws = []
    for _ in range(repetitions):
        sample = rng.randint(0, len(y), size=len(y))
        if len(np.unique(y[sample])) < 2:
            continue
        draws.append([roc_auc_score(y[sample], predictions[name][sample]) for name in METHODS])
    if len(draws) < 0.95 * repetitions:
        raise ValueError("Too many bootstrap samples contain only one outcome class.")
    draws = np.asarray(draws)
    rows = []
    for j, name in enumerate(METHODS):
        lo, hi = np.quantile(draws[:, j], [0.025, 0.975])
        rows.append(dict(comparison=name, estimate=roc_auc_score(y, predictions[name]), low=lo, high=hi))
    for a, b in [("logistic", "contract"), ("trees", "contract"), ("trees", "logistic")]:
        delta = draws[:, METHODS.index(a)] - draws[:, METHODS.index(b)]
        lo, hi = np.quantile(delta, [0.025, 0.975])
        rows.append(dict(comparison=a + " minus " + b,
                         estimate=roc_auc_score(y, predictions[a]) - roc_auc_score(y, predictions[b]),
                         low=lo, high=hi))
    return pd.DataFrame(rows), len(draws)


def probability_groups(y, p):
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    # The last group must include a prediction of exactly one.
    codes = np.minimum(np.searchsorted(bins, p, side="right") - 1, 4)
    rows = []
    for i in range(5):
        members = codes == i
        n = int(members.sum())
        rows.append(dict(group=f"{bins[i]:.1f} to {bins[i+1]:.1f}" + (" inclusive" if i == 4 else " exclusive"),
                         n=n, mean_prediction=float(p[members].mean()) if n else np.nan,
                         observed_churn_rate=float(y[members].mean()) if n else np.nan))
    return pd.DataFrame(rows)


def scenario_table(metrics):
    """Scenario dollars use each fixed list's observed historical churn rate.

    These are not measured savings and contain no estimated treatment effect.
    """
    rows = []
    for row in metrics.itertuples(index=False):
        r = row.top20_churn_rate
        for save_rate in SAVE_RATES:
            rows.append(dict(method=row.method, historical_list_churn_rate=r,
                             assumed_save_rate=save_rate,
                             net_per_1000_contacts=1000 * (r * save_rate * NET_VALUE - CONTACT_COST),
                             break_even_save_rate=CONTACT_COST / (r * NET_VALUE) if r else np.nan))
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["compare", "evaluate"])
    parser.add_argument("--csv", type=Path, default=Path("churn.csv"))
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--choice", choices=METHODS)
    args = parser.parse_args()
    if args.stage == "evaluate" and not args.choice:
        parser.error("Record your validation choice first, then supply --choice.")
    df = load_data(args.csv)
    y = df["Churn"].eq("Yes").to_numpy(dtype=int)
    train, validation, test = split_rows(y)
    # Fixed random tie priority for every source row; no outcome enters it.
    tie_order = np.random.RandomState(SEED).permutation(len(df))
    fitted = fit_methods(df, y, train)
    predictions = predict_methods(fitted, df, validation)
    validation_table = metric_table(y[validation], predictions, tie_order[validation])
    args.out.mkdir(parents=True, exist_ok=True)
    validation_table.to_csv(args.out / "validation.csv", index=False)
    assignment = np.empty(len(y), dtype=object)
    for name, rows in [("train", train), ("validation", validation), ("test", test)]:
        assignment[rows] = name
    pd.DataFrame({"source_row": np.arange(len(y)), "partition": assignment}).to_csv(
        args.out / "split_rows.csv", index=False)
    metadata = dict(
        stage=args.stage, source_file=args.csv.name,
        source_sha256=hashlib.sha256(args.csv.read_bytes()).hexdigest(),
        python=platform.python_version(), pandas=pd.__version__, numpy=np.__version__, sklearn=sklearn.__version__,
        split_seed=SEED, features=NUMERIC+CATEGORICAL,
        sizes=dict(train=len(train), validation=len(validation), test=len(test)),
        cleaning="11 blank TotalCharges at tenure 0 filled with 0; no rows removed",
        contact_share=CONTACT_SHARE, tie_break="fixed random priority per source row, seed 0",
    )
    # Stable sort preserves the simpler-method order on an exact AUC tie.
    suggested = validation_table.sort_values("auc", ascending=False, kind="stable").iloc[0]["method"]
    print("VALIDATION RESULTS\n" + validation_table.to_string(index=False))
    print("Highest validation AUC:", suggested)
    if args.stage == "compare":
        print("Record a choice and reason in analysis.md before running evaluate.")
    else:
        metadata.update(choice=args.choice, bootstrap_requested=BOOTSTRAPS)
        predictions = predict_methods(fitted, df, test)
        metrics = metric_table(y[test], predictions, tie_order[test])
        intervals, valid = paired_intervals(y[test], predictions)
        metadata["bootstrap_valid"] = valid
        metrics.to_csv(args.out / "test_metrics.csv", index=False)
        intervals.to_csv(args.out / "intervals.csv", index=False)
        probability_groups(y[test], predictions[args.choice]).to_csv(args.out / "probability_groups.csv", index=False)
        scenario_table(metrics).to_csv(args.out / "scenarios.csv", index=False)
        selected = top_rows(predictions[args.choice], tie_order[test])
        export = pd.DataFrame({"source_row": test, "churn": y[test], **predictions})
        export["selected_for_chosen_method"] = np.isin(np.arange(len(test)), selected)
        export.to_csv(args.out / "test_predictions.csv", index=False)
        print("FINAL TEST RESULTS\n" + metrics.to_string(index=False))
        print("\nAUC INTERVALS\n" + intervals.to_string(index=False))
        print("\nSCENARIOS: hypothetical dollars, not measured savings\n" + scenario_table(metrics).to_string(index=False))
    with (args.out / (args.stage + "_run.json")).open("w") as f:
        json.dump(metadata, f, indent=2, allow_nan=False)


if __name__ == "__main__":
    main()
