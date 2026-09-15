"""Create a reproducible PCA + K-means customer segmentation."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "superstore_data.csv"

FEATURES = [
    "Income", "Kidhome", "Teenhome", "Recency",
    "MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
    "MntSweetProducts", "MntGoldProds", "NumDealsPurchases",
    "NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases",
    "NumWebVisitsMonth",
]
SPEND = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds"]
PURCHASES = ["NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]


def main():
    df = pd.read_csv(INPUT)
    x = df[FEATURES].copy()

    # Same numeric data-quality treatment used for the preceding PCA: missing
    # values and the clearly erroneous income above $200,000 receive the mean.
    x.loc[x["Income"] > 200_000, "Income"] = np.nan
    x = x.fillna(x.mean(numeric_only=True))

    z = StandardScaler().fit_transform(x)
    full_pca = PCA().fit(z)
    cumulative = np.cumsum(full_pca.explained_variance_ratio_)
    n_components = int(np.argmax(cumulative >= 0.80) + 1)  # 7 PCs in this data
    pcs = PCA(n_components=n_components).fit_transform(z)

    # Compare practical candidate solutions. K-means is fit in retained-PC
    # space, so correlated spend and purchase measures do not get counted twice.
    diagnostics = []
    fits = {}
    for k in range(2, 9):
        model = KMeans(n_clusters=k, n_init=100, random_state=6620)
        labels = model.fit_predict(pcs)
        fits[k] = (model, labels)
        diagnostics.append({
            "k": k,
            "inertia": model.inertia_,
            "silhouette": silhouette_score(pcs, labels),
            "calinski_harabasz": calinski_harabasz_score(pcs, labels),
            "davies_bouldin": davies_bouldin_score(pcs, labels),
        })
    diagnostics = pd.DataFrame(diagnostics)
    diagnostics.to_csv(ROOT / "segmentation_cluster_diagnostics.csv", index=False)

    # The three-cluster solution is the best usable compromise: k=2 has the
    # highest mechanical separation but collapses distinct low-value household
    # patterns, while k>=4 materially reduces separation and fragments groups.
    k = 3
    _, labels = fits[k]
    df["Cluster"] = labels + 1
    segment_names = {
        1: "Budget family browsers",
        2: "Affluent omnichannel loyalists",
        3: "Deal-oriented wine shoppers",
    }
    df["Segment"] = df["Cluster"].map(segment_names)
    df["PC1"] = pcs[:, 0]
    df["PC2"] = pcs[:, 1]
    df["PC3"] = pcs[:, 2]

    profile = df.assign(
        TotalSpend=df[SPEND].sum(axis=1),
        TotalPurchases=df[PURCHASES].sum(axis=1),
    ).groupby("Cluster").agg(
        Customers=("Id", "size"),
        Pct_Customers=("Id", lambda s: 100 * len(s) / len(df)),
        Income=("Income", "mean"),
        Kidhome=("Kidhome", "mean"),
        Teenhome=("Teenhome", "mean"),
        Recency=("Recency", "mean"),
        TotalSpend=("TotalSpend", "mean"),
        MntWines=("MntWines", "mean"),
        MntMeatProducts=("MntMeatProducts", "mean"),
        MntGoldProds=("MntGoldProds", "mean"),
        NumDealsPurchases=("NumDealsPurchases", "mean"),
        NumWebPurchases=("NumWebPurchases", "mean"),
        NumCatalogPurchases=("NumCatalogPurchases", "mean"),
        NumStorePurchases=("NumStorePurchases", "mean"),
        NumWebVisitsMonth=("NumWebVisitsMonth", "mean"),
        ResponseRate=("Response", "mean"),
        ComplaintRate=("Complain", "mean"),
        PC1=("PC1", "mean"), PC2=("PC2", "mean"), PC3=("PC3", "mean"),
    ).reset_index()
    profile["ResponseRate"] *= 100
    profile["ComplaintRate"] *= 100
    profile["Segment"] = profile["Cluster"].map(segment_names)
    profile = profile[["Cluster", "Segment"] + [c for c in profile if c not in {"Cluster", "Segment"}]]
    profile.to_csv(ROOT / "segmentation_cluster_profiles.csv", index=False)

    df[["Id", "Cluster", "Segment", "PC1", "PC2", "PC3"]].to_csv(
        ROOT / "customer_segments.csv", index=False
    )
    print(f"PCA components used: {n_components}; cumulative variance: {cumulative[n_components-1]:.4%}")
    print(diagnostics.round(4).to_string(index=False))
    print("\nCluster profiles")
    print(profile.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
