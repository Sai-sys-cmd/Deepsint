import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'OSINT Visualizer',
  description: 'Advanced OSINT data collection and visualization tool',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
          <div className="relative">
            <header className="border-b border-border backdrop-blur-sm sticky top-0 z-50">
              <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-primary rounded-lg"></div>
                    <h1 className="text-xl font-bold text-foreground">OSINT Visualizer</h1>
                  </div>
                  <nav className="hidden md:flex items-center space-x-6">
                    <Link href="/" className="text-muted-foreground hover:text-foreground transition-colors">Home</Link>
                    <Link href="/visualize" className="text-muted-foreground hover:text-foreground transition-colors">Visualize</Link>
                    <Link href="/history" className="text-muted-foreground hover:text-foreground transition-colors">History</Link>
                    <Link href="/about" className="text-muted-foreground hover:text-foreground transition-colors">About</Link>
                  </nav>
                  <div className="md:hidden">
                    <button className="text-muted-foreground hover:text-foreground">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </header>
            <main className="container mx-auto px-4">
              {children}
            </main>
            <footer className="border-t border-border mt-20">
              <div className="container mx-auto px-4 py-8">
                <div className="grid md:grid-cols-4 gap-8">
                  <div>
                    <div className="flex items-center space-x-2 mb-4">
                      <div className="w-6 h-6 bg-primary rounded"></div>
                      <span className="font-bold text-foreground">OSINT Visualizer</span>
                    </div>
                    <p className="text-muted-foreground text-sm">
                      Advanced open source intelligence gathering and visualization platform.
                    </p>
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-4">Features</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li><a href="/search" className="hover:text-foreground transition-colors">Username Search</a></li>
                      <li><a href="/tools" className="hover:text-foreground transition-colors">Domain Analysis</a></li>
                      <li><a href="/gallery" className="hover:text-foreground transition-colors">Visual Reports</a></li>
                      <li><a href="/docs" className="hover:text-foreground transition-colors">API Access</a></li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-4">Resources</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li><a href="/docs" className="hover:text-foreground transition-colors">Documentation</a></li>
                      <li><a href="/docs/api" className="hover:text-foreground transition-colors">API Guide</a></li>
                      <li><a href="/about" className="hover:text-foreground transition-colors">Privacy Policy</a></li>
                      <li><a href="/about" className="hover:text-foreground transition-colors">Terms of Service</a></li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-4">Connect</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li><a href="#" className="hover:text-foreground transition-colors">GitHub</a></li>
                      <li><a href="#" className="hover:text-foreground transition-colors">Discord</a></li>
                      <li><a href="#" className="hover:text-foreground transition-colors">Twitter</a></li>
                      <li><a href="#" className="hover:text-foreground transition-colors">Contact</a></li>
                    </ul>
                  </div>
                </div>
                <div className="border-t border-border mt-8 pt-8 text-center text-sm text-muted-foreground">
                  <p>&copy; 2024 OSINT Visualizer. Built for ethical research purposes.</p>
                </div>
              </div>
            </footer>
          </div>
        </div>
      </body>
    </html>
  )
}