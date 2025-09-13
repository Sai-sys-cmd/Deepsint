'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Search, Clock, Eye, Download, Trash2, Filter } from 'lucide-react'

export default function HistoryPage() {
  const [searchHistory, setSearchHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, completed, failed

  // Mock search history data
  const mockHistory = [
    {
      id: 'search_1704067200_abc123',
      query: 'john_doe',
      status: 'completed',
      timestamp: '2024-01-01T10:00:00Z',
      platforms: ['github', 'reddit', 'twitter'],
      resultsCount: 15,
      riskScore: 65
    },
    {
      id: 'search_1704153600_def456',
      query: 'alice_smith',
      status: 'completed',
      timestamp: '2024-01-02T10:00:00Z',
      platforms: ['github', 'linkedin'],
      resultsCount: 8,
      riskScore: 32
    },
    {
      id: 'search_1704240000_ghi789',
      query: 'cybersec_expert',
      status: 'failed',
      timestamp: '2024-01-03T10:00:00Z',
      platforms: ['github', 'reddit', 'twitter', 'breach'],
      resultsCount: 0,
      riskScore: 0,
      error: 'Rate limit exceeded'
    },
    {
      id: 'search_1704326400_jkl012',
      query: 'data_analyst_pro',
      status: 'completed',
      timestamp: '2024-01-04T10:00:00Z',
      platforms: ['github', 'reddit'],
      resultsCount: 12,
      riskScore: 45
    },
    {
      id: 'search_1704412800_mno345',
      query: 'security_researcher',
      status: 'completed',
      timestamp: '2024-01-05T10:00:00Z',
      platforms: ['github', 'twitter', 'breach'],
      resultsCount: 23,
      riskScore: 78
    }
  ]

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setSearchHistory(mockHistory)
      setLoading(false)
    }, 1000)
  }, [])

  const filteredHistory = searchHistory.filter(search => {
    if (filter === 'all') return true
    return search.status === filter
  })

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-500'
      case 'failed': return 'text-red-500'
      case 'pending': return 'text-yellow-500'
      default: return 'text-muted-foreground'
    }
  }

  const getRiskColor = (score) => {
    if (score >= 70) return 'text-red-500'
    if (score >= 40) return 'text-yellow-500'
    return 'text-green-500'
  }

  const deleteSearch = (id) => {
    setSearchHistory(prev => prev.filter(search => search.id !== id))
  }

  if (loading) {
    return (
      <div className="py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading search history...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Search History</h1>
          <p className="text-muted-foreground">
            View and manage your previous OSINT investigations
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Filter:</span>
          </div>
          <div className="flex gap-2">
            {['all', 'completed', 'failed'].map((filterOption) => (
              <button
                key={filterOption}
                onClick={() => setFilter(filterOption)}
                className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                  filter === filterOption
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Search History List */}
        <div className="space-y-4">
          {filteredHistory.length === 0 ? (
            <div className="text-center py-12">
              <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">No searches found</h3>
              <p className="text-muted-foreground mb-4">
                {filter === 'all' 
                  ? "You haven't performed any searches yet." 
                  : `No ${filter} searches found.`}
              </p>
              <Link
                href="/"
                className="bg-primary hover:bg-primary/80 text-primary-foreground px-6 py-2 rounded-lg transition-colors inline-flex items-center gap-2"
              >
                <Search className="w-4 h-4" />
                Start New Search
              </Link>
            </div>
          ) : (
            filteredHistory.map((search) => (
              <div key={search.id} className="glass-card rounded-xl p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-foreground">
                        {search.query}
                      </h3>
                      <span className={`text-sm font-medium ${getStatusColor(search.status)}`}>
                        {search.status.charAt(0).toUpperCase() + search.status.slice(1)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                      <div className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatDate(search.timestamp)}
                      </div>
                      <div>
                        Platforms: {search.platforms.join(', ')}
                      </div>
                      {search.status === 'completed' && (
                        <>
                          <div>
                            Results: {search.resultsCount}
                          </div>
                          <div className={`font-medium ${getRiskColor(search.riskScore)}`}>
                            Risk: {search.riskScore}/100
                          </div>
                        </>
                      )}
                    </div>

                    {search.error && (
                      <div className="text-sm text-red-500 mb-3">
                        Error: {search.error}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    {search.status === 'completed' && (
                      <>
                        <Link
                          href={`/results/${search.id}`}
                          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
                          title="View Results"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        <Link
                          href={`/visualize?id=${search.id}`}
                          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
                          title="Visualize"
                        >
                          <Search className="w-4 h-4" />
                        </Link>
                        <button
                          className="p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors"
                          title="Download Results"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => deleteSearch(search.id)}
                      className="p-2 text-muted-foreground hover:text-red-500 hover:bg-muted rounded-lg transition-colors"
                      title="Delete Search"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Summary Stats */}
        {filteredHistory.length > 0 && (
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-primary mb-1">
                {filteredHistory.length}
              </div>
              <div className="text-sm text-muted-foreground">Total Searches</div>
            </div>
            <div className="glass-card rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-500 mb-1">
                {filteredHistory.filter(s => s.status === 'completed').length}
              </div>
              <div className="text-sm text-muted-foreground">Completed</div>
            </div>
            <div className="glass-card rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-yellow-500 mb-1">
                {filteredHistory.reduce((sum, s) => sum + (s.resultsCount || 0), 0)}
              </div>
              <div className="text-sm text-muted-foreground">Total Results</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
