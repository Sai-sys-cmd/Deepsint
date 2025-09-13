'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Search, ArrowRight, Shield, Globe, Users, BarChart3, Github, Twitter, Mail, Eye } from 'lucide-react'
import SearchForm from '@/components/search-form'

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      window.location.href = `/results?query=${encodeURIComponent(searchQuery.trim())}`
    }
  }

  const features = [
    {
      icon: <Search className="w-8 h-8" />,
      title: "Multi-Platform Search",
      description: "Search across social media platforms, forums, and databases simultaneously"
    },
    {
      icon: <Eye className="w-8 h-8" />,
      title: "Visual Analytics",
      description: "Interactive graphs and visualizations to understand connections and patterns"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Privacy Focused",
      description: "Ethical OSINT practices with respect for privacy and legal boundaries"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Real-time Results",
      description: "Live data collection with progress tracking and instant notifications"
    }
  ]

  const stats = [
    { label: "Platforms Supported", value: "50+" },
    { label: "Searches Completed", value: "10K+" },
    { label: "Data Points Analyzed", value: "1M+" },
    { label: "Active Users", value: "500+" }
  ]

  return (
    <div className="py-8">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-7xl font-bold text-foreground mb-6 tracking-tight">
          OSINT <span className="text-primary">Intelligence</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
          Advanced open-source intelligence gathering and visualization platform. 
          Discover digital footprints across multiple platforms with powerful analytics.
        </p>
        
        {/* Search Form Component */}
        <SearchForm />
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap justify-center gap-4 mb-16">
        <Link
          href="/visualize"
          className="glass-card hover:bg-background/10 px-6 py-3 rounded-xl transition-colors text-foreground font-medium"
        >
          View Demo
        </Link>
        <Link
          href="/history"
          className="glass-card hover:bg-background/10 px-6 py-3 rounded-xl transition-colors text-foreground font-medium"
        >
          Search History
        </Link>
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-20">
        {stats.map((stat, index) => (
          <div key={index} className="text-center">
            <div className="text-3xl font-bold text-primary mb-2">{stat.value}</div>
            <div className="text-muted-foreground">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Features Section */}
      <div className="mb-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground mb-4">Powerful OSINT Capabilities</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Everything you need for comprehensive digital investigations in one integrated platform
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="glass-card rounded-2xl p-8 text-center hover:scale-105 transition-transform">
              <div className="text-primary mb-4 flex justify-center">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-3">{feature.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tools Preview */}
      <div className="mb-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground mb-4">Featured Tools</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Specialized tools for different aspects of OSINT investigation
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <Link href="/visualize" className="glass-card rounded-2xl p-8 hover:scale-105 transition-transform group">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-foreground mb-3 group-hover:text-primary transition-colors">
              Data Visualization
            </h3>
            <p className="text-muted-foreground mb-4">
              Interactive network graphs and timeline analysis of discovered connections
            </p>
            <div className="flex items-center text-primary text-sm font-medium">
              View Demo <ArrowRight className="w-4 h-4 ml-2" />
            </div>
          </Link>

          <Link href="/history" className="glass-card rounded-2xl p-8 hover:scale-105 transition-transform group">
            <div className="text-4xl mb-4">📋</div>
            <h3 className="text-xl font-semibold text-foreground mb-3 group-hover:text-primary transition-colors">
              Search History
            </h3>
            <p className="text-muted-foreground mb-4">
              Track and manage your previous investigations and results
            </p>
            <div className="flex items-center text-primary text-sm font-medium">
              View History <ArrowRight className="w-4 h-4 ml-2" />
            </div>
          </Link>
        </div>
      </div>

      {/* CTA Section */}
      <div className="glass-card rounded-3xl p-12 text-center bg-primary/5 border-primary/20">
        <h2 className="text-3xl font-bold text-foreground mb-4">Ready to Start Investigating?</h2>
        <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
          Join security researchers, journalists, and investigators using our platform 
          for ethical OSINT operations worldwide.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/visualize"
            className="bg-primary hover:bg-primary/80 text-primary-foreground px-8 py-4 rounded-xl transition-colors font-medium inline-flex items-center justify-center gap-2"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/history"
            className="glass-card hover:bg-background/10 text-foreground px-8 py-4 rounded-xl transition-colors font-medium"
          >
            View History
          </Link>
        </div>
      </div>

      {/* Footer Links */}
      <div className="mt-16 pt-8 border-t border-border">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="text-muted-foreground text-sm">
            Built for ethical research and security professionals
          </div>
          <div className="flex items-center gap-6">
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
              <Github className="w-5 h-5" />
            </a>
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
              <Twitter className="w-5 h-5" />
            </a>
            <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
              <Mail className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}