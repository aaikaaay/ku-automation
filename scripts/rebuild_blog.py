#!/usr/bin/env python3
import json
from pathlib import Path

def load_posts():
    blog_dir = Path(__file__).parent.parent / "blog"
    with open(blog_dir / "posts.json") as f:
        return json.load(f)

def generate_post_html(post):
    return f'''
<article class="bg-white rounded-xl overflow-hidden shadow-md card-hover">
    <a href="blog-post.html?slug={post['slug']}" class="block">
        <img src="{post['image']}" alt="{post['title']}" class="w-full h-48 object-cover">
        <div class="p-6">
            <div class="flex flex-wrap gap-2 mb-3">
                {' '.join([f'<span class="bg-primary-50 text-primary-600 text-xs font-medium px-2 py-1 rounded">{tag}</span>' for tag in post['tags'][:2]])}
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-2 line-clamp-2 hover:text-primary-600 transition">{post['title']}</h3>
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">{post['excerpt']}</p>
            <div class="flex items-center justify-between text-sm text-gray-500">
                <span>{post['date']}</span>
                <span>{post['readTime']} min read</span>
            </div>
        </div>
    </a>
</article>'''

def update_blog_html():
    # Load posts
    data = load_posts()
    published_posts = [p for p in data['posts'] if p.get('published')]
    
    # Read existing blog.html
    blog_html_path = Path(__file__).parent.parent / "blog.html"
    with open(blog_html_path, 'r') as f:
        content = f.read()
    
    # Find the posts grid div
    start = content.find('<div id="posts-grid"')
    end = content.find('</div>', start)
    grid_content = content[start:end]
    
    # Generate new grid content
    new_grid = '<div id="posts-grid" class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">'
    for post in published_posts:
        new_grid += generate_post_html(post)
    new_grid += '</div>'
    
    # Replace old grid with new
    new_content = content[:start] + new_grid + content[end+6:]
    
    # Write updated file
    with open(blog_html_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated blog.html with {len(published_posts)} posts")

if __name__ == "__main__":
    update_blog_html()