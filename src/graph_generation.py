import networkx as nx
import polars as pl
from pathlib import Path

def generate_product_graph(year: int, product_code: int, output_filename: str) -> None:
    """
    Generates a directed, weighted trade graph for a specific year and product code.
    """

    # Define the base directory dynamically (assumes this script is in src/):
    BASE_DIR = Path(__file__).resolve().parent.parent

    # 1) Load the dataset from the specific year in Parquet format: 
    path = BASE_DIR / "data" / "processed" / f"trade_{year}.parquet"
    df = pl.read_parquet(path)

    # 2) Select a specific product (for example, petrol with code 2709): 
    df = df.filter(pl.col("Product_Code") == product_code)

    # 3) Group by country pairs to add up the total value of trade and prevent Networkx from overlapping each edge: 
    df = df.group_by(["Exporter", "Importer"]).agg(
        pl.col("Value_Thousands_USD").sum().alias("weight")
    )

    # 4) Create the graph as a directed graph (Exporter -> Importer) and the edges weighted by its trade value:
    graph = nx.from_pandas_edgelist(
        df.to_pandas(),
        source="Exporter",
        target="Importer",
        edge_attr="weight",
        create_using=nx.DiGraph()
    )

    # 5) Save the .gexf into the data/processed folder:
    output_path = BASE_DIR / "data" / "processed" / output_filename
    nx.write_gexf(graph, output_path)
    
    print(f"Graph successfully generated and saved at: {output_path}")

if __name__ == "__main__":
    # Test the function with Petrol (270900) for the year 2024:
    generate_product_graph(
        year=2024, 
        product_code=270900, 
        output_filename="world_trade_network_petrol_2024.gexf"
    )