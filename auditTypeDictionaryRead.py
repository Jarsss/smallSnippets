import pandas as pd

# ---- minimal config ----
CONFIG = {
    "groups": ["SBGroup", "ClaimsOps", "ClientServices"],  # precedence order
    "audit_type_points": {
        "Post-Pay":         {"SBGroup": 1},
        "Variance Review":  {"SBGroup": 1, "ClaimsOps": 1},   # shared → tie broken by precedence
        "Claims Accuracy":  {"ClaimsOps": 1},
        "Claim Reopen":     {"ClaimsOps": 1},
        "Client SLA":       {"ClientServices": 1},
        "Quality Review":   {"ClientServices": 1},
        # add your real audit types here
    }
}

def build_primary_group_map(config=CONFIG):
    """Precompute audit_type -> winner (highest points; ties by precedence)."""
    primary = {}
    precedence = config["groups"]
    for atype, ptmap in config["audit_type_points"].items():
        if not ptmap:
            continue
        max_pts = max(ptmap.values())
        tied = [g for g, v in ptmap.items() if v == max_pts]
        # tie-break by precedence order
        winner = next(g for g in precedence if g in tied)
        primary[atype.strip().lower()] = winner
    return primary

PRIMARY_MAP = build_primary_group_map(CONFIG)

def assign_groups_df(df, audit_type_col="audit_type"):
    """Vectorized assignment: adds a 'group' column to the DataFrame."""
    # normalize audit_type to lookup key
    norm = df[audit_type_col].fillna("").astype(str).str.strip().str.lower()
    df = df.copy()
    df["group"] = norm.map(PRIMARY_MAP).fillna("Unknown")
    return df

# ---- Example usage ----
# df = pd.read_excel("input.xlsx")  # columns include 'audit_type'
# out = assign_groups_df(df, audit_type_col="audit_type")
# out.to_excel("output_with_groups.xlsx", index=False)
