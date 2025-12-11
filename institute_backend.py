"""
Institutional Collaboration Network - Backend Data Processing
Contains all data loading, processing, and preparation logic.
"""

import pandas as pd
import numpy as np
import json
from collections import defaultdict
import sys
import os
import shutil
from institute_frontend import generate_html_template
def load_country_codes(json_path):
    """Load country code to full name mapping from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            country_mapping = json.load(f)
        print(f"  Loaded {len(country_mapping)} country code mappings")
        return country_mapping
    except FileNotFoundError:
        print(f"  Warning: Country codes file not found at {json_path}")
        return {}
    except json.JSONDecodeError:
        print(f"  Warning: Invalid JSON in {json_path}")
        return {}

def map_country_codes(df, country_mapping):
    """Map 2-digit country codes to full names."""
    if not country_mapping:
        print("  No country mapping available, using original codes")
        return df
    
    # Map institution_1_country
    df['institution_1_country'] = df['institution_1_country'].apply(
        lambda code: country_mapping.get(str(code).upper(), code) if pd.notna(code) else 'Unknown'
    )
    
    # Map institution_2_country
    df['institution_2_country'] = df['institution_2_country'].apply(
        lambda code: country_mapping.get(str(code).upper(), code) if pd.notna(code) else 'Unknown'
    )
    
    print(f"  Mapped country codes to full names")
    return df

def load_and_prepare_data(csv_path, country_mapping=None):
    """Load CSV with vectorized operations."""
    print("  Reading CSV...")
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Fill NaN values
    df['institution_1_country'] = df['institution_1_country'].fillna('Unknown')
    df['institution_2_country'] = df['institution_2_country'].fillna('Unknown')
    
    # Map country codes to full names if mapping provided
    if country_mapping:
        df = map_country_codes(df, country_mapping)
    
    df['institution_1_name'] = df['institution_1_name'].fillna('Unknown')
    df['institution_2_name'] = df['institution_2_name'].fillna('Unknown')
    df['institution_1_lat'] = df['institution_1_lat'].fillna(0)
    df['institution_1_lon'] = df['institution_1_lon'].fillna(0)
    df['institution_2_lat'] = df['institution_2_lat'].fillna(0)
    df['institution_2_lon'] = df['institution_2_lon'].fillna(0)
    df['collaboration_count'] = df['collaboration_count'].fillna(0).astype(int)
    df['authors_involved'] = df['authors_involved'].fillna(0).astype(int)
    df['institution_1_id'] = df['institution_1_id'].astype(str)
    df['institution_2_id'] = df['institution_2_id'].astype(str)
    
    return df

def build_institution_data(df):
    """Build institution metadata using vectorized ops."""
    print("  Building institution metadata...")
    
    # Stack both institution columns
    inst1 = df[['institution_1_id', 'institution_1_name', 'institution_1_country', 
                'institution_1_lat', 'institution_1_lon']].copy()
    inst1.columns = ['id', 'name', 'country', 'lat', 'lon']
    
    inst2 = df[['institution_2_id', 'institution_2_name', 'institution_2_country',
                'institution_2_lat', 'institution_2_lon']].copy()
    inst2.columns = ['id', 'name', 'country', 'lat', 'lon']
    
    all_inst = pd.concat([inst1, inst2], ignore_index=True)
    
    # Get unique institutions (first occurrence for metadata)
    institutions = all_inst.drop_duplicates(subset='id').set_index('id')
    
    # Compute degree (number of unique partners) for each institution
    partners1 = df.groupby('institution_1_id')['institution_2_id'].nunique()
    partners2 = df.groupby('institution_2_id')['institution_1_id'].nunique()
    degree = partners1.add(partners2, fill_value=0).astype(int)
    
    # Compute strength (total collaboration count)
    strength1 = df.groupby('institution_1_id')['collaboration_count'].sum()
    strength2 = df.groupby('institution_2_id')['collaboration_count'].sum()
    strength = strength1.add(strength2, fill_value=0).astype(int)
    
    institutions['degree'] = degree
    institutions['strength'] = strength
    institutions = institutions.fillna({'degree': 0, 'strength': 0})
    
    return institutions.reset_index()

def build_edges(df):
    """Build edge list with aggregation."""
    print("  Building edges...")
    
    # Aggregate edges (in case of duplicates)
    edges = df.groupby(['institution_1_id', 'institution_2_id']).agg({
        'collaboration_count': 'sum',
        'authors_involved': 'sum'
    }).reset_index()
    
    edges.columns = ['source', 'target', 'weight', 'authors']
    
    return edges

def compute_layout_fast(institutions):
    """Pre-compute layout positions using geographic coords + noise."""
    print("  Computing layout...")
    
    # Use actual geo coordinates, normalized to [-1, 1]
    lat_min, lat_max = institutions['lat'].min(), institutions['lat'].max()
    lon_min, lon_max = institutions['lon'].min(), institutions['lon'].max()
    
    lat_range = max(lat_max - lat_min, 1)
    lon_range = max(lon_max - lon_min, 1)
    
    # Normalize and add slight noise to prevent overlap
    np.random.seed(42)
    noise_scale = 0.02
    
    institutions['x'] = ((institutions['lon'] - lon_min) / lon_range * 2 - 1) + np.random.randn(len(institutions)) * noise_scale
    institutions['y'] = ((institutions['lat'] - lat_min) / lat_range * 2 - 1) + np.random.randn(len(institutions)) * noise_scale
    
    return institutions

def compute_country_aggregation(df):
    """Aggregate at country level."""
    print("  Computing country aggregation...")
    
    # Filter to international collaborations only
    intl = df[df['institution_1_country'] != df['institution_2_country']].copy()
    
    if len(intl) == 0:
        return [], []
    
    # Create sorted country pair keys
    intl['c1'] = intl[['institution_1_country', 'institution_2_country']].min(axis=1)
    intl['c2'] = intl[['institution_1_country', 'institution_2_country']].max(axis=1)
    
    # Aggregate
    country_edges = intl.groupby(['c1', 'c2']).agg({
        'collaboration_count': 'sum'
    }).reset_index()
    country_edges.columns = ['source', 'target', 'weight']
    
    # Country centroids
    inst1_geo = df.groupby('institution_1_country').agg({
        'institution_1_lat': 'mean',
        'institution_1_lon': 'mean'
    }).reset_index()
    inst1_geo.columns = ['country', 'lat', 'lon']
    
    inst2_geo = df.groupby('institution_2_country').agg({
        'institution_2_lat': 'mean',
        'institution_2_lon': 'mean'
    }).reset_index()
    inst2_geo.columns = ['country', 'lat', 'lon']
    
    country_geo = pd.concat([inst1_geo, inst2_geo]).groupby('country').mean().reset_index()
    
    # Count institutions per country
    inst_counts = pd.concat([
        df['institution_1_country'].value_counts(),
        df['institution_2_country'].value_counts()
    ]).groupby(level=0).first()
    
    country_geo['inst_count'] = country_geo['country'].map(inst_counts).fillna(0).astype(int)
    
    return country_geo.to_dict('records'), country_edges.to_dict('records')

def prepare_viz_data(institutions, edges, country_nodes, country_edges):
    """Prepare final data for visualization."""
    print("  Preparing visualization data...")
    
    # Normalize sizes
    max_strength = institutions['strength'].max() or 1
    institutions['size'] = 2 + 15 * (institutions['strength'] / max_strength)
    
    # Node data
    nodes = institutions[['id', 'name', 'country', 'lat', 'lon', 'x', 'y', 
                          'size', 'strength', 'degree']].to_dict('records')
    
    # Create node index map for edges
    node_idx = {n['id']: i for i, n in enumerate(nodes)}
    
    # Edge data - use indices for Cosmograph
    max_weight = edges['weight'].max() or 1
    edge_list = []
    for _, e in edges.iterrows():
        if e['source'] in node_idx and e['target'] in node_idx:
            edge_list.append({
                'source': node_idx[e['source']],
                'target': node_idx[e['target']],
                'weight': int(e['weight'])
            })
    
    # Stats
    stats = {
        'totalInstitutions': len(nodes),
        'totalCollaborations': len(edge_list),
        'totalCountries': institutions['country'].nunique()
    }
    
    return {
        'nodes': nodes,
        'edges': edge_list,
        'countryNodes': country_nodes,
        'countryEdges': country_edges,
        'stats': stats
    }

def process_data(csv_path, country_codes_path=None):
    """Main function to process data from CSV to visualization-ready format."""
    print("Loading data...")
    
    # Load country codes mapping
    country_mapping = {}
    if country_codes_path:
        country_mapping = load_country_codes(country_codes_path)
    
    df = load_and_prepare_data(csv_path, country_mapping)
    print(f"  {len(df)} rows loaded")
    
    print("Processing institutions...")
    institutions = build_institution_data(df)
    print(f"  {len(institutions)} unique institutions")
    
    print("Processing edges...")
    edges = build_edges(df)
    print(f"  {len(edges)} unique edges")
    
    print("Computing layout...")
    institutions = compute_layout_fast(institutions)
    
    print("Computing country aggregation...")
    country_nodes, country_edges = compute_country_aggregation(df)
    
    print("Building visualization data...")
    viz_data = prepare_viz_data(institutions, edges, country_nodes, country_edges)

    print("=== DEBUG VIZ DATA ===")
    print(f"Viz Nodes: {len(viz_data['nodes'])}")
    print(f"Viz Edges: {len(viz_data['edges'])}")
    
    
    return viz_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_csv> [country_codes_json] [output_html]")
        print("Example: python main.py data.csv country_codes.json output.html")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # Check if country codes JSON path is provided
    country_codes_path = None
    output_path = 'test.html'
    
    if len(sys.argv) >= 3:
        # Check if second argument is a JSON file
        if sys.argv[2].endswith('.json'):
            country_codes_path = sys.argv[2]
            if len(sys.argv) >= 4:
                output_path = sys.argv[3]
        else:
            output_path = sys.argv[2]
    
    # Try to find country_codes.json in common locations
    if not country_codes_path:
        potential_paths = [
            'country_codes.json',
            os.path.join(os.path.dirname(csv_path), 'country_codes.json'),
            os.path.join(os.getcwd(), 'country_codes.json')
        ]
        for path in potential_paths:
            if os.path.exists(path):
                country_codes_path = path
                print(f"Found country codes at: {path}")
                break
    
    # Process the data
    print("Processing data...")
    viz_data = process_data(csv_path, country_codes_path)
    
    # Generate the HTML
    print("Generating HTML...")
    html_content = generate_html_template(viz_data)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Visualization saved to: {output_path}")
    print("Done!")

if __name__ == '__main__':
    main()