from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from pathlib import Path
from functools import lru_cache

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year

nodes_df = None
edges_df = None
country_names = {}

# Cache for API responses
api_cache = {}

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

def load_country_codes(country_codes_path='country_codes.json'):
    """Load country code to name mapping"""
    global country_names
    try:
        # Use absolute path
        full_path = BASE_DIR / country_codes_path
        if full_path.exists():
            with open(full_path, 'r') as f:
                country_names = json.load(f)
            print(f"✓ Loaded country codes mapping for {len(country_names)} countries")
        else:
            print(f"⚠ No country_codes.json found at {full_path}, using country codes as-is")
            country_names = {}
    except Exception as e:
        print(f"✗ Error loading country codes: {e}")
        country_names = {}

def get_country_name(code):
    """Get country name from code, fallback to code if not found"""
    return country_names.get(code, code)

def load_data(nodes_path, edges_path):
    """Load CSV files into pandas dataframes"""
    global nodes_df, edges_df
    
    try:
        # Use absolute paths
        nodes_full_path = BASE_DIR / nodes_path
        edges_full_path = BASE_DIR / edges_path
        
        print(f"Loading data from:")
        print(f"  Nodes: {nodes_full_path}")
        print(f"  Edges: {edges_full_path}")
        
        if not nodes_full_path.exists():
            raise FileNotFoundError(f"Nodes file not found: {nodes_full_path}")
        if not edges_full_path.exists():
            raise FileNotFoundError(f"Edges file not found: {edges_full_path}")
        
        nodes_df = pd.read_csv(nodes_full_path)
        edges_df = pd.read_csv(edges_full_path)
        
        # Convert year to int, handling NaN values
        nodes_df['first_pubyear'] = pd.to_numeric(nodes_df['first_pubyear'], errors='coerce')
        nodes_df = nodes_df.dropna(subset=['first_pubyear'])
        nodes_df['first_pubyear'] = nodes_df['first_pubyear'].astype(int)
        
        print(f"✓ Loaded {len(nodes_df):,} nodes and {len(edges_df):,} edges")
        return True
        
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        print(f"Available files in {BASE_DIR}:")
        for file in os.listdir(BASE_DIR):
            print(f"  - {file}")
        return False

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('institute.html')

@app.route('/images')
def images():
    """Serve the images page"""
    return render_template('images.html')

@app.route('/author')
def author():
    return render_template('dashboard.html')

@app.route('/country')
def page2():
    return render_template('country.html')

@app.route('/debug')
def debug():
    """Debug endpoint to check file availability"""
    debug_info = {
        'base_dir': str(BASE_DIR),
        'current_working_directory': os.getcwd(),
        'files_in_directory': os.listdir(BASE_DIR),
        'csv_files': [f for f in os.listdir(BASE_DIR) if f.endswith('.csv')],
        'data_loaded': nodes_df is not None and edges_df is not None,
        'nodes_count': len(nodes_df) if nodes_df is not None else 0,
        'edges_count': len(edges_df) if edges_df is not None else 0,
    }
    
    html = "<html><head><title>Debug Info</title><style>body{font-family:monospace;padding:20px;}</style></head><body>"
    html += "<h1>Debug Information</h1>"
    for key, value in debug_info.items():
        html += f"<p><strong>{key}:</strong> {value}</p>"
    html += "</body></html>"
    
    return html

@app.route('/api/filters')
def get_filters():
    """Get available filter options"""
    if nodes_df is None:
        return jsonify({'error': 'Data not loaded'}), 400
    
    # Check cache first
    if 'filters' in api_cache:
        return jsonify(api_cache['filters'])
    
    countries_codes = sorted(nodes_df['country_code'].dropna().unique().tolist())
    countries = [{'code': code, 'name': get_country_name(code)} for code in countries_codes]
    
    result = {'countries': countries}
    api_cache['filters'] = result
    
    return jsonify(result)

def get_cache_key(country):
    """Generate cache key for statistics"""
    return f"stats_{country if country else 'all'}"

@app.route('/api/statistics')
def get_statistics():
    """Get filtered statistics based on query parameters"""
    if nodes_df is None or edges_df is None:
        return jsonify({'error': 'Data not loaded'}), 400
    
    country = request.args.get('country', '')
    cache_key = get_cache_key(country)
    
    # Check cache first
    if cache_key in api_cache:
        return jsonify(api_cache[cache_key])
    
    filtered_nodes = nodes_df.copy()
    
    if country:
        filtered_nodes = filtered_nodes[filtered_nodes['country_code'] == country]
    
    filtered_node_ids = set(filtered_nodes['author_id'].values)
    filtered_edges = edges_df[
        edges_df['author1'].isin(filtered_node_ids) & 
        edges_df['author2'].isin(filtered_node_ids)
    ]
    
    total_authors = len(filtered_nodes)
    total_collaborations = int(filtered_edges['collaboration_count'].sum())
    avg_collaborations = round(total_collaborations / total_authors, 1) if total_authors > 0 else 0
    
    # Only include country data if no country filter is applied
    top_countries = []
    all_countries = []
    
    if not country:
        country_counts = filtered_nodes['country_code'].value_counts().head(10)
        top_countries = [{'country': get_country_name(k), 'code': k, 'count': int(v)} for k, v in country_counts.items()]
        
        all_country_counts = filtered_nodes['country_code'].value_counts()
        all_countries = [{'country': get_country_name(k), 'code': k, 'count': int(v)} for k, v in all_country_counts.items()]
    
    author_collabs = {}
    for _, row in filtered_edges.iterrows():
        count = int(row['collaboration_count'])
        author_collabs[row['author1']] = author_collabs.get(row['author1'], 0) + count
        author_collabs[row['author2']] = author_collabs.get(row['author2'], 0) + count
    
    top_authors = []
    for author_id, collab_count in sorted(author_collabs.items(), key=lambda x: x[1], reverse=True)[:10]:
        author_info = filtered_nodes[filtered_nodes['author_id'] == author_id]
        if not author_info.empty:
            top_authors.append({
                'id': str(author_id),
                'name': author_info.iloc[0]['author_name'],
                'count': collab_count
            })
    
    year_counts = filtered_nodes['first_pubyear'].value_counts().sort_index()
    year_distribution = [{'year': int(k), 'count': int(v)} for k, v in year_counts.items()]
    
    collab_strength = filtered_edges['collaboration_count'].value_counts().sort_index()
    strength_distribution = [{'strength': int(k), 'count': int(v)} for k, v in collab_strength.items()]
    
    result = {
        'summary': {
            'total_authors': total_authors,
            'total_collaborations': total_collaborations,
            'avg_collaborations': avg_collaborations,
            'unique_connections': len(filtered_edges)
        },
        'top_countries': top_countries,
        'all_countries': all_countries,
        'top_authors': top_authors,
        'year_distribution': year_distribution,
        'strength_distribution': strength_distribution,
        'has_country_filter': bool(country)
    }
    
    # Cache the result
    api_cache[cache_key] = result
    
    return jsonify(result)

@app.route('/api/search/author')
def search_author():
    """Search for authors by ID or name"""
    if nodes_df is None or edges_df is None:
        return jsonify({'error': 'Data not loaded'}), 400
    
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    results = nodes_df[
        (nodes_df['author_id'].astype(str) == query) |
        (nodes_df['author_name'].str.contains(query, case=False, na=False))
    ]
    
    if results.empty:
        return jsonify({'results': [], 'count': 0})
    
    authors = []
    for _, author in results.iterrows():
        author_id = author['author_id']
        
        author_edges = edges_df[
            (edges_df['author1'] == author_id) | 
            (edges_df['author2'] == author_id)
        ]
        
        total_collabs = int(author_edges['collaboration_count'].sum())
        num_collaborators = len(author_edges)
        
        collaborator_ids = set()
        for _, edge in author_edges.iterrows():
            if edge['author1'] == author_id:
                collaborator_ids.add(edge['author2'])
            else:
                collaborator_ids.add(edge['author1'])
        
        collaborators = []
        for collab_id in list(collaborator_ids)[:5]:
            collab_info = nodes_df[nodes_df['author_id'] == collab_id]
            if not collab_info.empty:
                collab_edge = author_edges[
                    ((author_edges['author1'] == author_id) & (author_edges['author2'] == collab_id)) |
                    ((author_edges['author2'] == author_id) & (author_edges['author1'] == collab_id))
                ]
                collab_count = int(collab_edge['collaboration_count'].sum()) if not collab_edge.empty else 0
                
                collaborators.append({
                    'id': str(collab_id),
                    'name': collab_info.iloc[0]['author_name'],
                    'collaboration_count': collab_count
                })
        
        collaborators.sort(key=lambda x: x['collaboration_count'], reverse=True)
        
        authors.append({
            'author_id': str(author_id),
            'author_name': author['author_name'],
            'first_pubyear': int(author['first_pubyear']),
            'country_code': author['country_code'],
            'total_collaborations': total_collabs,
            'num_collaborators': num_collaborators,
            'top_collaborators': collaborators
        })
    
    return jsonify({
        'results': authors,
        'count': len(authors)
    })

@app.route('/api/author/<author_id>')
def get_author_details(author_id):
    """Get detailed information about a specific author"""
    if nodes_df is None or edges_df is None:
        return jsonify({'error': 'Data not loaded'}), 400
    
    author = nodes_df[nodes_df['author_id'].astype(str) == author_id]
    
    if author.empty:
        return jsonify({'error': 'Author not found'}), 404
    
    author = author.iloc[0]
    
    author_edges = edges_df[
        (edges_df['author1'].astype(str) == author_id) | 
        (edges_df['author2'].astype(str) == author_id)
    ]
    
    collaborators = []
    for _, edge in author_edges.iterrows():
        collab_id = edge['author2'] if str(edge['author1']) == author_id else edge['author1']
        collab_info = nodes_df[nodes_df['author_id'] == collab_id]
        
        if not collab_info.empty:
            collaborators.append({
                'id': str(collab_id),
                'name': collab_info.iloc[0]['author_name'],
                'country': collab_info.iloc[0]['country_code'],
                'collaboration_count': int(edge['collaboration_count'])
            })
    
    collaborators.sort(key=lambda x: x['collaboration_count'], reverse=True)
    
    return jsonify({
        'author_id': str(author['author_id']),
        'author_name': author['author_name'],
        'first_pubyear': int(author['first_pubyear']),
        'country_code': author['country_code'],
        'total_collaborations': int(author_edges['collaboration_count'].sum()),
        'num_collaborators': len(collaborators),
        'collaborators': collaborators
    })

# Initialize data on startup for production
def init_app():
    """Initialize the application with data"""
    print("\n" + "="*60)
    print("Research Collaboration Dashboard - Starting Up")
    print("="*60)
    
    # Try to load data automatically
    nodes_file = 'coauthors_nodes.csv'
    edges_file = 'coauthors_edges.csv'
    country_codes_file = 'country_codes.json'
    
    print(f"\nLooking for data files in: {BASE_DIR}")
    print(f"Files available: {os.listdir(BASE_DIR)}")
    
    load_country_codes(country_codes_file)
    success = load_data(nodes_file, edges_file)
    
    if success:
        print(f"\n✓ Data loaded successfully!")
        print(f"   Authors: {len(nodes_df):,}")
        print(f"   Collaborations: {len(edges_df):,}")
        print(f"\n✓ Server is ready!")
    else:
        print(f"\n⚠ Warning: Could not load data files")
        print(f"   Make sure CSV files are in the repository root")
    
    print("="*60 + "\n")

if __name__ == '__main__':
    # For local development with command line arguments
    import sys
    
    if len(sys.argv) >= 3:
        # Running with arguments (local development)
        nodes_file = sys.argv[1]
        edges_file = sys.argv[2]
        country_codes_file = sys.argv[3] if len(sys.argv) > 3 else 'country_codes.json'
        
        if not Path(nodes_file).exists():
            print(f"Error: {nodes_file} not found")
            sys.exit(1)
        
        if not Path(edges_file).exists():
            print(f"Error: {edges_file} not found")
            sys.exit(1)
        
        load_country_codes(country_codes_file)
        load_data(nodes_file, edges_file)
        
        print("\n" + "="*50)
        print("Research Collaboration Dashboard")
        print("="*50)
        print(f"\nData loaded successfully!")
        print(f"   Authors: {len(nodes_df):,}")
        print(f"   Collaborations: {len(edges_df):,}")
        print(f"\nStarting server...")
        print(f"   Open your browser to: http://localhost:5000")
        print(f"\nPress Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # Production mode - auto-load data
        init_app()
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)
else:
    # When running with gunicorn
    init_app()