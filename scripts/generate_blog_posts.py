#!/usr/bin/env python3
import json
import markdown
from pathlib import Path
import glob
import os

def load_posts():
    blog_dir = Path(__file__).parent.parent / "blog"
    with open(blog_dir / "posts.json") as f:
        return json.load(f)

def find_post_file(slug):
    posts_dir = Path(__file__).parent.parent / "blog" / "posts"
    # Look for files that end with the slug
    matches = list(posts_dir.glob(f"*{slug}.md"))
    if matches:
        return matches[0]
    return None

def read_post_content(slug):
    md_file = find_post_file(slug)
    if md_file and md_file.exists():
        with open(md_file, 'r') as f:
            return f.read()
    raise FileNotFoundError(f"Could not find markdown file for slug: {slug}")

def generate_post_html(post, content):
    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-BRQ8Q6W8N8"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-BRQ8Q6W8N8');
    </script>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post['title']} | KU Automation Blog</title>
    <meta name="description" content="{post['excerpt']}">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://ai-automation-agency-gilt.vercel.app/blog-post.html?slug={post['slug']}">
    <meta property="og:title" content="{post['title']}">
    <meta property="og:description" content="{post['excerpt']}">
    <meta property="og:image" content="{post['image']}">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{post['title']}">
    <meta name="twitter:description" content="{post['excerpt']}">
    <meta name="twitter:image" content="{post['image']}">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{ sans: ['Inter', 'sans-serif'] }},
                    colors: {{
                        primary: {{ 50: '#eef2ff', 100: '#e0e7ff', 200: '#c7d2fe', 300: '#a5b4fc', 400: '#818cf8', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca', 800: '#3730a3', 900: '#312e81' }},
                    }}
                }}
            }}
        }}
    </script>
    
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .gradient-text {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .nav-blur {{ backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }}
        .prose {{ max-width: 65ch; margin: 0 auto; }}
        .prose h1 {{ color: #111827; font-size: 2.25rem; margin-top: 0; margin-bottom: 2rem; font-weight: 800; }}
        .prose h2 {{ color: #1f2937; font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; font-weight: 700; }}
        .prose h3 {{ color: #374151; font-size: 1.25rem; margin-top: 1.5rem; margin-bottom: 0.75rem; font-weight: 600; }}
        .prose p {{ color: #4b5563; margin-bottom: 1.25rem; line-height: 1.75; }}
        .prose ul {{ margin-top: 1.25rem; margin-bottom: 1.25rem; }}
        .prose li {{ margin-top: 0.5rem; margin-bottom: 0.5rem; }}
        .prose a {{ color: #4f46e5; text-decoration: underline; }}
        .prose a:hover {{ color: #4338ca; }}
        .prose blockquote {{ border-left: 4px solid #e5e7eb; padding-left: 1rem; margin-left: 0; margin-right: 0; font-style: italic; color: #6b7280; }}
        .prose code {{ background: #f3f4f6; padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-size: 0.875rem; }}
        .prose pre {{ background: #1f2937; color: #f3f4f6; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }}
        .prose pre code {{ background: transparent; padding: 0; color: inherit; }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="fixed w-full z-50 nav-blur bg-white/80 border-b border-gray-100">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center h-16">
                <a href="index.html" class="flex items-center space-x-2">
                    <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
                        <span class="text-white font-bold text-sm">KU</span>
                    </div>
                    <span class="font-bold text-xl text-gray-900">KU Automation</span>
                </a>
                <div class="hidden md:flex items-center space-x-8">
                    <a href="index.html#solutions" class="text-gray-600 hover:text-primary-600 transition">Solutions</a>
                    <a href="use-cases.html" class="text-gray-600 hover:text-primary-600 transition">Use Cases</a>
                    <a href="pricing.html" class="text-gray-600 hover:text-primary-600 transition">Pricing</a>
                    <a href="blog.html" class="text-primary-600 font-medium">Blog</a>
                    <a href="index.html#contact" class="bg-primary-600 text-white px-5 py-2 rounded-lg hover:bg-primary-700 transition font-medium">Get Started</a>
                </div>
                <button id="mobile-menu-btn" class="md:hidden p-2">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                    </svg>
                </button>
            </div>
        </div>
        <!-- Mobile menu -->
        <div id="mobile-menu" class="hidden md:hidden bg-white border-t">
            <div class="px-4 py-4 space-y-3">
                <a href="index.html#solutions" class="block text-gray-600 hover:text-primary-600">Solutions</a>
                <a href="use-cases.html" class="block text-gray-600 hover:text-primary-600">Use Cases</a>
                <a href="pricing.html" class="block text-gray-600 hover:text-primary-600">Pricing</a>
                <a href="blog.html" class="block text-primary-600 font-medium">Blog</a>
                <a href="index.html#contact" class="block bg-primary-600 text-white px-4 py-2 rounded-lg text-center">Get Started</a>
            </div>
        </div>
    </nav>

    <!-- Article -->
    <main class="pt-32 pb-16">
        <article class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Hero -->
            <div class="mb-8">
                <div class="flex flex-wrap gap-2 mb-4">
                    {' '.join([f'<span class="bg-primary-50 text-primary-600 text-xs font-medium px-2 py-1 rounded">{tag}</span>' for tag in post['tags']])}
                </div>
                <h1 class="text-4xl font-bold text-gray-900 mb-4">{post['title']}</h1>
                <div class="flex items-center justify-between text-gray-500 text-sm">
                    <div class="flex items-center space-x-4">
                        <img src="{post['author']['avatar']}" alt="{post['author']['name']}" class="w-10 h-10 rounded-full">
                        <div>
                            <p class="font-medium text-gray-900">{post['author']['name']}</p>
                            <p>{post['author']['title']}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p>{post['date']}</p>
                        <p>{post['readTime']} min read</p>
                    </div>
                </div>
            </div>
            
            <!-- Featured Image -->
            <img src="{post['image']}" alt="{post['title']}" class="w-full rounded-xl mb-12">
            
            <!-- Content -->
            <div class="prose">
                {html_content}
            </div>
            
            <!-- Author Bio -->
            <div class="mt-16 pt-8 border-t">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">About the Author</h3>
                <div class="flex items-start space-x-4">
                    <img src="{post['author']['avatar']}" alt="{post['author']['name']}" class="w-16 h-16 rounded-full">
                    <div>
                        <p class="font-medium text-gray-900">{post['author']['name']}</p>
                        <p class="text-gray-500 mb-4">{post['author']['bio']}</p>
                        <a href="{post['author']['linkedin']}" target="_blank" rel="noopener" class="text-primary-600 hover:text-primary-700 font-medium flex items-center">
                            Connect on LinkedIn
                            <svg class="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
            
            <!-- CTA -->
            <div class="mt-16 bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl p-8 text-white text-center">
                <h3 class="text-2xl font-bold mb-4">Ready to Automate Your Engineering Workflows?</h3>
                <p class="mb-6 text-primary-100">Book a free consultation to discuss your specific needs and see AI automation in action.</p>
                <a href="index.html#contact" class="inline-block bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">Schedule Demo</a>
            </div>
        </article>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-400 py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid md:grid-cols-4 gap-8 mb-8">
                <div>
                    <div class="flex items-center space-x-2 mb-4">
                        <div class="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <span class="text-white font-bold text-sm">KU</span>
                        </div>
                        <span class="font-bold text-xl text-white">KU Automation</span>
                    </div>
                    <p class="text-sm">AI-powered automation for engineering companies. Built by engineers, for engineers.</p>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4">Solutions</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="use-cases.html#document-processing" class="hover:text-white transition">Document Processing</a></li>
                        <li><a href="use-cases.html#rfq-automation" class="hover:text-white transition">RFQ Automation</a></li>
                        <li><a href="use-cases.html#knowledge-base" class="hover:text-white transition">Knowledge Base AI</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4">Resources</h4>
                    <ul class="space-y-2 text-sm">
                        <li><a href="blog.html" class="hover:text-white transition">Blog</a></li>
                        <li><a href="demos.html" class="hover:text-white transition">Live Demos</a></li>
                        <li><a href="roi-calculator.html" class="hover:text-white transition">ROI Calculator</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="text-white font-semibold mb-4">Contact</h4>
                    <ul class="space-y-2 text-sm">
                        <li>kingsley.uzowulu@ku-automation.com</li>
                        <li><a href="https://linkedin.com/in/kingsleyuzowulu" class="hover:text-white transition">LinkedIn</a></li>
                    </ul>
                </div>
            </div>
            <div class="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center">
                <p class="text-sm">&copy; 2026 KU Automation. All rights reserved.</p>
                <div class="flex space-x-6 mt-4 md:mt-0">
                    <a href="legal/privacy.html" class="text-sm hover:text-white transition">Privacy Policy</a>
                    <a href="legal/terms.html" class="text-sm hover:text-white transition">Terms of Service</a>
                </div>
            </div>
        </div>
    </footer>

    <script>
        // Mobile menu toggle
        document.getElementById('mobile-menu-btn').addEventListener('click', () => {{
            document.getElementById('mobile-menu').classList.toggle('hidden');
        }});
    </script>
</body>
</html>'''

def main():
    data = load_posts()
    output_dir = Path(__file__).parent.parent
    
    # Generate post pages
    for post in data['posts']:
        if post.get('published'):
            try:
                content = read_post_content(post['slug'])
                html = generate_post_html(post, content)
                
                # Save as individual HTML file
                with open(output_dir / f"blog-post-{post['slug']}.html", 'w') as f:
                    f.write(html)
                print(f"✅ Generated blog-post-{post['slug']}.html")
            except Exception as e:
                print(f"❌ Error generating {post['slug']}: {str(e)}")

if __name__ == "__main__":
    main()