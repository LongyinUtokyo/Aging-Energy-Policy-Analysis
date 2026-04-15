# Step 10 KL Divergence

Observed distribution P_t was taken directly from Step 7 topic-share windows.
Theoretical reference distribution Q uses the default equal-weight baseline across the six taxonomy categories because no explicit numeric balanced mechanism vector was available in the project files.

## Window-level KL divergence
- 1972_1976: KL=0.488162 (Phase 3)
- 1977_1981: KL=0.389271 (Phase 3)
- 1982_1986: KL=0.293544 (Phase 3)
- 1987_1991: KL=0.237886 (Phase 3)
- 1992_1996: KL=0.326715 (Phase 3)
- 1997_2001: KL=0.252299 (Phase 4)
- 2002_2006: KL=0.188152 (Phase 4)
- 2007_2011: KL=0.141579 (Phase 4)
- 2012_2016: KL=0.122226 (Phase 4)
- 2017_2020: KL=0.104370 (Phase 4)
- 2021_2024: KL=0.146094 (Phase 4)

## Phase averages
- Phase 3: mean=0.347116, min=0.237886, max=0.488162, windows=5
- Phase 4: mean=0.159120, min=0.104370, max=0.252299, windows=6

## Rapid Expansion trend
- Phase 4 linear slope of KL over window mid-year: -0.00511572