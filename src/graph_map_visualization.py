import plotly.graph_objects as go
import networkx as nx
import pandas as pd
from pathlib import Path

def visualize_map_graph(input_filename: str, output_html: str = None, threshold: float = 500000, 
                        title: str = '', communities: dict = None, min_size: int|float = 3, 
                        colorscale = 'Turbo') -> go.Figure:
    """
    Visualizes a geographic network graph using Plotly, returing it as a figure object.
    Saves to HTML only if output_html is provided.
    Supports optional community coloring.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # 1) Read the respective graph: 
    graph_path = BASE_DIR / "data" / "processed" / input_filename
    graph = nx.read_gexf(graph_path)

    # 2) Get the dataframe with the coordinates of each country:
    url = "https://gist.githubusercontent.com/tadast/8827699/raw/3cd639fa34eec5067080a61c69e3ae25e3076abb/countries_codes_and_coordinates.csv"
    df_coords = pd.read_csv(url)

    # 2.1) Data cleaning:
    df_coords = df_coords[['Alpha-3 code', 'Latitude (average)', 'Longitude (average)']].astype('string')
    df_coords = df_coords.apply(lambda col: col.str.replace('"', '', regex=False).str.strip())
    df_coords.rename({'Alpha-3 code': 'ISO3', 'Latitude (average)': 'LAT', 'Longitude (average)': 'LONG'}, axis=1, inplace=True)

    # 2.2) Data type adjustment:
    df_coords.ISO3 = df_coords.ISO3.astype('category')
    df_coords[['LAT', 'LONG']] = df_coords[['LAT', 'LONG']].astype('float32')

    # 3) Filter the graph to avoid overloading the map (only routes over threshold USD) -> ADJUSTABLE:
    graph = nx.DiGraph(((u, v, d) for u, v, d in graph.edges(data=True) if d['weight'] > threshold))

    # 4) Create a coordinate dictionary for fast (O(1)) search:
    coords_dict = df_coords.set_index('ISO3')[['LAT', 'LONG']].T.to_dict('list')

    # 5) Prepare the coordinate lists for the edges (trade flows):
    edge_x = []
    edge_y = []

    for u, v, data in graph.edges(data=True):
        # Verify that both countries exist in the CSV of coordinates:
        if u in coords_dict and v in coords_dict:
            # Plotly uses (Longitude, Latitude) -> (X, Y):
            x0, y0 = coords_dict[u][1], coords_dict[u][0] 
            x1, y1 = coords_dict[v][1], coords_dict[v][0]
            
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

    # 6) Prepare the lists for the nodes (countries):
    node_x = []
    node_y = []
    node_text = []
    node_sizes = []
    node_colors = [] # List to store community IDs or default color.

    for node in graph.nodes():
        if node in coords_dict:
            node_x.append(coords_dict[node][1])
            node_y.append(coords_dict[node][0])
            
            # Calculate the total exports from this country in the filtered network (out-weight):
            out_weight = sum([d['weight'] for _, _, d in graph.out_edges(node, data=True)])
            
            # Add the respective text: 
            node_text.append(f"{node}<br>Exports (M USD): {out_weight/1000:.1f}")
            
            # Scale the size of the node so that it visually fits on the map:
            node_sizes.append(max(out_weight / 800000, min_size))
        
            # Logic for color assignment (in case of including the communities option):
            if communities and node in communities:
                node_colors.append(communities.get(node, -1))
            else:
                node_colors.append('rgba(211, 47, 47, 0.8)') # Default value (red) for the color scale.

    # 7) Build the interactive Plotly figure:
    fig = go.Figure()

    # Layer 1 - Trade routes lines:
    fig.add_trace(go.Scattergeo(
        lon=edge_x, lat=edge_y,
        mode='lines',
        line=dict(width=0.8, color='rgba(30, 136, 229, 0.4)'), # Blue.
        hoverinfo='none'
    ))

    # Layer 2 - Country nodes:
    marker_settings = dict(
        size=node_sizes,
        color=node_colors,
        line=dict(width=1, color='black'),
        sizemode='area'
    )
    
    if communities:
        marker_settings['colorscale'] = colorscale
        marker_settings['showscale'] = True
        marker_settings['reversescale'] = False

    fig.add_trace(go.Scattergeo(
        lon=node_x, lat=node_y, mode='markers',
        hoverinfo='text', text=node_text,
        marker=marker_settings
    ))

    # 8) Configure map style and display it:
    fig.update_layout(
        title_text=f"{title} (> {threshold/1000}M USD)",
        showlegend=False,
        geo=dict(
            showland=True,
            landcolor="rgb(243, 243, 243)",
            countrycolor="rgb(204, 204, 204)",
            showocean=True,
            oceancolor="rgb(230, 240, 255)",
            projection_type="equirectangular" 
        ),
        margin=dict(l=0, r=0, t=40, b=0)
    )

    # 9) Save it in html format (in the results folder) if provided: 
    if output_html:
        output_path = BASE_DIR / "results" / output_html
        fig.write_html(str(output_path), auto_open=False)
        print(f"Map successfully generated and saved at: {output_path}")
    
    # 10) Return the figure object: 
    return fig

if __name__ == "__main__":
    # Test the function with Petrol (270900) for the year 2024:
    visualize_map_graph(
        input_filename="world_trade_network_petrol_2024.gexf",
        output_html="world_trade_map_petrol_2024.html",
        threshold=500000,
        title="Geopolitics of Oil in 2024: Global Trade Routes"
    )