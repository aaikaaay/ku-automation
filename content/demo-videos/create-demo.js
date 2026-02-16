const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Demo video frame generator
async function createDemoFrames(demoName, url, outputDir, aspectRatio = '16:9') {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // Set viewport based on aspect ratio
    const viewport = aspectRatio === '16:9' 
        ? { width: 1920, height: 1080 }
        : { width: 1080, height: 1920 };
    
    await page.setViewport(viewport);
    
    // Ensure output directory exists
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    console.log(`Creating ${demoName} demo frames (${aspectRatio})...`);
    
    // Frame 1: Landing page
    await page.goto(url, { waitUntil: 'networkidle0' });
    await page.screenshot({ path: path.join(outputDir, 'frame_001.png') });
    console.log('Frame 1: Landing page captured');
    
    // Wait and capture more frames to simulate interaction
    await new Promise(r => setTimeout(r, 500));
    await page.screenshot({ path: path.join(outputDir, 'frame_002.png') });
    
    await browser.close();
    console.log(`Frames saved to ${outputDir}`);
}

// Create intro/outro frames with text
async function createTextFrame(text, subtitle, outputPath, aspectRatio = '16:9') {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    const viewport = aspectRatio === '16:9' 
        ? { width: 1920, height: 1080 }
        : { width: 1080, height: 1920 };
    
    await page.setViewport(viewport);
    
    const html = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                width: ${viewport.width}px;
                height: ${viewport.height}px;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                font-family: 'Segoe UI', sans-serif;
                color: white;
            }
            .title {
                font-size: ${aspectRatio === '16:9' ? '72px' : '64px'};
                font-weight: 800;
                text-align: center;
                margin-bottom: 30px;
                max-width: 80%;
            }
            .highlight {
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .subtitle {
                font-size: ${aspectRatio === '16:9' ? '36px' : '32px'};
                color: #888;
                text-align: center;
                max-width: 70%;
            }
            .logo {
                position: absolute;
                bottom: 60px;
                font-size: 32px;
                font-weight: 700;
                color: #555;
            }
        </style>
    </head>
    <body>
        <div class="title">${text}</div>
        <div class="subtitle">${subtitle}</div>
        <div class="logo">KU AUTOMATION</div>
    </body>
    </html>`;
    
    await page.setContent(html);
    await page.screenshot({ path: outputPath });
    await browser.close();
    console.log(`Text frame saved: ${outputPath}`);
}

// Main execution
async function main() {
    const baseDir = '/Users/kingsleysmac/.openclaw/workspace/projects/ai-automation-agency';
    const outputBase = path.join(baseDir, 'content/demo-videos');
    
    // Create P&ID Parser demo (16:9)
    const pidDir = path.join(outputBase, 'pid-parser-16x9');
    
    // Create intro frame
    await createTextFrame(
        '<span class="highlight">P&ID Parser</span> Demo',
        'Extract equipment data from P&ID diagrams in seconds',
        path.join(pidDir, 'frame_000_intro.png'),
        '16:9'
    );
    
    // Capture demo page
    await createDemoFrames(
        'P&ID Parser',
        `file://${path.join(baseDir, 'pid-parser.html')}`,
        pidDir,
        '16:9'
    );
    
    // Create outro frame
    await createTextFrame(
        '<span class="highlight">90%</span> Time Saved',
        'From days to hours. See it live at ku-automation.com',
        path.join(pidDir, 'frame_999_outro.png'),
        '16:9'
    );
    
    console.log('\\nAll frames created! Use ffmpeg to compile into video.');
}

main().catch(console.error);
