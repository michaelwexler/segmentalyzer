Segmentalyzer compares two segments and shows you **what** differences actually matter. It takes aggregated attribute data and applies multiple statistical lenses to separate signal from noise.

This version compares only 2 segments: a "segment of interest" vs. "all else".


# Getting Started

```bash
uv run streamlit run app.py
```
Open browser to localhost:8501.  

Upload a CSV or paste a public Google Sheets URL to begin.


# Input Format

**Format A — pre-aggregated percentages:**
```
attribute, pct_segment, pct_rest
age_18_24, 0.32, 0.18
```

**Format B — raw counts:**
```
attribute, count_segment, total_segment, count_rest, total_rest
age_18_24, 320, 1000, 180, 1000
```

Values can be on a 0–1 or 0–100 scale; the app auto-detects.


# Techniques

We include the following metrics:
* Lift Score (Uniqueness) = % Interest / % in rest; shown as 2.0x
    * note that Lift can go from 0 to infinity, biased towards rareness
    * assumes linearity of percentages (false); equal variance across attributes (false); symmetric interpretation (false)
* Difference (Impact) = % in Interest - % in rest; shown as +42%
    * note that Difference is bounded from -100% to +100%
* Standardized Lift = StdDiff=(𝑝1−𝑝2)/sqroot(𝑝(1−𝑝)), where 𝑝=(𝑝1+𝑝2)/2
    * adjusts for baseline prevalence and makes effects comparable across segments
    * (Akin to a Cohen’s h–style effect size for proportions.)
* Contribution to Overall Difference = Contribution_𝑖=(𝑝_𝑐𝑙𝑖𝑐𝑘,𝑖 − 𝑝_𝑛𝑜𝑛,𝑖) x 𝑤_𝑖, where 𝑤_𝑖 is category prevalence (or business weight).
    * A driver analysis, focusing on composition contribution
* Log Odds Ratio = log((𝑝1/(1−𝑝1))/(𝑝2/(1−𝑝2)))
    * symmetric for increases/decreases; handles baseline differences properly
    * 0.4 and above is strong positive association

The difference score can be used to filter to "big enough to care about" and then can be ranked by Lift.

Population Share aka Pop Share, in the pct only version, is just an average.  

# Visualizations

**Lift vs. Difference** — Y: Lift, X: Difference. Shows attributes that are both impactful and distinctive.

**Standardized Lift vs. Population Share** — X: Standardized Lift, Y: Population Share, Bubble size: Population share. Adjusts for base rate so rare and common traits are directly comparable.

**Log Odds Ratio vs. Population Share** — X: Log Odds Ratio, Y: Population Share, Bubble size: |Log Odds|. Symmetric metric that handles baseline differences properly.


# Future Work
* Support atomic person level data (which probably uses actual discriminant/classifier approaches)
* Support comparing more than 2 segments

# Dependencies:
* streamlit
* pandas
* plotly
* numpy
* requests

# Prior Art
Marketing agencies commonly use an "index" approach, which is a simple ratio approach, akin to a "lift" calculation.  They take an aggregate of all users, or of the larger group (say, non-clickers) and show the % higher for an attribute in clickers over the bulk, expressed as 108%, etc.  This can then be sorted to see the biggest difference.  However, this ignores the base rate, or how many people evidence this trait in either group.  1 person in non-clickers is over 6 ft tall; 10 people in clickers are over 6 ft tall.  This becomes a 1000% index, but if your sample is of a million people, that small incidence is just noise.

Other tools, such as the Adobe Segment Analyzer, use a "Relative risk differencing algorithm" which sounds sophisticated but is really just the difference in pcts.  So, for an attribute, what % of Group of Interest has this attribute, same for Rest, subtract.  This tells you how "unique" a trait is to a specific group. If 0, both groups have same amount.  1 or -1 says it's in more in one group (or the other).  The bounded differencing avoids the small difference that lift calculations highlight.


Profiles might include:
* Age 18-24; 25-34; 35-44; 45-54; 55-64; 65+
* Gender: M or F
* Device Platform: Mobile or Desktop
* Mobile OS: Android or iOS
* Top Cities
* Top Countries
