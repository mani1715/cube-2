"""Phase 9.2 - SEO & Sitemap Generation"""
from fastapi import APIRouter, HTTPException, Response
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

phase9_seo_router = APIRouter(
    prefix="/api/phase9/seo",
    tags=["Phase 9.2 - SEO"]
)


@phase9_seo_router.get("/sitemap.xml", response_class=Response)
async def generate_sitemap():
    """
    Generate dynamic sitemap.xml for SEO.
    Includes all public pages, blogs, events, and careers.
    """
    try:
        base_url = os.environ.get('BASE_URL', 'https://rubiks-builder.preview.emergentagent.com')
        
        # Create XML structure
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Static pages with priority and change frequency
        static_pages = [
            {'loc': '/', 'priority': '1.0', 'changefreq': 'daily'},
            {'loc': '/about', 'priority': '0.8', 'changefreq': 'monthly'},
            {'loc': '/services', 'priority': '0.9', 'changefreq': 'weekly'},
            {'loc': '/book-session', 'priority': '0.9', 'changefreq': 'daily'},
            {'loc': '/events', 'priority': '0.8', 'changefreq': 'daily'},
            {'loc': '/blogs', 'priority': '0.8', 'changefreq': 'daily'},
            {'loc': '/careers', 'priority': '0.7', 'changefreq': 'weekly'},
            {'loc': '/volunteer', 'priority': '0.7', 'changefreq': 'monthly'},
            {'loc': '/psychologist-portal', 'priority': '0.7', 'changefreq': 'monthly'},
            {'loc': '/privacy', 'priority': '0.5', 'changefreq': 'yearly'},
            {'loc': '/terms', 'priority': '0.5', 'changefreq': 'yearly'},
        ]
        
        for page in static_pages:
            url = ET.SubElement(urlset, 'url')
            loc = ET.SubElement(url, 'loc')
            loc.text = f"{base_url}{page['loc']}"
            
            lastmod = ET.SubElement(url, 'lastmod')
            lastmod.text = datetime.utcnow().strftime('%Y-%m-%d')
            
            changefreq = ET.SubElement(url, 'changefreq')
            changefreq.text = page['changefreq']
            
            priority = ET.SubElement(url, 'priority')
            priority.text = page['priority']
        
        # Dynamic content from database
        try:
            mongo_url = os.environ.get('MONGO_URL')
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ.get('DB_NAME')]
            
            # Add published blogs
            blogs = await db.blogs.find({'status': 'published'}).limit(100).to_list(100)
            for blog in blogs:
                url = ET.SubElement(urlset, 'url')
                loc = ET.SubElement(url, 'loc')
                loc.text = f"{base_url}/blogs/{blog.get('id', '')}"
                
                lastmod = ET.SubElement(url, 'lastmod')
                blog_date = blog.get('date', datetime.utcnow())
                if isinstance(blog_date, str):
                    lastmod.text = blog_date[:10]
                else:
                    lastmod.text = blog_date.strftime('%Y-%m-%d')
                
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = 'weekly'
                
                priority = ET.SubElement(url, 'priority')
                priority.text = '0.7'
            
            # Add active events
            events = await db.events.find({'is_active': True}).limit(50).to_list(50)
            for event in events:
                url = ET.SubElement(urlset, 'url')
                loc = ET.SubElement(url, 'loc')
                loc.text = f"{base_url}/events/{event.get('id', '')}"
                
                lastmod = ET.SubElement(url, 'lastmod')
                event_date = event.get('date', datetime.utcnow())
                if isinstance(event_date, str):
                    lastmod.text = event_date[:10]
                else:
                    lastmod.text = event_date.strftime('%Y-%m-%d')
                
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = 'daily'
                
                priority = ET.SubElement(url, 'priority')
                priority.text = '0.8'
            
            # Add active job postings
            jobs = await db.careers.find({'is_active': True}).limit(30).to_list(30)
            for job in jobs:
                url = ET.SubElement(urlset, 'url')
                loc = ET.SubElement(url, 'loc')
                loc.text = f"{base_url}/careers/{job.get('id', '')}"
                
                lastmod = ET.SubElement(url, 'lastmod')
                posted_at = job.get('posted_at', datetime.utcnow())
                if isinstance(posted_at, str):
                    lastmod.text = posted_at[:10]
                else:
                    lastmod.text = posted_at.strftime('%Y-%m-%d')
                
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = 'weekly'
                
                priority = ET.SubElement(url, 'priority')
                priority.text = '0.6'
            
            client.close()
            
        except Exception as e:
            print(f"Error fetching dynamic content for sitemap: {e}")
        
        # Generate XML string
        xml_string = ET.tostring(urlset, encoding='unicode', method='xml')
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        
        return Response(
            content=xml_declaration + xml_string,
            media_type='application/xml'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sitemap: {str(e)}")


@phase9_seo_router.get("/robots.txt", response_class=Response)
async def generate_robots_txt():
    """
    Generate robots.txt for search engine crawlers.
    """
    base_url = os.environ.get('BASE_URL', 'https://rubiks-builder.preview.emergentagent.com')
    
    robots_content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /admin/*
Disallow: /api/admin/

Sitemap: {base_url}/api/phase9/seo/sitemap.xml
"""
    
    return Response(content=robots_content, media_type='text/plain')
