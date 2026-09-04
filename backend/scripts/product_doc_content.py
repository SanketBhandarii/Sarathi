from __future__ import annotations

STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; }

body {
  font-family: 'Inter', system-ui, sans-serif;
  color: #16181d;
  font-size: 10.5pt;
  line-height: 1.62;
  margin: 0;
  -webkit-font-smoothing: antialiased;
}

h1 { font-size: 30pt; font-weight: 700; letter-spacing: -0.9px; margin: 0 0 6px; }
h2 {
  font-size: 15pt; font-weight: 600; letter-spacing: -0.35px;
  margin: 30px 0 10px; padding-top: 14px; border-top: 2px solid #16181d;
  break-after: avoid;
}
h3 { font-size: 11.5pt; font-weight: 600; margin: 20px 0 6px; break-after: avoid; }
p { margin: 0 0 10px; }
ul, ol { margin: 0 0 10px; padding-left: 18px; }
li { margin-bottom: 5px; }
strong { font-weight: 600; }

.lead { font-size: 12pt; color: #4a4f58; line-height: 1.58; }
.muted { color: #6b7079; }
.small { font-size: 9pt; }

code {
  font-family: 'Menlo', 'Consolas', monospace;
  font-size: 8.8pt; background: #f2f3f5; padding: 1px 5px;
  border-radius: 4px; color: #16181d;
}

pre {
  background: #f7f8f9; border: 1px solid #e6e8eb; border-radius: 8px;
  padding: 12px 14px; font-family: 'Menlo', 'Consolas', monospace;
  font-size: 8.6pt; line-height: 1.55; overflow-x: auto;
  margin: 0 0 12px; break-inside: avoid;
}
pre code { background: none; padding: 0; font-size: inherit; }

table { width: 100%; border-collapse: collapse; margin: 0 0 12px; font-size: 9.5pt; }
th {
  text-align: left; font-weight: 600; border-bottom: 1.5px solid #16181d;
  padding: 7px 9px 7px 0; vertical-align: bottom;
}
td { padding: 7px 9px 7px 0; border-bottom: 1px solid #e9ebee; vertical-align: top; }
tr { break-inside: avoid; }

.cover { padding-top: 30mm; break-after: page; }
.cover .kicker { font-size: 10pt; font-weight: 600; color: #2563eb; letter-spacing: 0.6px;
  text-transform: uppercase; margin-bottom: 14px; }
.cover .sub { font-size: 13pt; color: #4a4f58; margin: 10px 0 30px; line-height: 1.5; }
.cover dl { display: grid; grid-template-columns: 130px 1fr; gap: 7px 0; font-size: 10pt; }
.cover dt { color: #6b7079; }
.cover dd { margin: 0; font-weight: 500; }

.page-break { break-before: page; }

.box {
  border: 1px solid #e6e8eb; border-radius: 9px; padding: 13px 15px;
  margin: 0 0 12px; break-inside: avoid; background: #fbfbfc;
}
.box .title { font-weight: 600; margin-bottom: 4px; }

.rule {
  border-left: 3px solid #2563eb; background: #f4f7fe;
  padding: 12px 15px; margin: 0 0 14px; border-radius: 0 8px 8px 0;
  break-inside: avoid;
}

.warn {
  border-left: 3px solid #b4813a; background: #fdf8f0;
  padding: 12px 15px; margin: 0 0 14px; border-radius: 0 8px 8px 0;
  break-inside: avoid;
}

.flow { margin: 0 0 14px; break-inside: avoid; }
.flow .row { display: flex; align-items: stretch; gap: 8px; margin-bottom: 8px; }
.step {
  flex: 1; border: 1px solid #dfe2e6; border-radius: 8px; padding: 9px 11px;
  background: #fff; font-size: 9pt;
}
.step .n { font-weight: 600; font-size: 9.5pt; margin-bottom: 2px; display: block; }
.step .d { color: #6b7079; font-size: 8.6pt; line-height: 1.45; }
.arrow { display: flex; align-items: center; color: #a2a7ae; font-size: 13pt; padding: 0 1px; }

.tint-blue { background: #f4f7fe; border-color: #cfdcf8; }
.tint-green { background: #f2faf5; border-color: #c9e8d6; }
.tint-amber { background: #fdf8f0; border-color: #eddcc0; }
.tint-grey { background: #f5f6f7; border-color: #e0e3e7; }

.two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }

.foot { margin-top: 34px; padding-top: 12px; border-top: 1px solid #e6e8eb;
  font-size: 9pt; color: #6b7079; }
"""


COVER = """
<div class="cover">
  <div class="kicker">Product guide</div>
  <h1>Sarathi</h1>
  <p class="sub">
    An agent that watches every government exam in India for one student,<br>
    and stays quiet until something needs them.
  </p>
  <dl>
    <dt>What this is</dt><dd>A guide for anyone joining the project</dd>
    <dt>Written for</dt><dd>Developers who have never seen this code</dd>
    <dt>Frontend</dt><dd>Next.js 16, React 19, Tailwind v4</dd>
    <dt>Backend</dt><dd>FastAPI, Python 3.14, PostgreSQL</dd>
    <dt>Agents</dt><dd>Strands Agents SDK</dd>
    <dt>Tests</dt><dd>206, all passing</dd>
  </dl>
</div>
"""


BODY = """
<h2>1. What problem this solves</h2>

<p>A student in India sits one government exam a year. They fight paperwork all year. Three things go wrong, and they stack on top of each other.</p>

<p><strong>They do not know what exists.</strong> Thirty lakh people apply for SSC CGL. Meanwhile India Post GDS asks only for a 10th pass and holds no written exam, and far fewer people have heard of it.</p>

<p><strong>They do not know if they qualify.</strong> Being eligible means five rules being true at the same time: your age, the extra years your category gives you, your qualification level, your home state, and how many attempts you have used. Most students find out they were never eligible only after paying the fee.</p>

<p><strong>The paperwork takes it away.</strong> The photo must be between 20 and 50 KB. The correction window opens for five days and nobody announces it. A missed form costs a year of a life.</p>

<div class="rule">
  <p style="margin:0"><strong>The one rule the whole project rests on.</strong> Every fact Sarathi states must come from a line in an official notification PDF. If it cannot find the line, it does not state the fact. It says it does not know.</p>
</div>

<p>This is why the product is worth building. Coaching websites and Telegram channels retype exam rules by hand and get them wrong. None of them show you where the rule came from. Sarathi shows the page number and the exact sentence, so a student can check it in ten seconds.</p>


<h2>2. What it does, feature by feature</h2>

<table>
  <tr><th style="width:30%">Feature</th><th>What it does for a student</th></tr>
  <tr><td><strong>Exam Radar</strong></td><td>Shows every exam in four layers: central government, your state, your district, and other states open to everyone. Exams you cannot take are still shown, with the reason.</td></tr>
  <tr><td><strong>Result engine</strong></td><td>Works out age with category relaxation, qualification level, marks, fee and home state. Six answers, including "closed for now, it runs again", because telling a student CGL is "not for you" would be false.</td></tr>
  <tr><td><strong>Education ladder</strong></td><td>10th, 12th, ITI, Diploma, Graduation, Post graduation. Percentage or CGPA with live conversion. A diploma does not count as a degree.</td></tr>
  <tr><td><strong>Document maker</strong></td><td>Turns one phone photo into the exact pixel size and file size each commission asks for. SSC wants a 236x79 signature, IBPS wants 140x60.</td></tr>
  <tr><td><strong>Document sheet</strong></td><td>A single PDF with your details, pictures and marks, watermarked so nobody uploads it to a form by mistake.</td></tr>
  <tr><td><strong>Agent Journal</strong></td><td>A record of every nightly run: what was checked, what was re-verified, and how many messages were sent. Usually zero.</td></tr>
  <tr><td><strong>Corrections</strong></td><td>Lists corrections a commission published after the notification. Says plainly when a correction is a scan it cannot read.</td></tr>
  <tr><td><strong>Deadlines and age limit</strong></td><td>Every date read from the notification, plus the birthday on which an exam closes to you permanently.</td></tr>
  <tr><td><strong>Fee savings</strong></td><td>An SC candidate pays Rs 175 where others pay Rs 850. Most students never realise.</td></tr>
  <tr><td><strong>Two languages</strong></td><td>English and Hindi. A test fails if either is missing.</td></tr>
</table>


<h2>3. The tech stack, and why each piece</h2>

<table>
  <tr><th style="width:26%">Piece</th><th style="width:26%">What we use</th><th>Why</th></tr>
  <tr><td>Frontend</td><td>Next.js 16, React 19</td><td>Pages are rendered on the server, so data arrives with the page instead of being fetched by the browser.</td></tr>
  <tr><td>Styling</td><td>Tailwind v4</td><td>Colours are defined once in <code>globals.css</code> and used everywhere.</td></tr>
  <tr><td>Backend</td><td>FastAPI, Python 3.14</td><td>Types are checked at the edge, and the API documents itself at <code>/docs</code>.</td></tr>
  <tr><td>Database</td><td>PostgreSQL, Neon free tier</td><td>Rules are stored as JSON with their citations attached.</td></tr>
  <tr><td>Agents</td><td>Strands Agents SDK</td><td>Gives us tools, typed output, and a graph where one agent can send work back to another.</td></tr>
  <tr><td>Model</td><td>Groq, or AWS Bedrock</td><td>One environment variable switches provider. The rest of the code never knows which is in use.</td></tr>
  <tr><td>PDF reading</td><td>pypdf</td><td>Pulls text out of notification PDFs, page by page.</td></tr>
  <tr><td>Browser</td><td>Playwright</td><td>MPSC and some SSC pages only appear after JavaScript runs.</td></tr>
  <tr><td>Images</td><td>Pillow</td><td>Resizes photos to exact pixels and file size, and draws the PDF sheet.</td></tr>
  <tr><td>File storage</td><td>ImageKit</td><td>Signatures are stored privately, behind links that expire in an hour.</td></tr>
  <tr><td>Passwords</td><td>Argon2id</td><td>The current recommended way to store a password.</td></tr>
</table>

<p class="small muted">Everything runs on free tiers. Without ImageKit, documents save to local files. Without SMTP, verification codes go to <code>data/emails.log</code>. The project runs for anyone who clones it, with only a database and one model key.</p>


<h2 class="page-break">4. How the system fits together</h2>

<p>Read this top to bottom. It is the path a government PDF takes to become one sentence on a student's screen.</p>

<div class="flow">
  <div class="row">
    <div class="step tint-grey"><span class="n">1. Collect</span><span class="d">Fetch notification PDFs from SSC, UPSC, IBPS, MPSC and India Post. Some need a real browser.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-grey"><span class="n">2. Store</span><span class="d">Save each PDF by its SHA256 hash with the URL it came from. Cached files are committed to the repo.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-blue"><span class="n">3. Sort</span><span class="d">An agent decides: is this a recruitment notification, or a tender nobody cares about?</span></div>
  </div>
  <div class="row">
    <div class="step tint-blue"><span class="n">4. Read</span><span class="d">The reader agent writes down each rule with the page number and the exact sentence it came from.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-blue"><span class="n">5. Check</span><span class="d">The checker agent compares every recorded number against the page it claims to come from. If it finds a problem, the work goes back to step 4.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-green"><span class="n">6. Verify</span><span class="d">Plain code asks two questions with no model involved. Anything that fails is dropped.</span></div>
  </div>
  <div class="row">
    <div class="step tint-green"><span class="n">7. Find the last date</span><span class="d">Plain code reads "from 01.07.2026 to 21.07.2026" out of the sentence, and takes the end.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-grey"><span class="n">8. Save</span><span class="d">Rules and citations go into PostgreSQL as JSON.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-amber"><span class="n">9. Decide</span><span class="d">Ordinary arithmetic compares the rules against this student. No model touches this step.</span></div>
  </div>
  <div class="row">
    <div class="step tint-amber"><span class="n">10. Show</span><span class="d">The Radar groups exams into four layers and six answers, each with its citation.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-grey"><span class="n">11. Watch</span><span class="d">At 02:15 every night the whole check runs again for every student.</span></div>
    <div class="arrow">&rarr;</div>
    <div class="step tint-grey"><span class="n">12. Speak, rarely</span><span class="d">If something needs the student, one message goes out. Most nights, nothing does.</span></div>
  </div>
</div>

<h3>Why steps 5, 6 and 7 are separate</h3>

<p>This is the most important design decision in the project, so it is worth being clear about.</p>

<p>During development we planted two errors in real extracted data. We changed a maximum age from 30 to 45, and an OBC relaxation from 3 years to 9. The AI verifier <strong>missed both</strong>. The plain numeric check <strong>caught both instantly</strong>.</p>

<p>The most dangerous mistake this product can make is a real quote paired with a wrong number, because the quote looks correct and a model reading it can be persuaded. Arithmetic cannot be persuaded. So the two checks that matter run in ordinary code:</p>

<ol>
  <li><strong>Is that sentence really on that page?</strong> String matching.</li>
  <li><strong>Is that number really inside that sentence?</strong> Arithmetic.</li>
  <li><em>Anything the first two cannot see.</em> An agent, and only here.</li>
</ol>


<h2>5. How data moves</h2>

<h3>When a student opens the Radar</h3>

<pre><code>Browser  ->  Next.js server component
             reads the session cookie, calls the API with the token

Next.js  ->  GET /students/{id}/radar
             FastAPI loads the profile and every saved rule

FastAPI  ->  for each exam:
               is this exam open to your state?
               your age, plus the years your category adds
               your qualification level, then your marks
               the fee for your category
               each answer carries the citation it came from

FastAPI  ->  17 exams, in 4 layers, with 6 possible answers
Browser  ->  "You get 3 extra years because you are OBC."
             page 6: "Other Backward Classes (Non-Creamy Layer) 3 years"</code></pre>

<h3>When a student uploads a photo</h3>

<pre><code>Browser  ->  POST /me/documents/photograph   (the original file)
FastAPI  ->  check it is really an image, and big enough
         ->  keep the original on disk as the master copy
         ->  upload a copy to ImageKit
         ->  save width, height and size in PostgreSQL

Later, when the Documents page is opened:
Next.js  ->  GET /me/documents/photograph/sizes
FastAPI  ->  for each commission, resize the master to that exact
             pixel size, then adjust quality until the file lands
             inside the KB range that commission allows
         ->  return each one as base64

Browser  ->  four download buttons, one per commission</code></pre>

<div class="box">
  <div class="title">A detail worth copying</div>
  <p style="margin:0" class="small">The sizes are built while the page is rendered on the server, not fetched by the browser afterwards. An earlier version hid them behind a button that fetched from the browser, and when that fetch failed the screen simply did not change. The student saw nothing and had no idea why. Building it on the server removed that whole class of failure.</p>
</div>


<h2 class="page-break">6. Where everything lives</h2>

<h3>Backend</h3>

<table>
  <tr><th style="width:34%">Folder</th><th>What is in it</th></tr>
  <tr><td><code>app/sources/</code></td><td>One file per government website. Each knows how to find that site's notification PDFs.</td></tr>
  <tr><td><code>app/storage/</code></td><td>The PDF cache. Files are stored by hash so the same document is never processed twice.</td></tr>
  <tr><td><code>app/extraction/</code></td><td>Reading PDFs, checking citations, and the plain code that finds the last date to apply.</td></tr>
  <tr><td><code>agents/</code></td><td>The Strands agents: reader, checker, classifier, verifier, and the graph that joins them.</td></tr>
  <tr><td><code>app/eligibility/</code></td><td>The result engine. Age, categories, qualification levels, fees, layers. No models here at all.</td></tr>
  <tr><td><code>app/student/</code></td><td>The student profile and the education ladder.</td></tr>
  <tr><td><code>app/documents/</code></td><td>Image resizing, the per commission size rules, storage, and the PDF sheet.</td></tr>
  <tr><td><code>app/journal/</code></td><td>The nightly run, the scheduler and the record of what happened.</td></tr>
  <tr><td><code>app/auth/</code></td><td>Sign up, email codes, passwords, session tokens.</td></tr>
  <tr><td><code>app/api/routes/</code></td><td>Every HTTP endpoint.</td></tr>
  <tr><td><code>app/db/</code></td><td>Tables and the functions that read and write them.</td></tr>
  <tr><td><code>scripts/</code></td><td>Commands you run by hand: fetch notices, classify them, read one document, sync to the database.</td></tr>
  <tr><td><code>tests/</code></td><td>206 tests. They can never send a real email or a real message.</td></tr>
</table>

<h3>Frontend</h3>

<table>
  <tr><th style="width:34%">Path</th><th>What is in it</th></tr>
  <tr><td><code>app/(public)/</code></td><td>Landing page, sign up, email code, profile setup, first photos.</td></tr>
  <tr><td><code>app/(app)/</code></td><td>Everything behind sign in: dashboard, radar, deadlines, documents, corrections, journal, profile.</td></tr>
  <tr><td><code>components/</code></td><td>Sidebar, top bar, the education ladder form, shared cards and buttons.</td></tr>
  <tr><td><code>lib/</code></td><td>API calls, session reading, formatting.</td></tr>
  <tr><td><code>app/globals.css</code></td><td>Every colour in the product. Read section 8 before you add one.</td></tr>
</table>


<h2>7. Running it on your machine</h2>

<pre><code># Backend
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m playwright install chromium

cp .env.example .env          # fill in DATABASE_URL and GROQ_API_KEY
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn app.main:app --port 8020

# Frontend, in another terminal
cd frontend
npm install
cp .env.example .env.local    # point NEXT_PUBLIC_API_BASE at port 8020
npm run dev                   # opens on http://localhost:3000</code></pre>

<h3>Loading exam data</h3>

<pre><code>.venv/Scripts/python -m scripts.refresh_notices     # download official PDFs
.venv/Scripts/python -m scripts.classify_cached     # notification, or tender?
.venv/Scripts/python -m scripts.process_document "CRP-PO"   # read the rules out
.venv/Scripts/python -m scripts.sync_to_db          # put them in PostgreSQL</code></pre>

<div class="warn">
  <p style="margin:0"><strong>Do not skip <code>sync_to_db</code>.</strong> Reading a document writes the rules to a JSON file on disk. Until you sync, the website will not show them. This has confused people more than once.</p>
</div>

<h3>Tests</h3>

<pre><code>cd backend
.venv/Scripts/python -m pytest tests/ -q     # 206 tests, about 8 minutes</code></pre>


<h2 class="page-break">8. If you want to contribute</h2>

<p>The most useful thing you can add is <strong>another exam source</strong>. The radar is thin, and every new source makes the product more useful straight away.</p>

<h3>Adding a new commission, step by step</h3>

<ol>
  <li>Create <code>app/sources/your_source.py</code>. Copy <code>india_post.py</code>, it is the shortest one.</li>
  <li>Set <code>id</code>, <code>name</code>, <code>home_url</code> and <code>official_domains</code>. The domain list matters: it stops us following a link to some random website.</li>
  <li>Write <code>fetch_notices()</code>. If the PDFs are plain links, <code>collect_pdf_notices()</code> does the work for you.</li>
  <li>Filter out the noise. India Post publishes about two hundred shortlist PDFs and one real notification, so that source keeps only what is about applying.</li>
  <li>Add your module to <code>SOURCES</code> in <code>app/sources/registry.py</code>.</li>
  <li>Add the body name to <code>app/exams/naming.py</code>, so students see "India Post GDS" instead of "Descriptive Notification".</li>
  <li>If the exam is state level, add it to <code>SOURCE_PROFILES</code> in <code>app/eligibility/layers.py</code> with its state and whether it needs domicile.</li>
  <li>Run the four data commands above, then open the Radar.</li>
</ol>

<h3>The rules of this codebase</h3>

<ul>
  <li><strong>Never state a fact without a citation.</strong> If the reader cannot find the sentence, the fact is dropped, not guessed.</li>
  <li><strong>Never say an exam is open unless you found the closing date.</strong> Say you do not know and link to the official page.</li>
  <li><strong>No model decides eligibility.</strong> Models read documents. Arithmetic decides.</li>
  <li><strong>Plain, direct writing everywhere in the product.</strong> Say "result", not "verdict". Say "check", not "judge". One idea per sentence, no clever phrasing.</li>
  <li><strong>Small files, one job each.</strong> No comments unless something is genuinely surprising.</li>
  <li><strong>Only use colours defined in <code>globals.css</code>.</strong> A test enforces this. It exists because a download button once used a colour that did not exist, so it rendered as white text on a white card and was invisible for days.</li>
</ul>


<h2>9. What is not finished</h2>

<p>Being honest about this is more useful than pretending otherwise.</p>

<table>
  <tr><th style="width:34%">Gap</th><th>What it means</th></tr>
  <tr><td><strong>Only six sources</strong></td><td>SSC, UPSC, IBPS, MPSC, India Post and the SSC exam calendar. This is the biggest weakness. Usually only one or two exams are open at a time, so the Radar looks empty.</td></tr>
  <tr><td><strong>MPSC cannot be read</strong></td><td>Their notifications are photographs of paper with no text inside. They appear with their real title, date and official link, marked as unread. Reading them needs a vision model.</td></tr>
  <tr><td><strong>Not deployed</strong></td><td>Everything runs on one machine. Moving the nightly run to the cloud needs AWS credits.</td></tr>
  <tr><td><strong>Multi post adverts</strong></td><td>UPSC advertisements list many posts with different rules each. Sarathi handles single rule notifications well and says so when it cannot read one cleanly.</td></tr>
  <tr><td><strong>Old journal rows</strong></td><td>Runs recorded before 3 September counted messages that were never actually delivered. Newer runs are accurate.</td></tr>
</table>

<div class="foot">
  <p style="margin:0">Sarathi. Built for the AWS Agents for Humans hackathon, Everyday Agents track.<br>
  Regenerate this document with <code>python -m scripts.make_product_doc</code>.</p>
</div>
"""


PAGE_HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Sarathi product guide</title>
<style>{STYLE}</style>
</head>
<body>
{COVER}
{BODY}
</body>
</html>
"""
