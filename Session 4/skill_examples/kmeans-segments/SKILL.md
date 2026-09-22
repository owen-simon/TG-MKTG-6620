---
name: kmeans-segments
description: Build and assess customer segments with k-means, including feature and scaling choices, optional PCA, cluster profiles, and stability checks.
---

Read the segmentation decision and available fields. State the customer unit,
selected features, missing-value and outlier policies, transformations, scaling,
candidate k values, seed, and n_init. Keep identifiers and outcome labels out of
the distance calculation. Preserve requested settings and a bounded run budget.

Explain which differences drive distance. If using PCA, fit it after the chosen
preprocessing and report retained variance and loadings. PCA components summarize
variation; they are not automatically customer motivations.

Fit the requested candidates. Report silhouette with cluster sizes and profiles
in original units. Compare membership across a few stated seeds or resamples
using an agreement measure unaffected by cluster-number permutations. Do not
compare numeric cluster labels directly. Use a null comparison when the question
requires evidence beyond geometric separation; match its preprocessing and
search procedure to the observed analysis.

Explain whether segments identify an actionable distinction or mostly separate
high from low values on one variable. High silhouette and stable membership do
not prove natural customer types or different responses to marketing.

Return the settings table, membership file keyed by customer ID, profiles,
diagnostics, and limitations. Do not turn a proposed segment treatment into a
measured causal effect. Respect the assignment's rules on student-authored work.
