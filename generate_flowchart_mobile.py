"""
Generates mobile-optimized vertical system flowchart for ITSA Platform.
Outputs:
1. docs/ITSA_System_Flowchart_Mobile.svg
2. docs/ITSA_System_Flowchart_Mobile.png
3. docs/ITSA_System_Flowchart_Mobile.pdf
4. ITSA_System_Flowchart_Mobile.pdf (in project root)
"""
import os
import subprocess

MOBILE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 3400" width="1080" height="3400" style="background-color: #ffffff; font-family: 'Segoe UI', Arial, -apple-system, Roboto, sans-serif;">
  <defs>
    <!-- Arrow marker -->
    <marker id="m-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1e293b" />
    </marker>
    <filter id="m-shadow" x="-8%" y="-8%" width="116%" height="120%">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.10" flood-color="#0f172a" />
    </filter>
  </defs>

  <style>
    .title-main { font-size: 34px; font-weight: 800; fill: #0f172a; text-anchor: middle; letter-spacing: -0.5px; }
    .title-sub { font-size: 19px; font-weight: 500; fill: #64748b; text-anchor: middle; }
    .section-title { font-size: 22px; font-weight: 800; text-anchor: middle; letter-spacing: 0.5px; text-transform: uppercase; }
    .section-box { fill: #f8fafc; stroke: #cbd5e1; stroke-width: 2; stroke-dasharray: 6 4; rx: 18; }
    
    /* Flowchart Shape Styles from Reference Diagram */
    .shape-start-end { fill: #FCE0E3; stroke: #1e293b; stroke-width: 2.5; filter: url(#m-shadow); }
    .shape-io { fill: #D7E8FB; stroke: #1e293b; stroke-width: 2.5; filter: url(#m-shadow); }
    .shape-process { fill: #FDE68A; stroke: #1e293b; stroke-width: 2.5; filter: url(#m-shadow); rx: 8; }
    .shape-decision { fill: #FED7AA; stroke: #1e293b; stroke-width: 2.5; filter: url(#m-shadow); }
    .shape-doc { fill: #93C5FD; stroke: #1e293b; stroke-width: 2.5; filter: url(#m-shadow); }
    .shape-db { fill: #BFDBFE; stroke: #1e293b; stroke-width: 2.5; filter: url(#m-shadow); }
    .shape-ai { fill: #EDE9FE; stroke: #7C3AED; stroke-width: 2.2; stroke-dasharray: 6 4; rx: 14; }
    
    /* Text styles */
    .node-text { font-size: 20px; font-weight: 600; fill: #0f172a; text-anchor: middle; dominant-baseline: central; }
    .node-text-sm { font-size: 17px; font-weight: 600; fill: #0f172a; text-anchor: middle; dominant-baseline: central; }
    .node-text-bold { font-size: 21px; font-weight: 700; fill: #0f172a; text-anchor: middle; dominant-baseline: central; }
    .branch-yes { font-size: 18px; font-weight: 800; fill: #15803d; }
    .branch-no { font-size: 18px; font-weight: 800; fill: #b91c1c; }
    .flow-line { fill: none; stroke: #1e293b; stroke-width: 2.8; stroke-linecap: round; stroke-linejoin: round; marker-end: url(#m-arrow); }
    .flow-line-dashed { fill: none; stroke: #6366f1; stroke-width: 2.4; stroke-dasharray: 6 5; stroke-linecap: round; marker-end: url(#m-arrow); }
    .conn-circle { fill: #ffffff; stroke: #1e293b; stroke-width: 2.8; }
    .conn-cross { stroke: #1e293b; stroke-width: 2.5; }
    .legend-text { font-size: 17px; font-weight: 600; fill: #1e293b; text-anchor: start; dominant-baseline: central; }
  </style>

  <!-- ================= HEADER ================= -->
  <g transform="translate(540, 60)">
    <text class="title-main" y="0">ITSA Platform – System Flowchart</text>
    <text class="title-sub" y="36">AI-Powered Event Management &amp; Engagement Platform</text>
    <text class="title-sub" y="64" fill="#0284c7">📱 Optimized for Mobile &amp; Tablet Vertical View</text>
  </g>

  <!-- ================= FLOWCHART LEGEND ================= -->
  <g transform="translate(90, 155)">
    <rect x="0" y="0" width="900" height="150" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.8" rx="14" filter="url(#m-shadow)" />
    <text x="450" y="28" class="node-text-bold" fill="#0f172a">FLOWCHART SYMBOLS LEGEND</text>
    <line x1="30" y1="44" x2="870" y2="44" stroke="#e2e8f0" stroke-width="1.5" />
    
    <!-- Row 1 of Legend -->
    <ellipse cx="60" cy="74" rx="28" ry="14" class="shape-start-end" />
    <text x="100" y="74" class="legend-text">Start / End</text>

    <polygon points="265,60 300,60 288,88 253,88" class="shape-io" />
    <text x="315" y="74" class="legend-text">I/O Action</text>

    <rect x="460,62" width="46" height="24" class="shape-process" />
    <text x="520" y="74" class="legend-text">Process</text>

    <polygon points="700,60 720,74 700,88 680,74" class="shape-decision" />
    <text x="735" y="74" class="legend-text">Decision Point</text>

    <!-- Row 2 of Legend -->
    <path d="M 40,110 L 80,110 L 80,126 C 70,122 65,130 55,126 C 47,122 43,130 40,126 Z" class="shape-doc" />
    <text x="100" y="118" class="legend-text">E-Cert / Doc</text>

    <path d="M 265,112 A 16 5 0 0 1 297 112 L 297 127 A 16 5 0 0 1 265 127 Z" class="shape-db" />
    <ellipse cx="281" cy="112" rx="16" ry="5" fill="#93C5FD" stroke="#1e293b" />
    <text x="315" y="118" class="legend-text">Relational DB</text>

    <rect x="462,108" width="42" height="22" class="shape-ai" />
    <text x="520" y="118" class="legend-text">AI Services</text>

    <circle cx="700" cy="118" r="12" class="conn-circle" />
    <line x1="693" y1="111" x2="707" y2="125" class="conn-cross" />
    <line x1="707" y1="111" x2="693" y2="125" class="conn-cross" />
    <text x="735" y="118" class="legend-text">Connector</text>
  </g>

  <!-- ================= TOP SECTION: AUTHENTICATION FLOW ================= -->
  <!-- 1. Start Node -->
  <g transform="translate(540, 360)">
    <ellipse cx="0" cy="0" rx="110" ry="30" class="shape-start-end" />
    <text class="node-text-bold">Start</text>
  </g>
  <path d="M 540 390 L 540 425" class="flow-line" />

  <!-- 2. Open Platform -->
  <g transform="translate(540, 455)">
    <polygon points="-160,-28 190,-28 160,28 -190,28" class="shape-io" />
    <text class="node-text">Open ITSA Platform</text>
  </g>
  <path d="M 540 483 L 540 515" class="flow-line" />

  <!-- 3. User Login / Registration -->
  <g transform="translate(540, 545)">
    <rect x="-180" y="-28" width="360" height="56" class="shape-process" />
    <text class="node-text">User Login / Registration</text>
  </g>
  <path d="M 540 573 L 540 605" class="flow-line" />

  <!-- 4. Authenticate Credentials -->
  <g transform="translate(540, 635)">
    <rect x="-180" y="-28" width="360" height="56" class="shape-process" />
    <text class="node-text">Authenticate Credentials</text>
  </g>
  <path d="M 540 663 L 540 695" class="flow-line" />

  <!-- 5. Decision: Valid Credentials? -->
  <g transform="translate(540, 745)">
    <polygon points="0,-45 130,0 0,45 -130,0" class="shape-decision" />
    <text class="node-text-sm" y="-8">Valid</text>
    <text class="node-text-sm" y="12">Credentials?</text>
  </g>

  <!-- Auth Error Branch (No) -->
  <path d="M 410 745 L 210 745 L 210 545 L 350 545" class="flow-line" />
  <text x="310" y="730" class="branch-no">No</text>
  <g transform="translate(210, 645)">
    <rect x="-90" y="-22" width="180" height="44" class="shape-io" />
    <text class="node-text-sm">Show Error</text>
  </g>

  <!-- Valid Branch (Yes) -->
  <path d="M 540 790 L 540 835" class="flow-line" />
  <text x="555" y="815" class="branch-yes">Yes</text>

  <!-- Role Identification Hub -->
  <g transform="translate(540, 850)">
    <circle cx="0" cy="0" r="16" class="conn-circle" />
    <line x1="-11" y1="-11" x2="11" y2="11" class="conn-cross" />
    <line x1="11" y1="-11" x2="-11" y2="11" class="conn-cross" />
  </g>


  <!-- ================= SECTION 1: STUDENT WORKFLOW ================= -->
  <!-- Container Box -->
  <rect x="70" y="905" width="940" height="740" class="section-box" />
  <rect x="70" y="905" width="940" height="50" fill="#e0f2fe" stroke="#cbd5e1" stroke-width="2" rx="18" />
  <rect x="70" y="932" width="940" height="23" fill="#e0f2fe" />
  <text x="540" y="938" class="section-title" fill="#0369a1">🎓 1. STUDENT WORKFLOW</text>

  <path d="M 540 866 L 540 970" class="flow-line" />

  <!-- S1: Dashboard -->
  <g transform="translate(540, 1000)">
    <rect x="-170" y="-26" width="340" height="52" class="shape-process" />
    <text class="node-text">Student Dashboard</text>
  </g>
  <path d="M 540 1026 L 540 1055" class="flow-line" />

  <!-- S2: Browse & Select Event -->
  <g transform="translate(540, 1085)">
    <polygon points="-160,-26 190,-26 160,26 -190,26" class="shape-io" />
    <text class="node-text">View Upcoming Events</text>
  </g>
  <path d="M 540 1111 L 540 1140" class="flow-line" />

  <!-- S3: Register -->
  <g transform="translate(540, 1168)">
    <rect x="-170" y="-26" width="340" height="52" class="shape-process" />
    <text class="node-text">Register for Event</text>
  </g>
  <path d="M 540 1194 L 540 1225" class="flow-line" />

  <!-- S4: Decision: Seats Available? -->
  <g transform="translate(540, 1270)">
    <polygon points="0,-42 130,0 0,42 -130,0" class="shape-decision" />
    <text class="node-text-sm" y="-8">Seats &amp; Deadline</text>
    <text class="node-text-sm" y="12">Available?</text>
  </g>
  
  <!-- Reg Closed No Branch -->
  <path d="M 410 1270 L 190 1270 L 190 1085 L 340 1085" class="flow-line" />
  <text x="290" y="1255" class="branch-no">No</text>
  <g transform="translate(190, 1180)">
    <rect x="-70" y="-20" width="140" height="40" class="shape-io" />
    <text class="node-text-sm">Seats Full</text>
  </g>

  <!-- Reg Yes Branch -->
  <path d="M 540 1312 L 540 1345" class="flow-line" />
  <text x="555" y="1332" class="branch-yes">Yes</text>

  <!-- S5: Generate QR Ticket -->
  <g transform="translate(540, 1372)">
    <rect x="-180" y="-26" width="360" height="52" class="shape-process" />
    <text class="node-text">Generate Unique QR Ticket</text>
  </g>
  <path d="M 540 1398 L 540 1425" class="flow-line" />

  <!-- S6: Receive Ticket -->
  <g transform="translate(540, 1455)">
    <polygon points="-170,-26 200,-26 170,26 -200,26" class="shape-io" />
    <text class="node-text">Receive Ticket &amp; Confirmation</text>
  </g>
  <path d="M 540 1481 L 540 1510" class="flow-line" />

  <!-- S7: Attend & Present QR -->
  <g transform="translate(540, 1538)">
    <rect x="-180" y="-26" width="360" height="52" class="shape-process" />
    <text class="node-text">Attend Event &amp; Present QR</text>
  </g>
  <path d="M 540 1564 L 540 1595" class="flow-line" />

  <!-- S8: Decision: Attendance Verified? -->
  <g transform="translate(540, 1640)">
    <polygon points="0,-42 130,0 0,42 -130,0" class="shape-decision" />
    <text class="node-text-sm" y="-8">Attendance</text>
    <text class="node-text-sm" y="12">Verified?</text>
  </g>

  <!-- Att No Branch -->
  <path d="M 410 1640 L 260 1640 L 260 1538 L 350 1538" class="flow-line" />
  <text x="320" y="1625" class="branch-no">No</text>
  <text x="260" y="1595" class="node-text-sm" fill="#b91c1c">Retry</text>

  <!-- Att Yes Branch -->
  <path d="M 540 1682 L 540 1715" class="flow-line" />
  <text x="555" y="1700" class="branch-yes">Yes</text>

  <!-- S9: Auto Generate Certificate -->
  <g transform="translate(540, 1745)">
    <path d="M -160,-28 L 160,-28 L 160,18 C 100,10 60,32 0,20 C -60,8 -100,32 -160,18 Z" class="shape-doc" />
    <text class="node-text-sm" y="-6">Auto Generate &amp; Download</text>
    <text class="node-text-sm" y="12">E-Certificate (PDF)</text>
  </g>
  <path d="M 540 1775 L 540 1805" class="flow-line" />

  <!-- S10: Engagement Points -->
  <g transform="translate(540, 1832)">
    <rect x="-180" y="-26" width="360" height="52" class="shape-process" />
    <text class="node-text">Credit Engagement Points</text>
  </g>
  <path d="M 540 1858 L 540 1888" class="flow-line" />

  <!-- S11: Feed & Leaderboard -->
  <g transform="translate(540, 1918)">
    <polygon points="-160,-26 190,-26 160,26 -190,26" class="shape-io" />
    <text class="node-text">View Feed &amp; Leaderboard</text>
  </g>


  <!-- ================= SECTION 2: COORDINATOR WORKFLOW ================= -->
  <!-- Container Box -->
  <rect x="70" y="1980" width="940" height="660" class="section-box" />
  <rect x="70" y="1980" width="940" height="50" fill="#fef3c7" stroke="#cbd5e1" stroke-width="2" rx="18" />
  <rect x="70" y="2007" width="940" height="23" fill="#fef3c7" />
  <text x="540" y="2013" class="section-title" fill="#b45309">📋 2. COORDINATOR WORKFLOW</text>

  <!-- C1: Dashboard -->
  <g transform="translate(540, 2075)">
    <rect x="-170" y="-26" width="340" height="52" class="shape-process" />
    <text class="node-text">Coordinator Dashboard</text>
  </g>
  <path d="M 540 2101 L 540 2130" class="flow-line" />

  <!-- C2: Create Event -->
  <g transform="translate(540, 2160)">
    <polygon points="-160,-26 190,-26 160,26 -190,26" class="shape-io" />
    <text class="node-text">Create Event &amp; Schedule</text>
  </g>
  <path d="M 540 2186 L 540 2218" class="flow-line" />

  <!-- C3: Decision: Requires Admin Approval? -->
  <g transform="translate(540, 2262)">
    <polygon points="0,-42 130,0 0,42 -130,0" class="shape-decision" />
    <text class="node-text-sm" y="-8">Admin Approval</text>
    <text class="node-text-sm" y="12">Required?</text>
  </g>

  <!-- Approval Pipeline (Yes) -->
  <path d="M 670 2262 L 850 2262 L 850 2315" class="flow-line" />
  <text x="730" y="2248" class="branch-yes">Yes</text>
  <g transform="translate(850, 2340)">
    <rect x="-95" y="-22" width="190" height="44" class="shape-process" />
    <text class="node-text-sm">Submit to Admin</text>
  </g>

  <!-- Approval Direct Publish (No) -->
  <path d="M 540 2304 L 540 2355" class="flow-line" />
  <text x="555" y="2332" class="branch-no">No</text>

  <!-- C4: Publish Event -->
  <g transform="translate(540, 2382)">
    <rect x="-160" y="-26" width="320" height="52" class="shape-process" />
    <text class="node-text">Publish Event Live</text>
  </g>
  <path d="M 540 2408 L 540 2435" class="flow-line" />

  <!-- C5: Manage Registrations -->
  <g transform="translate(540, 2462)">
    <polygon points="-160,-26 190,-26 160,26 -190,26" class="shape-io" />
    <text class="node-text">Monitor Registered Students</text>
  </g>
  <path d="M 540 2488 L 540 2515" class="flow-line" />

  <!-- C6: In-App QR Scanner -->
  <g transform="translate(540, 2542)">
    <rect x="-170" y="-26" width="340" height="52" class="shape-process" />
    <text class="node-text">Launch Camera QR Scanner</text>
  </g>
  <path d="M 540 2568 L 540 2595" class="flow-line" />

  <!-- C7: Scan QR & Validate -->
  <g transform="translate(540, 2640)">
    <polygon points="0,-42 130,0 0,42 -130,0" class="shape-decision" />
    <text class="node-text-sm" y="-8">Valid Ticket &amp;</text>
    <text class="node-text-sm" y="12">Not Scanned?</text>
  </g>

  <!-- Duplicate/Error (No) -->
  <path d="M 410 2640 L 230 2640 L 230 2542 L 360 2542" class="flow-line" />
  <text x="310" y="2625" class="branch-no">No</text>
  <g transform="translate(230, 2595)">
    <rect x="-70" y="-18" width="140" height="36" class="shape-io" />
    <text class="node-text-sm" fill="#b91c1c">Duplicate Scan</text>
  </g>

  <!-- Scan Success (Yes) -->
  <path d="M 540 2682 L 540 2715" class="flow-line" />
  <text x="555" y="2700" class="branch-yes">Yes</text>

  <!-- C8: Record Attendance & Export -->
  <g transform="translate(540, 2742)">
    <rect x="-180" y="-26" width="360" height="52" class="shape-process" />
    <text class="node-text">Record Attendance &amp; Issue Certs</text>
  </g>


  <!-- ================= SECTION 3: ADMINISTRATOR, DB & AI ENGINE ================= -->
  <!-- Container Box -->
  <rect x="70" y="2815" width="940" height="385" class="section-box" />
  <rect x="70" y="2815" width="940" height="50" fill="#fae8ff" stroke="#cbd5e1" stroke-width="2" rx="18" />
  <rect x="70" y="2842" width="940" height="23" fill="#fae8ff" />
  <text x="540" y="2848" class="section-title" fill="#a21caf">🛡️ 3. ADMIN, DATABASE &amp; AI ENGINE</text>

  <!-- Admin Controls (Left) -->
  <g transform="translate(290, 2920)">
    <rect x="-160" y="-24" width="320" height="48" class="shape-process" />
    <text class="node-text-sm">Manage Users &amp; Roles (RBAC)</text>
  </g>
  <g transform="translate(290, 2985)">
    <rect x="-160" y="-24" width="320" height="48" class="shape-process" />
    <text class="node-text-sm">Approve Events &amp; Moderate Posts</text>
  </g>
  <g transform="translate(290, 3050)">
    <polygon points="-150,-24 170,-24 150,24 -170,24" class="shape-io" />
    <text class="node-text-sm">Security Audit Logs &amp; Rules</text>
  </g>
  <g transform="translate(290, 3120)">
    <path d="M -150,-24 L 150,-24 L 150,16 C 90,8 50,28 0,16 C -50,6 -90,28 -150,16 Z" class="shape-doc" />
    <text class="node-text-sm" y="-4">NAAC / Department Reports</text>
    <text class="node-text-sm" y="12">(PDF / CSV Analytics)</text>
  </g>

  <!-- Central Database (Center) -->
  <g transform="translate(565, 3030)">
    <path d="M -75,-28 A 75 15 0 0 1 75 -28 L 75 35 A 75 15 0 0 1 -75 35 Z" class="shape-db" />
    <ellipse cx="0" cy="-28" rx="75" ry="15" fill="#93C5FD" stroke="#1e293b" stroke-width="2.5" />
    <text class="node-text-bold" y="-4">ITSA DB</text>
    <text class="node-text-sm" y="16">(MySQL)</text>
    <text class="node-text-sm" y="56" fill="#475569">• Users &amp; RBAC</text>
    <text class="node-text-sm" y="76" fill="#475569">• Events &amp; QR</text>
    <text class="node-text-sm" y="96" fill="#475569">• Attendance</text>
    <text class="node-text-sm" y="116" fill="#475569">• Certificates</text>
  </g>

  <!-- AI Engine (Right) -->
  <g transform="translate(830, 3030)">
    <rect x="-120" y="-75" width="240" height="200" class="shape-ai" />
    <text class="node-text-bold" y="-50" fill="#6d28d9">🤖 AI ENGINE</text>
    <line x1="-100" y1="-32" x2="100" y2="-32" stroke="#c4b5fd" stroke-width="1.5" />
    <text class="node-text-sm" y="-12" fill="#4c1d95">• Event Recs</text>
    <text class="node-text-sm" y="12" fill="#4c1d95">• Sentiment Tone</text>
    <text class="node-text-sm" y="36" fill="#4c1d95">• Prediction</text>
    <text class="node-text-sm" y="60" fill="#4c1d95">• Spam Filter</text>
    <text class="node-text-sm" y="84" fill="#4c1d95">• Anomaly Alert</text>
    <text class="node-text-sm" y="108" fill="#4c1d95">• Auto Notify</text>
  </g>

  <!-- DB & AI Links -->
  <path d="M 645 3030 L 705 3030" class="flow-line-dashed" />
  <path d="M 705 3045 L 645 3045" class="flow-line-dashed" />


  <!-- ================= TERMINATION: LOGOUT -> END ================= -->
  <!-- Session Logout -->
  <g transform="translate(540, 3240)">
    <polygon points="-160,-28 190,-28 160,28 -190,28" class="shape-io" />
    <text class="node-text-bold">Session Logout / Close</text>
  </g>
  <path d="M 540 3268 L 540 3310" class="flow-line" />

  <!-- End Node -->
  <g transform="translate(540, 3345)">
    <ellipse cx="0" cy="0" rx="110" ry="30" class="shape-start-end" />
    <text class="node-text-bold">End</text>
  </g>

</svg>
'''

def main():
    base_dir = r"C:\Users\ritik\.gemini\antigravity\scratch\itsa-platform"
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    mobile_svg_path = os.path.join(docs_dir, "ITSA_System_Flowchart_Mobile.svg")
    mobile_svg_root = os.path.join(base_dir, "ITSA_System_Flowchart_Mobile.svg")
    html_path = os.path.join(docs_dir, "flowchart_mobile_render.html")
    mobile_png_path = os.path.join(docs_dir, "ITSA_System_Flowchart_Mobile.png")
    mobile_png_root = os.path.join(base_dir, "ITSA_System_Flowchart_Mobile.png")
    mobile_pdf_path = os.path.join(docs_dir, "ITSA_System_Flowchart_Mobile.pdf")
    mobile_pdf_root = os.path.join(base_dir, "ITSA_System_Flowchart_Mobile.pdf")

    # Save SVG
    with open(mobile_svg_path, "w", encoding="utf-8") as f:
        f.write(MOBILE_SVG)
    with open(mobile_svg_root, "w", encoding="utf-8") as f:
        f.write(MOBILE_SVG)
    print("Mobile SVG saved.")

    # Save HTML renderer
    html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 0; background: #ffffff; display: flex; justify-content: center; align-items: center; }}
  svg {{ width: 1080px; height: 3400px; }}
</style>
</head>
<body>
{MOBILE_SVG}
</body>
</html>'''
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Render PNG using Edge
    edge_cmd = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--headless",
        "--disable-gpu",
        "--force-device-scale-factor=1",
        "--window-size=1080,3400",
        f"--screenshot={mobile_png_path}",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    subprocess.run(edge_cmd, check=True, timeout=25)
    print(f"Mobile PNG rendered: {mobile_png_path}")
    
    if os.path.exists(mobile_png_path):
        with open(mobile_png_path, "rb") as rf, open(mobile_png_root, "wb") as wf:
            wf.write(rf.read())

    # Build mobile PDF using reportlab or Edge headless print-to-pdf
    # Option A: Edge print-to-pdf creates native vector PDF with custom page size!
    pdf_cmd = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={mobile_pdf_path}",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    try:
        subprocess.run(pdf_cmd, check=True, timeout=25)
        print(f"Native vector PDF created: {mobile_pdf_path}")
    except Exception as e:
        print(f"Edge print-to-pdf fallback: {e}")

    # Also build a custom high-quality single long-page mobile PDF via ReportLab for flawless scrolling on phones
    try:
        from reportlab.lib.pagesizes import portrait
        from reportlab.pdfgen import canvas
        from PIL import Image

        img = Image.open(mobile_png_path)
        w_px, h_px = img.size
        # 72 points per inch standard, map 1080px to ~540pt width and proportional height
        pt_w = 540.0
        pt_h = (h_px / w_px) * pt_w
        
        c = canvas.Canvas(mobile_pdf_path, pagesize=(pt_w, pt_h))
        c.drawImage(mobile_png_path, 0, 0, width=pt_w, height=pt_h)
        c.showPage()
        c.save()
        print(f"Optimized single-page mobile PDF generated via ReportLab: {mobile_pdf_path}")
    except Exception as e:
        print(f"Reportlab custom page exception: {e}")

    if os.path.exists(mobile_pdf_path):
        with open(mobile_pdf_path, "rb") as rf, open(mobile_pdf_root, "wb") as wf:
            wf.write(rf.read())
        print(f"Copied mobile PDF to root: {mobile_pdf_root}")

if __name__ == "__main__":
    main()
