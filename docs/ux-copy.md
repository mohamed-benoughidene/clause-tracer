# Clause Tracer — UX copy

Nov 7, 2026 · from `docs/spec.md` and the HTML prototype in `prototype/`

This is the copy deck for version 1: every word the app shows, screen by screen, and the rules behind it. When the spec, the prototype and this file disagree, fix all three. Section 6 records the disagreements found and how each was settled.

Contract text, sample names and amounts are prototype data (Spec 14.5), not copy, so they're left out. Words in `[brackets]` are filled in by the app. Rows marked **(new)** cover a spec state the prototype has no words for yet; they're proposals.

## 1. Voice

Clause Tracer talks like a careful friend who has read the contract and points at the words. It never sounds like a lawyer, and it never sounds sure when it isn't.

| Rule | Do | Don't |
| --- | --- | --- |
| The app never says "I" | "This one is a walk-away." | "I'd walk away from this one." |
| "I" and "my" only in the user's own words | Position names ("Days until I'm paid"), "why this matters" notes, the message the user sends | App text, headings, buttons (see 6.2 for controls) |
| Name the playbook as the source | "Walk-away by your playbook: payment is 60 days, your limit is 30." | "This payment term is unfair." |
| Never state what the law allows | "Ask which one applies before you sign." | "This clause is unenforceable." |
| Say why when unsure | "“Reasonable” has no number, so it can't be checked against your limit." | "Unclear." |
| Point to the words | "Read 5.4 on the page. Is this right?" | "Please verify." |
| Plain, everyday words | "Ending this agreement", "who owns the work" | "Termination", "IP assignment" (except in Help's plain-English list) |
| Never "client" | "customer", "the other side", "your party" | "client" |
| Click, not tap or press | "Click a row to tick or untick it." | "Press Replace" |

**Tone by moment**

| Moment | Tone | Example |
| --- | --- | --- |
| Success | Quiet. A fact, no cheering. | "Saved", "Your review is ready" |
| Warning | Clear. Names the risk and the next step. | "This link comes from the contract, so it may not be safe." |
| Error | Calm. Says nothing is lost, then gives the fix. | "Your OpenRouter credit ran out at step 3. Add credit, then resume. Nothing done so far is lost." |
| Delete | Exact. Names the thing and says it can't be undone. | "Delete “Atlas Media retainer”?" |
| Legal | Modest. The tool compares, it doesn't advise. | "Not legal advice. Check every result yourself." |

## 2. Word list

Use the left column everywhere: screens, buttons, toasts, Help and the spec. Terms come from the glossary (Spec 2).

| Use | Not | Notes |
| --- | --- | --- |
| review | analysis, scan, job | One contract checked against one playbook. |
| playbook | rule set, template | |
| position | rule, criterion | "Rule" stays only in the First launch heading, "your own rules". |
| label | result, rating, score | Preferred, Acceptable, Walk-away, Unsure. |
| Walk-away | deal-breaker, red flag | |
| Unsure | unknown, needs review, low confidence | Never a confidence number. |
| not covered | grey parts, uncovered parts, parts no rule checked | See 6.1. |
| Missing | absent, not found | The list of positions with no text in the contract. |
| your party / the other side | client, counterparty, you / them | |
| customer | client | For lawyers' customers only. |
| suggestion | edit, redline, change | Never changes the original file. |
| privacy check | redaction, anonymisation | |
| replace (personal details) | hide, redact, mask | Details are swapped for placeholders like “Person 1”. "Hidden" means only hidden text. |
| private mode | zero data retention, ZDR | Explain once: "Only providers that don't keep your contract." |
| OpenRouter key | API key, AI key, token | See 6.1. |
| isn't loaded | the app hasn't seen, missing document | For documents the contract refers to. |
| pencilled in | AI-generated, sparkle | An AI judgment label: the stamp drawn in pencil, followed by the words “AI judgment”. |
| notification | message | "Message" means only the message to the other side. See 6.1. |

**Spelling:** British English: colour, recognise, summarise, labelled, licence (noun). One exception: the **Functional Source License** is a proper name and keeps its own spelling. Say "source available", never "open source". Spec 14.4 notes that the app's copy is British.

**Hyphens:** "not covered" as a phrase ("35 parts not covered"), "not-covered" before a noun ("the not-covered parts").

**Quotation marks:** double curly quotes for quoted words and names: “Master Agreement”, “reasonable”. Use an apostrophe only for contractions.

**Capitals:** sentence case for headings and buttons. Capitalise a label when it's named as a label: on stamps, in the summary bar, and in "should be Walk-away, not Preferred". Use lower case when it describes something: "This one is a walk-away."

**Numbers:** digits always ("3 days", "2 rounds"). Money is "$0.42", "about $0.39". Clauses are "§ 5.4" in lists and panels, and "5.4" in sentences.

## 3. Patterns

| Pattern | Shape | Example |
| --- | --- | --- |
| Primary button | Verb + object, says what happens | "Send for review", "Save key", "Delete review" |
| Cost on a button | Put the cost in the label | "Re-run for about $0.39" |
| Confirmation title | The action as a question, with the thing named | "Delete “Design retainer”?", "Turn private mode off for this review?" |
| Confirmation body | What happens, what stays, "This can't be undone." last | "Those reviews keep their own copy and won't change. You just can't re-run them. This can't be undone." |
| Confirmation buttons | Cancel, then the action's own words | "Cancel" / "Delete playbook"; "Keep running" / "Cancel review" |
| Error | What happened + what to do. Mention what's kept. Every error has a fix. | "This PDF is pictures of pages, so its text can't be read. Upload a Word version, or paste the text." |
| Banner (top) | What's true + why it matters + one action | "Your playbook changed after this review ran. The labels use the old limits. [Re-run]" |
| Chip (small) | One fact, one sentence | "This contract follows England and Wales law." |
| Empty state | What's missing + what it does + how to start. Don't repeat the button. | "No reviews yet. Check a contract against your playbook. It takes about 3 minutes and costs about $0.39." |
| Toast | Past tense or a fact, 1 to 5 words. Longer news goes in a notice. | "Saved", "Copied", "Review deleted", "Key works. Saved." |
| Panel lead | The label in one sentence, then the plain why. Name the level, never "good" or "bad". | "This one is a walk-away. You'd wait 60 days to be paid; your limit is 30." |
| Source line | `[Label] by your playbook: [fact], your limit is [value].` Code writes it | "Acceptable by your playbook: the deposit is 25%, a level you accept." |
| What to check | A yes/no question about the quote | "What to check: Does the quote give a number of revision rounds?" |
| Question to ask | A polite question the user can send | "Can we agree consent won't be refused without a good reason?" |
| Link out | "(opens in your browser)" for screen readers on every link that leaves the app. It's a desktop app, so there are no tabs. | "Add credit (opens in your browser)" |

## 4. Screen by screen

### 4.1 First launch (`index.html`)

| Element | Copy |
| --- | --- |
| Heading | Check a contract against your own rules. |
| Intro | Every label shows the exact words it rests on, so you can check it yourself. It runs on your computer with your own OpenRouter key, the account that pays for the AI. |
| Key field | OpenRouter key · placeholder `sk-or-…` |
| Buttons | Save key · Skip for now |
| Checking state (new) | Checking key… |
| Key guide summary | No key yet? Get one in 4 steps |
| Step 1 | Create an OpenRouter account · openrouter.ai · free to sign up · [Open site (opens in your browser)] |
| Step 2 | Add credit · A typical review costs about $0.30 to $0.60. |
| Step 3 | Turn off Safety Retention · In OpenRouter: Settings › Privacy. Then providers don't keep your contract, except for legally required safety screening. |
| Step 4 | Create a key and paste it above · It starts with sk-or-. |
| Sample link | Or try a sample contract first, free |
| Sample note | One label in it is wrong on purpose. Find it, and see why real reviews need checking too. |
| Legal line | Not legal advice. Check every result yourself. |
| Hero alt text | A page of black-and-white etched butterflies on aged paper. In the middle, one butterfly is red, with four eyespots: three black and one red. |

### 4.2 Home: Reviews (`home.html`)

| Element | Copy |
| --- | --- |
| Heading | Reviews |
| Storage note | Saved on this computer, encrypted. Each one deletes itself after 30 days without changes. [Change in Settings] |
| Search | Search reviews |
| Columns | Name · Date · Status · Next step · Auto-delete · Actions |
| Date cells | Edited 2 min ago · Edited just now · Yesterday, 16:20 · 3 Nov 2026 |
| Next steps | Check 9 → (Ready to check: the unchecked count) · Step 2 of 4 · about 40 s (Running) · Continue (Draft) · Resume (Interrupted) · Retry (Failed) · Open message (Done) |
| Row reasons | Stopped at: matching clauses · Couldn't read Schedule 2 |
| Offline | Needs internet |
| Auto-delete cell | In 30 days · In 3 days, with [Keep it] [Delete now] |
| Keep it toast | Kept for another 30 days |
| Row menu label | More for [review name] |
| Auto-delete notice (new) | Deleted 2 reviews that hadn't changed in 30 days. |
| Empty state | No reviews yet · Check a contract against your playbook. It takes about 3 minutes and costs about $0.39. · [Start your first review] [Try a sample contract] |
| Rename dialog | Rename review · Name · Cancel / Save · toast: Saved |
| Delete dialog | Delete “[name]”? · This removes the review, its labels and your notes from this computer. This can't be undone. · Running: This review is running. It will be stopped first. · Cancel / Delete review · toast: Review deleted |

### 4.3 New review (`new-review.html`)

| Element | Copy |
| --- | --- |
| Heading | New review |
| Steps | 1 Contract · 2 Contract check · 3 Privacy check · 4 Review |
| No key | Add your OpenRouter key to run a review. What you've done here is kept. [Add key] |
| Offline | You're offline. You can prepare this draft, but sending it for review needs the internet. |
| Section 1 | Load the contract · [Upload] [Paste text] |
| File card | [file name] · PDF · 5 pages · 929 words · real text · [Replace] |
| Preview | First page · is this the right contract? |
| Preview hint | Wrong file? Click Replace, or drop another file on this card. |
| Paste field | Contract text · Keep the clause numbers and headings. Paste only the pages you want reviewed. |
| Review name | Review name · Pick a name you'll recognise later. |
| Scanned (blocks) | This PDF is pictures of pages, so its text can't be read. Upload a Word version, or paste the text. |
| Mixed (blocks) | Pages 7 and 8 are pictures, not text. They're skipped unless you paste their text. |
| Too large (blocks) | This file is 48 MB. The limit is 20 MB. Paste only the pages you want reviewed. |
| Empty (blocks) | This file has no text. Choose another file, or paste the text. |
| Old Word (blocks) | This is an old Word file. Open it in Word, save it as .docx, then load that. |
| Not English (warns) | This contract doesn't look like it's in English. Clause Tracer is built and tested for English contracts only, so: · fewer names and addresses are found for you. Check the privacy step carefully. · more labels may be wrong or unsure. · [Choose another file] |
| Section 2 | Pick a playbook · Playbook · [Copy a starter] |
| Playbook line | Side: service provider · 11 positions · edited 2 Nov |
| Unedited starter | Copied from the starter · side: service provider · 11 example positions. You haven't changed them yet. [Make the limits yours] |
| Playbook deleted | The playbook this draft used is gone. Pick another one. |
| Section 3 | Which party in this contract is the [side]? · Picked last time · [Add a party] |
| Party details | Filled in from the contract's opening lines. Every copy of them is replaced before anything is sent. |
| Party fields | Your party · name · Address · Other side · name · Address |
| Add party dialog | Add a party · Use the name exactly as the contract writes it. · Party name · Address · Cancel / Add party · toast: Party added |
| Footer | Continue |

### 4.4 Contract check (`contract-check.html`)

| Element | Copy |
| --- | --- |
| Heading | Contract check |
| Side card | Check the split |
| Guidance | Each box should hold one section. Merge or split if a sentence is cut or two sections share a box. |
| Facts | Clauses: 45, split by section numbers · Schedules: Schedule 1 · 1 table kept · Pages: 5, all with real text |
| Paragraph split note (new) | This contract has no section numbers, so it was split by paragraph. |
| Hidden text | Found 1 piece of hidden text in 2.2: white text a reader can't see. It's kept and marked so you can see it. Any label that rests on it becomes unsure. [Show me] |
| Cut box | One box looks cut · 12.1 ends mid-sentence and 12.2 starts with its end. “notice.” probably belongs at the end of 12.1. · [Fix it] [Show me] |
| Box controls | Split box [n] · Merge box [n] with the box below · toasts: Split at the cursor · Merged with the box below · Merged 12.1 and 12.2 |
| Keys hint | M merge with next · S split |
| Footer | Looks right, continue |

### 4.5 Privacy check (`privacy-check.html`)

| Element | Copy |
| --- | --- |
| Heading | Privacy check |
| Find to replace | Type words to find and replace · [Replace this] · toast: Replaced. Check the marked words. |
| Select hint | Drag across any words on the pages to replace them, like selecting text anywhere else. Details like “the only bakery in town” can identify someone too. |
| View switch | Pages show: Real text · What the AI sees |
| List heading | What gets replaced · 7 items |
| List note | Shown on this screen only. Ticked rows are marked on the pages. Click a row to tick or untick it. |
| Row | Person 1 · Karim Benali · 2 places |
| Name variant | “Ms Jones” in 14.5 looks like Sarah Jones (Person 2). · [Same person] [Different person] · toasts: Both are Person 2 · “Ms Jones” is now Person 3 |
| Kept note | Kept: amounts, dates, durations, roles like “the Developer”, and England and Wales in the governing-law clause. |
| Private mode | Private mode for this review · Only providers that don't keep your contract. |
| Private off warning | The contract goes to the AI models as it is, names and addresses included. The models may keep it. |
| Summary | 929 words go to OpenRouter, with 7 details replaced: 2 people, 1 company, 2 addresses, 1 email and 1 ID number. |
| Caution | The check can miss things. Please look over the marked words. |
| Cost | About $0.42 and 3 minutes · credit left: $3.10 |
| Over credit | This review costs about $0.42. You have $0.30 left. If the credit runs out, the review stops. You can resume it once you add credit. · [Add credit (opens in your browser)] [Send anyway] |
| Offline (new) | Sending for review needs the internet. Your draft is saved. |
| Footer | [Back to party details] [Send for review] |

### 4.6 Review running (`running.html`)

| Element | Copy |
| --- | --- |
| Stages | 1 Reading the pages · 2 Matching clauses · 3 Judging the labels · 4 Writing the notes |
| Progress | Step 1 of 4 · Reading the pages · Spent so far $0.05 of about $0.42 · About 1 min left |
| Log lines | Read 5 pages. · Found 45 clauses. · Matched all 45 clauses to 11 positions. · Judged the labels for 11 positions. · Wrote the explanations and the summary of not-covered parts. · Finished. |
| Privacy badge | Private mode is on. Providers don't keep your contract if you've turned off Safety Retention in OpenRouter. |
| Background | [Run in background] · toast: Running in the background |
| Close note | Closing the app pauses the review. Resume picks up from the last finished step. |
| Wrong key | Interrupted at step 2 of 4 · Matching clauses · OpenRouter turned down your key. Check it in Settings, then resume. · [Open key settings] [Resume] · log: Stopped at step 2. OpenRouter turned down the key. |
| No internet | The internet dropped at step 2. Resume picks up from here. · log: Stopped at step 2. The internet dropped. |
| No credit | Your OpenRouter credit ran out at step 3. Add credit, then resume. Nothing done so far is lost. · [Add credit (opens in your browser)] |
| No private model | No private-mode model is available for step 3 right now. Wait and resume, or turn private mode off for this review. · [Turn private mode off…] |
| Done | Your review is ready · Cost $0.39 · Took 4 min · credit left: $2.71 · [Open the review] |
| Cancel dialog | Cancel this review? · So far it has cost $0.05 of about $0.42. Finished steps are kept, so you won't pay for them again. · Keep running / Cancel review |
| Private off dialog | Turn private mode off for this review? · The contract goes to the AI models as it is, names and addresses included. The models may keep it. · Cancel / Turn off · toast: Private mode off for this review |

### 4.7 Review (`review.html`)

**Top bar and banners**

| Element | Copy |
| --- | --- |
| Title | [review name] · [playbook] · playbook as of 5 Nov, 10:31 |
| Actions | Output · Rewrite · Suggestions · Re-run · Start over · [cost button: $0.39] |
| Practice banner | Practice review · One label here is wrong on purpose. Find it, open it and fix it. Real reviews work the same way. [Start a real review] |
| Playbook changed | Your playbook changed after this review ran. The labels use the old limits. [Re-run] |
| Unedited starter | This review uses the example playbook, unedited. Its limits are examples, not yours. [Make the limits yours] |
| Hidden text | This contract contains hidden text (outlined in the contract). It may be trying to fool this review. [Show me] |
| Unloaded document | This contract depends on the “Master Agreement”, which isn't loaded. It can change any result here. Ask for it and read it before you sign. |
| Law chip, one | This contract follows England and Wales law. If there's a dispute, England and Wales law settles it. |
| Law chip, two | This contract names two places' law: England and Wales in 14.6, and Algeria in Schedule 2. Ask which one applies before you sign. |
| Law chip, none | This contract doesn't say which place's law applies. If there's a dispute, the two sides could argue over it. Ask for a governing-law clause. |
| Privacy badge | Private mode: only providers that don't keep your contract see this review. · Mixed: steps 1 and 2 ran in private mode, steps 3 and 4 didn't. · toast: Private mode stays on |

**Summary bar and checking card**

| Element | Copy |
| --- | --- |
| Summary bar (counts positions) | Preferred [n] · Acceptable [n] · Walk-away [n] · Unsure [n] · [n] pencilled in · [n] document not loaded · Not covered [n] parts |
| Label definitions (?) | Preferred: The clause gives you at least what your playbook says you want. · Acceptable: Not as good as preferred, but inside the limit you set in your playbook. · Walk-away: Past the limit you set in your playbook. Ask for a change before you sign. · Unsure: The wording is too unclear to label, or the quote couldn't be confirmed. The app always says why. You decide. · Help uses the same four definitions. |
| Counter | 2 of 11 positions checked · 35 parts not covered |
| Positions done | Every position is checked. To finish, read the not-covered parts, then tick the box in Not covered. |
| Done | Done. Every position is checked and you've read the rest. You can write the message now. |
| Next | Next unchecked · J |
| Unsure-heavy | More than half of these labels are unsure. That usually means the wording is vague, or your playbook suits a different kind of contract. Read the unsure ones first: each says what it couldn't decide. |
| Tabs | Labels [n] · Not covered [n] · Missing [n] |
| Not-covered tick | I've read the 35 not-covered parts |
| Not-covered row | § 2.2 · Renews by itself every 12 months unless someone gives 30 days' notice. |
| Status | Ready to check · Done |
| Find | Find · Ctrl+F |

**Detail panel** (one per position; the sample's wording shown)

| Element | Copy |
| --- | --- |
| Title | Position [n] · [position name] |
| Lead, walk-away | This one is a walk-away. You'd wait 60 days to be paid; your limit is 30. |
| Lead, acceptable | This one is acceptable by your playbook. You get a quarter of the fee when you sign. It isn't what you'd prefer, but it's inside your limit. |
| Lead, preferred | This one meets your preferred level. Extra work has to be agreed first, and you're paid by the hour for it. |
| Lead, unsure | This one is unsure. “Reasonable” has no number, so it can't be checked against your limit. |
| Lead, missing | The contract doesn't mention this. Nothing charges the Agency for paying late, and your playbook says that's acceptable. A late payer loses nothing by waiting. |
| Lead, conditional yes | Yes, but only with a condition. You can show the work, but only if the Agency agrees in writing first. They could say no. |
| Pencilled in | Pencilled in: judged from the wording, not a number. |
| Source line | Walk-away by your playbook: payment is 60 days, your limit is 30. |
| Starter source line (new) | Walk-away by the example playbook: payment is 60 days, the example limit is 30. |
| Other level | Why it could be walk-away · If the Agency decides what's reasonable, the rounds have no limit, and unlimited is the worst value. |
| Readings | Reading 1: a small number of rounds, decided together. · Reading 2: as many rounds as the Agency asks for. |
| Question | Question to ask: “Can we agree that 2 rounds of revisions are included, and extra rounds are paid at the hourly rate?” |
| Conflict | These clauses disagree. Ask which applies. |
| Range | 14.3 gives a range. The worse end was used. |
| Quote failed | Couldn't confirm the wording. Check 12.2 yourself. · Unsure: asked twice, and both times the AI's quote wasn't in the contract. |
| Unloaded doc | Document · Not loaded · Refers to a document that isn't loaded: Master Agreement |
| Trail heading | Evidence trail |
| What to check | What to check: Does the quote say you're paid within 60 days of the invoice date? |
| Decision (walk-away) | Read 5.4 on the page. Is this right? · 1 Yes, it's a walk-away · Kept. Goes into the message. · 2 No, change the label… · Opens Change it. · 3 Doesn't matter for this deal · Kept. Left out of the message. |
| Decision (unsure) | 1 Yes, ask about it · Kept. Goes into the message. (2 and 3 as above) |
| Decision (others) | [Looks right] [Change it] · toast: Checked |
| Note | Note · Add a note (optional) |
| More | More |

**Dialogs**

| Dialog | Copy |
| --- | --- |
| Change it | Change label · § [n] · [position] · Tool label · Your label · New label · Note · History: Tool label Walk-away · your label Unsure · Cancel / Save · toasts: Saved. Your label: Unsure · Back to the tool label, unchecked |
| Rewrite | Rewrite § [n] · [Write it yourself] [Ask AI] · The AI aims for the preferred level of every position this clause affects: [positions]. · Instruction (optional) · Before / After · Removed words are struck through. Added words are highlighted. · The smallest change that meets your position. · Information only. Doesn't change the counter or the review status. · [Use as suggestion] · toast: Saved as a suggestion |
| Rewrite, new details | Before the re-check, known names and addresses are swapped for placeholders. No new personal details found. |
| Rewrite failed | The new wording didn't pass the quote check, so it can't be labelled. You can still save it, as unsure. · [Save as unsure] · toast: Saved as an unsure suggestion |
| Suggestions | Suggestions · [n] · One per clause. The original file is never changed. Suggestions go in the message you send. · Written with AI · label is information only · Written by you · label is information only · [Edit] [Remove] |
| Remove suggestion | Remove this suggestion? · It won't go in the message. The clause in the contract is unchanged. · Cancel / Remove · toast: Suggestion removed |
| Link warning | Open a link from the contract? · This link comes from the contract, so it may not be safe. It opens in your browser, outside Clause Tracer. · [address] · Cancel / Open link · toast: Opened in your browser |
| Re-run | Re-run this review? · Uses your playbook as it is now, asks again which party is yours, and keeps your privacy check. Estimated cost: about $0.39. Labels and notes stay for positions whose levels didn't change. · Cancel / Re-run for about $0.39 |
| Start over | Start over with this contract? · Makes a new review from the same file. This review stays in your list, so nothing is lost. · Cancel / Start over |
| Unloaded document | “Master Agreement” isn't loaded · This contract refers to it, and it can change any result here, such as the liability cap. Ask the other side for it and read it before you sign. · Got it |
| Models and cost | Models and cost · Step / Model · Match · Extract · Judge words positions · Explain (the same step names as Settings) · This review cost $0.39 so far. · [Change in Settings] · Close |
| Practice answer | Practice review · Position 10 · My liability is capped · You found it. This label was wrong: § 11.1 says your liability is unlimited, so it should be Walk-away, not Preferred. With no cap you could owe far more than the whole fee. · Real reviews can be wrong too, so always read the clause. · Your position: your liability is capped at the fees paid · Tool label / It should be · [Back to the practice review] |

### 4.8 Output (`output.html`)

| Element | Copy |
| --- | --- |
| Title | Output · [review name] |
| Type | Message · Report · Both |
| Unchecked warning | 9 positions aren't checked yet · Unchecked items are marked in the report and the checklist, never in the message. · [Go back and check] [Continue anyway] · toast: Continuing with unchecked positions |
| Legal line | Not legal advice. Check every result yourself. [What this means] |
| Message fields | To · From · Tone: Friendly · Formal |
| Ask for | Ask for · One line for each issue. Tick a line to send it, untick it to leave it out. · unticked suffix: Left out |
| Ask-for line | Payment (5.4): could invoices be paid within 15 days of the invoice date? |
| Nothing to ask | Nothing to ask for from your playbook. This only means the contract matches your playbook. It doesn't mean it's safe to sign. |
| Message | Message · [Regenerate] [Copy] · toasts: Message regenerated · Copied |
| Labels changed | Labels changed since this message · Regenerate to use the new labels. This replaces your current text. · [Keep this message] [Regenerate] |
| Report options | Summary · Full contract · Include your notes |
| Report preview | Review report · Asked for · Not checked: 9 positions aren't checked yet. They're marked here as unchecked. |
| Both tab | Edit the text on the Message tab. · Summary of the six points asked for, with the review labels. Includes your notes only when you turn that on. · [Open the report] |
| Save PDF | Save report as PDF · Cancel / Save PDF · notice: Saved with the review. · toast: Saved |

### 4.9 Playbooks (`playbooks.html`)

| Element | Copy |
| --- | --- |
| Heading | Playbooks |
| Intro | The positions you want in a contract. Each review keeps its own copy, so editing a playbook never changes past reviews. |
| Actions | Create blank · Copy a starter · Import · Search positions |
| Filter | All customers · None · [customer] · toasts: Showing playbooks for every customer · Showing playbooks with no customer · Showing playbooks for [customer] |
| Card | Side · Customer · Positions · Used by 4 reviews · edited 2 Nov · Not used by any review |
| Card actions | Edit · Duplicate · Export · Delete · toasts: Copy made: [name] (copy) · Exported as [file].ctplaybook |
| Starter card | Want a place to start? The freelancer starter has 11 example positions. Copy it, then make the limits yours. · Starter · Freelancer receiving a service agreement · read-only · [Preview starter] |
| Import failed | That file isn't a Clause Tracer playbook, so it can't be imported. Playbook files end in .ctplaybook. · [Choose another file] |
| Delete, used | Delete “[name]”? · 4 reviews use this playbook. Those reviews keep their own copy and won't change. You just can't re-run them. This can't be undone. · Cancel / Delete playbook · toast: Playbook deleted |
| Delete, unused | Delete “[name]”? · No reviews use this playbook. This can't be undone. |

### 4.10 Starter preview (`starter-preview.html`)

| Element | Copy |
| --- | --- |
| Heading | Freelancer receiving a service agreement |
| Line | Starter · side: service provider · example positions, edit them for your situation. |
| Read-only note | These are examples, so you can't change them here. Copy them, then make the limits yours. |
| Wording note | Reviews that use an unedited copy say “by the example playbook”. |
| Columns | # · Position · Type · Preferred · Acceptable · Walk-away · Missing |
| Notes prefix | Why this matters: |
| Button | Copy to your playbooks |

The eleven starter positions and their "why this matters" notes are in Spec 7; they're in the user's voice on purpose.

### 4.11 Import preview (`import-preview.html`)

| Element | Copy |
| --- | --- |
| Heading | Import “[file name]”? |
| Line | [playbook] · side: [side] · [n] positions |
| Warning | This file came from someone else. Read every position before you import it. |
| Duplicate | You already have “[name]”, so this one is saved as “[name] (imported)”. |
| Buttons | Cancel / Import · toast: Imported |

### 4.12 Playbook editor (`playbook-editor.html`)

| Element | Copy |
| --- | --- |
| Header | [playbook name] · Unsaved changes · [Save] · toast: Saved |
| Details | Name · Side · Customer (None) |
| List | Positions · [n] · Drag position [n] to reorder · Delete position [n] |
| Starter copy note | Copied to your playbooks. These are example positions, so make the limits yours. Until you do, reviews say “by the example playbook”. |
| Position form | Position [n] · Topic · Type: Number · Yes/no · Words |
| Number | Unit (days, %, months, rounds) · Direction: Lower is better · Higher is better · At or under · [unit], 1–120 · Everything beyond Acceptable · Filled in from Acceptable |
| Missing level | If the contract says nothing · The level used when no clause matches |
| Yes/no | If the answer is yes · Must be better than the no level · If no, unclear or missing · Missing always counts as no, so there is no separate missing level · Reads as: Yes counts as Preferred · No, unclear or missing counts as Acceptable |
| Words | Preferred reads as · Acceptable reads as · Walk-away reads as · placeholder: Describe this level in a sentence |
| Why this matters | Why this matters to me (optional) · Never exported. Only sent to the AI if you turn that on in Settings. |
| Validation (new) | Acceptable must be worse than Preferred. · Enter a number from 1 to 120. · Give the position a topic. |
| Leave dialog | Leave without saving? · If you leave now, you'll lose your changes to “[name]”. · Stay / Leave without saving |
| Delete position | Delete “[position]”? · It's removed from this playbook when you save. Once you save, it can't be undone. The other positions stay. · Cancel / Delete position · toast: Position deleted |

### 4.13 Customers (`customers.html`)

| Element | Copy |
| --- | --- |
| Heading | Customers |
| Intro | Link a playbook to a customer to keep their positions apart. |
| Columns | Customer · Playbooks · Actions · 1 playbook / [n] playbooks |
| Footnote | Deleting a customer unlinks its playbooks and keeps them. |
| Add | Add customer · Customer name · e.g. Atlas Media · Cancel / Add customer · toast: Saved |
| Rename | Rename “[name]” · Name · Cancel / Rename · toast: Saved |
| Delete | Delete “[name]”? · Its 1 playbook stays / Its [n] playbooks stay, unlinked from this customer. This can't be undone. · No playbooks use this customer. This can't be undone. · Cancel / Delete customer · toast: Customer deleted |

### 4.14 Settings (`settings.html`)

| Element | Copy |
| --- | --- |
| Key | OpenRouter key · sk-or-v1-8f2c…a91e · saved in your password store · [Change] [Remove] [Open the key guide] |
| Change key | Change the OpenRouter key · New key · It's checked with OpenRouter, then replaces the old one in your password store. · Cancel / Check and save · toast: Key works. Saved. |
| Remove key | Remove the OpenRouter key? · This removes the key from your password store. Reviews won't run until you paste a key again. · Cancel / Remove key · toast: Key removed |
| Privacy | Private mode for new reviews · Only providers that don't keep your contract. Reviews you've already started keep their own setting. |
| Notes toggle | Send “why this matters” notes to the AI · Gives better explanations. Known names are replaced, but the privacy check doesn't cover notes. · [What gets sent] |
| Notifications | Notify when a review finishes · Shows a notification when a review is done, even if you're in another window. |
| Appearance | Colours: Match system · Light · Dark · Follows your computer's setting. · Text size: 100% · 125% · 150% · 200% |
| Storage | Delete reviews after no changes for: 7 days · 30 days · 90 days · 12 reviews on this computer · [Delete all reviews] |
| Delete reviews | Delete all 12 reviews? · This removes every review on this computer, with its labels and notes. Your playbooks, customers and key stay. This can't be undone. · Cancel / Delete all reviews · toast: Reviews deleted |
| Lower auto-delete | Lower auto-delete to 7 days? · 4 reviews haven't changed in 7 days. They'll be deleted on 9 Nov, in 3 days, unless you change them first. · Cancel / Lower to 7 days |
| Data | Nothing is removed without asking first. · Everything · Reviews, playbooks, customers, settings and the key, all from this computer. · [Delete everything] |
| Delete everything | Delete everything? · Reviews, playbooks, customers, settings and the key are all removed from this computer. This can't be undone. · Cancel / Delete everything · toast: Everything deleted |
| Advanced: models | Model choice: One for every step · One per step · Model: Claude Sonnet 5.5 (recommended) · Steps: Match · Extract · Judge words positions · Explain · Summarise not-covered parts · Rewrite · Write message · Jev is only offered for match and judge. In private mode, only models that don't keep your contract are offered. |
| Model can't do step (new) | [Model] can't do this step. Pick another model. |
| Untested model (new) | This model isn't tested with Clause Tracer yet. Labels may be less reliable. |
| About | Clause Tracer 1.0.0 · Functional Source License · Not legal advice. · [Check for updates] · You have the latest version. · (new) Version [n] is out. [Open release page (opens in your browser)] |

### 4.15 Help (`help.html`)

| Element | Copy |
| --- | --- |
| How a review works | Load a contract and pick a playbook. · Check the split and the private details. · The app labels each position and shows its evidence. · You check every label: confirm it or change it. · Write a message to the other side, or save a report. |
| Words used in this app | There are four labels, plus grey for parts no position covers. Each is shown as a stamp. · Preferred, Acceptable, Walk-away, Unsure: the same definitions as the review's “?” ·  Not covered: No position covers this part. |
| Legal terms in plain English | Indemnity, Limitation of liability, Governing law, Termination, Confidential information, Intellectual property (IP), Work made for hire, Non-compete, Warranty, Force majeure (definitions as in the prototype) |
| Key guide | Get an OpenRouter key · Create an account, add credit, turn off Safety Retention, create a key. |
| What gets sent | Only your positions and the contract go to OpenRouter, with names swapped for placeholders like “Person 1”. Never playbook names, customers, your notes, or To and From names. No telemetry. · [Change what gets sent in Settings] |
| Shortcuts | Ctrl+K Commands · J Next unchecked · ] / [ Next / previous label · 1 / 2 / 3 Decide on a walk-away or unsure label · Ctrl+F Find in contract · Ctrl+/ opens the full list. |
| Legal | Not legal advice · Clause Tracer isn't a lawyer, and this isn't legal advice. · Free to use, including for paid work. Source available under the Functional Source License, with no warranty. Each version becomes Apache 2.0 two years after its release. Sample contract: Dominic Fallows, CC BY-SA 4.0. · [Read the licence (opens in your browser)] |

### 4.16 Error (`error.html`)

| Element | Copy |
| --- | --- |
| Heading | Something in the app broke |
| Log | Opened your review. · Something in the app broke while loading it. |
| Reassurance | Your files are safe. Copy the details and report the problem on GitHub. |
| Details | Details · ERR-STEP6B-412 · The details hold only the app version, the step and this code. No contract text. · [Copy the details] · toast: Copied |
| Way out | Back to reviews |

### 4.17 Everywhere

| Element | Copy |
| --- | --- |
| Command palette | Search commands · Ctrl+K |
| Toasts | Saved · Copied |
| Close buttons | Close (icon label) |
| Back | Back to reviews |
| Legal line on every message and report page | Not legal advice. Check every result yourself. |

## 5. Localisation notes

Version 1 is English only (Spec 9). Write now so translation later is cheap:

- Build sentences from whole strings with placeholders (`[n] positions aren't checked yet`), never by joining fragments. Arabic and French change word order.
- Give every count its own singular and plural string ("1 playbook" / "2 playbooks"). Arabic has more plural forms.
- Leave room: French runs about 20% longer than English. Buttons with costs ("Re-run for about $0.39") are the tightest.
- Keep label names (Preferred, Acceptable, Walk-away, Unsure) as single terms in a glossary file, so they translate once.
- "Walk-away" and "pencilled in" are idioms. Translators need the glossary meaning, not the words.

## 6. Disagreements found, with fixes

Found on 7 Nov 2026 by comparing every string in the prototype with the spec. **All fixes below were applied the same day** to the prototype and the spec, using the recommended option each time ("position" over "rule", no "my" in controls, one count on the review screen). Kept as a record of why the words are what they are.

### 6.1 Terms used two ways

| # | Where | Now | Fix |
| --- | --- | --- | --- |
| 1 | Review counter, Help, Spec 4.4 and 14.1 | "2 of 11 rules checked", "parts no rule checked", but "Position 1", "9 positions aren't checked yet" | Pick one word. Recommended: keep **position** (the glossary term) everywhere: "2 of 11 positions checked · 35 parts not covered". "Rule" is plainer, but then it must replace "position" everywhere, including the editor. |
| 2 | Review, running log, Settings, Spec | "Not covered", "grey parts", "uncovered parts", "parts no rule checked" | Use **not covered**: "Summarise not-covered parts", "I've read the 35 not-covered parts". |
| 3 | Settings heading, Spec 14.3 | "AI key" | **OpenRouter key**, as everywhere else. |
| 4 | Running toast, Settings notifications | "You'll get a message when it's done", "Shows a message when a review is done" | **notification**. "Message" means only the message to the other side. |
| 5 | Unloaded-document banner | "which the app hasn't seen" | "which isn't loaded", as in the panel and the dialog. |
| 6 | Starter wording, three versions | "check the limits fit you", "change the limits to yours", "Make the limits yours" | **Make the limits yours** everywhere. |
| 7 | Running, no private model | "No private-mode model is free" | "available". "Free" reads as no cost. |
| 8 | New review | "Press Replace" | "Click Replace". |
| 9 | Help "How a review works", Spec 3 step 10 | "Looks right or Change it" | Walk-away and unsure labels take a three-way decision (Spec 4.4). Help: "You check every label: confirm it or change it." |

### 6.2 "My" in the app's own controls

The voice rule (Spec 14.4) keeps "I" and "my" for the user's own words. These controls break it:

| Now | Fix |
| --- | --- |
| Delete all my data (Settings, button and dialog) | Delete everything · Delete everything? |
| Send my ‘why this matters’ notes to the AI | Send “why this matters” notes to the AI |
| Tell me when a review finishes | Notify when a review finishes |
| Copy to my playbooks (Starter preview) | Copy to your playbooks |
| Include my notes (Output) | Include your notes |
| Write it myself (Rewrite) | Write it yourself |
| (my copy) in the playbook picker | Remove. The picker lists only the user's playbooks. |

Decision: controls don't use "my". The not-covered tick, "I've read the 35 not-covered parts", stays in first person because the user is stating something they did.

### 6.3 Wrong or clashing numbers on the review screen

| # | Problem | Fix |
| --- | --- | --- |
| 1 | § 12.2 (position 4) has a **walk-away** pin and list row, but its panel says **Unsure** ("The quote found doesn't match the contract word for word"). | Make the pin and the row Unsure, since this is the sample for the quote-check state (Spec 14.2). Then recount the summary bar and the checking line. |
| 2 | The summary bar counts positions (Walk-away 4, Acceptable 4 including 3 missing). The checking line counts labels ("5 walk-away · 1 acceptable · 3 missing"). Same screen, different numbers. | Keep one count. Recommended: the summary bar's (positions). Drop the second line, or make it match. |
| 3 | The panel lead for acceptable says "fine by your rules". | "This one is acceptable by your playbook." |

### 6.4 Spec text to update

- Spec 14.3 and 6.1 step 11: "Summarize uncovered parts" becomes "Summarise not-covered parts". Spec 14.4: "colour" is already British; make the rest of the spec British too, or note that the app's copy is British.
- Spec 14.3: "AI key" becomes "OpenRouter key". "Delete all my data" becomes "Delete everything".
- Spec 4.4 and 14.1: "rules checked" becomes "positions checked" .
- Spec 14.3 Notifications: "Tell me when a review finishes" becomes "Notify when a review finishes".

### 6.5 Small things

- Quotation marks are mixed: 'Reasonable' (straight), ‘why this matters’ (single curly), ‘Master Agreement,’ (US comma inside). Use double curly quotes, with the punctuation outside: “Master Agreement”,
- Contract check shows "Contract check: clauses" and "Contract check" as two headings. Keep one: "Contract check".
- Settings: "Private mode default for new reviews" reads awkwardly. Use "Private mode for new reviews".
- Change it uses a short position name ("Days until paid") in its title and the full one below it. Short names aren't in the spec. Either add them to the playbook model or use the full name.

### 6.6 Second review, 7 Nov 2026

A review of this file against its own rules. All applied the same day to this file, the prototype and the spec.

| # | Problem | Fix |
| --- | --- | --- |
| 1 | The unedited-starter row in 4.3 wasn't synced. | Now matches the prototype. |
| 2 | Examples broke the deck's own rules: straight quotes, "Your rule", "(opens in a new tab)" in a desktop app, "playbook(s)". | Curly quotes, "Your position", "(opens in your browser)", separate singular and plural strings. |
| 3 | Two verbs for one action in the privacy check: "hide" and "replace". | **Replace** everywhere. "Hidden" now only means hidden text. |
| 4 | Each label had two definitions: one in the review's “?”, another in Help. | One definition each, used in both. "Deal-breaker" is gone. |
| 5 | Leads that judged ("This one is good") or were unclear ("This one isn't in the contract"). | "This one meets your preferred level." "The contract doesn't mention this." |
| 6 | Errors with no fix (too large, empty) and an empty state that repeated its button. | Each now says what to do next. |
| 7 | The hidden-text banner named only a colour ("marked in yellow"). | "outlined in the contract". Colour is never the only signal. |
| 8 | The background toast had 11 words. | "Running in the background". |
| 9 | The sample review cost $0.39 on the review screen but $0.42 when it finished running. "Check 5 →" counted nothing visible. | $0.39 everywhere, with $2.71 credit left. "Check 9 →", the unchecked count. |
| 10 | "licence" in the spelling rule, but "MIT license" in the copy. | "MIT License", a proper name, as the one exception. |

### 6.7 Cross-check with the spec and design system, 7 Nov 2026

The spec, this file, `design-system.md` and the prototype were compared. All fixes were applied the same day.

| # | Problem | Fix |
| --- | --- | --- |
| 1 | The licence: the repo was AGPL-3.0, the spec said "MIT or Apache 2.0", and the app said "MIT License" and "Open source". | The **Functional Source License** (FSL-1.1-ALv2) everywhere. The app says "source available", never "open source". |
| 2 | The spec still said not-covered parts get a grey mark on the page, but ADR 0001 says they're only listed. Help said every label is "a stamp in the margin". | Not covered parts aren't marked on the page. Help: "Each is shown as a stamp." |
| 3 | Two spec lines missed the earlier fixes: the unloaded-document banner and "parts not checked by any rule". | Synced with 4.7. |
| 4 | "Orange marks" in the privacy check named only a colour. | "the marked words" |
| 5 | The Models dialog named the steps differently from Settings. | The Settings names in both. |
| 6 | "The AI judgment tag" described a separate tag, but it's a pencilled stamp. | Word list updated. |

