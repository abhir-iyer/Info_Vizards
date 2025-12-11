"""
Frontend HTML generator for Institutional Collaboration Network
This file generates the HTML with embedded JavaScript.
"""

import json
import os

def generate_html_template(viz_data):
    """Generate HTML with embedded data and JavaScript."""
    
    # Extract CSS and JS into variables for cleaner code
    css_styles = get_css_styles()
    js_visualization = get_js_visualization()
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Institutional Collaboration Network</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
    <style>
{css_styles}
    </style>
</head>
<body>
    <div class="app-container">
        
        <div class="main-viz">
            <div id="network-container"></div>
            <div id="map-container" style="display:none;"></div>
            <div id="compare-container" style="display:none;"></div>
            <div class="tooltip" id="tooltip"></div>
            <div class="loading" id="loading" style="position: absolute; top:50%; left:50%; transform:translate(-50%,-50%);">
                Loading Network...
            </div>
        </div>

        <div class="top-bar glass-panel" id="top-bar">
            <div class="title-group">
                <h1 id="top-bar-title">Institutions Collaboration Network</h1>
            </div>
            <div class="stats-group">
                <div class="stat-item">
                    <span class="stat-value" id="stat-institutions">-</span>
                    <span class="stat-label">Institutions</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" id="stat-collaborations">-</span>
                    <span class="stat-label">Collaborations</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" id="stat-countries">-</span>
                    <span class="stat-label">Countries</span>
                </div>
            </div>
        </div>

        <div class="controls-panel glass-panel">
            <h2>Display</h2>
            <div class="segmented-control">
                <button class="segment-btn active" data-view="network">Network</button>
                <button class="segment-btn" data-view="map">Geo Map</button>
                <button class="segment-btn" data-view="compare">Compare</button>
            </div>

            <div id="normal-controls" style="display: block;">
                <h2>Search</h2>
                <input type="text" class="search-box" id="search-input" placeholder="Find institution...">
                
                <div class="section-spacer"></div>

                <h2>Filters</h2>
                
                <div class="control-group">
                    <div class="control-header">
                        <label>Min. Collaborations</label>
                        <span class="control-value" id="collab-value">1</span>
                    </div>
                    <input type="range" id="collab-filter" min="1" max="100" value="1">
                </div>

                <div class="control-group">
                    <div class="control-header">
                        <label>Connectivity</label>
                        <span class="control-value" id="degree-value">1</span>
                    </div>
                    <input type="range" id="degree-filter" min="1" max="50" value="1">
                </div>
                
                <div class="control-group">
                    <div class="control-header"><label>Country</label></div>
                    <select id="country-filter">
                        <option value="">All Regions</option>
                    </select>
                </div>

                <div class="control-group">
                    <div class="control-header">
                        <label>Limit Nodes</label>
                        <span class="control-value" id="topn-value">All</span>
                    </div>
                    <input type="range" id="topn-filter" min="100" max="5000" value="5000" step="100">
                </div>
            </div>

            <div id="compare-controls" style="display: none;">
                <h2>Select Countries (Max 3)</h2>
                
                <div class="compare-zone">
                    <div class="country-slot" data-slot="0">
                        <div class="country-slot-label">Click to select country 1</div>
                    </div>
                    <div class="country-slot" data-slot="1">
                        <div class="country-slot-label">Click to select country 2</div>
                    </div>
                    <div class="country-slot" data-slot="2">
                        <div class="country-slot-label">Click to select country 3</div>
                    </div>
                </div>

                <div class="country-picker" id="country-picker"></div>

                <div class="section-spacer"></div>

                <h2>Filters</h2>
                
                <div class="control-group">
                    <div class="control-header">
                        <label>Min. Collaborations</label>
                        <span class="control-value" id="compare-collab-value">1</span>
                    </div>
                    <input type="range" id="compare-collab-filter" min="1" max="100" value="1">
                </div>

                <div class="control-group">
                    <div class="control-header">
                        <label>Connectivity</label>
                        <span class="control-value" id="compare-degree-value">1</span>
                    </div>
                    <input type="range" id="compare-degree-filter" min="1" max="50" value="1">
                </div>

                <div class="control-group">
                    <div class="control-header">
                        <label>Limit Nodes</label>
                        <span class="control-value" id="compare-topn-value">All</span>
                    </div>
                    <input type="range" id="compare-topn-filter" min="100" max="5000" value="5000" step="100">
                </div>

                <div id="comparison-stats-container"></div>
            </div>
        </div>

        <div class="details-panel glass-panel">
            <div class="details-content">
                <div class="selected-info" id="node-info">
                    <h3 id="info-name">-</h3>
                    <div class="subtitle" id="info-country">-</div>
                    
                    <div class="metric-row">
                        <span class="metric-label">Total Collaborations</span>
                        <span class="metric-val" id="info-collabs">-</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Unique Partners</span>
                        <span class="metric-val" id="info-degree">-</span>
                    </div>
                </div>
                
                <div style="padding: 16px 16px 8px 16px; border-bottom: 1px solid rgba(0,0,0,0.05);">
                    <h2 id="network-table-title">Top Institutions</h2>
                </div>
                
                <div class="table-wrapper" id="network-table-wrapper">
                    <table id="institutions-table">
                        <thead>
                            <tr>
                                <th data-sort="name">Name</th>
                                <th data-sort="country">Region</th>
                                <th data-sort="strength">Val</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                
                <div style="padding: 16px 16px 8px 16px; border-bottom: 1px solid rgba(0,0,0,0.05); display: none;" id="compare-table-header">
                    <h2 id="compare-table-title">Top Institutions</h2>
                </div>
                
                <div class="table-wrapper" id="compare-table-wrapper" style="display: none;">
                    <table id="compare-institutions-table">
                        <thead>
                            <tr>
                                <th data-sort="name">Name</th>
                                <th data-sort="country">Region</th>
                                <th data-sort="strength">Val</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="bottom-actions">
        </div>

    </div>
    
    <script>
    const DATA = {json.dumps(viz_data)};
    
    {js_visualization}
    </script>
</body>
</html>'''
    
    return html

def get_css_styles():
    """Return the CSS styles."""
    return '''        :root {
            --glass-bg: rgba(255, 255, 255, 0.72);
            --glass-border: rgba(255, 255, 255, 0.5);
            --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            --text-primary: #1d1d1f;
            --text-secondary: #86868b;
            --accent: #0071e3;
            --accent-hover: #0077ed;
            --danger: #ff3b30;
            --success: #34c759;
            --warning: #ffcc00;
            --compare-1: #0071e3;
            --compare-2: #ff375f;
            --compare-3: #30d158;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
            background: #f5f5f7;
            color: var(--text-primary);
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }
        
        .app-container {
            position: relative;
            width: 100%;
            height: 100%;
        }

        .main-viz {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }

        #network-container, #map-container, #compare-container {
            width: 100%;
            height: 100%;
        }
        
        .glass-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid var(--glass-border);
            box-shadow: var(--glass-shadow);
            border-radius: 18px;
            z-index: 10;
        }

        .top-bar {
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            max-width: fit-content;
            padding: 12px 24px;
            display: flex;
            align-items: center;
            gap: 32px;
            z-index: 10;
            transition: opacity 0.3s;
        }
        
        .top-bar.hidden {
            display: none;
        }

        .title-group h1 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }

        .stats-group {
            display: flex;
            gap: 24px;
            border-left: 1px solid rgba(0,0,0,0.1);
            padding-left: 24px;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
        }

        .stat-value {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.2;
        }

        .stat-label {
            font-size: 11px;
            font-weight: 500;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }

        .controls-panel {
            position: absolute;
            top: 100px;
            left: 20px;
            width: 280px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 24px;
            max-height: calc(100vh - 120px);
            overflow-y: auto;
        }

        h2 {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }

        .search-box {
            width: 100%;
            padding: 10px 14px;
            background: rgba(118, 118, 128, 0.12);
            border: none;
            border-radius: 10px;
            font-size: 15px;
            color: var(--text-primary);
            outline: none;
            transition: background 0.2s;
        }

        .search-box:focus {
            background: rgba(118, 118, 128, 0.18);
        }
        
        .search-box::placeholder {
            color: var(--text-secondary);
        }

        .control-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-bottom: 16px;
        }

        .control-header {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: var(--text-primary);
            font-weight: 500;
        }

        .control-value {
            color: var(--text-secondary);
            font-variant-numeric: tabular-nums;
        }

        input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            background: transparent;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            height: 20px;
            width: 20px;
            border-radius: 50%;
            background: #ffffff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            margin-top: -8px;
            cursor: pointer;
            border: 0.5px solid rgba(0,0,0,0.04);
        }

        input[type="range"]::-webkit-slider-runnable-track {
            width: 100%;
            height: 4px;
            background: rgba(0,0,0,0.1);
            border-radius: 2px;
        }
        
        select {
            appearance: none;
            width: 100%;
            padding: 10px 14px;
            background: rgba(118, 118, 128, 0.12);
            border: none;
            border-radius: 10px;
            font-size: 15px;
            color: var(--text-primary);
            outline: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2386868b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 16px;
        }

        .segmented-control {
            display: flex;
            background: rgba(118, 118, 128, 0.12);
            padding: 2px;
            border-radius: 9px;
        }

        .segment-btn {
            flex: 1;
            padding: 6px 12px;
            border: none;
            background: transparent;
            font-size: 13px;
            font-weight: 500;
            border-radius: 7px;
            cursor: pointer;
            color: var(--text-primary);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .segment-btn.active {
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        /* Comparison Mode Styles */
        .compare-zone {
            display: flex;
            gap: 16px;
            flex-direction: column;
        }

        .country-slot {
            background: rgba(118, 118, 128, 0.08);
            border: 2px dashed rgba(118, 118, 128, 0.3);
            border-radius: 12px;
            padding: 16px;
            min-height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }

        .country-slot.active {
            background: rgba(0, 113, 227, 0.08);
            border-color: var(--accent);
            border-style: solid;
        }

        .country-slot.filled {
            justify-content: space-between;
            align-items: stretch;
        }

        .country-slot-label {
            font-size: 12px;
            color: var(--text-secondary);
            text-align: center;
        }

        .country-slot-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
        }

        .country-slot-name {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .country-slot-remove {
            background: rgba(255, 59, 48, 0.1);
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--danger);
            font-size: 16px;
            transition: all 0.2s;
        }

        .country-slot-remove:hover {
            background: rgba(255, 59, 48, 0.2);
        }

        .country-picker {
            max-height: 200px;
            overflow-y: auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            margin-top: 8px;
            display: none;
        }

        .country-picker.active {
            display: block;
        }

        .country-option {
            padding: 10px 14px;
            cursor: pointer;
            font-size: 14px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }

        .country-option:hover {
            background: rgba(0, 113, 227, 0.08);
        }

        .country-option:last-child {
            border-bottom: none;
        }

        .comparison-stats {
            display: flex;
            gap: 12px;
            flex-direction: column;
            padding: 16px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 12px;
            margin-top: 12px;
        }

        .comparison-stat-row {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
        }

        .comparison-stat-label {
            color: var(--text-secondary);
        }

        .comparison-stat-value {
            font-weight: 600;
            font-variant-numeric: tabular-nums;
        }
        
        .section-spacer {
            height: 24px;
        }

        .details-panel {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 300px;
            bottom: 20px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .details-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .selected-info {
            padding: 24px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            background: rgba(255,255,255,0.4);
            display: none;
        }
        
        .selected-info.visible {
            display: block;
            animation: slideDown 0.3s ease-out;
        }
        
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .selected-info h3 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 4px;
            color: var(--text-primary);
        }

        .selected-info .subtitle {
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .metric-label { color: var(--text-secondary); }
        .metric-val { font-weight: 600; color: var(--accent); }

        .table-wrapper {
            flex: 1;
            overflow: auto;
            padding: 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th {
            position: sticky;
            top: 0;
            background: rgba(245, 245, 247, 0.95);
            backdrop-filter: blur(10px);
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            cursor: pointer;
            z-index: 5;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        
        th:hover { color: var(--text-primary); }

        td {
            padding: 12px 16px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 140px;
        }
        
        tr { cursor: pointer; transition: background 0.1s; }
        tr:hover { background: rgba(0, 113, 227, 0.08); }

        .tooltip {
            position: fixed;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            padding: 12px 16px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.15s;
            z-index: 1000;
            font-size: 13px;
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .tooltip h4 { margin-bottom: 4px; font-weight: 600; }
        .tooltip p { color: var(--text-secondary); margin-bottom: 0; }
        
        .bottom-actions {
            position: absolute;
            bottom: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
        }

        .action-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: none;
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            box-shadow: var(--glass-shadow);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--text-primary);
            transition: transform 0.2s;
        }
        
        .action-btn:hover { transform: scale(1.05); }

        #loading {
            font-weight: 500;
            color: var(--text-secondary);
            background: rgba(255,255,255,0.8);
            padding: 12px 24px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.25); }'''

def get_js_visualization():
    """Return the JavaScript visualization code."""
    return '''    // Comparison Colors
    const COMPARE_COLORS = ['#0071e3', '#ff375f', '#30d158'];
    
    // Apple-inspired Palette
    const COLORS = [
        '#0071e3', '#5e5ce6', '#bf5af2', '#ff375f', '#ff9f0a', 
        '#ffd60a', '#30d158', '#64d2ff', '#0a84ff', '#ac8e68'
    ];
    
    // Stats Initialization
    document.getElementById('stat-institutions').textContent = DATA.stats.totalInstitutions.toLocaleString();
    document.getElementById('stat-collaborations').textContent = DATA.stats.totalCollaborations.toLocaleString();
    document.getElementById('stat-countries').textContent = DATA.stats.totalCountries.toLocaleString();
    
    // Application State
    let currentView = 'network';
    let allNodes = DATA.nodes;
    let allEdges = DATA.edges;
    let simulation = null;
    let canvas, ctx;
    let transform = d3.zoomIdentity;
    let currentNodes = [];
    let currentEdges = [];
    let hoveredNode = null;
    
    // Separate selection state for each view
    let selectedNodeNetwork = null;  // For network view
    let selectedNodeCompare = null;  // For compare view
    
    // Comparison State
    let selectedCountries = [null, null, null];
    let activeSlot = null;
    let compareFilters = { minCollab: 1, minDegree: 1, topN: 5000 };
    
    // Filters Default
    const filters = { minCollab: 1, minDegree: 1, country: '', search: '', topN: 5000 };
    
    // Data Processing: Countries
    const countries = [...new Set(allNodes.map(n => n.country))].sort();
    const countryColorMap = {};
    countries.forEach((c, i) => { countryColorMap[c] = i % COLORS.length; });
    
    // Populate Select
    const countrySelect = document.getElementById('country-filter');
    countries.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        countrySelect.appendChild(opt);
    });
    
    // Populate Country Picker
    const countryPicker = document.getElementById('country-picker');
    countries.forEach(c => {
        const div = document.createElement('div');
        div.className = 'country-option';
        div.textContent = c;
        div.onclick = () => selectCountryForSlot(c);
        countryPicker.appendChild(div);
    });
    
    // Set Range Limits
    const maxCollab = Math.max(...allNodes.map(n => n.strength));
    const maxDegree = Math.max(...allNodes.map(n => n.degree));
    document.getElementById('collab-filter').max = Math.min(maxCollab, 1000);
    document.getElementById('degree-filter').max = Math.min(maxDegree, 200);
    document.getElementById('topn-filter').max = allNodes.length;
    document.getElementById('topn-filter').value = Math.min(5000, allNodes.length);
    
    // Function to update top bar
    function updateTopBar() {
        const topBar = document.getElementById('top-bar');
        const topBarTitle = document.getElementById('top-bar-title');
        
        // Hide top bar in compare mode
        if (currentView === 'compare') {
            topBar.classList.add('hidden');
            return;
        }
        
        topBar.classList.remove('hidden');
        
        if (currentView === 'network') {
            // Get filtered nodes to calculate stats
            let filtered = allNodes;
            
            // Update title based on country filter
            if (filters.country) {
                filtered = filtered.filter(n => n.country === filters.country);
                topBarTitle.textContent = filters.country;
            } else {
                topBarTitle.textContent = 'Institutions Collaboration Network';
            }
            
            if (filters.minCollab > 1) filtered = filtered.filter(n => n.strength >= filters.minCollab);
            if (filters.minDegree > 1) filtered = filtered.filter(n => n.degree >= filters.minDegree);
            if (filters.search) {
                const s = filters.search.toLowerCase();
                filtered = filtered.filter(n => n.name.toLowerCase().includes(s));
            }
            
            // Calculate stats for filtered nodes
            const filteredInstitutions = filtered.length;
            const uniqueCountries = new Set(filtered.map(n => n.country)).size;
            
            // Calculate collaborations (edges between filtered nodes)
            const filteredNodeIds = new Set(filtered.map((n, idx) => {
                const origIdx = allNodes.findIndex(an => an.id === n.id);
                return origIdx;
            }));
            const filteredEdges = allEdges.filter(e => 
                filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target)
            );
            const totalCollabs = filteredEdges.reduce((sum, e) => sum + e.weight, 0);
            
            document.getElementById('stat-institutions').textContent = filteredInstitutions.toLocaleString();
            document.getElementById('stat-collaborations').textContent = totalCollabs.toLocaleString();
            document.getElementById('stat-countries').textContent = uniqueCountries.toLocaleString();
        } else if (currentView === 'map') {
            topBarTitle.textContent = 'Geographic Distribution';
            // Keep global stats for map view
            document.getElementById('stat-institutions').textContent = DATA.stats.totalInstitutions.toLocaleString();
            document.getElementById('stat-collaborations').textContent = DATA.stats.totalCollaborations.toLocaleString();
            document.getElementById('stat-countries').textContent = DATA.stats.totalCountries.toLocaleString();
        }
    }
    
    // --- Canvas Network ---
    function initNetwork() {
        const container = document.getElementById('network-container');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        canvas = document.createElement('canvas');
        canvas.width = width * window.devicePixelRatio;
        canvas.height = height * window.devicePixelRatio;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        container.appendChild(canvas);
        
        ctx = canvas.getContext('2d');
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {
                transform = event.transform;
                render();
            });
        
        d3.select(canvas).call(zoom);
        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('click', handleClick);
        
        applyFilters();
        document.getElementById('loading').style.display = 'none';
    }
    
    function handleMouseMove(event) {
        const rect = canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left - transform.x) / transform.k;
        const y = (event.clientY - rect.top - transform.y) / transform.k;
        
        hoveredNode = null;
        for (let i = currentNodes.length - 1; i >= 0; i--) {
            const node = currentNodes[i];
            const dx = node.x - x;
            const dy = node.y - y;
            const r = node.size + 4;
            if (dx * dx + dy * dy < r * r) {
                hoveredNode = node;
                break;
            }
        }
        
        if (hoveredNode) {
            showTooltip(hoveredNode, event);
            canvas.style.cursor = 'pointer';
        } else {
            hideTooltip();
            canvas.style.cursor = 'default';
        }
        render();
    }
    
    function handleClick(event) {
        if (hoveredNode) {
            selectNode(hoveredNode, 'network');
        }
    }
    
    function applyFilters() {
        // Clear selection when filters change
        document.getElementById('node-info').classList.remove('visible');
        selectedNodeNetwork = null;
        hoveredNode = null;
        
        let filtered = allNodes.map((n, i) => ({...n, originalIndex: i}));
        
        if (filters.minCollab > 1) filtered = filtered.filter(n => n.strength >= filters.minCollab);
        if (filters.minDegree > 1) filtered = filtered.filter(n => n.degree >= filters.minDegree);
        if (filters.country) filtered = filtered.filter(n => n.country === filters.country);
        if (filters.search) {
            const s = filters.search.toLowerCase();
            filtered = filtered.filter(n => n.name.toLowerCase().includes(s));
        }
        
        filtered.sort((a, b) => b.strength - a.strength);
        if (filters.topN < filtered.length) filtered = filtered.slice(0, filters.topN);
        
        const nodeIdxMap = new Map(filtered.map((n, newIdx) => [n.originalIndex, newIdx]));
        
        const filteredEdges = allEdges
            .filter(e => nodeIdxMap.has(e.source) && nodeIdxMap.has(e.target))
            .map(e => ({ 
                source: nodeIdxMap.get(e.source), 
                target: nodeIdxMap.get(e.target), 
                weight: e.weight 
            }));
        
        currentNodes = filtered.map((n, i) => ({
            ...n,
            index: i,
            x: n.x * 350 + canvas.width / (2 * window.devicePixelRatio),
            y: n.y * 350 + canvas.height / (2 * window.devicePixelRatio),
            color: COLORS[countryColorMap[n.country] || 0]
        }));
        
        currentEdges = filteredEdges;
        
        // Stop any existing simulation to prevent interference
        if (simulation) {
            simulation.stop();
            simulation = null;
        }
        
        if (currentNodes.length > 0 && currentNodes.length < 4000) {
            simulation = d3.forceSimulation(currentNodes)
                .force('link', d3.forceLink(currentEdges.map(e => ({...e}))).id((d, i) => i).distance(50).strength(0.2))
                .force('charge', d3.forceManyBody().strength(-20).distanceMax(150))
                .force('center', d3.forceCenter(canvas.width / (2 * window.devicePixelRatio), canvas.height / (2 * window.devicePixelRatio)))
                .force('collision', d3.forceCollide().radius(d => d.size + 1).iterations(2))
                .alpha(0.6)
                .alphaDecay(0.03)
                .on('tick', render);
        } else {
            render();
        }
        
        updateTable(filtered);
        updateTopBar();
    }
    
    function render() {
        const width = canvas.width / window.devicePixelRatio;
        const height = canvas.height / window.devicePixelRatio;
        
        ctx.save();
        ctx.clearRect(0, 0, width, height);
        ctx.translate(transform.x, transform.y);
        ctx.scale(transform.k, transform.k);
        
        ctx.strokeStyle = '#a1a1aa';
        ctx.lineWidth = 0.5 / transform.k;
        ctx.globalAlpha = 0.3;
        
        for (const edge of currentEdges) {
            const source = currentNodes[edge.source];
            const target = currentNodes[edge.target];
            if (source && target) {
                ctx.beginPath();
                ctx.moveTo(source.x, source.y);
                ctx.lineTo(target.x, target.y);
                ctx.stroke();
            }
        }
        
        ctx.globalAlpha = 1;
        
        for (const node of currentNodes) {
            const isHovered = hoveredNode === node;
            const isSelected = selectedNodeNetwork && selectedNodeNetwork.id === node.id;
            
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI);
            ctx.fillStyle = node.color;
            ctx.fill();
            
            if (isHovered || isSelected) {
                ctx.lineWidth = 2.5 / transform.k;
                ctx.strokeStyle = '#000000';
                ctx.stroke();
                
                ctx.shadowColor = 'rgba(0,0,0,0.2)';
                ctx.shadowBlur = 10;
                ctx.fill();
                ctx.shadowBlur = 0;
            } else {
                 ctx.lineWidth = 1 / transform.k;
                 ctx.strokeStyle = 'rgba(255,255,255,0.8)';
                 ctx.stroke();
            }
        }
        
        ctx.restore();
    }
    
    // --- Comparison Mode ---
    let compareCanvas, compareCtx;
    let compareTransform = d3.zoomIdentity;
    
    function initCompare() {
        const container = document.getElementById('compare-container');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        if (!compareCanvas) {
            compareCanvas = document.createElement('canvas');
            compareCanvas.width = width * window.devicePixelRatio;
            compareCanvas.height = height * window.devicePixelRatio;
            compareCanvas.style.width = width + 'px';
            compareCanvas.style.height = height + 'px';
            container.appendChild(compareCanvas);
            
            compareCtx = compareCanvas.getContext('2d');
            compareCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
            
            const zoom = d3.zoom()
                .scaleExtent([0.1, 10])
                .on('zoom', (event) => {
                    compareTransform = event.transform;
                    renderComparison();
                });
            
            d3.select(compareCanvas).call(zoom);
            compareCanvas.addEventListener('mousemove', handleCompareMouseMove);
        }
        
        renderComparison();
    }
    
    function handleCompareMouseMove(event) {
        const rect = compareCanvas.getBoundingClientRect();
        const x = (event.clientX - rect.left - compareTransform.x) / compareTransform.k;
        const y = (event.clientY - rect.top - compareTransform.y) / compareTransform.k;
        
        hoveredNode = null;
        for (let i = currentNodes.length - 1; i >= 0; i--) {
            const node = currentNodes[i];
            const dx = node.x - x;
            const dy = node.y - y;
            const r = node.size + 4;
            if (dx * dx + dy * dy < r * r) {
                hoveredNode = node;
                break;
            }
        }
        
        if (hoveredNode) {
            showTooltip(hoveredNode, event);
            compareCanvas.style.cursor = 'pointer';
        } else {
            hideTooltip();
            compareCanvas.style.cursor = 'default';
        }
        renderComparison();
    }
    
    function updateComparison() {
        // Clear selection when comparison updates
        document.getElementById('node-info').classList.remove('visible');
        selectedNodeCompare = null;
        hoveredNode = null;
        
        const activeCountries = selectedCountries.filter(c => c !== null);
        
        if (activeCountries.length === 0) {
            currentNodes = [];
            currentEdges = [];
            renderComparison();
            updateComparisonStats();
            
            // Update compare table
            const compareTableTitle = document.getElementById('compare-table-title');
            compareTableTitle.textContent = 'Top Institutions';
            updateCompareTableOnly([]);
            return;
        }
        
        // Filter nodes by selected countries first
        let filtered = allNodes.filter(n => activeCountries.includes(n.country));
        
        // Apply comparison filters
        if (compareFilters.minCollab > 1) {
            filtered = filtered.filter(n => n.strength >= compareFilters.minCollab);
        }
        if (compareFilters.minDegree > 1) {
            filtered = filtered.filter(n => n.degree >= compareFilters.minDegree);
        }
        
        // Sort by strength and limit
        filtered.sort((a, b) => b.strength - a.strength);
        if (compareFilters.topN < filtered.length) {
            filtered = filtered.slice(0, compareFilters.topN);
        }
        
        filtered = filtered.map((n, i) => ({...n, originalIndex: allNodes.indexOf(n)}));
        
        // Color by country
        const countryColorIndex = {};
        activeCountries.forEach((c, i) => {
            countryColorIndex[c] = i;
        });
        
        // Get edges between filtered nodes
        const nodeIdxMap = new Map(filtered.map((n, newIdx) => [n.originalIndex, newIdx]));
        
        const filteredEdges = allEdges
            .filter(e => nodeIdxMap.has(e.source) && nodeIdxMap.has(e.target))
            .map(e => ({ 
                source: nodeIdxMap.get(e.source), 
                target: nodeIdxMap.get(e.target), 
                weight: e.weight 
            }));
        
        // Create node positions
        currentNodes = filtered.map((n, i) => ({
            ...n,
            index: i,
            x: n.x * 350 + compareCanvas.width / (2 * window.devicePixelRatio),
            y: n.y * 350 + compareCanvas.height / (2 * window.devicePixelRatio),
            color: COMPARE_COLORS[countryColorIndex[n.country]] || '#999'
        }));
        
        currentEdges = filteredEdges;
        
        // Stop any existing simulation to prevent interference
        if (simulation) {
            simulation.stop();
            simulation = null;
        }
        
        // Force simulation
        if (currentNodes.length > 0 && currentNodes.length < 4000) {
            simulation = d3.forceSimulation(currentNodes)
                .force('link', d3.forceLink(currentEdges.map(e => ({...e}))).id((d, i) => i).distance(60).strength(0.3))
                .force('charge', d3.forceManyBody().strength(-30).distanceMax(200))
                .force('center', d3.forceCenter(compareCanvas.width / (2 * window.devicePixelRatio), compareCanvas.height / (2 * window.devicePixelRatio)))
                .force('collision', d3.forceCollide().radius(d => d.size + 2).iterations(2))
                .alpha(0.7)
                .alphaDecay(0.03)
                .on('tick', renderComparison);
        } else {
            renderComparison();
        }
        
        updateComparisonStats();
        
        // Update compare table with all institutions from selected countries (not just filtered ones)
        const allCountryInstitutions = allNodes.filter(n => activeCountries.includes(n.country));
        const compareTableTitle = document.getElementById('compare-table-title');
        compareTableTitle.textContent = `Top Institutions (${activeCountries.join(', ')})`;
        updateCompareTableOnly(allCountryInstitutions);
    }
    
    function renderComparison() {
        if (!compareCanvas) return;
        
        const width = compareCanvas.width / window.devicePixelRatio;
        const height = compareCanvas.height / window.devicePixelRatio;
        
        compareCtx.save();
        compareCtx.clearRect(0, 0, width, height);
        compareCtx.translate(compareTransform.x, compareTransform.y);
        compareCtx.scale(compareTransform.k, compareTransform.k);
        
        // Edges
        compareCtx.strokeStyle = '#a1a1aa';
        compareCtx.lineWidth = 0.8 / compareTransform.k;
        compareCtx.globalAlpha = 0.4;
        
        for (const edge of currentEdges) {
            const source = currentNodes[edge.source];
            const target = currentNodes[edge.target];
            if (source && target) {
                compareCtx.beginPath();
                compareCtx.moveTo(source.x, source.y);
                compareCtx.lineTo(target.x, target.y);
                compareCtx.stroke();
            }
        }
        
        compareCtx.globalAlpha = 1;
        
        // Nodes
        for (const node of currentNodes) {
            const isHovered = hoveredNode === node;
            const isSelected = selectedNodeCompare && selectedNodeCompare.id === node.id;
            
            compareCtx.beginPath();
            compareCtx.arc(node.x, node.y, node.size, 0, 2 * Math.PI);
            compareCtx.fillStyle = node.color;
            compareCtx.fill();
            
            if (isHovered || isSelected) {
                compareCtx.lineWidth = 2.5 / compareTransform.k;
                compareCtx.strokeStyle = '#000000';
                compareCtx.stroke();
                
                compareCtx.shadowColor = 'rgba(0,0,0,0.2)';
                compareCtx.shadowBlur = 10;
                compareCtx.fill();
                compareCtx.shadowBlur = 0;
            } else {
                 compareCtx.lineWidth = 1.2 / compareTransform.k;
                 compareCtx.strokeStyle = 'rgba(255,255,255,0.9)';
                 compareCtx.stroke();
            }
        }
        
        compareCtx.restore();
    }
    
    function updateComparisonStats() {
        const activeCountries = selectedCountries.filter(c => c !== null);
        const container = document.getElementById('comparison-stats-container');
        
        if (activeCountries.length === 0) {
            container.innerHTML = '';
            return;
        }
        
        let html = '<div class="comparison-stats">';
        
        activeCountries.forEach((country, idx) => {
            const countryNodes = allNodes.filter(n => n.country === country);
            const totalInst = countryNodes.length;
            const totalCollab = countryNodes.reduce((sum, n) => sum + n.strength, 0);
            
            html += `
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <div style="width: 12px; height: 12px; border-radius: 50%; background: ${COMPARE_COLORS[idx]};"></div>
                        <strong style="font-size: 14px;">${country}</strong>
                    </div>
                    <div class="comparison-stat-row">
                        <span class="comparison-stat-label">Institutions</span>
                        <span class="comparison-stat-value">${totalInst.toLocaleString()}</span>
                    </div>
                    <div class="comparison-stat-row">
                        <span class="comparison-stat-label">Collaborations</span>
                        <span class="comparison-stat-value">${totalCollab.toLocaleString()}</span>
                    </div>
                </div>
            `;
        });
        
        // Cross-country collaborations
        if (activeCountries.length > 1) {
            let crossCount = 0;
            for (const edge of allEdges) {
                const sourceNode = allNodes[edge.source];
                const targetNode = allNodes[edge.target];
                if (sourceNode && targetNode && 
                    activeCountries.includes(sourceNode.country) && 
                    activeCountries.includes(targetNode.country) &&
                    sourceNode.country !== targetNode.country) {
                    crossCount += edge.weight;
                }
            }
            
            html += `
                <div style="border-top: 1px solid rgba(0,0,0,0.1); padding-top: 12px;">
                    <div class="comparison-stat-row">
                        <span class="comparison-stat-label">Cross-Country Links</span>
                        <span class="comparison-stat-value" style="color: #ff9f0a;">${crossCount.toLocaleString()}</span>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    // Node Selection Function
    function selectNode(node, viewType = 'network') {
        if (viewType === 'network') {
            selectedNodeNetwork = node;
            selectedNodeCompare = null;
            
            const info = document.getElementById('node-info');
            info.dataset.id = node.id;
            
            document.getElementById('info-name').textContent = node.name;
            document.getElementById('info-country').textContent = node.country;
            document.getElementById('info-collabs').textContent = node.strength.toLocaleString();
            document.getElementById('info-degree').textContent = node.degree;
            
            info.classList.add('visible');
        } else if (viewType === 'compare') {
            selectedNodeCompare = node;
            selectedNodeNetwork = null;
            
            const info = document.getElementById('node-info');
            info.dataset.id = node.id;
            
            document.getElementById('info-name').textContent = node.name;
            document.getElementById('info-country').textContent = node.country;
            document.getElementById('info-collabs').textContent = node.strength.toLocaleString();
            document.getElementById('info-degree').textContent = node.degree;
            
            info.classList.add('visible');
        }
        
        // Render the appropriate view
        if (currentView === 'network') {
            render();
        } else if (currentView === 'compare') {
            renderComparison();
        }
    }
    
    // Country Selection UI
    document.querySelectorAll('.country-slot').forEach(slot => {
        slot.addEventListener('click', (e) => {
            if (e.target.classList.contains('country-slot-remove')) {
                return; // Handle remove separately
            }
            
            const slotIndex = parseInt(slot.dataset.slot);
            activeSlot = slotIndex;
            
            countryPicker.classList.toggle('active');
            
            // Position picker below slot
            const rect = slot.getBoundingClientRect();
            countryPicker.style.position = 'absolute';
            countryPicker.style.top = (slot.offsetTop + slot.offsetHeight + 4) + 'px';
            countryPicker.style.left = slot.offsetLeft + 'px';
            countryPicker.style.width = slot.offsetWidth + 'px';
        });
    });
    
    function selectCountryForSlot(country) {
        if (activeSlot === null) return;
        
        // Check if already selected
        if (selectedCountries.includes(country)) {
            alert('Country already selected!');
            return;
        }
        
        selectedCountries[activeSlot] = country;
        updateCountrySlot(activeSlot, country);
        
        countryPicker.classList.remove('active');
        activeSlot = null;
        
        updateComparison();
    }
    
    function updateCountrySlot(slotIndex, country) {
        const slot = document.querySelector(`.country-slot[data-slot="${slotIndex}"]`);
        
        if (country) {
            slot.classList.add('filled');
            slot.innerHTML = `
                <div class="country-slot-content">
                    <div>
                        <div style="width: 12px; height: 12px; border-radius: 50%; background: ${COMPARE_COLORS[slotIndex]}; margin-bottom: 4px;"></div>
                        <div class="country-slot-name">${country}</div>
                    </div>
                    <button class="country-slot-remove" onclick="removeCountry(${slotIndex})">×</button>
                </div>
            `;
        } else {
            slot.classList.remove('filled');
            slot.innerHTML = `<div class="country-slot-label">Click to select country ${slotIndex + 1}</div>`;
        }
    }
    
    window.removeCountry = function(slotIndex) {
        selectedCountries[slotIndex] = null;
        updateCountrySlot(slotIndex, null);
        updateComparison();
    };
    
    // Close picker when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.country-slot') && !e.target.closest('.country-picker')) {
            countryPicker.classList.remove('active');
        }
    });
    
    // UI Helpers
    const tooltip = document.getElementById('tooltip');
    
    function showTooltip(node, event) {
        tooltip.innerHTML = '<h4>' + node.name + '</h4><p>' + node.country + '</p>';
        tooltip.style.left = (event.clientX + 16) + 'px';
        tooltip.style.top = (event.clientY - 16) + 'px';
        tooltip.style.opacity = 1;
    }
    
    function hideTooltip() {
        tooltip.style.opacity = 0;
    }
    
    // Table Logic
    let sortColumn = 'strength';
    let sortAsc = false;
    let compareSortColumn = 'strength';
    let compareSortAsc = false;
    
    function updateTable(nodes) {
        const sorted = [...nodes].sort((a, b) => {
            const av = a[sortColumn], bv = b[sortColumn];
            if (typeof av === 'string') return sortAsc ? av.localeCompare(bv) : bv.localeCompare(av);
            return sortAsc ? av - bv : bv - av;
        });
        
        const tbody = document.querySelector('#institutions-table tbody');
        tbody.innerHTML = sorted.slice(0, 100).map((n, i) => 
            '<tr data-idx="' + i + '"><td title="' + n.name + '">' + n.name + '</td><td>' + n.country + '</td><td>' + n.strength.toLocaleString() + '</td></tr>'
        ).join('');
        
        const sortedRef = sorted.slice(0, 100);
        tbody.querySelectorAll('tr').forEach((row, i) => {
            row.onclick = () => {
                const node = currentNodes.find(n => n.id === sortedRef[i].id);
                if (node) selectNode(node, 'network');
            };
        });
    }
    
    function updateCompareTableOnly(nodes) {
        const sorted = [...nodes].sort((a, b) => {
            const av = a[compareSortColumn], bv = b[compareSortColumn];
            if (typeof av === 'string') return compareSortAsc ? av.localeCompare(bv) : bv.localeCompare(av);
            return compareSortAsc ? av - bv : bv - av;
        });
        
        const tbody = document.querySelector('#compare-institutions-table tbody');
        tbody.innerHTML = sorted.slice(0, 100).map((n, i) => 
            '<tr data-idx="' + i + '"><td title="' + n.name + '">' + n.name + '</td><td>' + n.country + '</td><td>' + n.strength.toLocaleString() + '</td></tr>'
        ).join('');
        
        const sortedRef = sorted.slice(0, 100);
        tbody.querySelectorAll('tr').forEach((row, i) => {
            row.onclick = () => {
                const node = currentNodes.find(n => n.id === sortedRef[i].id);
                if (node) selectNode(node, 'compare');
            };
        });
    }
    
    document.querySelectorAll('#institutions-table th').forEach(th => {
        th.onclick = () => {
            const col = th.dataset.sort;
            if (sortColumn === col) sortAsc = !sortAsc;
            else { sortColumn = col; sortAsc = false; }
            applyFilters();
        };
    });
    
    document.querySelectorAll('#compare-institutions-table th').forEach(th => {
        th.onclick = () => {
            const col = th.dataset.sort;
            if (compareSortColumn === col) compareSortAsc = !compareSortAsc;
            else { compareSortColumn = col; compareSortAsc = false; }
            const activeCountries = selectedCountries.filter(c => c !== null);
            if (activeCountries.length > 0) {
                const filtered = allNodes.filter(n => activeCountries.includes(n.country));
                updateCompareTableOnly(filtered);
            }
        };
    });
    
    // Geo Map
    let map = null;
    function initMap() {
        if (map) return;
        map = L.map('map-container').setView([20, 0], 2);
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            maxZoom: 19
        }).addTo(map);
        
        updateMap();
    }
    
    function updateMap() {
        if (!map) return;
        map.eachLayer(l => { 
            if (l instanceof L.CircleMarker || l instanceof L.Polyline) map.removeLayer(l); 
        });
        
        const countryNodes = DATA.countryNodes;
        const countryEdges = DATA.countryEdges;
        
        const maxWeight = Math.max(...countryEdges.map(e => e.weight), 1);
        countryEdges.forEach(e => {
            const src = countryNodes.find(n => n.country === e.source);
            const tgt = countryNodes.find(n => n.country === e.target);
            if (src && tgt) {
                L.polyline([[src.lat, src.lon], [tgt.lat, tgt.lon]], {
                    color: '#0071e3',
                    weight: Math.max(1, 3 * e.weight / maxWeight),
                    opacity: 0.3
                }).addTo(map);
            }
        });
        
        countryNodes.forEach(n => {
            L.circleMarker([n.lat, n.lon], {
                radius: 4 + Math.sqrt(n.inst_count),
                fillColor: '#0071e3',
                color: '#fff',
                weight: 1.5,
                fillOpacity: 0.8
            }).bindPopup('<strong>' + n.country + '</strong><br>' + n.inst_count + ' institutions').addTo(map);
        });
    }
    
    // View Switcher
    document.querySelectorAll('.segment-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Stop any running simulation before switching views
            if (simulation) {
                simulation.stop();
                simulation = null;
            }
            
            // Clear node info panel when switching views
            document.getElementById('node-info').classList.remove('visible');
            selectedNodeNetwork = null;
            selectedNodeCompare = null;
            hoveredNode = null;
            
            currentView = btn.dataset.view;
            
            document.getElementById('network-container').style.display = currentView === 'network' ? 'block' : 'none';
            document.getElementById('map-container').style.display = currentView === 'map' ? 'block' : 'none';
            document.getElementById('compare-container').style.display = currentView === 'compare' ? 'block' : 'none';
            
            document.getElementById('normal-controls').style.display = currentView === 'compare' ? 'none' : 'block';
            document.getElementById('compare-controls').style.display = currentView === 'compare' ? 'block' : 'none';
            
            // Show/hide appropriate tables
            const networkTableHeader = document.querySelector('#network-table-wrapper').previousElementSibling;
            const compareTableHeader = document.getElementById('compare-table-header');
            
            if (currentView === 'compare') {
                networkTableHeader.style.display = 'none';
                document.getElementById('network-table-wrapper').style.display = 'none';
                compareTableHeader.style.display = 'block';
                document.getElementById('compare-table-wrapper').style.display = 'block';
            } else {
                networkTableHeader.style.display = 'block';
                document.getElementById('network-table-wrapper').style.display = 'block';
                compareTableHeader.style.display = 'none';
                document.getElementById('compare-table-wrapper').style.display = 'none';
            }
            
            if (currentView === 'map') {
                initMap();
                setTimeout(() => map.invalidateSize(), 150);
            } else if (currentView === 'compare') {
                initCompare();
                updateComparison();
            } else if (currentView === 'network') {
                // Re-apply filters when returning to network view
                applyFilters();
            }
            
            updateTopBar();
        };
    });
    
    // Debounce Inputs
    let filterTimeout;
    function debounceFilter() {
        clearTimeout(filterTimeout);
        filterTimeout = setTimeout(applyFilters, 150);
    }
    
    document.getElementById('collab-filter').oninput = function() {
        filters.minCollab = parseInt(this.value);
        document.getElementById('collab-value').textContent = this.value;
        debounceFilter();
    };
    
    document.getElementById('degree-filter').oninput = function() {
        filters.minDegree = parseInt(this.value);
        document.getElementById('degree-value').textContent = this.value;
        debounceFilter();
    };
    
    document.getElementById('topn-filter').oninput = function() {
        filters.topN = parseInt(this.value);
        document.getElementById('topn-value').textContent = this.value >= allNodes.length ? 'All' : this.value.toLocaleString();
        debounceFilter();
    };
    
    document.getElementById('country-filter').onchange = function() {
        filters.country = this.value;
        applyFilters();
    };
    
    document.getElementById('search-input').oninput = function() {
        filters.search = this.value;
        debounceFilter();
    };
    
    // Comparison Filter Handlers
    let compareFilterTimeout;
    function debounceCompareFilter() {
        clearTimeout(compareFilterTimeout);
        compareFilterTimeout = setTimeout(updateComparison, 150);
    }
    
    document.getElementById('compare-collab-filter').oninput = function() {
        compareFilters.minCollab = parseInt(this.value);
        document.getElementById('compare-collab-value').textContent = this.value;
        debounceCompareFilter();
    };
    
    document.getElementById('compare-degree-filter').oninput = function() {
        compareFilters.minDegree = parseInt(this.value);
        document.getElementById('compare-degree-value').textContent = this.value;
        debounceCompareFilter();
    };
    
    document.getElementById('compare-topn-filter').oninput = function() {
        compareFilters.topN = parseInt(this.value);
        document.getElementById('compare-topn-value').textContent = this.value >= allNodes.length ? 'All' : this.value.toLocaleString();
        debounceCompareFilter();
    };
    
    // Initialize comparison filter ranges
    document.getElementById('compare-collab-filter').max = Math.min(maxCollab, 1000);
    document.getElementById('compare-degree-filter').max = Math.min(maxDegree, 200);
    document.getElementById('compare-topn-filter').max = allNodes.length;
    document.getElementById('compare-topn-filter').value = Math.min(5000, allNodes.length);
    
    window.addEventListener('resize', () => {
        if (currentView === 'network') {
            const container = document.getElementById('network-container');
            const width = container.clientWidth;
            const height = container.clientHeight;
            canvas.width = width * window.devicePixelRatio;
            canvas.height = height * window.devicePixelRatio;
            canvas.style.width = width + 'px';
            canvas.style.height = height + 'px';
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
            render();
        } else if (currentView === 'compare' && compareCanvas) {
            const container = document.getElementById('compare-container');
            const width = container.clientWidth;
            const height = container.clientHeight;
            compareCanvas.width = width * window.devicePixelRatio;
            compareCanvas.height = height * window.devicePixelRatio;
            compareCanvas.style.width = width + 'px';
            compareCanvas.style.height = height + 'px';
            compareCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
            renderComparison();
        }
    });

    // Start
    initNetwork();'''