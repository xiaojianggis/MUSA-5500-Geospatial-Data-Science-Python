Census tract-level dataset — ACS 2020–2024

acs2024_tracts.geojson: one polygon feature per unique 11-digit tract GEOID, EPSG:4326.
acs2024_tracts.csv: same tract attributes, one row per GEOID, without geometry.
counties/: tract-only subsets for prepared counties. No county polygon features or county totals.
Coverage: only the counties prepared locally; this is not a nationwide tract dataset.

Variables: population (B01003), income (B19013, 2024 dollars), poverty (B17001,
percent below poverty among people with poverty status determined), home_value
(B25077, median owner-occupied value in 2024 dollars). Direct-estimate _moe fields
are 90% margins of error. Poverty rate MOE is not calculated; its numerator,
denominator, and their MOEs are included. Missing estimates are null/blank, not zero.
_topcoded=true means income $250,000+ or home value $2,000,000+.
county_name and county_geoid identify the parent county. Each row is a census
tract observation. No county-level aggregates are included.
Open CSV GEOID and FIPS columns as text to preserve leading zeros.

Tracts are selected by their parent county FIPS, never by town overlap. Population
is a count, not density. Medians cannot be summed. Geometries are slightly simplified.
Sources: U.S. Census ACS via https://api.censusreporter.org/ and matching Census
TIGERweb ACS 2024 boundaries. Source URLs also appear in the GeoJSON metadata.
