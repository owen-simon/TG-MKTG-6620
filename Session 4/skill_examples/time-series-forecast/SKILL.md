---
name: time-series-forecast
description: Compare time-series forecasts at fixed origins and horizons, including seasonal baselines, fitted methods, and supplied or locally run foundation-model forecasts.
---

State the series key, target units, frequency, forecast origins, horizon, history
window, and information available at each origin. Check duplicate keys and
missing dates. An absent row is not automatically zero demand. Learn any fill
rule from history and disclose it; do not fill unknown evaluation outcomes.

Build the baseline from information available at the origin. For seasonal naive,
repeat the last complete training week throughout the horizon. Never read later
actuals to refresh a fixed-origin forecast. Fit other methods on history only.
Use a known future calendar only under an explicit availability assumption.

Select on earlier validation windows and preserve a later evaluation window.
Compare common rows with MAE and a defined denominator, such as WAPE. Report
counts and undefined cases. MASE uses training seasonal-difference errors; its
value of one need not tie the baseline on this test window.

For foundation forecasts, record model revision, context, output meaning, and
whether predictions were supplied or generated. Check quantile ordering and
coverage with denominators. Do not sum daily quantiles into a total-demand
quantile. Preserve dependent observations when resampling model differences.

Return forecasts keyed by origin, date, and series; comparison tables; checks;
and limits. Do not install, download, or call services without task authorization.
Respect coursework rules on student-written judgments.
