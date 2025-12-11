let charts = {};

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('authorSearch').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    document.getElementById('countryFilter').addEventListener('change', loadStatistics);
}

async function initializeDashboard() {
    try {
        await loadFilters();
        await loadStatistics();
        
        document.getElementById('loadingOverlay').style.display = 'none';
        document.getElementById('mainContainer').style.display = 'block';
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        document.getElementById('loadingOverlay').innerHTML = `
            <div class="loading-text" style="color: #ff3b30;">Error loading data. Please refresh the page.</div>
        `;
    }
}

async function loadFilters() {
    const response = await fetch('/api/filters');
    const data = await response.json();
    
    if (data.error) {
        console.error('Error loading filters:', data.error);
        return;
    }
    
    const countrySelect = document.getElementById('countryFilter');
    countrySelect.innerHTML = '<option value="">All Countries</option>' +
        data.countries.map(c => `<option value="${c.code}">${c.name}</option>`).join('');
}

async function loadStatistics() {
    const country = document.getElementById('countryFilter').value;
    
    const params = new URLSearchParams();
    if (country) params.append('country', country);
    
    const response = await fetch(`/api/statistics?${params}`);
    const data = await response.json();
    
    if (data.error) {
        console.error('Error loading statistics:', data.error);
        return;
    }
    
    renderDashboard(data);
}

function renderDashboard(data) {
    const { summary, top_countries, all_countries, top_authors, year_distribution, strength_distribution, has_country_filter } = data;
    
    // Destroy existing charts
    Object.values(charts).forEach(chart => chart.destroy());
    charts = {};
    
    // Build charts section HTML conditionally
    let chartsHTML = `
        <div class="charts-section">
            <div class="chart-card full-width">
                <div class="chart-title">Authors by Publication Year</div>
                <div class="chart-container tall">
                    <canvas id="yearChart"></canvas>
                </div>
            </div>
    `;
    
    // Only show country charts if no country filter is applied
    if (!has_country_filter) {
        chartsHTML += `
            <div class="chart-card">
                <div class="chart-title">Top 10 Countries</div>
                <div class="chart-container">
                    <canvas id="countryChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <div class="chart-title">Country Distribution</div>
                <div class="chart-container">
                    <canvas id="countryDonutChart"></canvas>
                </div>
            </div>
        `;
    }
    
    chartsHTML += `
            <div class="chart-card">
                <div class="chart-title">Top 10 Most Collaborative Authors</div>
                <div class="chart-container">
                    <canvas id="authorsChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <div class="chart-title">Collaboration Strength Distribution</div>
                <div class="chart-container">
                    <canvas id="strengthChart"></canvas>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('content').innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Authors</div>
                <div class="stat-value">${summary.total_authors.toLocaleString()}</div>
                <div class="stat-description">in dataset</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Collaborations</div>
                <div class="stat-value">${summary.total_collaborations.toLocaleString()}</div>
                <div class="stat-description">total instances</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Avg per Author</div>
                <div class="stat-value">${summary.avg_collaborations}</div>
                <div class="stat-description">collaborations</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Unique Connections</div>
                <div class="stat-value">${summary.unique_connections.toLocaleString()}</div>
                <div class="stat-description">author pairs</div>
            </div>
        </div>

        ${chartsHTML}

        <div class="top-list-card">
            <div class="section-title">Most Collaborative Authors</div>
            ${top_authors.map((a, i) => `
                <div class="list-item" onclick="searchAuthorById('${a.id}')">
                    <div class="list-rank">#${i + 1}</div>
                    <div class="list-content">
                        <div class="list-name">${a.name}</div>
                        <div class="list-meta">Click to view details</div>
                    </div>
                    <div class="list-count">${a.count}</div>
                </div>
            `).join('')}
        </div>
    `;
    
    createYearChart(year_distribution);
    
    // Only create country charts if data is available
    if (!has_country_filter) {
        createCountryChart(top_countries);
        createCountryDonutChart(all_countries);
    }
    
    createAuthorsChart(top_authors);
    createStrengthChart(strength_distribution);
}

function createYearChart(data) {
    const ctx = document.getElementById('yearChart').getContext('2d');
    charts.year = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.year),
            datasets: [{
                label: 'Number of Authors',
                data: data.map(d => d.count),
                borderColor: '#007aff',
                backgroundColor: 'rgba(0, 122, 255, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#007aff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1d1d1f',
                    bodyColor: '#1d1d1f',
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}

function createCountryChart(data) {
    const ctx = document.getElementById('countryChart').getContext('2d');
    charts.country = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.country),
            datasets: [{
                label: 'Authors',
                data: data.map(d => d.count),
                backgroundColor: '#007aff',
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1d1d1f',
                    bodyColor: '#1d1d1f',
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}

function createCountryDonutChart(data) {
    const ctx = document.getElementById('countryDonutChart').getContext('2d');
    const colors = [
        '#007aff', '#34c759', '#ff9500', '#5856d6', '#ff2d55',
        '#5ac8fa', '#ffcc00', '#ff3b30', '#af52de', '#32ade6'
    ];
    
    charts.countryDonut = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.country),
            datasets: [{
                data: data.map(d => d.count),
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#1d1d1f',
                        font: { size: 12 },
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1d1d1f',
                    bodyColor: '#1d1d1f',
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 }
                }
            }
        }
    });
}

function createAuthorsChart(data) {
    const ctx = document.getElementById('authorsChart').getContext('2d');
    charts.authors = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.name),
            datasets: [{
                label: 'Collaborations',
                data: data.map(d => d.count),
                backgroundColor: '#5856d6',
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1d1d1f',
                    bodyColor: '#1d1d1f',
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}

function createStrengthChart(data) {
    const ctx = document.getElementById('strengthChart').getContext('2d');
    charts.strength = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.strength + ' collabs'),
            datasets: [{
                label: 'Number of Pairs',
                data: data.map(d => d.count),
                backgroundColor: '#34c759',
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1d1d1f',
                    bodyColor: '#1d1d1f',
                    borderColor: 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    titleFont: { size: 14, weight: '600' },
                    bodyFont: { size: 13 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6e6e73',
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}

async function performSearch() {
    const query = document.getElementById('authorSearch').value.trim();
    
    if (!query) {
        alert('Please enter an author ID or name to search');
        return;
    }
    
    const searchResults = document.getElementById('searchResults');
    searchResults.style.display = 'block';
    searchResults.innerHTML = '<div class="no-results"><div class="loading-spinner"></div></div>';
    
    try {
        const response = await fetch(`/api/search/author?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.error) {
            searchResults.innerHTML = `
                <div class="no-results">
                    <div class="no-results-text">${data.error}</div>
                </div>
            `;
            return;
        }
        
        if (data.count === 0) {
            searchResults.innerHTML = `
                <div class="no-results">
                    <div class="no-results-text">No authors found matching "${query}"</div>
                </div>
            `;
            return;
        }
        
        renderSearchResults(data.results);
        
    } catch (error) {
        console.error('Search error:', error);
        searchResults.innerHTML = `
            <div class="no-results">
                <div class="no-results-text">Error performing search. Please try again.</div>
            </div>
        `;
    }
}

function renderSearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    
    searchResults.innerHTML = results.map(author => `
        <div class="search-result-card">
            <div class="author-header">
                <div class="author-info">
                    <h2>${author.author_name}</h2>
                    <div class="author-meta">
                        <span class="meta-tag">ID: ${author.author_id}</span>
                        <span class="meta-tag">${author.country_code}</span>
                        <span class="meta-tag">Since ${author.first_pubyear}</span>
                    </div>
                </div>
            </div>
            
            <div class="author-stats">
                <div class="stat-item">
                    <div class="stat-item-value">${author.total_collaborations}</div>
                    <div class="stat-item-label">Total Collaborations</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-value">${author.num_collaborators}</div>
                    <div class="stat-item-label">Unique Collaborators</div>
                </div>
                <div class="stat-item">
                    <div class="stat-item-value">${author.num_collaborators > 0 ? 
                        Math.round(author.total_collaborations / author.num_collaborators) : 0}</div>
                    <div class="stat-item-label">Avg per Collaborator</div>
                </div>
            </div>
            
            ${author.top_collaborators.length > 0 ? `
                <div class="collaborators-section">
                    <h3>Top Collaborators</h3>
                    ${author.top_collaborators.map(collab => `
                        <div class="collaborator-item" onclick="searchAuthorById('${collab.id}')">
                            <div class="collaborator-info">
                                <div class="collaborator-name">${collab.name}</div>
                                <div class="collaborator-meta">ID: ${collab.id}</div>
                            </div>
                            <div class="collaborator-count">${collab.collaboration_count} collabs</div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

function searchAuthorById(authorId) {
    document.getElementById('authorSearch').value = authorId;
    performSearch();
    document.getElementById('searchResults').scrollIntoView({ behavior: 'smooth', block: 'start' });
}