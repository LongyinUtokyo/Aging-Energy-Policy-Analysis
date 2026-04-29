# Panel D

This folder contains the underlying data and code for the Figure 3 blind-spot map.

Files:
- `figure3_panel_d_data.xlsx`: workbook with the map data tables.
- `panel_d_raw_topic_share_by_country.csv`: source country-category table used for the map.
- `panel_d_blind_spot_country_map.csv`: processed country-level blind-spot index table.
- `panel_d_donut_overlay_data.csv`: category composition for the donut-overlay countries.
- `rebuild_figure3_panel_d_map.py`: reproducible code stub showing how the panel-d data are constructed.

Blind-spot definition:
- `macro_share = welfare and care + health and vulnerability`
- `mechanism_share = housing and thermal comfort + household behaviour and adoption + affordability and income constraints + energy transition and efficiency`
- `blind_spot_index = macro_share - mechanism_share`

Governance and planning is preserved in the raw source file and summarized separately as `governance_share`, but it is not part of the blind-spot index itself.