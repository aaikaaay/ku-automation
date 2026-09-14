const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');
const { marked } = require('marked');
const { markedHighlight } = require('marked-highlight');
const hljs = require('highlight.js');
const { JSDOM } = require('jsdom'); // For DOM manipulation

// Define paths
const PROJECT_ROOT = process.cwd();
const POSTS_DIR = path.join(PROJECT_ROOT, 'blog', 'posts');
const OUTPUT_DIR = path.join(PROJECT_ROOT, 'blog');
const BLOG_JSON_PATH = path.join(PROJECT_ROOT, 'blog', 'posts.json');
const TEMPLATE_PATH = path.join(PROJECT_ROOT, 'blog-post-agentic-ai-for-engineering-autonomous-workflows-that-actually-work.html');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Custom renderer for code blocks to handle Mermaid
const customRenderer = new marked.Renderer();
customRenderer.code = (code, lang) => {
    if (lang === 'mermaid') {
        return `<pre class="mermaid">${code}</pre>`; // Render mermaid block client-side
    }

    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    const highlightedCode = hljs.highlight(code, { language }).value;
    return `<pre><code class="hljs language-${language}">${highlightedCode}</code></pre>`;
};

// Configure marked
marked.use(markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    }
}));
marked.use({
    gfm: true, // Enable GitHub Flavored Markdown
    renderer: customRenderer,
});


async function buildBlogPosts() {
    console.log('Starting blog post generation...');

    const postsData = JSON.parse(fs.readFileSync(BLOG_JSON_PATH, 'utf8'));
    const templateHtml = fs.readFileSync(TEMPLATE_PATH, 'utf8');

    const publishedPosts = postsData.posts.filter(post => post.published);
    const failures = [];
    let successCount = 0;

    for (const post of publishedPosts) {
        try {
        console.log(`Processing post: ${post.slug}`);
        const markdownFilePath = path.join(POSTS_DIR, `${post.slug}.md`);

        if (!fs.existsSync(markdownFilePath)) {
            console.warn(`Markdown file not found for slug: ${post.slug}. Skipping.`);
            failures.push({ slug: post.slug, reason: 'markdown file missing' });
            continue;
        }

        const markdownContent = fs.readFileSync(markdownFilePath, 'utf8');
        let content, frontmatter;
        try {
            const parsed = matter(markdownContent);
            content = parsed.content;
            frontmatter = parsed.data;
        } catch (yamlErr) {
            // YAML broken in .md frontmatter — fall back to posts.json metadata + strip frontmatter block
            console.warn(`YAML parse failed for ${post.slug}: ${yamlErr.message}. Using posts.json metadata only.`);
            const stripped = markdownContent.replace(/^---[\s\S]*?---\n?/, '');
            content = stripped;
            frontmatter = {};
        }
        
        // Ensure post object has all necessary data from posts.json,
        // prioritizing posts.json for consistent metadata
        const postData = { ...post, ...frontmatter };

        const postHtmlContent = marked.parse(content);

        // Create a DOM from the template to manipulate it
        const dom = new JSDOM(templateHtml);
        const document = dom.window.document;

        // --- SEO Metadata ---
        document.title = `${postData.title} | KU Automation Blog`;
        document.querySelector('meta[name="description"]').setAttribute('content', postData.excerpt);
        document.querySelector('meta[property="og:url"]').setAttribute('content', `https://www.ku-automation.com/blog/${postData.slug}`);
        document.querySelector('meta[property="og:title"]').setAttribute('content', postData.title);
        document.querySelector('meta[property="og:description"]').setAttribute('content', postData.excerpt);
        document.querySelector('meta[property="og:image"]').setAttribute('content', `https://www.ku-automation.com${postData.image}`);
        document.querySelector('meta[name="twitter:title"]').setAttribute('content', postData.title);
        document.querySelector('meta[name="twitter:description"]').setAttribute('content', postData.excerpt);
        document.querySelector('meta[name="twitter:image"]').setAttribute('content', `https://www.ku-automation.com${postData.image}`);
        
        // Add JSON-LD Article Schema
        const jsonLd = document.createElement('script');
        jsonLd.type = 'application/ld+json';
        jsonLd.textContent = JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": postData.title,
            "description": postData.excerpt,
            "image": `https://www.ku-automation.com${postData.image}`,
            "datePublished": postData.date,
            "dateModified": postData.modified || postData.date,
            "author": {
                "@type": "Person",
                "name": postData.author.name,
                "url": postData.author.linkedin
            },
            "publisher": {
                "@type": "Organization",
                "name": "KU Automation",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://www.ku-automation.com/assets/favicon-32x32.png"
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": `https://www.ku-automation.com/blog/${postData.slug}`
            }
        });
        document.head.appendChild(jsonLd);


        // --- Article Content Injection ---
        // Tags
        const tagsContainer = document.querySelector('article .flex.flex-wrap.gap-2.mb-4');
        tagsContainer.innerHTML = ''; // Clear existing tags
        postData.tags.forEach(tag => {
            const span = document.createElement('span');
            span.className = 'bg-primary-50 text-primary-600 text-xs font-medium px-2 py-1 rounded';
            span.textContent = tag;
            tagsContainer.appendChild(span);
        });

        // Title
        document.querySelector('article h1').textContent = postData.title;

        // Author Info
        const authorAvatar = document.querySelector('article .flex.items-center.space-x-4 img');
        authorAvatar.src = postData.author.avatar;
        authorAvatar.alt = postData.author.name;
        document.querySelector('article .flex.items-center.space-x-4 p.font-medium').textContent = postData.author.name;
        document.querySelector('article .flex.items-center.space-x-4 p:last-child').textContent = postData.author.title;

        // Date and Read Time
        document.querySelector('article .text-right p:first-child').textContent = postData.date;
        document.querySelector('article .text-right p:last-child').textContent = `${postData.readTime} min read`;

        // Featured Image
        const featuredImage = document.querySelector('article > img');
        featuredImage.src = postData.image.startsWith('http') ? postData.image : `https://www.ku-automation.com${postData.image}`; // Handle absolute vs relative image paths
        featuredImage.alt = postData.title;

        // Main Content
        document.querySelector('article .prose').innerHTML = postHtmlContent;

        // --- Author Bio Box ---
        const bioAvatar = document.querySelector('.mt-16.pt-8.border-t img');
        bioAvatar.src = postData.author.avatar;
        bioAvatar.alt = postData.author.name;
        document.querySelector('.mt-16.pt-8.border-t p.font-medium').textContent = postData.author.name;
        document.querySelector('.mt-16.pt-8.border-t p.text-gray-500').textContent = postData.author.bio;
        document.querySelector('.mt-16.pt-8.border-t a').href = postData.author.linkedin;

        // --- Related Posts (Placeholder for now) ---
        // This part needs more complex logic to filter and display related posts.
        // For now, I'll leave the template's existing placeholder/remove it if it exists.
        // I will add a script to initialize Mermaid client-side.
        const body = document.body;
        const mermaidScript = document.createElement('script');
        mermaidScript.type = 'module';
        mermaidScript.textContent = `
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({ startOnLoad: true });
        `;
        body.appendChild(mermaidScript);


        // Output paths
        const postOutputDir = path.join(OUTPUT_DIR, postData.slug);
        if (!fs.existsSync(postOutputDir)) {
            fs.mkdirSync(postOutputDir, { recursive: true });
        }

        const outputPathIndex = path.join(postOutputDir, 'index.html');
        const outputPathFallback = path.join(OUTPUT_DIR, `${postData.slug}.html`);

        const finalHtml = dom.serialize();
        fs.writeFileSync(outputPathIndex, finalHtml, 'utf8');
        fs.writeFileSync(outputPathFallback, finalHtml, 'utf8');

        console.log(`Generated: ${outputPathIndex}`);
        console.log(`Generated: ${outputPathFallback}`);
        successCount++;
        } catch (postErr) {
            console.error(`FAILED ${post.slug}: ${postErr.message}`);
            failures.push({ slug: post.slug, reason: postErr.message });
        }
    }

    console.log(`\n=== Blog post generation complete. ===`);
    console.log(`Success: ${successCount} / ${publishedPosts.length}`);
    if (failures.length) {
        console.log(`\nFailures (${failures.length}):`);
        failures.forEach(f => console.log(`  - ${f.slug}: ${f.reason}`));
    }
}

buildBlogPosts().catch(console.error);
