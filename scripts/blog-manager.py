#!/usr/bin/env python3
"""
Blog Manager for KU Automation
==============================
CLI tool to manage blog posts, update sitemap, and deploy.

Usage:
    python blog-manager.py new "Post Title" --tags "AI,Engineering"
    python blog-manager.py list
    python blog-manager.py publish <slug>
    python blog-manager.py unpublish <slug>
    python blog-manager.py sitemap
    python blog-manager.py deploy
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
import argparse

# Configuration
BLOG_DIR = Path(__file__).parent.parent / "blog"
POSTS_JSON = BLOG_DIR / "posts.json"
POSTS_DIR = BLOG_DIR / "posts"
SITEMAP_PATH = Path(__file__).parent.parent / "sitemap.xml"
BASE_URL = "https://ai-automation-agency-gilt.vercel.app"

# Default author
DEFAULT_AUTHOR = {
    "name": "Kingsley Uzowulu",
    "title": "Founder & Lead Engineer, CEng MIMechE",
    "avatar": f"{BASE_URL}/assets/avatar-kingsley.png",
    "bio": "Chartered Engineer with 21+ years of experience in oil & gas, EPC, and manufacturing. Passionate about applying AI to solve real engineering challenges.",
    "linkedin": "https://linkedin.com/in/kingsleyuzowulu"
}


def slugify(title: str) -> str:
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def load_posts() -> dict:
    """Load posts from JSON file."""
    if POSTS_JSON.exists():
        with open(POSTS_JSON, 'r') as f:
            return json.load(f)
    return {"posts": []}


def save_posts(data: dict):
    """Save posts to JSON file."""
    with open(POSTS_JSON, 'w') as f:
        json.dump(data, f, indent=2)


def estimate_read_time(content: str) -> int:
    """Estimate reading time in minutes (200 wpm average)."""
    words = len(content.split())
    return max(1, round(words / 200))


def count_words(content: str) -> int:
    """Count words in content."""
    return len(content.split())


def create_post(title: str, tags: list, excerpt: str = "") -> str:
    """Create a new blog post."""
    slug = slugify(title)
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Check if slug exists
    data = load_posts()
    existing_slugs = [p["slug"] for p in data["posts"]]
    if slug in existing_slugs:
        print(f"⚠️  Post with slug '{slug}' already exists!")
        return None
    
    # Create markdown file
    md_path = POSTS_DIR / f"{slug}.md"
    template = f"""<!-- 
Title: {title}
Date: {date}
Tags: {', '.join(tags)}
-->

Write your introduction here. This first paragraph often becomes the excerpt.

## Section 1

Your content here...

## Section 2

More content...

## Conclusion

Wrap up with a call to action.

---

Ready to learn more? [Schedule a consultation](/index.html#contact) to discuss your specific needs.
"""
    
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(md_path, 'w') as f:
        f.write(template)
    
    # Add to posts.json (unpublished by default)
    new_post = {
        "slug": slug,
        "title": title,
        "excerpt": excerpt or f"Learn about {title.lower()}. Expert insights for engineering professionals.",
        "date": date,
        "modified": date,
        "published": False,
        "featured": False,
        "image": f"{BASE_URL}/assets/blog/{slug}.png",
        "tags": tags,
        "readTime": 5,
        "wordCount": 0,
        "author": DEFAULT_AUTHOR
    }
    
    data["posts"].insert(0, new_post)
    save_posts(data)
    
    print(f"✅ Created new post: {slug}")
    print(f"   📝 Edit: {md_path}")
    print(f"   🔖 Status: Draft (unpublished)")
    print(f"   ➡️  Publish with: python blog-manager.py publish {slug}")
    
    return slug


def list_posts():
    """List all blog posts."""
    data = load_posts()
    
    print("\n📚 Blog Posts")
    print("=" * 60)
    
    for post in data["posts"]:
        status = "✅" if post.get("published") else "📝"
        featured = "⭐" if post.get("featured") else "  "
        print(f"{status} {featured} {post['date']} | {post['title'][:40]}")
        print(f"      Slug: {post['slug']}")
        print(f"      Tags: {', '.join(post.get('tags', []))}")
        print()


def publish_post(slug: str):
    """Publish a post (set published=True and update metadata)."""
    data = load_posts()
    
    for post in data["posts"]:
        if post["slug"] == slug:
            # Read markdown to update metadata
            md_path = POSTS_DIR / f"{slug}.md"
            if md_path.exists():
                with open(md_path, 'r') as f:
                    content = f.read()
                post["readTime"] = estimate_read_time(content)
                post["wordCount"] = count_words(content)
            
            post["published"] = True
            post["modified"] = datetime.now().strftime("%Y-%m-%d")
            save_posts(data)
            
            print(f"✅ Published: {post['title']}")
            print(f"   🕐 Read time: {post['readTime']} min")
            print(f"   📊 Word count: {post['wordCount']}")
            
            # Prompt to update sitemap
            print(f"\n   ➡️  Update sitemap: python blog-manager.py sitemap")
            return
    
    print(f"❌ Post not found: {slug}")


def unpublish_post(slug: str):
    """Unpublish a post."""
    data = load_posts()
    
    for post in data["posts"]:
        if post["slug"] == slug:
            post["published"] = False
            save_posts(data)
            print(f"📝 Unpublished: {post['title']}")
            return
    
    print(f"❌ Post not found: {slug}")


def update_sitemap():
    """Regenerate sitemap.xml with all published posts."""
    data = load_posts()
    today = datetime.now().strftime("%Y-%m-%d")
    
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  
  <!-- Main Pages -->
  <url>
    <loc>{BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/use-cases.html</loc>
    <lastmod>2026-02-28</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/pricing.html</loc>
    <lastmod>2026-02-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/demos.html</loc>
    <lastmod>2026-02-17</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/roi-calculator.html</loc>
    <lastmod>2026-02-11</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/rfq-analyzer.html</loc>
    <lastmod>2026-02-11</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/datasheet-parser.html</loc>
    <lastmod>2026-02-11</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/pid-parser.html</loc>
    <lastmod>2026-02-18</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/knowledge-bot.html</loc>
    <lastmod>2026-02-11</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  
  <!-- Blog -->
  <url>
    <loc>{BASE_URL}/blog.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <!-- Blog Posts -->
'''
    
    # Add published posts
    for post in data["posts"]:
        if post.get("published"):
            # Escape special characters for XML
            title = post["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            sitemap += f'''  <url>
    <loc>{BASE_URL}/blog-post.html?slug={post["slug"]}</loc>
    <lastmod>{post.get("modified", post["date"])}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
    <news:news>
      <news:publication>
        <news:name>KU Automation Blog</news:name>
        <news:language>en</news:language>
      </news:publication>
      <news:publication_date>{post["date"]}</news:publication_date>
      <news:title>{title}</news:title>
    </news:news>
  </url>
  
'''
    
    sitemap += '''  <!-- Legal Pages -->
  <url>
    <loc>{BASE_URL}/legal/privacy.html</loc>
    <lastmod>2026-02-13</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  
  <url>
    <loc>{BASE_URL}/legal/terms.html</loc>
    <lastmod>2026-02-13</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  
</urlset>'''
    
    with open(SITEMAP_PATH, 'w') as f:
        f.write(sitemap.replace("{BASE_URL}", BASE_URL))
    
    published_count = len([p for p in data["posts"] if p.get("published")])
    print(f"✅ Updated sitemap.xml")
    print(f"   📄 {published_count} blog posts included")


def deploy():
    """Commit and push changes to trigger Vercel deployment."""
    project_dir = Path(__file__).parent.parent
    
    try:
        # Check for changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True
        )
        
        if not result.stdout.strip():
            print("ℹ️  No changes to deploy")
            return
        
        # Git add
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
        
        # Git commit
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(
            ["git", "commit", "-m", f"Blog update: {date}"],
            cwd=project_dir,
            check=True
        )
        
        # Git push
        subprocess.run(["git", "push"], cwd=project_dir, check=True)
        
        print("✅ Deployed successfully!")
        print("   🚀 Vercel will auto-deploy in ~1 minute")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="KU Automation Blog Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # New post
    new_parser = subparsers.add_parser("new", help="Create a new blog post")
    new_parser.add_argument("title", help="Post title")
    new_parser.add_argument("--tags", "-t", default="AI Automation,Engineering",
                           help="Comma-separated tags")
    new_parser.add_argument("--excerpt", "-e", default="",
                           help="Post excerpt/description")
    
    # List posts
    subparsers.add_parser("list", help="List all blog posts")
    
    # Publish
    pub_parser = subparsers.add_parser("publish", help="Publish a post")
    pub_parser.add_argument("slug", help="Post slug")
    
    # Unpublish
    unpub_parser = subparsers.add_parser("unpublish", help="Unpublish a post")
    unpub_parser.add_argument("slug", help="Post slug")
    
    # Sitemap
    subparsers.add_parser("sitemap", help="Update sitemap.xml")
    
    # Deploy
    subparsers.add_parser("deploy", help="Commit and push to deploy")
    
    args = parser.parse_args()
    
    if args.command == "new":
        tags = [t.strip() for t in args.tags.split(",")]
        create_post(args.title, tags, args.excerpt)
    elif args.command == "list":
        list_posts()
    elif args.command == "publish":
        publish_post(args.slug)
    elif args.command == "unpublish":
        unpublish_post(args.slug)
    elif args.command == "sitemap":
        update_sitemap()
    elif args.command == "deploy":
        deploy()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
