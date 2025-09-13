'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { Loader2, ArrowLeft, Download, Share, RefreshCw } from 'lucide-react'

/**
 * @typedef {Object} SearchStatus
 * @property {'pending' | 'running' | 'completed' | 'failed'} status
 * @property {number} progress
 * @property {any} [results]
 * @property {string} [error]
 * @property {number} [estimatedTimeRemaining]
 */

function ResultsContent() {
  const searchParams = useSearchParams()
  const query = searchParams.get('query')
  const searchId = searchParams.get('id')
  
  const [searchStatus, setSearchStatus] = useState({
    status: 'pending',
    progress: 0
  })
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const [isPolling, setIsPolling] = useState(true)

  // Mock data
  const mockResults = {
    query: query || 'john_doe',
    platforms: {
      github: {
        found: true,
        profiles: [
          {
            username: 'john_doe',
            name: 'John Doe',
            bio: 'Full-stack developer passionate about open source',
            followers: 156,
            following: 89,
            repos: 23,
            avatar: '/api/placeholder/64/64'
          }
        ],
        repositories: [
          { name: 'awesome-project', stars: 45, language: 'JavaScript' },
          { name: 'data-viz-tool', stars: 12, language: 'Python' }
        ]
      },
      reddit: {
        found: true,
        profiles: [
          {
            username: 'johndoe_dev',
            karma: 1247,
            accountAge: '2 years',
            posts: 23,
            comments: 156
          }
        ]
      },
      twitter: {
        found: true,
        profiles: [
          {
            username: '@johndoe',
            name: 'John Doe',
            followers: 234,
            following: 189,
            tweets: 456
          }
        ]
      },
      breach: {
        found: true,
        breaches: [
          { site: 'Adobe', date: '2013-10-04', records: 152000000 },
          { site: 'LinkedIn', date: '2012-05-05', records: 164000000 }
        ]
      }
    },
    summary: {
      totalProfiles: 4,
      riskScore: 65,
      lastUpdated: new Date().toISOString()
    }
  }

  useEffect(() => {
    if (!query && !searchId) return

    // Use mock data for now
    setTimeout(() => {
      setSearchStatus({ status: 'completed', progress: 100 })
      setResults(mockResults)
      setIsPolling(false)
    }, 2000)
    return
    
    // Real polling logic (commented out)
    // const pollInterval = setInterval(async () => {
    //   try {
    //     const response = await fetch(`/api/search?id=${searchId || query}`)
    //     const data = await response.json()
    //     
    //     setSearchStatus(data)
    //     
    //     if (data.status === 'completed' || data.status === 'failed') {
    //       setIsPolling(false)
    //       clearInterval(pollInterval)
    //     }
    //   } catch (error) {
    //     console.error('Failed to fetch search status:', error)
    //     setSearchStatus(prev => ({
    //       ...prev,
    //       status: 'failed',
    //       error: 'Failed to fetch search status'
    //     }))
    //     setIsPolling(false)
    //     clearInterval(pollInterval)
    //   }
    // }, 2000)
    //
    // return () => clearInterval(pollInterval)
  }, [query, searchId])

  const goBack = () => {
    window.history.back()
  }

  const exportResults = () => {
    if (results) {
      const dataStr = JSON.stringify(results, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(dataBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `osint_results_${query}_${new Date().toISOString().split('T')[0]}.json`
      link.click()
    }
  }

  const shareResults = async () => {
    if (navigator.share && results) {
      try {
        await navigator.share({
          title: `OSINT Results for ${query}`,
          text: `Found ${results.summary?.totalProfiles || 0} data points for ${query}`,
          url: window.location.href,
        })
      } catch (error) {
        // Fallback to clipboard
        navigator.clipboard.writeText(window.location.href)
      }
    } else {
      navigator.clipboard.writeText(window.location.href)
    }
  }

  return (
    <div className="py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <button
            onClick={goBack}
            className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Search Results</h1>
            <p className="text-muted-foreground">Query: <span className="text-foreground">{query}</span></p>
          </div>
        </div>
        
        {searchStatus.status === 'completed' && (
          <div className="flex gap-2">
            <button
              onClick={exportResults}
              className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary/80 text-primary-foreground rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={shareResults}
              className="flex items-center gap-2 px-4 py-2 bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded-lg transition-colors"
            >
              <Share className="w-4 h-4" />
              Share
            </button>
          </div>
        )}
      </div>

      {/* Status Card */}
      <div className="glass-card rounded-2xl p-8 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            {searchStatus.status === 'running' && (
              <Loader2 className="w-6 h-6 text-primary animate-spin" />
            )}
            {searchStatus.status === 'completed' && (
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-background rounded-full"></div>
              </div>
            )}
            {searchStatus.status === 'failed' && (
              <div className="w-6 h-6 bg-destructive rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-background rounded-full"></div>
              </div>
            )}
            {searchStatus.status === 'pending' && (
              <RefreshCw className="w-6 h-6 text-muted-foreground animate-spin" />
            )}
            <h2 className="text-xl font-semibold text-foreground capitalize">
              {searchStatus.status === 'running' ? 'Searching' : searchStatus.status}
            </h2>
          </div>
          
          {searchStatus.estimatedTimeRemaining && (
            <div className="text-sm text-muted-foreground">
              ~{searchStatus.estimatedTimeRemaining}s remaining
            </div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-muted rounded-full h-2 mb-4">
          <div
            className="bg-primary h-2 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${searchStatus.progress}%` }}
          ></div>
        </div>

        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Progress: {searchStatus.progress}%</span>
          <span>
            {searchStatus.status === 'completed' && 'Search completed successfully'}
            {searchStatus.status === 'running' && 'Scanning platforms and databases...'}
            {searchStatus.status === 'failed' && `Error: ${searchStatus.error}`}
            {searchStatus.status === 'pending' && 'Initializing search...'}
          </span>
        </div>
      </div>

      {/* Results Section */}
      {searchStatus.status === 'completed' && results && (
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-foreground mb-4">Investigation Results</h2>
          
          {/* Graph Visualization Placeholder */}
          <div className="glass-card rounded-2xl p-8">
            <h3 className="text-lg font-semibold text-foreground mb-4">Connection Graph</h3>
            <div className="h-96 bg-muted/50 rounded-lg flex items-center justify-center border-2 border-dashed border-border">
              <div className="text-center">
                <div className="w-16 h-16 bg-primary rounded-full mx-auto mb-4 flex items-center justify-center">
                  <div className="w-8 h-8 border-2 border-primary-foreground rounded-full"></div>
                </div>
                <p className="text-muted-foreground mb-2">Graph visualization will appear here</p>
                <p className="text-sm text-muted-foreground/70">
                  Found {results.summary?.totalProfiles || 0} profiles
                </p>
              </div>
            </div>
          </div>

          {/* Raw Data */}
          <div className="glass-card rounded-2xl p-8">
            <h3 className="text-lg font-semibold text-foreground mb-4">Raw Data</h3>
            <pre className="bg-muted rounded-lg p-4 overflow-auto text-sm text-muted-foreground max-h-96">
              {JSON.stringify(results, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Error State */}
      {searchStatus.status === 'failed' && (
        <div className="glass-card rounded-2xl p-8 border-destructive/20">
          <div className="text-center">
            <div className="w-16 h-16 bg-destructive rounded-full mx-auto mb-4 flex items-center justify-center">
              <div className="w-8 h-8 text-destructive-foreground font-bold">!</div>
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">Search Failed</h3>
            <p className="text-muted-foreground mb-4">{searchStatus.error}</p>
            <button
              onClick={goBack}
              className="px-6 py-2 bg-destructive hover:bg-destructive/80 text-destructive-foreground rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ResultsPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    }>
      <ResultsContent />
    </Suspense>
  )
}