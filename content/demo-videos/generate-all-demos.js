const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const BASE_DIR = '/Users/kingsleysmac/.openclaw/workspace/projects/ai-automation-agency/content/demo-videos';

// Demo configurations
const demos = {
    'rfq-analyzer': {
        title: 'RFQ Analyzer',
        subtitle: 'AI-Powered Tender Analysis',
        problem: 'Manual RFQ review takes <span style="color:#ef4444;">2-3 days</span>',
        problemDays: '2-3',
        solution: 'AI analyzes in <span style="color:#4ade80;">30 minutes</span>',
        solutionTime: '30 min',
        steps: [
            { icon: '📤', text: 'Upload RFQ/Tender' },
            { icon: '🤖', text: 'AI Analyzes Requirements' },
            { icon: '📋', text: 'Extract Scope & Specs' },
            { icon: '💰', text: 'Flag Pricing Risks' }
        ],
        results: [
            { tag: 'Technical Specs', value: '147 items extracted', confidence: '96%' },
            { tag: 'Delivery Terms', value: 'FOB Houston, 12 weeks', confidence: '98%' },
            { tag: 'Payment Terms', value: 'Net 30, LC required', confidence: '99%' },
            { tag: 'Risk Flags', value: '3 clauses highlighted', confidence: '—' }
        ],
        exports: ['Requirements Matrix', 'Scope Checklist', 'Risk Report'],
        timeSaved: '95%',
        beforeTime: '2-3 days',
        afterTime: '30 min'
    },
    'datasheet-parser': {
        title: 'Datasheet Parser',
        subtitle: 'Extract Equipment Specifications',
        problem: 'Manual datasheet entry takes <span style="color:#ef4444;">hours per document</span>',
        problemDays: '4-6h',
        solution: 'AI extracts in <span style="color:#4ade80;">minutes</span>',
        solutionTime: '5 min',
        steps: [
            { icon: '📤', text: 'Upload Datasheets' },
            { icon: '🤖', text: 'AI Reads All Fields' },
            { icon: '📊', text: 'Map to Database' },
            { icon: '✅', text: 'Validate & Export' }
        ],
        results: [
            { tag: 'Design Pressure', value: '150 PSIG', confidence: '99%' },
            { tag: 'Design Temp', value: '-20°F to 300°F', confidence: '98%' },
            { tag: 'Material', value: 'A516 Gr.70', confidence: '97%' },
            { tag: 'Dimensions', value: '48" ID x 120" T/T', confidence: '96%' }
        ],
        exports: ['Equipment Database', 'Spec Comparison', 'Procurement List'],
        timeSaved: '90%',
        beforeTime: '4-6 hours',
        afterTime: '5 min'
    },
    'knowledge-bot': {
        title: 'Knowledge Bot',
        subtitle: 'AI Assistant for Your Docs',
        problem: 'Searching documents takes <span style="color:#ef4444;">hours</span>',
        problemDays: '2-3h',
        solution: 'AI answers in <span style="color:#4ade80;">seconds</span>',
        solutionTime: 'Instant',
        steps: [
            { icon: '📚', text: 'Upload Your Docs' },
            { icon: '🧠', text: 'AI Learns Content' },
            { icon: '💬', text: 'Ask Questions' },
            { icon: '📍', text: 'Get Cited Answers' }
        ],
        results: [
            { tag: 'Query', value: '"What is the max pressure for V-101?"', confidence: '' },
            { tag: 'Answer', value: '150 PSIG per Datasheet DS-V-101', confidence: '98%' },
            { tag: 'Source', value: 'Page 3, Section 2.1', confidence: '' },
            { tag: 'Related', value: '3 more references found', confidence: '' }
        ],
        exports: ['Q&A Export', 'Source Report', 'Knowledge Base'],
        timeSaved: '80%',
        beforeTime: '2-3 hours',
        afterTime: 'Seconds'
    },
    'roi-calculator': {
        title: 'ROI Calculator',
        subtitle: 'See Your Savings',
        problem: 'Unsure about <span style="color:#ef4444;">automation ROI?</span>',
        problemDays: '???',
        solution: 'Calculate your <span style="color:#4ade80;">exact savings</span>',
        solutionTime: '2 min',
        steps: [
            { icon: '👥', text: 'Enter Team Size' },
            { icon: '⏱️', text: 'Input Hours/Week' },
            { icon: '💰', text: 'Set Hourly Rate' },
            { icon: '📊', text: 'See ROI' }
        ],
        results: [
            { tag: 'Weekly Hours Saved', value: '25 hours', confidence: '' },
            { tag: 'Annual Savings', value: '$104,000', confidence: '' },
            { tag: 'Payback Period', value: '2.4 weeks', confidence: '' },
            { tag: 'Year 1 ROI', value: '2,080%', confidence: '' }
        ],
        exports: ['ROI Report', 'Business Case', 'Proposal Draft'],
        timeSaved: '20x',
        beforeTime: '$104k/yr',
        afterTime: 'Saved'
    }
};

function generateFrameHtml16x9(demo, frameType) {
    const d = demos[demo];
    
    const templates = {
        intro: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:80px;font-weight:800;text-align:center;margin-bottom:30px;">
                <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">${d.title}</span>
            </div>
            <div style="font-size:42px;color:#888;">${d.subtitle}</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        problem: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:80px;">
            <div style="font-size:36px;color:#888;margin-bottom:40px;text-transform:uppercase;letter-spacing:4px;">The Problem</div>
            <div style="font-size:64px;font-weight:700;text-align:center;margin-bottom:50px;">${d.problem}</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        solution: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:80px;">
            <div style="font-size:36px;color:#888;margin-bottom:40px;text-transform:uppercase;letter-spacing:4px;">The Solution</div>
            <div style="font-size:64px;font-weight:700;text-align:center;margin-bottom:50px;">${d.solution}</div>
            <div style="display:flex;gap:40px;font-size:32px;color:#999;">
                ${d.steps.map(s => `<div>${s.icon} ${s.text}</div>`).join('<div>→</div>')}
            </div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        results: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:48px;font-weight:700;margin-bottom:40px;">Results</div>
            <div style="background:rgba(255,255,255,0.05);border-radius:20px;padding:30px;width:1200px;">
                <table style="width:100%;border-collapse:collapse;font-size:24px;">
                    ${d.results.map(r => `
                    <tr style="border-bottom:1px solid #333;">
                        <td style="padding:15px;color:#6366f1;font-weight:600;">${r.tag}</td>
                        <td style="padding:15px;">${r.value}</td>
                        <td style="padding:15px;text-align:center;color:#4ade80;">${r.confidence}</td>
                    </tr>`).join('')}
                </table>
            </div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        comparison: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:48px;font-weight:700;margin-bottom:60px;">Time Saved</div>
            <div style="display:flex;gap:100px;margin-bottom:50px;">
                <div style="text-align:center;">
                    <div style="font-size:80px;font-weight:800;color:#ef4444;">${d.beforeTime}</div>
                    <div style="font-size:24px;color:#888;margin-top:15px;">Before</div>
                </div>
                <div style="font-size:80px;color:#4ade80;display:flex;align-items:center;">→</div>
                <div style="text-align:center;">
                    <div style="font-size:80px;font-weight:800;color:#4ade80;">${d.afterTime}</div>
                    <div style="font-size:24px;color:#888;margin-top:15px;">After</div>
                </div>
            </div>
            <div style="font-size:56px;font-weight:700;"><span style="color:#4ade80;">${d.timeSaved}</span> Time Saved</div>
            <div style="position:absolute;bottom:60px;font-size:28px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        cta: `
        <div style="width:1920px;height:1080px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;">
            <div style="font-size:64px;font-weight:800;text-align:center;margin-bottom:50px;">
                Ready to <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">automate</span>?
            </div>
            <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:25px 60px;border-radius:20px;font-size:32px;font-weight:700;margin-bottom:40px;">
                Try it free → ku-automation.com
            </div>
            <div style="font-size:28px;color:#888;">Free consultation • Quick setup • Real results</div>
            <div style="position:absolute;bottom:80px;display:flex;flex-direction:column;align-items:center;">
                <div style="font-size:42px;font-weight:800;letter-spacing:2px;">KU AUTOMATION</div>
                <div style="font-size:22px;color:#888;margin-top:10px;">Engineering Intelligence, Automated</div>
            </div>
        </div>`
    };
    
    return templates[frameType];
}

function generateFrameHtml9x16(demo, frameType) {
    const d = demos[demo];
    
    const templates = {
        intro: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:72px;font-weight:800;text-align:center;margin-bottom:40px;">
                <span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">${d.title}</span>
            </div>
            <div style="font-size:36px;color:#888;text-align:center;">${d.subtitle}</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        problem: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:32px;color:#888;margin-bottom:40px;text-transform:uppercase;">Before</div>
            <div style="font-size:100px;font-weight:800;color:#ef4444;margin-bottom:20px;">${d.problemDays}</div>
            <div style="font-size:36px;color:#888;text-align:center;">Manual process</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        solution: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:32px;color:#888;margin-bottom:40px;text-transform:uppercase;">After</div>
            <div style="font-size:100px;font-weight:800;color:#4ade80;margin-bottom:20px;">${d.solutionTime}</div>
            <div style="font-size:36px;color:#888;text-align:center;">With AI</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        steps: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:48px;font-weight:700;margin-bottom:60px;">How It Works</div>
            <div style="display:flex;flex-direction:column;gap:30px;">
                ${d.steps.map((s, i) => `
                <div style="display:flex;align-items:center;gap:20px;">
                    <div style="font-size:50px;">${s.icon}</div>
                    <div style="font-size:28px;color:#888;">${s.text}</div>
                </div>`).join('')}
            </div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        result: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:56px;font-weight:800;text-align:center;margin-bottom:60px;">
                <span style="color:#4ade80;">${d.timeSaved}</span><br>Time Saved
            </div>
            <div style="font-size:28px;color:#888;text-align:center;">Same quality<br>Fewer errors</div>
            <div style="position:absolute;bottom:100px;font-size:32px;color:#555;font-weight:600;">KU AUTOMATION</div>
        </div>`,
        
        cta: `
        <div style="width:1080px;height:1920px;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:Segoe UI,sans-serif;color:white;padding:60px;">
            <div style="font-size:48px;font-weight:800;text-align:center;margin-bottom:50px;">Try It Free</div>
            <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:25px 50px;border-radius:20px;font-size:28px;font-weight:700;margin-bottom:40px;text-align:center;">
                ku-automation.com
            </div>
            <div style="font-size:24px;color:#888;text-align:center;">Built by engineers<br>for engineers</div>
            <div style="position:absolute;bottom:100px;font-size:36px;font-weight:800;">KU AUTOMATION</div>
        </div>`
    };
    
    return templates[frameType];
}

async function generateDemoVideos(demoName) {
    const browser = await puppeteer.launch({ headless: 'new' });
    
    // Generate 16:9
    const dir16x9 = path.join(BASE_DIR, `${demoName}-16x9`);
    if (!fs.existsSync(dir16x9)) fs.mkdirSync(dir16x9, { recursive: true });
    
    const page16x9 = await browser.newPage();
    await page16x9.setViewport({ width: 1920, height: 1080 });
    
    const frames16x9 = ['intro', 'problem', 'solution', 'results', 'comparison', 'cta'];
    for (let i = 0; i < frames16x9.length; i++) {
        const html = generateFrameHtml16x9(demoName, frames16x9[i]);
        await page16x9.setContent(`<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;">${html}</body></html>`);
        await page16x9.screenshot({ path: path.join(dir16x9, `frame_${String(i+1).padStart(3,'0')}.png`) });
        console.log(`  16:9 frame ${i+1}/${frames16x9.length}`);
    }
    
    // Generate 9:16
    const dir9x16 = path.join(BASE_DIR, `${demoName}-9x16`);
    if (!fs.existsSync(dir9x16)) fs.mkdirSync(dir9x16, { recursive: true });
    
    const page9x16 = await browser.newPage();
    await page9x16.setViewport({ width: 1080, height: 1920 });
    
    const frames9x16 = ['intro', 'problem', 'solution', 'steps', 'result', 'cta'];
    for (let i = 0; i < frames9x16.length; i++) {
        const html = generateFrameHtml9x16(demoName, frames9x16[i]);
        await page9x16.setContent(`<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:0;">${html}</body></html>`);
        await page9x16.screenshot({ path: path.join(dir9x16, `frame_${String(i+1).padStart(3,'0')}.png`) });
        console.log(`  9:16 frame ${i+1}/${frames9x16.length}`);
    }
    
    await browser.close();
    
    // Compile videos with ffmpeg
    console.log(`  Compiling 16:9 video...`);
    execSync(`cd "${dir16x9}" && ffmpeg -y -framerate 1/3 -pattern_type glob -i '*.png' -c:v libx264 -r 30 -pix_fmt yuv420p "${demoName}-demo.mp4"`, { stdio: 'pipe' });
    
    console.log(`  Compiling 9:16 video...`);
    execSync(`cd "${dir9x16}" && ffmpeg -y -framerate 1/3 -pattern_type glob -i '*.png' -c:v libx264 -r 30 -pix_fmt yuv420p "${demoName}-demo-vertical.mp4"`, { stdio: 'pipe' });
    
    console.log(`✅ ${demoName} complete!`);
}

async function main() {
    const demoNames = Object.keys(demos);
    
    for (const demo of demoNames) {
        console.log(`\n📹 Creating ${demo}...`);
        await generateDemoVideos(demo);
    }
    
    console.log('\n🎉 All demos complete!');
}

main().catch(console.error);
