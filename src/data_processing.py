import polars as pl
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent  # Goes up two levels from the current file.

def process_year(year: str | int, version: str = "V202601") -> None:
    """Load, clean, and normalize BACI trade data for a single year."""

    year = int(year)

    # 1) Load the country dictionary according to the version added into a LazyFrame using scan in order to prevent RAM saturation:
    countries = pl.scan_csv(BASE_DIR / "data" / f"country_codes_{version}.csv")

    # 2) Load the specific year into a LazyFrame using scan in order to prevent RAM saturation:
    df = pl.scan_csv(BASE_DIR / "data" / "raw" / f"BACI_HS92_Y{year}_{version}.csv")

    # 3.1) Join the country code of the exporters in df with the countries df to get the country ISO3 code: 
    df = df.join(countries, left_on='i', right_on='country_code').rename({'country_iso3': 'Exporter'})

    # 3.2) Join the country code of the importers in df with the countries df to get the country ISO3 code: 
    df = df.join(countries, left_on='j', right_on='country_code').rename({'country_iso3': 'Importer'})

    # 3.3) Select the necessary columns and rename them: 
    df = df.select([
            pl.col("t").alias("Year"),
            pl.col("Exporter"),
            pl.col("Importer"),
            pl.col("k").alias("Product_Code"),
            pl.col("v").alias("Value_Thousands_USD")
        ])
    
    # 4) Data type adjustment: 
    df = df.with_columns([pl.col('Product_Code').cast(pl.UInt32), 
                        pl.col('Value_Thousands_USD').cast(pl.Float64), 
                        pl.col('Year').cast(pl.UInt16), 
                        pl.col('Exporter').cast(pl.Categorical), 
                        pl.col('Importer').cast(pl.Categorical)])
    
    # 5) Save in Parquet format (a more efficient version for CSV-type files): 
    df.collect().write_parquet(BASE_DIR / "data" / "processed" / f"trade_{year}.parquet")


def process_all_years(init_year: str | int, end_year: str | int, version: str = "V202601") -> None:
    """Load, clean, and normalize BACI trade data for a all introduced years."""

    init_year = int(init_year)
    end_year = int(end_year)

    # 1) Make sure the init_year is less than the end_year:
    if init_year > end_year:
        raise ValueError("init_year must be less than or equal to end_year.")
    
    # 2) Main loop: 
    # StringCache ensures that categories are the same in all files: 
    with pl.StringCache():
        for year in range(init_year, end_year + 1): 
            process_year(year, version=version)

if __name__ == "__main__":

    START_YEAR = 1995
    END_YEAR = 2024
    
    print(f"Starting data processing from {START_YEAR} to {END_YEAR}.")
    
    process_all_years(START_YEAR, END_YEAR)
    
    print("Process completed successfully.")