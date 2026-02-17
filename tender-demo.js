// AI Tender Response Demo - Interactive Simulation

const responseTemplates = {
    executive: {
        title: "Executive Summary",
        icon: "📋",
        content: `KU Automation is pleased to submit this proposal in response to your Request for Quotation. With over 21 years of engineering experience in oil & gas and EPC projects, we are uniquely positioned to deliver this scope with excellence.

**Key Highlights:**
• Full compliance with specified standards (ASME B31.3)
• Competitive pricing with transparent cost breakdown
• Proven track record in similar offshore applications
• Committed delivery timeline with milestone tracking`
    },
    technical: {
        title: "Technical Approach",
        icon: "⚙️",
        content: `**Scope Understanding:**
We have thoroughly reviewed the requirements for the produced water handling piping system and confirm our capability to meet all specifications.

**Proposed Solution:**
• Material: ASTM A106 Grade B seamless pipe as specified
• All welding per ASME Section IX with certified welders
• Full material traceability and MTCs provided
• Hydrostatic testing at 1.5x design pressure

**Quality Assurance:**
• ISO 9001:2015 certified manufacturing
• Third-party inspection available
• Complete documentation package included`
    },
    compliance: {
        title: "Compliance Matrix",
        icon: "✅",
        content: `| Requirement | Compliance | Notes |
|-------------|------------|-------|
| ASME B31.3 | ✅ FULL | All design per latest edition |
| Material Spec | ✅ FULL | ASTM A106 Gr.B certified |
| Design Pressure | ✅ FULL | 150 PSI with margin |
| Design Temp | ✅ FULL | 200°F rated |
| Delivery | ✅ FULL | 10 weeks (2 weeks early) |
| Documentation | ✅ FULL | Complete package |`
    },
    pricing: {
        title: "Commercial Summary",
        icon: "💰",
        content: `**Pricing Structure:**

| Item | Description | Amount |
|------|-------------|--------|
| 1 | Piping Materials (500m) | $XX,XXX |
| 2 | Fittings & Flanges | $XX,XXX |
| 3 | Supports & Hardware | $XX,XXX |
| 4 | Testing & Certification | $X,XXX |
| 5 | Documentation | Included |
| | **TOTAL** | **$XXX,XXX** |

*Pricing valid for 30 days. Delivery DDP Singapore.*

**Payment Terms:** 30% with order, 70% before shipment`
    }
};

function analyzeTender() {
    const input = document.getElementById('tenderInput').value;
    const outputArea = document.getElementById('outputArea');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const statsBar = document.getElementById('statsBar');
    
    if (input.trim().length < 50) {
        outputArea.innerHTML = `
            <div class="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-400">
                <strong>Please enter more details.</strong><br>
                Paste actual tender requirements (at least a few sentences) for the AI to analyze.
            </div>
        `;
        return;
    }
    
    // Disable button and show loading
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `
        <svg class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Analyzing Requirements...
    `;
    
    outputArea.innerHTML = `
        <div class="space-y-3">
            <div class="flex items-center text-blue-400">
                <svg class="animate-spin w-5 h-5 mr-3" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="typing-animation">Extracting key requirements</span>
            </div>
        </div>
    `;
    
    // Simulate AI processing with staged reveals
    const stages = [
        { delay: 800, text: "Identifying compliance requirements..." },
        { delay: 1600, text: "Matching technical specifications..." },
        { delay: 2400, text: "Generating response sections..." },
        { delay: 3200, text: "Formatting output..." }
    ];
    
    stages.forEach((stage, index) => {
        setTimeout(() => {
            outputArea.innerHTML = `
                <div class="space-y-3">
                    ${stages.slice(0, index + 1).map((s, i) => `
                        <div class="flex items-center ${i === index ? 'text-blue-400' : 'text-green-400'}">
                            ${i === index ? `
                                <svg class="animate-spin w-5 h-5 mr-3" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            ` : `
                                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                </svg>
                            `}
                            <span class="${i === index ? 'typing-animation' : ''}">${s.text}</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }, stage.delay);
    });
    
    // Show final output
    setTimeout(() => {
        outputArea.innerHTML = Object.values(responseTemplates).map(section => `
            <div class="bg-gray-900 rounded-lg p-4 border border-gray-700 fade-in mb-4">
                <h3 class="font-semibold text-lg mb-3 flex items-center">
                    <span class="mr-2">${section.icon}</span>
                    ${section.title}
                </h3>
                <div class="text-gray-300 text-sm whitespace-pre-line prose prose-invert prose-sm max-w-none">
                    ${formatContent(section.content)}
                </div>
            </div>
        `).join('');
        
        // Show stats
        statsBar.classList.remove('hidden');
        animateStats();
        
        // Re-enable button
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            Analyze with AI
        `;
    }, 4000);
}

function formatContent(content) {
    // Convert markdown-style formatting to HTML
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\| (.*?) \|/g, '<span class="font-mono text-xs">| $1 |</span>')
        .replace(/• /g, '<span class="text-blue-400">•</span> ')
        .replace(/✅/g, '<span class="text-green-400">✅</span>');
}

function animateStats() {
    const stats = [
        { id: 'timeSaved', target: 8, suffix: '+' },
        { id: 'sectionsGen', target: 4, suffix: '' },
        { id: 'complianceItems', target: 6, suffix: '' },
        { id: 'accuracy', target: 94, suffix: '%' }
    ];
    
    stats.forEach(stat => {
        const el = document.getElementById(stat.id);
        let current = 0;
        const increment = stat.target / 20;
        const interval = setInterval(() => {
            current += increment;
            if (current >= stat.target) {
                current = stat.target;
                clearInterval(interval);
            }
            el.textContent = Math.round(current) + stat.suffix;
        }, 50);
    });
}
