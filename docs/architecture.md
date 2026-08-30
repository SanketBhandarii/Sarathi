# Sarathi architecture

## The whole system

```mermaid
flowchart TB
    subgraph sources["Official sources only"]
        ssc["SSC<br/>public JSON API"]
        upsc["UPSC<br/>HTML + PDFs"]
        ibps["IBPS<br/>HTML + PDFs"]
        mpsc["MPSC<br/>real browser, JS rendered"]
        cal["SSC exam calendar<br/>real browser"]
    end

    subgraph ingest["Ingest"]
        cache["PDF cache<br/>sha256 + origin url<br/>committed to the repo"]
        classify["Classifier agent<br/>notification, or tender?"]
    end

    subgraph reading["Reading the rules"]
        graph["Strands cyclic Graph<br/>reader ⇄ checker"]
        verify["Verification<br/>3 layers, 2 need no AI"]
        prune["Prune what cannot be proven"]
    end

    subgraph store["Postgres"]
        rules[("exam_rules<br/>JSONB + citations")]
        student[("students<br/>+ qualification ladder")]
        journal[("journal_runs<br/>journal_events")]
    end

    subgraph decide["Deciding, in plain Python"]
        engine["Verdict engine<br/>age · relaxation · level<br/>marks · fee · domicile"]
        radar["Exam Radar<br/>4 layers, 6 buckets"]
    end

    subgraph out["What the student sees"]
        web["Next.js dashboard"]
        docs["Document maker<br/>exact pixels and bytes"]
        wrong["When I was wrong"]
        msg["WhatsApp / email"]
    end

    sources --> cache --> classify --> graph --> verify --> prune --> rules
    cal --> rules
    rules --> engine
    student --> engine
    engine --> radar --> web
    rules --> docs --> web
    rules --> wrong --> web
    engine --> journal --> web
    journal --> msg
```

## The Strands graph that reads a notification

The reader records what it finds. The checker calls a tool that compares every recorded number against the page it claims to come from. The edge back to the reader **only fires when problems were reported**, so a bad reading is corrected instead of saved.

```mermaid
flowchart LR
    start([document]) --> reader

    reader["**reader** (Agent)<br/>tools:<br/>read_section<br/>record_age_rule<br/>record_age_relaxation"]
    checker["**checker** (Agent)<br/>tool:<br/>check_what_was_recorded"]

    reader -->|always| checker
    checker -->|"problems found"| reader
    checker -->|clean| done([saved with citations])

    style reader fill:#eff4ff,stroke:#2563eb
    style checker fill:#eff4ff,stroke:#2563eb
```

Built with `GraphBuilder`, `reset_on_revisit(True)`, an `EdgeCondition` on the loop-back, and `set_max_node_executions` so it can never spin forever.

## Verification, and why two layers use no AI

```mermaid
flowchart TB
    claim["a recorded claim<br/>'maximum age 30'<br/>page 6, quoted sentence"]

    l1{"1 · is that sentence<br/>actually on page 6?<br/><br/>string matching"}
    l2{"2 · does '30' appear<br/>in that sentence?<br/><br/>arithmetic"}
    l3{"3 · anything the first<br/>two cannot see<br/><br/>agent with tools"}

    claim --> l1
    l1 -->|no| drop["dropped, recorded<br/>as unverifiable"]
    l1 -->|yes| l2
    l2 -->|no| drop
    l2 -->|yes| l3
    l3 -->|problem| retry["sent back to the reader"]
    l3 -->|clean| keep["shown to the student"]

    style l1 fill:#d9f5e3,stroke:#0f7a3d
    style l2 fill:#d9f5e3,stroke:#0f7a3d
    style l3 fill:#eff4ff,stroke:#2563eb
    style drop fill:#fde5eb,stroke:#a8324b
```

**Why this shape.** During development we planted errors in real extracted data: maximum age 30 changed to 45, OBC relaxation 3 changed to 9. The AI verifier **missed both**. The plain numeric check **caught both instantly**.

The most dangerous error in this product is a real quote paired with a wrong number, because the quote looks legitimate and a model reading it can be persuaded. Arithmetic cannot be persuaded. So the two checks that matter run in code, and the model handles only what code cannot.

## A verdict, end to end

```mermaid
sequenceDiagram
    participant S as Student
    participant W as Dashboard
    participant A as API
    participant E as Verdict engine
    participant D as Postgres

    S->>W: opens the dashboard
    W->>A: GET /students/{id}/radar
    A->>D: profile + every exam rule
    D-->>A: ladder, category, domicile, rules with citations

    loop for each exam
        A->>E: decide(rules, student)
        E->>E: domicile? then age + relaxation
        E->>E: qualification LEVEL, then marks
        E->>E: fee for this category
        E-->>A: bucket + reasons, each with its citation
    end

    A-->>W: 17 exams, 4 layers, 6 buckets
    W-->>S: "You get 3 extra years because you are OBC"<br/>page 6: "Other Backward Classes (Non-Creamy Layer) 3 years"
```

## The nightly run, and the silence

```mermaid
flowchart LR
    wake([nightly]) --> check

    check["check every source"] --> reread["re-verify every cached quote<br/>against the original pdf"]
    reread --> evaluate["re-evaluate every rule<br/>for this student"]
    evaluate --> worth{"anything worth<br/>telling them?"}

    worth -->|no| silent["record the run<br/>**send nothing**"]
    worth -->|yes| send["send one message<br/>whatsapp or email"]

    silent --> log[("journal_runs<br/>journal_events")]
    send --> log

    style silent fill:#efeff1,stroke:#63676e
    style send fill:#dfeaff,stroke:#1c5fc4
```

A real pair of runs from the journal:

```
15 July      64 checks run  →  0 messages   "nothing needed your attention"
29 August    64 checks run  →  1 message    "closes in 13 days and you can apply"
```

Same work. Different answer. The Agent Journal exists so that silence is visible instead of looking like nothing happened.

## Choosing a model, and staying inside its limits

```mermaid
flowchart TB
    call["an agent needs a model"]
    pacer["token budget pacer<br/>Strands hook on BeforeModelCallEvent"]
    router{"MODEL_PROVIDER"}

    groq["LiteLLMModel → Groq<br/>free tier, 8000 tokens per minute"]
    bedrock["BedrockModel<br/>Nova for bulk, Claude for judgement"]

    call --> pacer --> router
    router -->|groq| groq
    router -->|bedrock| bedrock

    style pacer fill:#fdefdb,stroke:#8a5a12
```

Groq's free tier allows 8,000 tokens a minute, and a tool-calling agent resends its whole conversation every turn. The pacer tracks a rolling minute and waits rather than failing. One environment variable switches to Bedrock; no other code changes.

## Data model

```mermaid
erDiagram
    students ||--o{ qualifications : "10th, 12th, diploma, degree"
    students ||--o{ student_documents : "photo, signature, thumb"
    students ||--o{ journal_runs : "one per nightly check"
    students ||--o{ deadlines : "dates to keep"
    journal_runs ||--o{ journal_events : "what it looked at"
    users ||--o| students : "one profile"
    users ||--o{ email_codes : "6 digit, hashed, single use"
    source_documents ||--o| exam_rules : "rules read from it"

    source_documents {
        string sha256 PK
        string origin_url
        string kind "notification or other"
    }
    exam_rules {
        string document_sha256 FK
        jsonb payload "rules + every citation"
    }
    journal_runs {
        int citations_verified
        int rules_evaluated
        int messages_sent "usually 0"
    }
```

## Deployment

```mermaid
flowchart LR
    subgraph now["Runs today"]
        fe["Next.js"] --> be["FastAPI"] --> pg[("Neon Postgres")]
        be --> groq["Groq"]
        be --> ik["ImageKit"]
    end

    subgraph next["With AWS credits"]
        agentcore["AgentCore Runtime<br/>nightly agent"]
        eb["EventBridge<br/>the alarm clock"]
        bedrock["Bedrock<br/>incl. vision for scanned MPSC pdfs"]
    end

    eb --> agentcore --> bedrock
    agentcore --> pg

    style next stroke-dasharray: 5 5
```

Two things are genuinely waiting on AWS credits, and both are real rather than decorative:

- **AgentCore Runtime + EventBridge** give the agent an alarm clock. Today the nightly script exists and works; what is missing is the cloud runtime that calls it.
- **Bedrock vision** would read MPSC's scanned notifications. They are photographs of paper, so no amount of text extraction will ever read them.
