
import asyncio
import json
import re
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import requests
from bs4 import BeautifulSoup


@dataclass
class Profile:
    platform: str
    url: str
    username: str
    handle: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    links: List[str] = field(default_factory=list)
    avatar_url: Optional[str] = None
    page_title: Optional[str] = None
    page_text: Optional[str] = None
    domain: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    social_links: List[str] = field(default_factory=list)
    posts: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: Optional[str] = None
    
    scrape_status: str = 'unknown' #one of: ok, auth_gate, challenge, empty, error, unknown
    scrape_reason: Optional[str] = None

    def __post_init__(self):
        if self.scraped_at is None:
            from datetime import datetime
            self.scraped_at = datetime.now().isoformat()


class UniversalScraper:
    def __init__(self, use_playwright: bool = True, headless: bool = True):
        self.use_playwright = use_playwright
        self.headless = headless
        
        #Requests session for fallback
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        #Generic selectors to try on any site
        self.generic_selectors = {
            #Display name possibilities (ordered by specificity)
            'display_name': [
                'h1', 'h2.name', '.name', '.username', '.display-name', 
                '.profile-name', '.user-name', '.full-name', '.headline',
                '[data-testid*="name"]', '[data-testid*="title"]',
                '.vcard-fullname', '.p-name', '.fn'
            ],
            
            #Bio/description possibilities
            'bio': [
                '.bio', '.description', '.about', '.summary', '.intro',
                '.profile-description', '.user-bio', '.about-me',
                '[data-testid*="bio"]', '[data-testid*="description"]',
                '.p-note', '.user-summary', '.profile-summary'
            ],
            
            #Avatar/profile picture
            'avatar': [
                '.avatar img', '.profile-img', '.profile-picture img',
                '.user-avatar img', '.profile-photo img',
                'img[alt*="profile"]', 'img[alt*="avatar"]', 'img[alt*="photo"]',
                '.headshot img', '.user-image img'
            ],
            
            #Follower counts
            'followers': [
                '.followers', '.follower-count', '[data-testid*="follower"]',
                'a[href*="follower"] span', 'span[title*="follower"]',
                '.stat-followers', '.counter-followers'
            ],
            
            #Following counts  
            'following': [
                '.following', '.following-count', '[data-testid*="following"]',
                'a[href*="following"] span', 'span[title*="following"]',
                '.stat-following', '.counter-following'
            ],
            
            #Location
            'location': [
                '.location', '.geo', '.address', '.city',
                '[data-testid*="location"]', '.user-location',
                '.profile-location', '.vcard-location'
            ],
            
            #Social links
            'social_links': [
                'a[href*="github.com"]', 'a[href*="twitter.com"]', 'a[href*="x.com"]',
                'a[href*="linkedin.com"]', 'a[href*="instagram.com"]', 'a[href*="facebook.com"]',
                'a[href*="youtube.com"]', 'a[href*="tiktok.com"]', 'a[href*="medium.com"]'
            ],
            
            #Posts/content
            'posts': [
                'article', '.post', '.tweet', '.story', '.content-item',
                '.timeline-item', '.feed-item', '.activity-item'
            ]
        }

    def identify_platform(self, url: str):
        """Extract platform name from URL"""
        domain = urlparse(url).netloc.lower().replace('www.', '')
        return domain

    def extract_username_from_url(self, url: str):
        """Extract username from URL path"""
        path_parts = [p for p in url.split('/') if p and p not in ['http:', 'https:', '']]
        
        #Remove domain part
        if len(path_parts) > 1:
            #Common patterns: domain.com/username or domain.com/u/username
            if path_parts[1] in ['u', 'user', 'users', 'profile', 'in']:
                return path_parts[2] if len(path_parts) > 2 else path_parts[1]
            else:
                return path_parts[1]
        
        return path_parts[-1] if path_parts else 'unknown'

    def parse_number(self, text: str):
        """Parse follower counts with K, M, B suffixes"""
        if not text:
            return None
        
        #Extract numbers and suffixes
        clean_text = re.sub(r'[^\d.KMB,]', '', str(text).upper().replace(',', ''))
        
        if not clean_text:
            return None
        
        try:
            if 'K' in clean_text:
                return int(float(clean_text.replace('K', '')) * 1000)
            elif 'M' in clean_text:
                return int(float(clean_text.replace('M', '')) * 1000000)
            elif 'B' in clean_text:
                return int(float(clean_text.replace('B', '')) * 1000000000)
            else:
                return int(float(clean_text))
        except (ValueError, TypeError):
            #Try to extract just numbers
            numbers = re.findall(r'\d+', str(text))
            return int(numbers[0]) if numbers else None

    def normalize_url(self, url: str, base_url: str):
        """Convert relative URLs to absolute"""
        if not url:
            return url
        
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return urljoin(base_url, url)
        elif not url.startswith('http'):
            return urljoin(base_url, url)
        
        return url

    async def scrape_with_playwright(self, url: str):
        """Scrape using Playwright (reuses browser/context if you refactor later)"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            try:
                page = await context.new_page()
                #Navigate to page; use networkidle for JS-heavy sites
                await page.goto(url, wait_until='networkidle', timeout=45000)
                #Small wait for lazy content
                await page.wait_for_timeout(1000)
                #Try to dismiss cookie banners / easy popups
                await self._handle_common_popups(page)
                #Detect auth/login blocks ASAP
                blocked, reason = await self.detect_auth_block(page)
                platform = self.identify_platform(url)
                username = self.extract_username_from_url(url)
                #Create a minimal profile early so we can return with status
                profile = Profile(
                    platform=platform,
                    url=url,
                    username=username,
                    domain=urlparse(url).netloc,
                    page_title=await page.title() if await page.title() else None
                )

                if blocked:
                    profile.scrape_status = 'auth_gate'
                    profile.scrape_reason = reason
                    try:
                        body_text = await page.evaluate("() => document.documentElement.innerText")
                        profile.page_text = (body_text or "")[:1000]
                    except Exception:
                        profile.page_text = None
                    await browser.close()
                    return profile

                #If not blocked, proceed to extract the full content
                content = await page.content()
                page_title = await page.title()

                #Use evaluate to get the full page text reliably
                try:
                    page_text = await page.evaluate("() => document.documentElement.innerText")
                except Exception:
                    page_text = None

                #Extract profile data normally
                profile = await self._extract_profile_data(page, url, content, page_title)
                profile.page_text = page_text[:2000] if page_text else profile.page_text
                profile.scrape_status = 'ok'
                profile.scrape_reason = None

                return profile

            except PlaywrightTimeoutError:
                print(f"Timeout loading {url}")
                return None
            except Exception as e:
                print(f"Playwright error for {url}: {e}")
                return None
            finally:
                await browser.close()

    async def _handle_common_popups(self, page):
        """Handle common popups that block content"""
        popups_to_close = [
            'button:has-text("Accept")',
            'button:has-text("Accept All")',
            'button:has-text("Got it")',
            'button:has-text("Close")',
            '[aria-label="Close"]',
            '.cookie-banner button',
            '.modal-close',
            '[data-testid="close"]'
        ]
        
        for selector in popups_to_close:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    await element.click()
                    await page.wait_for_timeout(500)
                    break
            except:
                continue

    async def _extract_profile_data(self, page, url: str, content: str, page_title: str):
        """Extract profile data using generic selectors"""
        platform = self.identify_platform(url)
        username = self.extract_username_from_url(url)
        
        profile = Profile(
            platform=platform,
            url=url,
            username=username,
            domain=urlparse(url).netloc,
            page_title=page_title
        )
        
        #Try to extract each field using multiple selectors
        for field, selectors in self.generic_selectors.items():
            value = await self._try_extract_field(page, selectors, field)
            
            if field == 'display_name':
                profile.display_name = value
            elif field == 'bio':
                profile.bio = value
            elif field == 'avatar':
                profile.avatar_url = self.normalize_url(value, url) if value else None
            elif field == 'followers':
                profile.followers = self.parse_number(value)
            elif field == 'following':
                profile.following = self.parse_number(value)
            elif field == 'location':
                profile.location = value
            elif field == 'social_links':
                if isinstance(value, list):
                    profile.social_links = [self.normalize_url(link, url) for link in value if link]
            elif field == 'posts':
                if isinstance(value, list):
                    profile.posts = [{'content': post[:200]} for post in value[:5]]
        
        #Try to extract any links on the page
        try:
            links = await page.query_selector_all('a[href^="http"]')
            all_links = []
            for link in links[:20]:  #Limit to prevent spam
                href = await link.get_attribute('href')
                if href and urlparse(url).netloc not in href:
                    all_links.append(href)
            profile.links = list(set(all_links))  #Remove duplicates
        except:
            pass
        
        #Get page text for analysis
        try:
            page_text = await page.inner_text('body')
            profile.page_text = page_text[:1000] if page_text else None  #Limit size
        except:
            pass
        
        return profile

    async def _try_extract_field(self, page, selectors: List[str], field: str):
        """Try multiple selectors to extract a field"""
        for selector in selectors:
            try:
                if field == 'social_links':
                    #For social links, get all matches
                    elements = await page.query_selector_all(selector)
                    links = []
                    for elem in elements:
                        href = await elem.get_attribute('href')
                        if href:
                            links.append(href)
                    if links:
                        return links
                elif field == 'posts':
                    #For posts, get text content
                    elements = await page.query_selector_all(selector)
                    posts = []
                    for elem in elements[:10]:  #Limit posts
                        text = await elem.inner_text()
                        if text and len(text.strip()) > 10:
                            posts.append(text.strip())
                    if posts:
                        return posts
                else:
                    #For single values
                    element = await page.query_selector(selector)
                    if element:
                        if selector.endswith('img') or 'img' in selector:
                            #For images, get src attribute
                            src = await element.get_attribute('src')
                            if src:
                                return src
                        else:
                            #For text content
                            text = await element.inner_text()
                            if text and text.strip():
                                return text.strip()
            except Exception as e:
                continue
        
        return None

    async def detect_auth_block(self, page):
        url = page.url.lower()
        title = (await page.title()).lower()
        
        #URL redirect check
        if any(x in url for x in ["login", "signin", "auth"]):
            return True, "redirected_to_login"
        
        #Title check
        if any(x in title for x in ["sign in", "log in", "login", "sign up"]):
            return True, "login_title"
        
        #Password field check
        if await page.query_selector("input[type=password]"):
            return True, "password_input"
        
        #Very short page content
        body_text = await page.inner_text("body")
        if len(body_text.strip()) < 200:
            return True, "short_page"
        
        return False, "ok"


    async def scrape_profile(self, url: str):
        """Main scraping method - tries Playwright first, then requests"""
        print(f"Scraping: {url}")
        

        try:
            profile = await self.scrape_with_playwright(url)
            if profile:
                return profile
        except Exception as e:
            print(f"Playwright failed for {url}: {e}")
        

    async def batch_scrape(self, urls: List[str], delay: float = 3.0):
        """Scrape multiple URLs with rate limiting"""
        results = []
        
        print(f"Starting batch scrape of {len(urls)} URLs...")
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"\n[{i}/{len(urls)}] Processing: {url}")
                profile = await self.scrape_profile(url)
                if profile:
                    if profile.scrape_status == 'auth_gate':
                        print(f"Auth gate at {url}: {profile.scrape_reason}")
                        #save for manual review, or queue for storageState attempt
                    elif profile.scrape_status == 'ok':
                        print("Scraped normally")

                if profile:
                    results.append(profile)
                    print(f"Success: {profile.platform} - {profile.username}")
                    if profile.display_name:
                        print(f"  Name: {profile.display_name}")
                    if profile.bio:
                        print(f"  Bio: {profile.bio[:100]}...")
                    if profile.followers:
                        print(f"  Followers: {profile.followers:,}")
                else:
                    print("Failed to scrape")
                
                #Rate limiting
                if i < len(urls):
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        
        print(f"\n=== BATCH COMPLETE ===")
        print(f"Successfully scraped: {len(results)}/{len(urls)} profiles")
        return results

    def export_results(self, profiles: List[Profile], filename: str = 'scraped_profiles.json'):
        """Export results to JSON"""
        data = [asdict(profile) for profile in profiles]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"Results exported to {filename}")
        return data


async def test_scraper():
    """Test the scraper with various sites"""
    
    scraper = UniversalScraper(use_playwright=True, headless=True)  #Set to False to see browser
    
    #Test URLs 
    test_urls = [
        'https://github.com/torvalds',
        'https://www.linkedin.com/in/tristan-butcher-1881a5325/', #Auth block
        'https://twitter.com/elonmusk', #Requires JS
        'https://instagram.com/cristiano', #Requires JS
        'https://medium.com/@tim_cook',
        'https://dev.to/ben',
        #Add more test URLs here
    ]
    
    results = await scraper.batch_scrape(test_urls, delay=2.0)
    
    if results:
        for profile in results:
            print(f"\n{profile.platform} ({profile.url})")
            print(f"Username: {profile.username}")
            print(f"Display Name: {profile.display_name or 'Not found'}")
            print(f"Bio: {profile.bio[:150] if profile.bio else 'Not found'}...")
            print(f"Avatar: {'Found' if profile.avatar_url else 'Not found'}")
            print(f"Followers: {profile.followers if profile.followers else 'Not found'}")
            print(f"Social Links: {len(profile.social_links)}")
            print(f"Posts Found: {len(profile.posts)}")
        
        #Export results
        scraper.export_results(results, 'generic_scrape_results.json')
        



async def main():
    await test_scraper()


if __name__ == '__main__':
    asyncio.run(main())