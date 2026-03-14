import http.server
import socketserver
import json
import csv
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import sys

# Append current directory so graph functions can be imported
sys.path.append(str(Path(__file__).parent))

from data_processing import process_year
from graph_generation import generate_product_graph
from graph_map_visualization import visualize_map_graph

PORT = 8080
BASE_DIR = Path(__file__).resolve().parent.parent

class MinimalServer(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR / "results"), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/options':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Find available years from raw files
            raw_dir = BASE_DIR / "data" / "raw"
            years = sorted([int(f.stem.split('_')[2][1:]) for f in raw_dir.glob("BACI_HS92_Y*.csv")])
            
            # Read product codes
            products = []
            try:
                with open(raw_dir / 'product_codes_HS92_V202601.csv', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        products.append({"code": row['code'], "description": row['description']})
            except Exception as e:
                print(f"Error reading products csv: {e}")
                    
            self.wfile.write(json.dumps({"years": years, "products": products}).encode())
            return
            
        elif parsed.path == '/api/generate':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            query = parse_qs(parsed.query)
            year = int(query.get('year', [2024])[0])
            product = int(query.get('product', [270900])[0])
            top_n = int(query.get('top_n', [100])[0])
            
            gexf_filename = f"network_{product}_{year}.gexf"
            html_filename = f"mapa_{product}_{year}.html"
            
            # Temporary workaround to avoid leaving the files in the git tree
            gexf_path = BASE_DIR / "data" / "processed" / gexf_filename
            html_path = BASE_DIR / "results" / html_filename
            
            try:
                # Check if parquet exists, if not generate it on the fly
                parquet_path = BASE_DIR / "data" / "processed" / f"trade_{year}.parquet"
                if not parquet_path.exists():
                    print(f"Processing data for {year} (this might take a few seconds)...")
                    process_year(year)

                print(f"Generating map for Product {product} in Year {year}...")
                
                # Delete existing gexf if any to avoid errors
                if gexf_path.exists():
                    gexf_path.unlink()
                
                generate_product_graph(year, product, gexf_filename)
                
                # Delete existing HTML if any to avoid conflicts
                if html_path.exists():
                    html_path.unlink()
                
                visualize_map_graph(
                    input_filename=gexf_filename,
                    output_html=html_filename,
                    top_n=top_n, 
                    title=f"Comercio Global de Producto {product} ({year})"
                )
                
                # IMPORTANT: Read the generated HTML, then delete the files, and serve it directly to the browser
                # This way no garbage is left in the local directory
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Clean up immediately after reading
                if gexf_path.exists(): gexf_path.unlink()
                if html_path.exists(): html_path.unlink()
                
                self.wfile.write(json.dumps({
                    "success": True, 
                    "html_content": html_content
                }).encode())
                
            except Exception as e:
                print(f"Error during generation: {e}")
                
                 # Clean up in case of error
                if gexf_path.exists(): gexf_path.unlink()
                if html_path.exists(): html_path.unlink()
                
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return
            
        else:
            super().do_GET()

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), MinimalServer) as httpd:
        print("=="*20)
        print(f" Servidor API y Web Iniciado en http://127.0.0.1:{PORT}")
        print(f" Carga el HTML generado local o abre http://127.0.0.1:{PORT}/mapa_interactivo.html")
        print("=="*20)
        httpd.serve_forever()
