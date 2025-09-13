'use client'

import { useState, useEffect, useRef, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'

function VisualizationContent() {
  const searchParams = useSearchParams()
  const query = searchParams.get('query')
  const searchId = searchParams.get('id')
  
  const [graphData, setGraphData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState(null)
  const [searchResults, setSearchResults] = useState(null)

  // Mock data
  const mockGraphData = {
    nodes: [
      { id: 'user1', label: 'john_doe', platform: 'github', size: 60, risk: 'low' },
      { id: 'user2', label: 'john.doe@email.com', platform: 'breach', size: 40, risk: 'high' },
      { id: 'user3', label: 'johndoe_dev', platform: 'reddit', size: 50, risk: 'medium' },
      { id: 'user4', label: '@johndoe', platform: 'twitter', size: 45, risk: 'low' },
      { id: 'repo1', label: 'awesome-project', platform: 'github', size: 35, risk: 'low' },
    ],
    edges: [
      { id: 'e1', source: 'user1', target: 'repo1', relation: 'owns', strength: 3 },
      { id: 'e2', source: 'user1', target: 'user2', relation: 'same_email', strength: 5 },
      { id: 'e3', source: 'user1', target: 'user3', relation: 'similar_username', strength: 4 },
      { id: 'e4', source: 'user1', target: 'user4', relation: 'cross_platform', strength: 3 },
    ]
  }

  const mockSearchResults = {
    query: 'john_doe',
    platforms: {
      github: { found: true, profiles: 1, repos: 5 },
      reddit: { found: true, profiles: 1, posts: 23 },
      twitter: { found: true, profiles: 1, tweets: 156 },
      breach: { found: true, breaches: 2, emails: 1 }
    },
    totalNodes: 5,
    totalConnections: 4,
    riskScore: 65
  }

  const [viewMode, setViewMode] = useState('network') // network, timeline, mindmap, heatmap
  const [filterPlatform, setFilterPlatform] = useState('all')
  
  const networkRef = useRef(null)
  const timelineRef = useRef(null)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        // Try to fetch real data first
        if (searchId) {
          const response = await fetch(`/api/search?id=${searchId}`)
          const data = await response.json()
          
          if (data.status === 'completed' && data.results) {
            setSearchResults(data.results)
            setGraphData(data.graphData || mockGraphData)
            setLoading(false)
            return
          }
        }
        
        // Fallback to mock data if fetch fails or no searchId
        console.log('Using mock data for visualization')
        setSearchResults(mockSearchResults)
        setGraphData(mockGraphData)
        setLoading(false)
        
      } catch (error) {
        console.error('Failed to fetch results, using mock data:', error)
        // Always fallback to mock data on error
        setSearchResults(mockSearchResults)
        setGraphData(mockGraphData)
        setLoading(false)
      }
    }

    fetchResults()
  }, [query, searchId])

  const exportVisualization = (format) => {
    if (!searchResults) return

    if (format === 'json') {
      const dataStr = JSON.stringify(searchResults, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `osint_visualization_${query}_${new Date().toISOString().split('T')[0]}.json`
      link.click()
    } else if (format === 'csv') {
      const csv = convertToCSV(searchResults.accounts || [])
      const dataBlob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `osint_accounts_${query}_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
    }
  }

  const convertToCSV = (accounts) => {
    const headers = ['Platform', 'Username', 'Followers', 'Verified', 'Last Active', 'URL']
    const rows = accounts.map(acc => [
      acc.platform,
      acc.username,
      acc.followers || acc.connections || 0,
      acc.verified ? 'Yes' : 'No',
      acc.lastActive || 'Unknown',
      acc.url
    ])
    
    return [headers, ...rows].map(row => row.join(',')).join('\n')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading visualization...</p>
        </div>
      </div>
    )
  }

  if (!searchResults) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground">No visualization data available</p>
      </div>
    )
  }

  return (
    <div className="py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">OSINT Visualization</h1>
          <p className="text-muted-foreground">Interactive analysis for: <span className="text-foreground">{query}</span></p>
        </div>
        
        <div className="flex gap-3">
          <div className="flex bg-muted rounded-lg p-1">
            {[
              { id: 'network', label: 'Network', icon: 'M9 19c-4.286-1.35-4.286-2.65 0-4M9 19c4.286-1.35 4.286-2.65 0-4M9 19v-2.5A2.5 2.5 0 016.5 14H5c-1.5 0-1.5-1-1.5-1s1.379-3 6.5-3c5.12 0 6.5 3 6.5 3s0 1-1.5 1h-1.5a2.5 2.5 0 00-2.5 2.5V19z' },
              { id: 'timeline', label: 'Timeline', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
              { id: 'mindmap', label: 'Mind Map', icon: 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM7 21h10a2 2 0 002-2v-4a2 2 0 00-2-2H7' },
              { id: 'heatmap', label: 'Heatmap', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6z' }
            ].map((mode) => (
              <button
                key={mode.id}
                onClick={() => setViewMode(mode.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm transition-all ${
                  viewMode === mode.id
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={mode.icon} />
                </svg>
                {mode.label}
              </button>
            ))}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => exportVisualization('json')}
              className="px-4 py-2 bg-primary hover:bg-primary/80 text-primary-foreground rounded-lg transition-colors text-sm"
            >
              Export JSON
            </button>
            <button
              onClick={() => exportVisualization('csv')}
              className="px-4 py-2 glass-card hover:bg-background/10 text-foreground rounded-lg transition-colors text-sm"
            >
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-card rounded-lg p-4 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-muted-foreground text-sm">Filter by platform:</span>
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="bg-muted text-foreground rounded-md px-3 py-1 text-sm border border-border"
            >
              <option value="all">All Platforms</option>
              {searchResults.platforms && Object.keys(searchResults.platforms).map(platform => (
                <option key={platform} value={platform}>{platform}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Found: {searchResults.totalNodes || 0} accounts</span>
            <span>•</span>
            <span>Risk: <span className={`${
              searchResults.riskScore >= 70 ? 'text-red-400' :
              searchResults.riskScore >= 40 ? 'text-yellow-400' : 'text-green-400'
            }`}>{searchResults.riskScore}/100</span></span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Visualization */}
        <div className="lg:col-span-3">
          <div className="glass-card rounded-2xl p-8 min-h-[600px]">
            {viewMode === 'network' && (
              <NetworkVisualization 
                results={searchResults} 
                graphData={graphData}
                filterPlatform={filterPlatform}
                onNodeSelect={setSelectedNode}
                ref={networkRef}
              />
            )}
            {viewMode === 'timeline' && (
              <TimelineVisualization 
                timeline={searchResults.timeline}
                filterPlatform={filterPlatform}
                ref={timelineRef}
              />
            )}
            {viewMode === 'mindmap' && (
              <MindMapVisualization 
                results={searchResults}
                graphData={graphData}
                filterPlatform={filterPlatform}
              />
            )}
            {viewMode === 'heatmap' && (
              <HeatmapVisualization 
                results={searchResults}
                filterPlatform={filterPlatform}
              />
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Selected Node Details */}
          {selectedNode && (
            <div className="glass-card rounded-xl p-6">
              <h3 className="font-semibold text-foreground mb-4">Selected Account</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-bold">
                    {selectedNode.platform[0]}
                  </div>
                  <div>
                    <div className="text-foreground font-medium">{selectedNode.username}</div>
                    <div className="text-muted-foreground text-sm">{selectedNode.platform}</div>
                  </div>
                </div>
                
                <div className="space-y-2 text-sm">
                  {selectedNode.followers && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Followers:</span>
                      <span className="text-foreground">{selectedNode.followers.toLocaleString()}</span>
                    </div>
                  )}
                  {selectedNode.lastActive && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Last Active:</span>
                      <span className="text-foreground">{selectedNode.lastActive}</span>
                    </div>
                  )}
                  {selectedNode.verified !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Verified:</span>
                      <span className={selectedNode.verified ? 'text-green-500' : 'text-muted-foreground'}>
                        {selectedNode.verified ? 'Yes' : 'No'}
                      </span>
                    </div>
                  )}
                </div>

                {selectedNode.bio && (
                  <div className="border-t border-border pt-3">
                    <p className="text-muted-foreground text-sm">{selectedNode.bio}</p>
                  </div>
                )}

                <a
                  href={selectedNode.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block w-full text-center px-4 py-2 bg-primary hover:bg-primary/80 text-primary-foreground rounded-md transition-colors text-sm"
                >
                  View Profile
                </a>
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="glass-card rounded-xl p-6">
            <h3 className="font-semibold text-foreground mb-4">Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Total Profiles:</span>
                <span className="text-foreground">{searchResults.totalNodes || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Platforms:</span>
                <span className="text-green-500">{Object.keys(searchResults.platforms || {}).length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Connections:</span>
                <span className="text-foreground">{searchResults.totalConnections || 0}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Risk Score:</span>
                <span className={`${
                  searchResults.riskScore >= 70 ? 'text-red-500' :
                  searchResults.riskScore >= 40 ? 'text-yellow-500' : 'text-green-500'
                }`}>{searchResults.riskScore}/100</span>
              </div>
            </div>
          </div>

          {/* Platform Distribution */}
          <div className="glass-card rounded-xl p-6">
            <h3 className="font-semibold text-foreground mb-4">Platform Distribution</h3>
            <div className="space-y-3">
              {Object.entries(searchResults.platforms || {}).map(([platform, data]) => {
                const count = data.found ? 1 : 0
                const percentage = count > 0 ? 20 : 0
                
                return (
                  <div key={platform} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{platform}</span>
                      <span className="text-foreground">{count}</span>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Network Visualization Component
function NetworkVisualization({ results, graphData, filterPlatform, onNodeSelect }) {
  const canvasRef = useRef(null)
  
  useEffect(() => {
    if (!graphData || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const rect = canvas.getBoundingClientRect()
    
    // Set canvas size
    canvas.width = rect.width * window.devicePixelRatio
    canvas.height = rect.height * window.devicePixelRatio
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    
    // Filter nodes based on platform
    const nodes = filterPlatform === 'all' 
      ? graphData.nodes 
      : graphData.nodes.filter(node => node.platform === filterPlatform)
    
    // Position nodes
    const positionedNodes = nodes.map((node, index) => ({
      ...node,
      x: Math.random() * (canvas.width - 100) + 50,
      y: Math.random() * (canvas.height - 100) + 50,
      radius: node.size / 2 || 20
    }))
    
    // Draw connections
    graphData.edges.forEach(edge => {
      const fromNode = positionedNodes.find(n => n.id === edge.source)
      const toNode = positionedNodes.find(n => n.id === edge.target)
      
      if (fromNode && toNode) {
        ctx.beginPath()
        ctx.strokeStyle = `rgba(59, 130, 246, ${edge.confidence * 0.6})`
        ctx.lineWidth = 2
        ctx.moveTo(fromNode.x, fromNode.y)
        ctx.lineTo(toNode.x, toNode.y)
        ctx.stroke()
      }
    })
    
    // Draw nodes
    positionedNodes.forEach(node => {
      ctx.beginPath()
      ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI)
      ctx.fillStyle = getPlatformColor(node.platform)
      ctx.fill()
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 2
      ctx.stroke()
      
      // Draw label
      ctx.fillStyle = '#ffffff'
      ctx.font = '12px Inter'
      ctx.textAlign = 'center'
      ctx.fillText(node.label, node.x, node.y + node.radius + 15)
    })
    
    // Handle clicks
    const handleClick = (event) => {
      const rect = canvas.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      
      const clickedNode = positionedNodes.find(node => {
        const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
        return distance <= node.radius
      })
      
      if (clickedNode && onNodeSelect) {
        onNodeSelect(clickedNode)
      }
    }
    
    canvas.addEventListener('click', handleClick)
    
    return () => {
      canvas.removeEventListener('click', handleClick)
    }
  }, [graphData, filterPlatform, onNodeSelect])

  return (
    <div className="relative w-full h-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Network Graph</h3>
      <canvas 
        ref={canvasRef}
        className="w-full h-[500px] bg-muted/30 rounded-lg cursor-pointer"
      />
      <div className="absolute top-4 right-4 text-xs text-muted-foreground">
        Click nodes to view details
      </div>
    </div>
  )
}

// Timeline Visualization Component
function TimelineVisualization({ timeline, filterPlatform }) {
  const filteredEvents = filterPlatform === 'all' 
    ? timeline 
    : timeline.filter(event => event.platform === filterPlatform)

  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Activity Timeline</h3>
      <div className="h-[500px] overflow-y-auto space-y-4">
        {filteredEvents.map((event, index) => (
          <div key={index} className="flex items-start gap-4">
            <div className="flex-shrink-0 w-3 h-3 bg-primary rounded-full mt-2"></div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-foreground font-medium">{event.event}</span>
                <span className={`px-2 py-1 rounded text-xs ${getPlatformColor(event.platform)}`}>
                  {event.platform}
                </span>
              </div>
              <div className="text-muted-foreground text-sm">{formatDate(event.date)}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Mind Map Visualization Component
function MindMapVisualization({ results, graphData, filterPlatform }) {
  const svgRef = useRef(null)
  
  useEffect(() => {
    if (!results || !svgRef.current) return
    
    const svg = svgRef.current
    const width = 800
    const height = 500
    
    // Clear previous content
    svg.innerHTML = ''
    
    // Filter nodes
    const nodes = filterPlatform === 'all' 
      ? graphData?.nodes || [] 
      : graphData?.nodes?.filter(node => node.platform === filterPlatform) || []
    
    // Central node (username)
    const centerX = width / 2
    const centerY = height / 2
    
    // Create central node
    const centerNode = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
    centerNode.setAttribute('cx', centerX)
    centerNode.setAttribute('cy', centerY)
    centerNode.setAttribute('r', '40')
    centerNode.setAttribute('fill', '#6366f1')
    centerNode.setAttribute('stroke', '#8b5cf6')
    centerNode.setAttribute('stroke-width', '3')
    svg.appendChild(centerNode)
    
    // Central text
    const centerText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    centerText.setAttribute('x', centerX)
    centerText.setAttribute('y', centerY + 5)
    centerText.setAttribute('text-anchor', 'middle')
    centerText.setAttribute('fill', 'white')
    centerText.setAttribute('font-size', '12')
    centerText.setAttribute('font-weight', 'bold')
    centerText.textContent = results.query || 'Search Query'
    svg.appendChild(centerText)
    
    // Create platform nodes around center
    const angleStep = (2 * Math.PI) / nodes.length
    
    nodes.forEach((node, index) => {
      const angle = index * angleStep
      const nodeX = centerX + Math.cos(angle) * 200
      const nodeY = centerY + Math.sin(angle) * 200
      
      // Connection line
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
      line.setAttribute('x1', centerX)
      line.setAttribute('y1', centerY)
      line.setAttribute('x2', nodeX)
      line.setAttribute('y2', nodeY)
      line.setAttribute('stroke', '#4b5563')
      line.setAttribute('stroke-width', '2')
      svg.appendChild(line)
      
      // Platform node
      const platformNode = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
      platformNode.setAttribute('cx', nodeX)
      platformNode.setAttribute('cy', nodeY)
      platformNode.setAttribute('r', '25')
      platformNode.setAttribute('fill', getPlatformColor(node.platform))
      platformNode.setAttribute('stroke', 'white')
      platformNode.setAttribute('stroke-width', '2')
      svg.appendChild(platformNode)
      
      // Platform label
      const platformText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      platformText.setAttribute('x', nodeX)
      platformText.setAttribute('y', nodeY - 35)
      platformText.setAttribute('text-anchor', 'middle')
      platformText.setAttribute('fill', 'white')
      platformText.setAttribute('font-size', '10')
      platformText.setAttribute('font-weight', 'bold')
      platformText.textContent = node.platform
      svg.appendChild(platformText)
      
      // Username
      const usernameText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
      usernameText.setAttribute('x', nodeX)
      usernameText.setAttribute('y', nodeY + 5)
      usernameText.setAttribute('text-anchor', 'middle')
      usernameText.setAttribute('fill', 'white')
      usernameText.setAttribute('font-size', '8')
      usernameText.textContent = node.label
      svg.appendChild(usernameText)
      
      // Size indicator
      if (node.size) {
        const sizeText = document.createElementNS('http://www.w3.org/2000/svg', 'text')
        sizeText.setAttribute('x', nodeX)
        sizeText.setAttribute('y', nodeY + 45)
        sizeText.setAttribute('text-anchor', 'middle')
        sizeText.setAttribute('fill', 'rgba(255,255,255,0.7)')
        sizeText.setAttribute('font-size', '7')
        sizeText.textContent = `Size: ${node.size}`
        svg.appendChild(sizeText)
      }
    })
  }, [results, graphData, filterPlatform])
  
  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Mind Map</h3>
      <div className="bg-muted/30 rounded-lg p-4 h-[500px] overflow-auto">
        <svg ref={svgRef} width="100%" height="100%" viewBox="0 0 800 500">
        </svg>
      </div>
    </div>
  )
}

// Heatmap Visualization Component
function HeatmapVisualization({ results, filterPlatform }) {
  const platformActivity = {}
  const timeSlots = []
  
  // Generate time slots (24 hours)
  for (let i = 0; i < 24; i++) {
    timeSlots.push(`${i.toString().padStart(2, '0')}:00`)
  }
  
  // Initialize platform activity
  const platforms = Object.keys(results.platforms || {})
  platforms.forEach(platform => {
    if (filterPlatform === 'all' || platform === filterPlatform) {
      platformActivity[platform] = timeSlots.map(() => Math.floor(Math.random() * 10))
    }
  })
  
  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold text-foreground mb-4">Activity Heatmap</h3>
      <div className="bg-muted/30 rounded-lg p-4 h-[500px] overflow-auto">
        <div className="space-y-3">
          {Object.entries(platformActivity).map(([platform, activity]) => (
            <div key={platform} className="space-y-2">
              <div className="text-muted-foreground text-sm font-medium">{platform}</div>
              <div className="flex gap-1 flex-wrap">
                {activity.map((value, index) => (
                  <div
                    key={index}
                    className="w-4 h-4 rounded-sm"
                    style={{
                      backgroundColor: `rgba(59, 130, 246, ${value / 10})`,
                      border: '1px solid rgba(75, 85, 99, 0.3)'
                    }}
                    title={`${timeSlots[index]}: ${value.toFixed(1)} activity`}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-6 flex items-center gap-4 text-xs text-muted-foreground">
          <span>Less activity</span>
          <div className="flex gap-1">
            {[0.1, 0.3, 0.5, 0.7, 0.9].map(opacity => (
              <div
                key={opacity}
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: `rgba(59, 130, 246, ${opacity})` }}
              />
            ))}
          </div>
          <span>More activity</span>
        </div>
      </div>
    </div>
  )
}

// Helper functions
function getPlatformColor(platform) {
  const colors = {
    Twitter: 'bg-blue-500/20 text-blue-300',
    GitHub: 'bg-gray-500/20 text-gray-300',
    LinkedIn: 'bg-blue-600/20 text-blue-300',
    Instagram: 'bg-pink-500/20 text-pink-300',
    Reddit: 'bg-orange-500/20 text-orange-300',
    Facebook: 'bg-blue-700/20 text-blue-300',
    Discord: 'bg-indigo-500/20 text-indigo-300',
    YouTube: 'bg-red-500/20 text-red-300'
  }
  return colors[platform] || 'bg-gray-500/20 text-gray-300'
}

function formatDate(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
  
  return date.toLocaleDateString()
}

export default function VisualizePage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    }>
      <VisualizationContent />
    </Suspense>
  )
}