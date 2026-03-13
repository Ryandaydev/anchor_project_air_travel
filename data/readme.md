# Anchor Project Datasets

This repository contains datasets related to air travel and transportation analytics for the Anchor Project.

## Datasets Overview

The datasets in this directory provide comprehensive data for analyzing air travel patterns, carrier performance, and market trends.

## Available Datasets

### 1. Airline Market Carrier On-Time Data

**Description:** This dataset contains on-time performance data for airline carriers, including arrival and departure times, delays, and cancellation information.

**Source:** Bureau of Transportation Statistics (BTS)

**Key Features:**
- Flight schedules and actual performance
- Delay reasons and durations
- Carrier and airport information
- Monthly and yearly aggregations

**Files:**
- `carrier_on_time_data.csv` - Raw performance data
- `carrier_on_time_summary.csv` - Aggregated statistics

**Usage:**
```python
import pandas as pd
df = pd.read_csv('data/carrier_on_time_data.csv')
```

#### Source and license

Downloaded from this website:
https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK&QO_fu146_anzr=b0-gvzr

US Government data is by default in the public domain:
https://resources.data.gov/open-licenses/

Definition of terms:
https://www.bts.gov/learn-about-bts-and-our-work/acronyms-and-terms-guide

### 2. [Dataset Name Placeholder]

**Description:** [Brief description of the dataset]

**Source:** [Data source]

**Key Features:**
- [Feature 1]
- [Feature 2]

**Files:**
- [file1.csv]
- [file2.csv]

### 3. [Dataset Name Placeholder]

**Description:** [Brief description of the dataset]

**Source:** [Data source]

**Key Features:**
- [Feature 1]
- [Feature 2]

**Files:**
- [file1.csv]
- [file2.csv]



## License

[Specify license information]

## Contributing

[Guidelines for contributing to the dataset collection]