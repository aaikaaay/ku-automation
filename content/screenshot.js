const puppeteer = require('puppeteer');
const path = require('path');

async function takeScreenshots() {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // Set viewport to LinkedIn carousel size (1080x1350)
    await page.setViewport({ width: 1080, height: 1350 });
    
    const slides = ['slide1.html', 'slide2.html', 'slide3.html', 'slide4.html', 'slide5.html'];
    const outputDir = path.join(__dirname, 'carousel-40-percent');
    
    for (const slide of slides) {
        const filePath = `file://${path.join(outputDir, slide)}`;
        console.log(`Taking screenshot of ${slide}...`);
        
        await page.goto(filePath, { waitUntil: 'networkidle0' });
        
        const outputPath = path.join(outputDir, slide.replace('.html', '.png'));
        await page.screenshot({ path: outputPath, type: 'png' });
        
        console.log(`Saved: ${outputPath}`);
    }
    
    await browser.close();
    console.log('All screenshots completed!');
}

takeScreenshots().catch(console.error);
