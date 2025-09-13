import { NextResponse } from 'next/server'
import { apiClient } from '@/lib/api-client'

export async function POST(request) {
  try {
    const body = await request.json()
    
    // Validate required fields
    if (!body.username) {
      return NextResponse.json(
        { success: false, error: 'Username is required' },
        { status: 400 }
      )
    }

    // Forward the request to the backend
    const response = await apiClient.post('/api/search', {
      username: body.username,
      email: body.email || null,
      name: body.name || null
    })

    // Generate a mock search ID for now
    const searchId = `search_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    return NextResponse.json({
      success: true,
      searchId: searchId,
      message: 'Search initiated successfully'
    })

  } catch (error) {
    console.error('Search API error:', error)
    
    if (error.response?.status === 429) {
      return NextResponse.json(
        { success: false, error: 'Rate limit exceeded. Please try again later.' },
        { status: 429 }
      )
    }
    
    if (error.response?.status >= 500) {
      return NextResponse.json(
        { success: false, error: 'Server error. Please try again.' },
        { status: 500 }
      )
    }

    return NextResponse.json(
      { success: false, error: 'Failed to initiate search' },
      { status: 500 }
    )
  }
}

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const searchId = searchParams.get('id')
    
    if (!searchId) {
      return NextResponse.json(
        { error: 'Search ID is required' },
        { status: 400 }
      )
    }

    // Mock search status response
    const mockStatus = {
      id: searchId,
      status: 'completed',
      progress: 100,
      results: {
        query: 'john_doe',
        platforms: {
          github: { found: true, profiles: 1, repos: 5 },
          reddit: { found: true, profiles: 1, posts: 23 },
          twitter: { found: true, profiles: 1, tweets: 156 },
          breach: { found: true, breaches: 2, emails: 1 }
        },
        summary: {
          totalProfiles: 4,
          riskScore: 65,
          lastUpdated: new Date().toISOString()
        }
      }
    }

    return NextResponse.json(mockStatus)

  } catch (error) {
    console.error('Search status API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch search status' },
      { status: 500 }
    )
  }
}
