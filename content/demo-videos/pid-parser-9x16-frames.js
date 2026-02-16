const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = '/Users/kingsleysmac/.openclaw/workspace/projects/ai-automation-agency/content/demo-videos/pid-parser-9x16';

// Frame templates for vertical video (9:16)
const frames = [
    {
        name: 'frame_001_intro',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:72px;font-weight:800;text-align:center;margin-bottom:40px;">
                <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">P&ID Parser</span>
            </div>
            <div style="font-size:36px;color:#888;text-align:center;">AI-Powered<br>Document Extraction</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_002_problem',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:32px;color:#888;margin-bottom:40px;text-transform:uppercase;letter-spacing:4px;">The Problem</div>
            <div style="font-size:120px;font-weight:800;color:#ef4444;margin-bottom:20px;">3-4</div>
            <div style="font-size:48px;color:#ef4444;margin-bottom:40px;">DAYS</div>
            <div style="font-size:36px;color:#888;text-align:center;">Manual P&ID<br>data extraction</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_003_solution',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:32px;color:#888;margin-bottom:40px;text-transform:uppercase;letter-spacing:4px;">With AI</div>
            <div style="font-size:120px;font-weight:800;color:#4ade80;margin-bottom:20px;">2-3</div>
            <div style="font-size:48px;color:#4ade80;margin-bottom:40px;">HOURS</div>
            <div style="font-size:36px;color:#888;text-align:center;">Same results<br>90% faster</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_004_step1',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:28px;color:#6366f1;margin-bottom:30px;">STEP 1</div>
            <div style="font-size:48px;font-weight:700;text-align:center;margin-bottom:60px;">Upload Your<br>P&ID</div>
            <div style="width:400px;height:300px;border:3px dashed #6366f1;border-radius:30px;display:flex;flex-direction:column;justify-content:center;align-items:center;background:rgba(99,102,241,0.1);">
                <div style="font-size:80px;margin-bottom:20px;">📄</div>
                <div style="font-size:28px;color:#6366f1;text-align:center;">Drop file here</div>
            </div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_005_step2',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:28px;color:#6366f1;margin-bottom:30px;">STEP 2</div>
            <div style="font-size:48px;font-weight:700;text-align:center;margin-bottom:60px;">AI Extracts<br>Everything</div>
            <div style="display:flex;flex-direction:column;gap:30px;">
                <div style="display:flex;align-items:center;gap:20px;">
                    <div style="font-size:50px;">🔍</div>
                    <div style="font-size:28px;color:#888;">Equipment Tags</div>
                </div>
                <div style="display:flex;align-items:center;gap:20px;">
                    <div style="font-size:50px;">⚙️</div>
                    <div style="font-size:28px;color:#888;">Valves</div>
                </div>
                <div style="display:flex;align-items:center;gap:20px;">
                    <div style="font-size:50px;">📊</div>
                    <div style="font-size:28px;color:#888;">Instruments</div>
                </div>
                <div style="display:flex;align-items:center;gap:20px;">
                    <div style="font-size:50px;">🔗</div>
                    <div style="font-size:28px;color:#888;">Line Data</div>
                </div>
            </div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_006_step3',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:28px;color:#6366f1;margin-bottom:30px;">STEP 3</div>
            <div style="font-size:48px;font-weight:700;text-align:center;margin-bottom:60px;">Export to<br>Excel</div>
            <div style="display:flex;flex-direction:column;gap:30px;">
                <div style="background:rgba(74,222,128,0.15);border:2px solid rgba(74,222,128,0.3);border-radius:15px;padding:25px 40px;text-align:center;">
                    <div style="font-size:28px;color:#4ade80;">📊 Equipment List</div>
                </div>
                <div style="background:rgba(74,222,128,0.15);border:2px solid rgba(74,222,128,0.3);border-radius:15px;padding:25px 40px;text-align:center;">
                    <div style="font-size:28px;color:#4ade80;">📋 Valve Schedule</div>
                </div>
                <div style="background:rgba(74,222,128,0.15);border:2px solid rgba(74,222,128,0.3);border-radius:15px;padding:25px 40px;text-align:center;">
                    <div style="font-size:28px;color:#4ade80;">📝 Line List</div>
                </div>
            </div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_007_result',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:56px;font-weight:800;text-align:center;margin-bottom:60px;">
                <span style="color:#4ade80;">90%</span><br>Time Saved
            </div>
            <div style="display:flex;gap:60px;margin-bottom:60px;">
                <div style="text-align:center;">
                    <div style="font-size:48px;font-weight:700;color:#ef4444;">3-4d</div>
                    <div style="font-size:20px;color:#888;">Before</div>
                </div>
                <div style="font-size:48px;color:#4ade80;">→</div>
                <div style="text-align:center;">
                    <div style="font-size:48px;font-weight:700;color:#4ade80;">2-3h</div>
                    <div style="font-size:20px;color:#888;">After</div>
                </div>
            </div>
            <div style="font-size:28px;color:#888;text-align:center;">Same accuracy<br>Fewer errors</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_008_cta',
        html: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:48px;font-weight:800;text-align:center;margin-bottom:50px;">
                Try It Free
            </div>
            <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:25px 50px;border-radius:20px;font-size:28px;font-weight:700;margin-bottom:40px;text-align:center;">
                ku-automation.com
            </div>
            <div style="font-size:24px;color:#888;text-align:center;">Built by engineers<br>for engineers</div>
            <div style="position:absolute;bottom:100px;display:flex;flex-direction:column;align-items:center;">
                <div style="font-size:36px;font-weight:800;">KU AUTOMATION</div>
                <div style="font-size:20px;color:#888;margin-top:10px;">Engineering Intelligence, Automated</div>
            </div>
        </div>`
    }
];

async function generateFrames() {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setViewport({ width: 1080, height: 1920 });
    
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    
    for (const frame of frames) {
        const fullHtml = `<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;">${frame.html}</body></html>`;
        await page.setContent(fullHtml);
        await page.screenshot({ path: path.join(OUTPUT_DIR, `${frame.name}.png`) });
        console.log(`Created: ${frame.name}.png`);
    }
    
    await browser.close();
    console.log(`\\nAll frames saved to: ${OUTPUT_DIR}`);
}

generateFrames().catch(console.error);
