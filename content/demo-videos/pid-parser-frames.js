const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = '/Users/kingsleysmac/.openclaw/workspace/projects/ai-automation-agency/content/demo-videos/pid-parser-16x9';

// Frame templates for the demo video
const frames = [
    {
        name: 'frame_001_intro',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:80px;font-weight:800;text-align:center;margin-bottom:30px;">
                <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">P&ID Parser</span>
            </div>
            <div style="font-size:42px;color:#888;">AI-Powered Document Extraction</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_002_problem',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:80px;">
            <div style="font-size:36px;color:#888;margin-bottom:40px;text-transform:uppercase;letter-spacing:4px;">The Problem</div>
            <div style="font-size:64px;font-weight:700;text-align:center;margin-bottom:50px;">
                Manual P&ID data extraction takes <span style="color:#ef4444;">3-4 days</span>
            </div>
            <div style="display:flex;gap:40px;font-size:32px;color:#999;">
                <div>📋 Copy from PDF</div>
                <div>→</div>
                <div>📝 Type into Excel</div>
                <div>→</div>
                <div>🔄 Repeat 500x</div>
                <div>→</div>
                <div>❌ Fix errors</div>
            </div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_003_solution',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:80px;">
            <div style="font-size:36px;color:#888;margin-bottom:40px;text-transform:uppercase;letter-spacing:4px;">The Solution</div>
            <div style="font-size:64px;font-weight:700;text-align:center;margin-bottom:50px;">
                AI extracts data in <span style="color:#4ade80;">2-3 hours</span>
            </div>
            <div style="display:flex;gap:40px;font-size:32px;color:#999;">
                <div>📤 Upload P&ID</div>
                <div>→</div>
                <div>🤖 AI Processes</div>
                <div>→</div>
                <div>📊 Review Data</div>
                <div>→</div>
                <div>✅ Export Excel</div>
            </div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_004_upload',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:28px;color:#888;margin-bottom:30px;">Step 1</div>
            <div style="font-size:56px;font-weight:700;margin-bottom:60px;">Upload Your P&ID</div>
            <div style="width:700px;height:400px;border:3px dashed #6366f1;border-radius:30px;display:flex;flex-direction:column;justify-content:center;align-items:center;background:rgba(99,102,241,0.1);">
                <div style="font-size:80px;margin-bottom:20px;">📄</div>
                <div style="font-size:32px;color:#6366f1;">Drop P&ID here or click to upload</div>
                <div style="font-size:24px;color:#666;margin-top:15px;">Supports PDF, PNG, JPG</div>
            </div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_005_processing',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:28px;color:#888;margin-bottom:30px;">Step 2</div>
            <div style="font-size:56px;font-weight:700;margin-bottom:60px;">AI Analyzes Your Document</div>
            <div style="display:flex;gap:60px;margin-bottom:40px;">
                <div style="text-align:center;">
                    <div style="font-size:60px;margin-bottom:15px;">🔍</div>
                    <div style="font-size:24px;color:#888;">Detecting<br>Equipment</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:60px;margin-bottom:15px;">⚙️</div>
                    <div style="font-size:24px;color:#888;">Reading<br>Valves</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:60px;margin-bottom:15px;">📊</div>
                    <div style="font-size:24px;color:#888;">Extracting<br>Instruments</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:60px;margin-bottom:15px;">🔗</div>
                    <div style="font-size:24px;color:#888;">Mapping<br>Lines</div>
                </div>
            </div>
            <div style="font-size:32px;color:#6366f1;">Processing... 47%</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_006_results',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:28px;color:#888;margin-bottom:20px;">Step 3</div>
            <div style="font-size:48px;font-weight:700;margin-bottom:40px;">Review Extracted Data</div>
            <div style="background:rgba(255,255,255,0.05);border-radius:20px;padding:30px;width:1200px;">
                <table style="width:100%;border-collapse:collapse;font-size:22px;">
                    <tr style="color:#6366f1;border-bottom:2px solid #333;">
                        <th style="padding:15px;text-align:left;">Tag</th>
                        <th style="padding:15px;text-align:left;">Type</th>
                        <th style="padding:15px;text-align:left;">Description</th>
                        <th style="padding:15px;text-align:left;">Line</th>
                        <th style="padding:15px;text-align:center;">Confidence</th>
                    </tr>
                    <tr style="border-bottom:1px solid #333;">
                        <td style="padding:15px;">V-101</td>
                        <td style="padding:15px;">Vessel</td>
                        <td style="padding:15px;">Separator Drum</td>
                        <td style="padding:15px;">6"-HC-001</td>
                        <td style="padding:15px;text-align:center;color:#4ade80;">98%</td>
                    </tr>
                    <tr style="border-bottom:1px solid #333;">
                        <td style="padding:15px;">P-101A/B</td>
                        <td style="padding:15px;">Pump</td>
                        <td style="padding:15px;">Transfer Pump</td>
                        <td style="padding:15px;">4"-HC-002</td>
                        <td style="padding:15px;text-align:center;color:#4ade80;">96%</td>
                    </tr>
                    <tr style="border-bottom:1px solid #333;">
                        <td style="padding:15px;">HV-1001</td>
                        <td style="padding:15px;">Valve</td>
                        <td style="padding:15px;">Hand Valve</td>
                        <td style="padding:15px;">6"-HC-001</td>
                        <td style="padding:15px;text-align:center;color:#4ade80;">99%</td>
                    </tr>
                    <tr>
                        <td style="padding:15px;">PT-1001</td>
                        <td style="padding:15px;">Instrument</td>
                        <td style="padding:15px;">Pressure Transmitter</td>
                        <td style="padding:15px;">—</td>
                        <td style="padding:15px;text-align:center;color:#4ade80;">97%</td>
                    </tr>
                </table>
            </div>
            <div style="margin-top:30px;font-size:24px;color:#888;">Found: 24 Equipment • 47 Valves • 31 Instruments • 18 Lines</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_007_export',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:28px;color:#888;margin-bottom:30px;">Step 4</div>
            <div style="font-size:56px;font-weight:700;margin-bottom:50px;">Export to Excel</div>
            <div style="display:flex;gap:40px;">
                <div style="background:rgba(74,222,128,0.15);border:2px solid rgba(74,222,128,0.3);border-radius:20px;padding:40px;text-align:center;">
                    <div style="font-size:60px;margin-bottom:15px;">📊</div>
                    <div style="font-size:28px;font-weight:600;color:#4ade80;">Equipment List</div>
                    <div style="font-size:20px;color:#888;margin-top:10px;">.xlsx</div>
                </div>
                <div style="background:rgba(74,222,128,0.15);border:2px solid rgba(74,222,128,0.3);border-radius:20px;padding:40px;text-align:center;">
                    <div style="font-size:60px;margin-bottom:15px;">📋</div>
                    <div style="font-size:28px;font-weight:600;color:#4ade80;">Valve Schedule</div>
                    <div style="font-size:20px;color:#888;margin-top:10px;">.xlsx</div>
                </div>
                <div style="background:rgba(74,222,128,0.15);border:2px solid rgba(74,222,128,0.3);border-radius:20px;padding:40px;text-align:center;">
                    <div style="font-size:60px;margin-bottom:15px;">📝</div>
                    <div style="font-size:28px;font-weight:600;color:#4ade80;">Line List</div>
                    <div style="font-size:20px;color:#888;margin-top:10px;">.xlsx</div>
                </div>
            </div>
            <div style="margin-top:50px;font-size:28px;color:#4ade80;">✓ Ready for download</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_008_comparison',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:48px;font-weight:700;margin-bottom:60px;">Time Saved</div>
            <div style="display:flex;gap:100px;margin-bottom:50px;">
                <div style="text-align:center;">
                    <div style="font-size:100px;font-weight:800;color:#ef4444;">3-4</div>
                    <div style="font-size:36px;color:#ef4444;">DAYS</div>
                    <div style="font-size:24px;color:#888;margin-top:15px;">Manual Process</div>
                </div>
                <div style="font-size:80px;color:#4ade80;display:flex;align-items:center;">→</div>
                <div style="text-align:center;">
                    <div style="font-size:100px;font-weight:800;color:#4ade80;">2-3</div>
                    <div style="font-size:36px;color:#4ade80;">HOURS</div>
                    <div style="font-size:24px;color:#888;margin-top:15px;">With AI</div>
                </div>
            </div>
            <div style="font-size:56px;font-weight:700;"><span style="color:#4ade80;">90%</span> Time Reduction</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`
    },
    {
        name: 'frame_009_cta',
        html: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:64px;font-weight:800;text-align:center;margin-bottom:50px;">
                Ready to <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">automate</span>?
            </div>
            <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:25px 60px;border-radius:20px;font-size:32px;font-weight:700;margin-bottom:40px;">
                Try the Demo → ku-automation.com
            </div>
            <div style="font-size:28px;color:#888;">Free consultation • No commitment • Results in weeks</div>
            <div style="position:absolute;bottom:80px;display:flex;flex-direction:column;align-items:center;">
                <div style="font-size:42px;font-weight:800;letter-spacing:2px;">KU AUTOMATION</div>
                <div style="font-size:22px;color:#888;margin-top:10px;">Engineering Intelligence, Automated</div>
            </div>
        </div>`
    }
];

async function generateFrames() {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
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
    console.log('\\nTo create video, run:');
    console.log(`ffmpeg -framerate 0.5 -pattern_type glob -i '${OUTPUT_DIR}/*.png' -c:v libx264 -pix_fmt yuv420p -vf "scale=1920:1080" ${OUTPUT_DIR}/pid-parser-demo.mp4`);
}

generateFrames().catch(console.error);
