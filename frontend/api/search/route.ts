import { NextResponse } from 'next/server'

// This would connect to your FastAPI backend
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export async function POST(request) {
  try {
    const body = await request.json()
    
    // Validate required fields
    if (!body.username || body.username.trim().length === 0) {
      return NextResponse.json(
        { error: 'Username is required' },
        { status: 400 }
      )
    }

    // Sanitize inputs
    const sanitizedData = {
      username: body.username.trim(),
      email: body.email?.trim() || undefined,
      name: body.name?.trim() || undefined,
      searchType: body.searchType || 'basic'
    }

    // Generate search ID
    const searchId = `search_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // In development, simulate backend response
    if (process.env.NODE_ENV === 'development') {
      // Store search data in memory (in production, this would go to backend)
      global.searches = global.searches || {}
      global.searches[searchId] = {
        ...sanitizedData,
        status: 'pending',
        progress: 0,
        startTime: Date.now()
      }

      // Start simulated search process
      setTimeout(() => simulateSearch(searchId, sanitizedData), 1000)

      return NextResponse.json({
        success: true,
        searchId,
        query: sanitizedData,
        timestamp: new Date().toISOString(),
        estimatedTime: getEstimatedTime(sanitizedData.searchType)
      })
    }

    // Forward request to FastAPI backend in production
    const backendResponse = await fetch(`${BACKEND_URL}/api/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sanitizedData),
    })

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({}))
      return NextResponse.json(
        { 
          error: errorData.message || 'Backend search failed',
          details: errorData.details || 'Unknown error occurred'
        },
        { status: backendResponse.status }
      )
    }

    const result = await backendResponse.json()
    return NextResponse.json(result)

  } catch (error) {
    console.error('Search API error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const searchId = searchParams.get('id')
  
  if (!searchId) {
    return NextResponse.json(
      { error: 'Search ID is required' },
      { status: 400 }
    )
  }

  try {
    // In development, get from memory
    if (process.env.NODE_ENV === 'development') {
      global.searches = global.searches || {}
      const search = global.searches[searchId]
      
      if (!search) {
        return NextResponse.json(
          { error: 'Search not found' },
          { status: 404 }
        )
      }

      return NextResponse.json(search)
    }

    // Get search status from backend in production
    const backendResponse = await fetch(`${BACKEND_URL}/api/search/${searchId}`)
    
    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: 'Failed to get search status' },
        { status: backendResponse.status }
      )
    }

    const result = await backendResponse.json()
    return NextResponse.json(result)

  } catch (error) {
    console.error('Search status API error:', error)
    
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Helper functions for development simulation
function getEstimatedTime(searchType) {
  switch (searchType) {
    case 'basic': return 30
    case 'comprehensive': return 120
    case 'deep': return 300
    default: return 30
  }
}

function simulateSearch(searchId, searchData) {
  if (!global.searches || !global.searches[searchId]) return

  const platforms = ['Twitter', 'GitHub', 'LinkedIn', 'Instagram', 'Reddit', 'Facebook', 'Discord', 'YouTube']
  let currentProgress = 0
  
  const progressInterval = setInterval(() => {
    currentProgress += Math.random() * 15 + 5
    
    if (currentProgress >= 100) {
      // Complete the search
      global.searches[searchId] = {
        ...global.searches[searchId],
        status: 'completed',
        progress: 100,
        currentPlatform: 'Completed',
        results: generateMockResults(searchData),
        completedAt: Date.now()
      }
      clearInterval(progressInterval)
      return
    }

    // Update progress
    const platformIndex = Math.floor(currentProgress / 12.5)
    global.searches[searchId] = {
      ...global.searches[searchId],
      status: 'running',
      progress: Math.min(currentProgress, 95),
      currentPlatform: platforms[platformIndex] || 'Finalizing...',
      estimatedTimeRemaining: Math.max(0, Math.floor((100 - currentProgress) / 10))
    }
  }, 2000)
}

function generateMockResults(searchData) {
  const { username, email, name } = searchData
  
  // Generate realistic mock data
  const accounts = [
    {
      platform: 'Twitter',
      username: username,
      displayName: name || `${username}_dev`,
      url: `https://twitter.com/${username}`,
      verified: true,
      followers: Math.floor(Math.random() * 5000) + 100,
      following: Math.floor(Math.random() * 1000) + 50,
      posts: Math.floor(Math.random() * 2000) + 10,
      lastActive: randomDate(30),
      bio: 'Software developer and tech enthusiast',
      profileImage: `https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`,
      joinDate: randomDate(1500, 365),
      location: 'San Francisco, CA',
      website: `https://${username}.dev`
    },
    {
      platform: 'GitHub',
      username: username,
      displayName: name || username,
      url: `https://github.com/${username}`,
      verified: true,
      followers: Math.floor(Math.random() * 500) + 20,
      following: Math.floor(Math.random() * 200) + 10,
      repositories: Math.floor(Math.random() * 50) + 5,
      lastActive: randomDate(7),
      bio: 'Full-stack developer passionate about open source',
      profileImage: `https://api.dicebear.com/7.x/identicon/svg?seed=${username}`,
      joinDate: randomDate(1200, 365),
      location: 'California, USA',
      company: 'TechCorp'
    },
    {
      platform: 'LinkedIn',
      username: `${username}-dev`,
      displayName: name || `${username.charAt(0).toUpperCase() + username.slice(1)} Developer`,
      url: `https://linkedin.com/in/${username}-dev`,
      verified: false,
      connections: Math.floor(Math.random() * 1000) + 100,
      lastActive: randomDate(14),
      bio: 'Senior Software Engineer | React | Node.js',
      profileImage: `https://api.dicebear.com/7.x/personas/svg?seed=${username}`,
      position: 'Senior Software Engineer',
      company: 'Tech Solutions Inc.'
    }
  ]

  // Add more platforms based on search type
  if (searchData.searchType === 'comprehensive' || searchData.searchType === 'deep') {
    accounts.push(
      {
        platform: 'Reddit',
        username: username,
        url: `https://reddit.com/u/${username}`,
        karma: Math.floor(Math.random() * 10000) + 100,
        postKarma: Math.floor(Math.random() * 5000) + 50,
        commentKarma: Math.floor(Math.random() * 5000) + 50,
        lastActive: randomDate(3),
        accountAge: Math.floor(Math.random() * 1000) + 100,
        verified: false
      },
      {
        platform: 'Instagram',
        username: username,
        url: `https://instagram.com/${username}`,
        followers: Math.floor(Math.random() * 2000) + 50,
        following: Math.floor(Math.random() * 500) + 20,
        posts: Math.floor(Math.random() * 200) + 10,
        verified: false,
        lastActive: randomDate(5),
        bio: '📸 Developer life | ☕ Coffee enthusiast'
      }
    )
  }

  // Generate connections between accounts
  const connections = []
  for (let i = 0; i < accounts.length - 1; i++) {
    for (let j = i + 1; j < accounts.length; j++) {
      if (Math.random() > 0.4) { // 60% chance of connection
        connections.push({
          from: accounts[i].platform,
          to: accounts[j].platform,
          type: getConnectionType(),
          confidence: Math.random() * 0.3 + 0.7, // 0.7 to 1.0
          evidence: getConnectionEvidence()
        })
      }
    }
  }

  // Generate timeline events
  const timeline = []
  accounts.forEach(account => {
    timeline.push({
      date: account.joinDate || randomDate(365),
      event: `Account created on ${account.platform}`,
      platform: account.platform,
      type: 'account_created'
    })
    
    if (account.lastActive) {
      timeline.push({
        date: account.lastActive,
        event: `Recent activity on ${account.platform}`,
        platform: account.platform,
        type: 'activity'
      })
    }
  })

  // Sort timeline by date
  timeline.sort((a, b) => new Date(b.date) - new Date(a.date))

  return {
    summary: {
      username,
      totalAccounts: accounts.length,
      verifiedAccounts: accounts.filter(a => a.verified).length,
      riskScore: calculateRiskScore(accounts),
      lastActive: accounts.reduce((latest, acc) => {
        const accDate = new Date(acc.lastActive || 0)
        const latestDate = new Date(latest)
        return accDate > latestDate ? acc.lastActive : latest
      }, '1970-01-01'),
      firstSeen: accounts.reduce((earliest, acc) => {
        const accDate = new Date(acc.joinDate || Date.now())
        const earliestDate = new Date(earliest)
        return accDate < earliestDate ? acc.joinDate : earliest
      }, new Date().toISOString()),
      totalFollowers: accounts.reduce((sum, acc) => sum + (acc.followers || 0), 0),
      platformsFound: accounts.map(a => a.platform)
    },
    accounts,
    connections,
    timeline: timeline.slice(0, 20), // Limit to recent 20 events
    metadata: {
      searchDuration: Math.floor(Math.random() * 120) + 30,
      platformsScanned: searchData.searchType === 'basic' ? 8 : searchData.searchType === 'comprehensive' ? 15 : 25,
      confidence: Math.random() * 0.2 + 0.8
    }
  }
}

function randomDate(daysAgo, minDaysAgo = 0) {
  const now = new Date()
  const randomDays = Math.floor(Math.random() * (daysAgo - minDaysAgo)) + minDaysAgo
  const date = new Date(now.getTime() - randomDays * 24 * 60 * 60 * 1000)
  return date.toISOString().split('T')[0]
}

function getConnectionType() {
  const types = ['same_email', 'same_name', 'similar_bio', 'cross_reference', 'timing_correlation']
  return types[Math.floor(Math.random() * types.length)]
}

function getConnectionEvidence() {
  const evidence = [
    'Matching email hash patterns',
    'Similar profile creation dates',
    'Cross-platform username references',
    'Identical profile information',
    'Correlated activity patterns'
  ]
  return evidence[Math.floor(Math.random() * evidence.length)]
}

function calculateRiskScore(accounts) {
  let score = 0
  
  // More accounts = higher exposure
  score += accounts.length * 10
  
  // Verified accounts reduce risk
  const verifiedCount = accounts.filter(a => a.verified).length
  score -= verifiedCount * 5
  
  // High follower counts increase visibility
  const totalFollowers = accounts.reduce((sum, acc) => sum + (acc.followers || 0), 0)
  if (totalFollowers > 10000) score += 20
  else if (totalFollowers > 1000) score += 10
  
  // Normalize to Low/Medium/High
  if (score < 30) return 'Low'
  if (score < 60) return 'Medium'
  return 'High'
}