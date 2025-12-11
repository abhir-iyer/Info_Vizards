import pandas as pd
import json

# Read the CSV file
df = pd.read_csv('country_collaborations.csv')

# Hardcoded ISO-2 to ISO-3 mapping and country names
iso2_to_iso3 = {
    'US': 'USA', 'CN': 'CHN', 'GB': 'GBR', 'CA': 'CAN', 'DE': 'DEU', 'AU': 'AUS',
    'IT': 'ITA', 'FR': 'FRA', 'KR': 'KOR', 'JP': 'JPN', 'NL': 'NLD', 'ES': 'ESP',
    'IN': 'IND', 'CH': 'CHE', 'BR': 'BRA', 'SE': 'SWE', 'AT': 'AUT', 'BE': 'BEL',
    'DK': 'DNK', 'FI': 'FIN', 'GR': 'GRC', 'IE': 'IRL', 'IL': 'ISR', 'NO': 'NOR',
    'NZ': 'NZL', 'PL': 'POL', 'PT': 'PRT', 'RU': 'RUS', 'SG': 'SGP', 'ZA': 'ZAF',
    'TR': 'TUR', 'MX': 'MEX', 'AR': 'ARG', 'CL': 'CHL', 'CO': 'COL', 'CZ': 'CZE',
    'HU': 'HUN', 'TH': 'THA', 'MY': 'MYS', 'PH': 'PHL', 'ID': 'IDN', 'VN': 'VNM',
    'PK': 'PAK', 'BD': 'BGD', 'EG': 'EGY', 'SA': 'SAU', 'AE': 'ARE', 'NG': 'NGA',
    'KE': 'KEN', 'GH': 'GHA', 'TW': 'TWN', 'HK': 'HKG', 'UA': 'UKR', 'RO': 'ROU',
    'HR': 'HRV', 'SI': 'SVN', 'SK': 'SVK', 'BG': 'BGR', 'RS': 'SRB', 'LT': 'LTU',
    'LV': 'LVA', 'EE': 'EST', 'IS': 'ISL', 'LU': 'LUX', 'MT': 'MLT', 'CY': 'CYP'
}

iso3_to_iso2 = {v: k for k, v in iso2_to_iso3.items()}

iso2_to_name = {
    'US': 'United States', 'CN': 'China', 'GB': 'United Kingdom', 'CA': 'Canada',
    'DE': 'Germany', 'AU': 'Australia', 'IT': 'Italy', 'FR': 'France',
    'KR': 'South Korea', 'JP': 'Japan', 'NL': 'Netherlands', 'ES': 'Spain',
    'IN': 'India', 'CH': 'Switzerland', 'BR': 'Brazil', 'SE': 'Sweden',
    'AT': 'Austria', 'BE': 'Belgium', 'DK': 'Denmark', 'FI': 'Finland',
    'GR': 'Greece', 'IE': 'Ireland', 'IL': 'Israel', 'NO': 'Norway',
    'NZ': 'New Zealand', 'PL': 'Poland', 'PT': 'Portugal', 'RU': 'Russia',
    'SG': 'Singapore', 'ZA': 'South Africa', 'TR': 'Turkey', 'MX': 'Mexico',
    'AR': 'Argentina', 'CL': 'Chile', 'CO': 'Colombia', 'CZ': 'Czech Republic',
    'HU': 'Hungary', 'TH': 'Thailand', 'MY': 'Malaysia', 'PH': 'Philippines',
    'ID': 'Indonesia', 'VN': 'Vietnam', 'PK': 'Pakistan', 'BD': 'Bangladesh',
    'EG': 'Egypt', 'SA': 'Saudi Arabia', 'AE': 'UAE', 'NG': 'Nigeria',
    'KE': 'Kenya', 'GH': 'Ghana', 'TW': 'Taiwan', 'HK': 'Hong Kong',
    'UA': 'Ukraine', 'RO': 'Romania', 'HR': 'Croatia', 'SI': 'Slovenia',
    'SK': 'Slovakia', 'BG': 'Bulgaria', 'RS': 'Serbia', 'LT': 'Lithuania',
    'LV': 'Latvia', 'EE': 'Estonia', 'IS': 'Iceland', 'LU': 'Luxembourg',
    'MT': 'Malta', 'CY': 'Cyprus'
}

# Build collaboration data structure for JavaScript
collaborations = {}
for _, row in df.iterrows():
    c1, c2 = row['country_1'], row['country_2']
    count = int(row['collaboration_count'])
    
    if c1 not in collaborations:
        collaborations[c1] = {}
    if c2 not in collaborations:
        collaborations[c2] = {}
    
    collaborations[c1][c2] = count
    collaborations[c2][c1] = count

# Aggregate collaboration counts by country
country_counts = {}
for _, row in df.iterrows():
    country_1 = row['country_1']
    country_2 = row['country_2']
    count = int(row['collaboration_count'])
    
    country_counts[country_1] = country_counts.get(country_1, 0) + count
    country_counts[country_2] = country_counts.get(country_2, 0) + count

# Prepare data for choropleth
choropleth_data = []
for code, count in country_counts.items():
    if code in iso2_to_iso3:
        choropleth_data.append({
            'iso3': iso2_to_iso3[code],
            'iso2': code,
            'name': iso2_to_name.get(code, code),
            'count': count
        })

# Create the HTML with Apple Light Theme
html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Global Research Collaborations</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --apple-bg: #ffffff;
            --apple-bg-secondary: #f5f5f7;
            --apple-surface: #ffffff;
            --apple-surface-secondary: #f5f5f7;
            --apple-text-primary: #1d1d1f;
            --apple-text-secondary: #86868b;
            --apple-text-tertiary: #6e6e73;
            --apple-accent: #0071e3;
            --apple-accent-hover: #0077ed;
            --apple-blue: #007aff;
            --apple-purple: #af52de;
            --apple-pink: #ff2d55;
            --apple-orange: #ff9500;
            --apple-green: #34c759;
            --apple-teal: #5ac8fa;
            --apple-border: rgba(0, 0, 0, 0.06);
            --apple-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            --apple-shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.12);
            --apple-radius: 20px;
            --apple-radius-sm: 12px;
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
            background: var(--apple-bg-secondary);
            min-height: 100vh;
            color: var(--apple-text-primary);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            letter-spacing: -0.01em;
        }
        
        .container {
            max-width: 2200px;
            margin: 0 auto;
            padding: 40px 60px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 48px;
        }
        
        h1 {
            font-size: 56px;
            font-weight: 700;
            letter-spacing: -0.04em;
            line-height: 1.07;
            color: var(--apple-text-primary);
            margin-bottom: 12px;
        }
        
        .subtitle {
            font-size: 21px;
            font-weight: 400;
            color: var(--apple-text-secondary);
            letter-spacing: -0.01em;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 420px;
            gap: 24px;
        }
        
        .card {
            background: var(--apple-surface);
            border-radius: var(--apple-radius);
            box-shadow: var(--apple-shadow);
            overflow: hidden;
            transition: transform 0.3s cubic-bezier(0.25, 0.1, 0.25, 1), 
                        box-shadow 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: var(--apple-shadow-hover);
        }
        
        .map-container {
            padding: 24px;
        }
        
        #choropleth-map {
            width: 100%;
            height: 1000px;
            border-radius: var(--apple-radius-sm);
        }
        
        .network-panel {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .network-card {
            flex: 1;
        }
        
        .network-header {
            padding: 24px 28px 20px;
            border-bottom: 1px solid var(--apple-border);
        }
        
        .network-title {
            font-size: 24px;
            font-weight: 600;
            color: var(--apple-text-primary);
            letter-spacing: -0.02em;
        }
        
        .network-subtitle {
            font-size: 15px;
            color: var(--apple-text-secondary);
            margin-top: 4px;
            font-weight: 400;
        }
        
        .network-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 380px;
            color: var(--apple-text-tertiary);
            text-align: center;
            padding: 40px;
        }
        
        .placeholder-icon {
            width: 56px;
            height: 56px;
            margin-bottom: 16px;
            opacity: 0.4;
            stroke-width: 1;
        }
        
        .placeholder-text {
            font-size: 17px;
            font-weight: 600;
            color: var(--apple-text-secondary);
            margin-bottom: 6px;
        }
        
        .placeholder-hint {
            font-size: 14px;
            color: var(--apple-text-tertiary);
            font-weight: 400;
        }
        
        #network-svg {
            width: 100%;
            height: 380px;
        }
        
        .node circle {
            transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1);
            cursor: pointer;
        }
        
        .node:hover circle {
            filter: brightness(1.1);
            transform: scale(1.05);
        }
        
        .node.center circle {
            filter: drop-shadow(0 4px 12px rgba(0, 122, 255, 0.3));
        }
        
        .node text {
            font-family: 'Inter', -apple-system, sans-serif;
            font-size: 11px;
            font-weight: 600;
            fill: #ffffff;
            pointer-events: none;
            letter-spacing: 0.01em;
        }
        
        .link {
            fill: none;
            stroke-linecap: round;
        }
        
        .stats-card {
            padding: 0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr;
        }
        
        .stat-item {
            padding: 18px 28px;
            border-bottom: 1px solid var(--apple-border);
            transition: background 0.2s ease;
        }
        
        .stat-item:last-child {
            border-bottom: none;
        }
        
        .stat-item:hover {
            background: var(--apple-surface-secondary);
        }
        
        .stat-label {
            font-size: 13px;
            font-weight: 500;
            color: var(--apple-text-secondary);
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .stat-icon {
            width: 16px;
            height: 16px;
            opacity: 0.6;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: var(--apple-text-primary);
            letter-spacing: -0.03em;
        }
        
        .stat-value.accent {
            color: var(--apple-blue);
        }
        
        .legend-card {
            padding: 20px 28px;
        }
        
        .legend-title {
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--apple-text-tertiary);
            margin-bottom: 14px;
        }
        
        .legend-gradient {
            height: 8px;
            border-radius: 4px;
            background: linear-gradient(90deg, 
                #34c759 0%, 
                #5ac8fa 33%,
                #af52de 66%, 
                #ff2d55 100%
            );
        }
        
        .legend-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 12px;
            font-weight: 500;
            color: var(--apple-text-tertiary);
        }
        
        .tooltip {
            position: absolute;
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            color: var(--apple-text-primary);
            padding: 16px 20px;
            border-radius: var(--apple-radius-sm);
            font-size: 14px;
            pointer-events: none;
            z-index: 1000;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
            border: 1px solid var(--apple-border);
            display: none;
            max-width: 280px;
        }
        
        .tooltip-title {
            font-size: 17px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--apple-text-primary);
        }
        
        .tooltip-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--apple-blue);
            letter-spacing: -0.03em;
        }
        
        .tooltip-label {
            font-size: 13px;
            color: var(--apple-text-secondary);
            margin-top: 2px;
            font-weight: 400;
        }
        
        @media (max-width: 1200px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .network-panel {
                flex-direction: row;
                flex-wrap: wrap;
            }
            
            .network-card {
                flex: 1 1 100%;
            }
            
            .stats-card, .legend-card {
                flex: 1 1 calc(50% - 8px);
            }
            
            .container {
                padding: 30px 40px;
            }
            
            h1 {
                font-size: 44px;
            }
        }
        
        @media (max-width: 768px) {
            .network-panel {
                flex-direction: column;
            }
            
            .stats-card, .legend-card {
                flex: 1 1 100%;
            }
            
            h1 {
                font-size: 34px;
            }
            
            .container {
                padding: 20px;
            }
            
            .subtitle {
                font-size: 17px;
            }
        }

        /* Plotly overrides for Apple light style */
        .js-plotly-plot .plotly .modebar {
            right: 20px !important;
            top: 10px !important;
        }
        
        .js-plotly-plot .plotly .modebar-btn {
            color: var(--apple-text-tertiary) !important;
        }
        
        .js-plotly-plot .plotly .modebar-btn:hover {
            color: var(--apple-text-primary) !important;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Global Research Collaborations</h1>
            <p class="subtitle">Explore international research partnerships across countries</p>
        </header>
        
        <main class="main-content">
            <div class="card map-container">
                <div id="choropleth-map"></div>
            </div>
            
            <div class="network-panel">
                <div class="card network-card">
                    <div class="network-header">
                        <div class="network-title" id="network-title">Select a Country</div>
                        <div class="network-subtitle" id="network-subtitle">Click on the map to explore partnerships</div>
                    </div>
                    <div id="network-container">
                        <div class="network-placeholder">
                            <svg class="placeholder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <circle cx="12" cy="12" r="10"/>
                                <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                            </svg>
                            <div class="placeholder-text">No country selected</div>
                            <div class="placeholder-hint">Click any country on the map to view its collaboration network</div>
                        </div>
                    </div>
                </div>
                
                <div class="card stats-card" id="stats-panel" style="display: none;">
                    <div class="stats-grid" id="stats-content">
                    </div>
                </div>
                
                <div class="card legend-card" id="legend-panel" style="display: none;">
                    <div class="legend-title">Collaboration Intensity</div>
                    <div class="legend-gradient"></div>
                    <div class="legend-labels">
                        <span>Lower</span>
                        <span>Higher</span>
                    </div>
                </div>
            </div>
        </main>
    </div>
    
    <div class="tooltip" id="tooltip"></div>
    
    <script>
        // Data
        const choroplethData = ''' + json.dumps(choropleth_data) + ''';
        const collaborations = ''' + json.dumps(collaborations) + ''';
        const countryNames = ''' + json.dumps(iso2_to_name) + ''';
        const iso3ToIso2 = ''' + json.dumps(iso3_to_iso2) + ''';
        const countryCounts = ''' + json.dumps(country_counts) + ''';
        
        // Create choropleth map with Apple light colors
        const locations = choroplethData.map(d => d.iso3);
        const values = choroplethData.map(d => d.count);
        const hoverText = choroplethData.map(d => 
            '<b style="font-size:17px;">' + d.name + '</b><br>' +
            '<span style="font-size:28px;font-weight:700;color:#007aff;">' + d.count.toLocaleString() + '</span><br>' +
            '<span style="color:#86868b;font-size:13px;">collaborations</span>'
        );
        const customData = choroplethData.map(d => d.iso2);
        
        const mapData = [{
            type: 'choropleth',
            locations: locations,
            z: values,
            customdata: customData,
            text: hoverText,
            hovertemplate: '%{text}<extra></extra>',
            colorscale: [
                [0, '#f5f5f7'],
                [0.15, '#34c759'],
                [0.35, '#5ac8fa'],
                [0.55, '#007aff'],
                [0.75, '#af52de'],
                [1, '#ff2d55']
            ],
            showscale: false,
            marker: {
                line: {
                    color: '#ffffff',
                    width: 1
                }
            }
        }];
        
        const mapLayout = {
            geo: {
                showframe: false,
                showcoastlines: true,
                coastlinecolor: '#d2d2d7',
                showland: true,
                landcolor: '#f5f5f7',
                showocean: true,
                oceancolor: '#ffffff',
                showlakes: true,
                lakecolor: '#ffffff',
                showcountries: true,
                countrycolor: '#d2d2d7',
                projection: {
                    type: 'natural earth'
                },
                bgcolor: 'rgba(255,255,255,0)'
            },
            paper_bgcolor: 'rgba(255,255,255,0)',
            plot_bgcolor: 'rgba(255,255,255,0)',
            margin: { t: 0, b: 0, l: 0, r: 0 },
            hoverlabel: {
                bgcolor: 'rgba(255, 255, 255, 0.98)',
                bordercolor: 'rgba(0,0,0,0.06)',
                font: {
                    family: 'Inter, -apple-system, sans-serif',
                    size: 14,
                    color: '#1d1d1f'
                }
            }
        };
        
        const mapConfig = {
            displayModeBar: true,
            modeBarButtonsToRemove: ['select2d', 'lasso2d', 'toImage'],
            displaylogo: false,
            responsive: true
        };
        
        Plotly.newPlot('choropleth-map', mapData, mapLayout, mapConfig);
        
        // Handle map clicks
        document.getElementById('choropleth-map').on('plotly_click', function(data) {
            if (data.points && data.points.length > 0) {
                const iso3 = data.points[0].location;
                const iso2 = iso3ToIso2[iso3];
                if (iso2 && collaborations[iso2]) {
                    drawNetwork(iso2);
                }
            }
        });
        
        // Draw network visualization
        function drawNetwork(centerCountry) {
            const container = document.getElementById('network-container');
            const title = document.getElementById('network-title');
            const subtitle = document.getElementById('network-subtitle');
            const statsPanel = document.getElementById('stats-panel');
            const statsContent = document.getElementById('stats-content');
            const legendPanel = document.getElementById('legend-panel');
            const countryName = countryNames[centerCountry] || centerCountry;
            
            title.textContent = countryName;
            subtitle.textContent = 'Top research partnerships';
            
            container.innerHTML = '<svg id="network-svg"></svg>';
            const svg = d3.select('#network-svg');
            
            const rect = container.getBoundingClientRect();
            const width = rect.width || 380;
            const height = 380;
            
            svg.attr('width', width).attr('height', height);
            
            const collabs = collaborations[centerCountry] || {};
            const sortedCollabs = Object.entries(collabs)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10);
            
            if (sortedCollabs.length === 0) {
                container.innerHTML = '<div class="network-placeholder"><div class="placeholder-text">No data available</div></div>';
                statsPanel.style.display = 'none';
                legendPanel.style.display = 'none';
                return;
            }
            
            // Show panels
            statsPanel.style.display = 'block';
            legendPanel.style.display = 'block';
            
            // Calculate statistics
            const totalCollabs = Object.values(collabs).reduce((a, b) => a + b, 0);
            const numPartners = Object.keys(collabs).length;
            const topPartner = sortedCollabs[0];
            
            statsContent.innerHTML = `
                <div class="stat-item">
                    <div class="stat-label">
                        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                            <circle cx="9" cy="7" r="4"/>
                            <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
                        </svg>
                        Total Collaborations
                    </div>
                    <div class="stat-value accent">${totalCollabs.toLocaleString()}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">
                        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                        </svg>
                        Partner Countries
                    </div>
                    <div class="stat-value">${numPartners}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">
                        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                        </svg>
                        Top Partner
                    </div>
                    <div class="stat-value">${countryNames[topPartner[0]] || topPartner[0]}</div>
                </div>
            `;
            
            // Build nodes and links
            const nodes = [{
                id: centerCountry,
                name: countryName,
                isCenter: true,
                total: totalCollabs
            }];
            
            const links = [];
            const maxWeight = Math.max(...sortedCollabs.map(c => c[1]));
            const minWeight = Math.min(...sortedCollabs.map(c => c[1]));
            
            sortedCollabs.forEach(function(item) {
                const country = item[0];
                const weight = item[1];
                nodes.push({
                    id: country,
                    name: countryNames[country] || country,
                    isCenter: false,
                    total: countryCounts[country] || weight,
                    weight: weight
                });
                links.push({
                    source: centerCountry,
                    target: country,
                    weight: weight
                });
            });
            
            // Apple light color scale for edges
            const colorScale = d3.scaleLinear()
                .domain([minWeight, (minWeight + maxWeight) / 2, maxWeight])
                .range(['#34c759', '#5ac8fa', '#ff2d55']);
            
            const widthScale = d3.scaleLinear()
                .domain([minWeight, maxWeight])
                .range([2, 6]);
            
            const nodeScale = d3.scaleSqrt()
                .domain([0, Math.max(...nodes.map(n => n.total))])
                .range([14, 32]);
            
            // Create force simulation
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(90))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(d => nodeScale(d.total) + 10));
            
            // Add subtle shadow filter
            const defs = svg.append('defs');
            
            const shadowFilter = defs.append('filter')
                .attr('id', 'shadow')
                .attr('x', '-50%')
                .attr('y', '-50%')
                .attr('width', '200%')
                .attr('height', '200%');
            
            shadowFilter.append('feDropShadow')
                .attr('dx', '0')
                .attr('dy', '2')
                .attr('stdDeviation', '4')
                .attr('flood-color', 'rgba(0, 122, 255, 0.25)');
            
            // Draw links
            const link = svg.append('g')
                .selectAll('line')
                .data(links)
                .enter()
                .append('line')
                .attr('class', 'link')
                .attr('stroke', d => colorScale(d.weight))
                .attr('stroke-width', d => widthScale(d.weight))
                .attr('stroke-opacity', 0.7);
            
            // Draw nodes
            const node = svg.append('g')
                .selectAll('.node')
                .data(nodes)
                .enter()
                .append('g')
                .attr('class', d => d.isCenter ? 'node center' : 'node')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            node.append('circle')
                .attr('r', d => nodeScale(d.total))
                .attr('fill', d => d.isCenter ? '#007aff' : '#af52de')
                .attr('stroke', '#ffffff')
                .attr('stroke-width', 3)
                .style('filter', d => d.isCenter ? 'url(#shadow)' : 'none');
            
            node.append('text')
                .attr('dy', 4)
                .attr('text-anchor', 'middle')
                .text(d => d.id)
                .style('font-size', d => d.isCenter ? '12px' : '10px');
            
            // Tooltip
            const tooltip = d3.select('#tooltip');
            
            node.on('mouseover', function(event, d) {
                let html;
                if (d.isCenter) {
                    html = `
                        <div class="tooltip-title">${d.name}</div>
                        <div class="tooltip-value">${d.total.toLocaleString()}</div>
                        <div class="tooltip-label">total collaborations</div>
                    `;
                } else {
                    html = `
                        <div class="tooltip-title">${d.name}</div>
                        <div class="tooltip-value">${d.weight.toLocaleString()}</div>
                        <div class="tooltip-label">collaborations with ${countryName}</div>
                    `;
                }
                tooltip.style('display', 'block').html(html);
            })
            .on('mousemove', function(event) {
                tooltip.style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', function() {
                tooltip.style('display', 'none');
            })
            .on('click', function(event, d) {
                if (!d.isCenter && collaborations[d.id]) {
                    drawNetwork(d.id);
                }
            });
            
            link.on('mouseover', function(event, d) {
                const sourceName = countryNames[d.source.id] || d.source.id;
                const targetName = countryNames[d.target.id] || d.target.id;
                tooltip.style('display', 'block')
                    .html(`
                        <div class="tooltip-title">${sourceName} ↔ ${targetName}</div>
                        <div class="tooltip-value">${d.weight.toLocaleString()}</div>
                        <div class="tooltip-label">collaborations</div>
                    `);
            })
            .on('mousemove', function(event) {
                tooltip.style('left', (event.pageX + 15) + 'px')
                    .style('top', (event.pageY - 10) + 'px');
            })
            .on('mouseout', function() {
                tooltip.style('display', 'none');
            });
            
            simulation.on('tick', function() {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
            });
            
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        }
    </script>
</body>
</html>
'''

# Save to HTML with UTF-8 encoding
with open('country_collaborations_apple.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Apple white theme interactive map saved to country_collaborations_apple.html")