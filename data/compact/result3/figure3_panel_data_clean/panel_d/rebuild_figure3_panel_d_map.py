from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
SOURCE_CSV = ROOT / "third_part_ageing_energy_policy_focus_20260408" / "tables" / "topic_share_by_country.csv"


def build_panel_d_tables():
    raw = pd.read_csv(SOURCE_CSV)
    macro_cats = {"Welfare and care", "Health and vulnerability"}
    mechanism_cats = {
        "Housing and thermal comfort",
        "Household behaviour and adoption",
        "Affordability and income constraints",
        "Energy transition and efficiency",
    }
    map_df = (
        raw.groupby("Country")
        .apply(
            lambda g: pd.Series(
                {
                    "macro_share": g.loc[g["category"].isin(macro_cats), "TopicShare"].sum(),
                    "mechanism_share": g.loc[g["category"].isin(mechanism_cats), "TopicShare"].sum(),
                    "governance_share": g.loc[g["category"].eq("Governance and planning"), "TopicShare"].sum(),
                }
            )
        )
        .reset_index()
    )
    map_df["blind_spot_index"] = map_df["macro_share"] - map_df["mechanism_share"]
    return raw, map_df


if __name__ == "__main__":
    raw, map_df = build_panel_d_tables()
    print(raw.head())
    print(map_df.head())
