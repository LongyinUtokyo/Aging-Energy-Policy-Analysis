# Step 8 Policy Attention Elasticity

Model form: ln(TopicShare_k,t) = alpha_k + epsilon_k ln(OADR_t) + eta_t.
Data basis: Step 7 topic-share windows merged with window-mean OADR.
Controls: no additional controls used.
Fixed effects: not used in the final estimates because the available structure is window-level and the usable OADR overlap begins only in 1990.
Coverage note: windows without observed OADR values were dropped from estimation rather than imputed.

## Ranked elasticity estimates
- housing and thermal comfort: epsilon=3.1657, SE=0.6961, p=5.417e-06, 95% CI [1.8014, 4.5300]
- energy transition and efficiency: epsilon=1.7505, SE=0.4245, p=3.723e-05, 95% CI [0.9186, 2.5824]
- health and vulnerability: epsilon=0.8830, SE=0.4687, p=0.05954, 95% CI [-0.0355, 1.8016]
- household behaviour and adoption: epsilon=-0.1800, SE=0.3450, p=0.6017, 95% CI [-0.8562, 0.4961]
- affordability and income constraints: epsilon=-0.9976, SE=0.2192, p=5.351e-06, 95% CI [-1.4272, -0.5679]
- welfare and care: epsilon=-1.4102, SE=0.3642, p=0.0001079, 95% CI [-2.1240, -0.6964]

## Mechanism-focused comparison
- housing and thermal comfort: epsilon=3.1657, ranked 1 of 6.
- energy transition and efficiency: epsilon=1.7505, ranked 2 of 6.
- household behaviour and adoption: epsilon=-0.1800, ranked 4 of 6.
- affordability and income constraints: epsilon=-0.9976, ranked 5 of 6.