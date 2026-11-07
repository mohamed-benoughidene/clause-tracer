# Clause Tracer — Version 1 Spec

Nov 4, 2026 · @Mohammed

Version 2, after a five-reviewer inspection on 4 Nov 2026. This is the standalone description of what Clause Tracer version 1 is and how it works. The decision history lives in the Decision history tab.

## 1. What it is

Clause Tracer is a free, source-available desktop app that checks a contract against the user's own rules, called a playbook, and shows the evidence for every result. It runs on the user's computer with the user's own OpenRouter key (the account that pays for the AI). Nothing goes to a server run by the project.

**Who it's for**

- **Primary:** freelancers who aren't lawyers, checking contracts the other side sends them.
- **Secondary:** solo lawyers and small firms reviewing contracts for their customers.

**Core idea:** the AI can be wrong, so every result comes with evidence the user can check in one click. The user checks every position. Code, not the AI, makes every decision it can.

**The name:** the review follows a trail through the contract, like a red thread from each result to the text that supports it. See the brand file `clause-tracer-brand-philosophy.md`.

**Version 1 scope:** English contracts only, one starter playbook for freelancers, Linux and Windows.

## 2. Glossary

The app's own text never uses the word "client," because contracts use it for one of the parties.

| Term | Meaning |
| --- | --- |
| Review | One contract checked against one playbook, from loading to output. Saved until deleted. |
| Review status | Draft, Running, Interrupted, Failed, Ready to check, or Done. See 6.3. |
| Playbook | A saved set of positions the user wants in a contract. Users create blank ones or copy a starter. |
| Starter playbook | A read-only playbook shipped with the app, marked as example positions. Copied before use. |
| Playbook snapshot | The copy of the playbook a review takes at "Send for review." Later edits don't change it. |
| Side | The role a playbook protects, named by the user, such as "service provider" or "receiving party." |
| Customer | A person or business a lawyer works for, kept in the Customers list. A playbook can be linked to one customer. |
| Position | One rule in a playbook, like "paid within 15 days." Has a topic, a type, levels, and a missing level. |
| Position type | Number, yes/no, or words. Decides whether code or AI picks the label. |
| Level | Preferred, acceptable, or walk-away. Each position defines what counts at each level. |
| Acceptable level | A position's middle level. Never revealed in messages sent to the other side. |
| Missing level | The label a position gets when the contract says nothing about it. Can be preferred, acceptable, walk-away, or unsure. |
| Party | A person or company named in the contract. |
| Your party | The party the user picks as the playbook's side at each review. |
| Other side | Every party that isn't your party. |
| Label | The result for one position: preferred, acceptable, walk-away, or unsure. A clause can carry several labels. |
| Tool label | The label code or AI gave. |
| Your label | The label after the user checks it. Outputs use this one. |
| Unsure | A label meaning the tool couldn't decide or couldn't confirm the wording. Always explains why. |
| AI judgment | A label picked by AI (words positions), telling the user to look closer. It is drawn in pencil, not ink: a dashed graphite stamp with a hatched colour block and a grey dashed underline on the clause, and the note says "Pencilled in: judged from the wording, not a number." No sparkle icon. |
| Missing | A value meaning the contract has no text for a position. It gets the missing level. |
| Missing list | Positions with no text in the contract whose missing level isn't preferred. |
| Clause | One numbered piece of the contract as the app splits it, or one paragraph when the contract has no numbers. |
| Original pages | A PDF contract's own pages, shown as pictures of the page the way a PDF reader shows them. |
| Typeset pages | Pages the app lays out itself for a Word file, a text or Markdown file, or pasted text, which have no pages of their own. |
| Not covered | A clause no position covers. It gets no label and no mark on the page; it's listed with a one-line summary in the Not covered tab. |
| Evidence | The exact clause text behind a label, with its location. |
| Evidence trail | Links from a label to every clause that affects it, including cross-references. |
| Hidden text | Text in the file a reader can't see, such as white or tiny text, Word comments, or tracked changes. |
| Suggestion | Wording the user or AI wrote for a clause. Has an information-only label. Never changes the original file. |
| Placeholder | A stand-in like "Person 1" that replaces personal data before text is sent to the AI. |
| Privacy check | A required screen where the user confirms what gets replaced, before anything is sent. |
| Private mode | Requests go only to AI providers that promise zero data retention. On by default. See 8.2 for what this does and doesn't cover. |
| Quote check | Code confirming that every quote the AI returns exists word for word in the text that was sent. Before comparing, curly quotes become straight quotes and repeated spaces and line breaks collapse, in both texts. |
| Jev | A decision model from TypeSafe AI that returns choices with probabilities but can't write text. Optional, under test. |
| Test set | Ten contracts with known correct answers, used to check accuracy after every change. |

## 3. User flow

One review, from opening the app to sending a reply.

1. **First launch only.** The user sees the "not legal advice" notice and a guide to creating an OpenRouter key, adding credit, and turning off Safety Retention. They paste the key, or skip to look around first.
2. **Start a review.** From Home (titled "Reviews" in the app), click New review.
3. **Load the contract.** Upload a PDF with real text, a Word file (.docx), or a text or Markdown file (.txt, .md); drag it in, or paste text. Name the review.
4. **Pick a playbook.** Choose one of their playbooks, or copy a starter.
5. **Pick your party.** The app asks "Which party in this contract is the \[playbook's side\]?" The party picked last time is preselected. Then type each party's name and address once, prefilled from the contract's opening lines.
6. **Contract check.** See how the app split the contract into clauses, and fix any bad split. Hidden text is shown and marked.
7. **Privacy check.** The contract is shown with personal data highlighted. The user adds missed items, removes false alarms, and marks name variants as the same or different person. They see the estimated cost and click "Send for review."
8. **Review running.** Progress and cost are shown. The user can leave the screen. The review runs while the app is open.
9. **Review screen.** The contract appears with labels on clauses, the Not covered and Missing lists beside it, and a summary bar. Each label opens to show the plain-words why and its evidence trail.
10. **Check every position.** The user confirms or changes each label and each Missing item (walk-away and unsure labels take a decision, see 4.4). Then they tick that they've read the not-covered parts.
11. **Fix wording (optional).** The user highlights a clause to rewrite it, by hand or with AI, or adds a clause from the Missing list.
12. **Output.** The user makes a message to the other side, a report, or both. For a message, they tick which items to ask for, then fill in to, from and tone.

The review is saved at every step, so the user can stop and come back.

## 4. Features

### 4.1 Playbooks

- Users create as many playbooks as they want: blank, copied from a starter, duplicated, or imported from a file. Starters are read-only and must be copied to edit.
- Each playbook has a name, a side (typed by the user, such as "service provider"), and optionally one customer.
- Each position has a topic, a type, levels, a missing level, and an optional "why this matters to me" note.
- **Number positions** set a unit (days, %, months, rounds), a direction (lower is better, or higher is better), two limits, and a missing level. Preferred is at or beyond the first limit, acceptable at or beyond the second, and everything past that is walk-away.
- **Yes/no positions** set the question and two levels: one for "yes" and one for "no, unclear or missing." Their missing level is always the "no" level, not a separate field. The "yes" level must be better than the "no" level.
- **Words positions** describe each level in a sentence and set a missing level.
- Validation: limits must be numbers of zero or more, percentages at most 100, and the preferred limit must be stricter than the acceptable limit for the chosen direction. Every required level must be filled.
- Exported playbook files contain name, side and positions. Never the customer link or "why this matters" notes.
- Version 1 positions cover business terms only, not what a country's law allows.

### 4.2 Privacy check

- Required before anything is sent to the AI. After "Send for review," the contract check, privacy check and party details are read-only. "Start over with this contract" makes a new review.
- **Replaced:** names of people and companies, addresses, emails, phone numbers, ID numbers, bank numbers.
- **Kept:** amounts, dates, durations, roles the contract defines (such as "the Contractor"), and the place named in the governing-law clause.
- Every copy of a party's typed name and address is replaced. Presidio (a local tool that finds personal data) catches the rest, set up to detect company names and full addresses.
- Placeholder types: Person N, Company N, Address N, Email N, Phone N, ID N, Bank N. They use a marker format ordinary contract text can't contain. Contract text that already looks like a placeholder is escaped first.
- Name variants ("Sarah Jones," "Ms. Jones," "Sarah") share one placeholder. The user can split or merge them.
- The user can select any text to replace it, or untick a false alarm.
- A hint on screen: "Drag across any words on the pages to replace them, like selecting text anywhere else. Details like “the only bakery in town” can identify someone too."

### 4.3 Review screen

- The contract is shown in full, with real names, page by page and scrollable, like reading it in a PDF reader. A PDF is shown as its original pages; a Word file, a text or Markdown file, or pasted text is shown as typeset pages. Both look and work the same way: page thumbnails, zoom, search. The user never sees placeholders after the privacy check.
- A link printed in the contract opens only after a warning: "Open a link from the contract?" It then opens outside the app.
- Each clause a position covers is highlighted on the page with a wash in its label's colour and a numbered pin in the margin. A clause affecting several positions shows several labels on its pin. Hidden text, which may be invisible on the original page, is outlined where it sits.
- Clauses no position covers are not drawn on the page. Each one is listed, with its one-line summary, in the Not covered tab.
- **Summary bar:** counts of each label, pencilled-in labels, documents not loaded, and parts not covered. If more than half the labels are unsure, a note above the labels says: "More than half of these labels are unsure. That usually means the wording is vague, or your playbook suits a different kind of contract. Read the unsure ones first: each says what it couldn't decide."
- **Governing-law chip:** "This contract follows \[place\] law. If there's a dispute, \[place\] law settles it." Or, with none: "This contract doesn't say which place's law applies. If there's a dispute, the two sides could argue over it. Ask for a governing-law clause." Or, with two: "This contract names two places' law: \[place\] in \[clause\], and \[place\] in \[clause\]. Ask which one applies before you sign." It is never judged.
- **Unloaded document banner:** "This contract depends on the “\[document name\]”, which isn't loaded. It can change any result here. Ask for it and read it before you sign."
- **Hidden text banner:** "This contract contains hidden text (outlined in the contract). It may be trying to fool this review."
- **Playbook changed banner:** "Your playbook changed after this review ran. The labels use the old limits." with a Re-run button. Shown when the playbook differs from the review's snapshot.
- **Unedited starter banner:** "This review uses the example playbook, unedited. Its limits are examples, not yours." with a "Make the limits yours" button to the playbook editor. Labels then say "by the example playbook."
- Beside the contract: the checking card (counter, "Next unchecked"), then three tabs. **Labels** lists every pinned label; **Not covered** lists the clauses no position covers and holds the not-covered tick; **Missing** is the Missing list, where each item says what's absent and why it matters.
- Every label word has a "?" with a plain definition. Four warnings get a top banner, because each can change every result: hidden text, an unloaded document, a changed playbook, and an unedited starter. Everything else, such as governing law and the privacy badge, is a small chip, so the warnings that matter don't get lost among many.

### 4.4 Checking

- Each label and each Missing item opens a detail panel. It shows the quoted evidence first, with the exact words highlighted, and the plain-words why below it. AI judgment and unsure labels also show "Why it could be \[the next level\]." The panel has "Looks right" and "Change it," both with an optional note. Notes can be edited later.
- "Change it" offers preferred, acceptable, walk-away, or unsure. Both the tool label and your label are kept. Undo returns to the tool label and marks the position unchecked.
- **Checking a walk-away or unsure label takes a decision, not a tick.** The card asks "Read [clause] on the page. Is this right?" with three answers (keys 1, 2, 3): "Yes, it's a walk-away" for a walk-away, or "Yes, ask about it" for an unsure label (kept, goes into the message), "No, change the label…" (opens Change it), and "Doesn't matter for this deal" (label kept, left out of the message). Preferred and acceptable labels are checked with one tick. A small mark on the pin shows the decision. This stops checking from becoming a habit of clicking.
- Each panel has a "What to check" line, such as "Does the quote say you're paid within 15 days?" AI judgment labels add: "If you're not sure, choose Change it, then Unsure."
- The counter shows "11 of 11 positions checked · 35 parts not covered." It counts each position once, and each not-covered clause once.
- The review becomes **Done** automatically when every position is checked and the tick "I've read the 35 not-covered parts" is set.

### 4.5 Evidence trail

This is the feature the product is named after.

- Each label lists every place in the contract that affects it. Clicking one scrolls to it and highlights the exact words, not the whole clause. Back returns to the label.
- Code builds the links: references like "see Section 14.2," and defined terms like "Services" back to their definition.
- Override clauses ("in case of conflict, this section prevails") join a label's trail when they name its clause, section or subject. Overrides that name nothing join every trail.
- A reference to a document that isn't loaded ("as defined in the Master Agreement") appears as "Refers to a document that isn't loaded."

### 4.6 Writing

- The user highlights a clause and rewrites it by hand, or asks the AI with an optional instruction. The AI aims for the preferred level of every position the clause affects.
- The user can add a clause from a Missing list item.
- Before a rewrite is sent for re-check, code replaces every known name and address with its placeholder, and Presidio checks for new personal data, which the user confirms.
- Each suggestion is re-checked against every position its clause affects and shown before and after. Its label is for information only and doesn't change the counter or status.
- One suggestion per clause. A new one replaces the old after confirmation. Suggestions can be edited or removed.
- A suggestion that fails its quote check can still be saved, labeled unsure.
- The original contract file is never changed.

### 4.7 Outputs

The user makes a message, a report, or both. If positions are unchecked, a warning says how many, with "Continue anyway." Unchecked items are marked in the report and checklist, never in the message text.

**Message to the other side**

1. A checklist of what to ask for. Ticked by default: walk-away labels, unsure labels, unloaded documents, and suggestions. Unticked: acceptable labels. Preferred labels aren't listed.
2. To, from, and tone (friendly or formal), prefilled from the contract.
3. The AI writes the message with "\[TO\]" and "\[FROM\]" markers. Code fills in real names afterwards.
4. Editable text, regenerate, and copy. The "not legal advice" line shows above the message box, never inside the copied text.
5. If nothing needs asking: "Nothing to ask for from your playbook. This only means the contract matches your rules. It doesn't mean it's safe to sign."
6. The last message is saved with the review. If labels change afterwards: "Labels changed. Regenerate?"

**Report**, saved as PDF, in one of two formats:

- **One-page summary:** a legend, label counts, each label with its quote, why, and changes you made, the Missing list, unsure questions, suggestions, the playbook name and snapshot date, and the privacy mode used. Quotes are cut at two lines. It may run to a second page.
- **Full contract:** the whole contract with highlights, labels and suggestions.
- An "Include your notes" tickbox, off by default. Every page has a "Private" footer and the "not legal advice" line. The save dialog notes that saved PDFs aren't encrypted and aren't removed by auto-delete.

## 5. Labeling rules

These rules decide every label. Code applies them the same way every time.

**Who picks the label**

| Position type | Who picks | How |
| --- | --- | --- |
| Number | Code | AI pulls the value, unit and quote from each matching clause. Code converts and compares. |
| Yes/no | Code | AI answers yes, conditional yes, no, unclear, or missing per clause, with its quote. Code applies the levels. |
| Words | AI | AI picks a level per matching clause. Code applies Rule 4. The label gets the "AI judgment" tag. |

**Rule 1: Limits, not ranges.** Number levels are limits. Example, lower is better: preferred at or under 15, acceptable at or under 30, anything above is walk-away. "None" counts as 0. "Unlimited" is the worst value for the direction.

**Rule 2: "No" equals "missing."** For yes/no positions, a clear "no," an unclear answer, and silence get the same level. A clear "no" is a label on its clause, not a Missing list item. A conditional yes ("with prior written consent," "at the Client's discretion") is different: it gives unsure, with the condition quoted and a suggested question, such as "Can we agree consent won't be refused without a good reason?"

**Rule 3: Failed quote, retry once.** If a quote isn't found in the text that was sent, or the extracted number isn't in its quote, the AI is asked again and told what failed. If it fails again, that value becomes unsure: "Couldn't confirm the wording. Check \[location\] yourself." Rule 4 then combines it with the position's other values. A position is never dropped silently.

**Rule 4: Mixed values, in this order.**

1. If any readable value gives walk-away, the label is walk-away.
2. Otherwise, if any value is unsure, the label is unsure.
3. Otherwise, the worst level wins.

Whenever matching clauses give different values, every one appears in the evidence trail with "These clauses disagree. Ask which applies." This applies to every position type. An override clause never changes the label, but the note names it.

**Rule 5: Unreadable values are unsure.** Vague wording ("reasonable time"), a start point other than the invoice date for payment days ("30 days after acceptance"), a cap that depends on unknown figures, or business days against a calendar-day limit all give unsure. The why shows at least two possible readings and one suggested question.

**Rule 6: Conversions.** One week is 7 days, one month 30 days, one year 12 months or 365 days, in either direction. Business days never convert. A range ("15 to 30 days") counts as two values, so Rule 4 applies, and the note says "This clause gives a range. The worse end was used." A deposit given as an amount becomes a percentage when the total is also found. Otherwise it's unsure. An amount and a percentage that disagree in one clause count as a conflict.

**Rule 7: Missing.** A position with no matching text gets its missing level. It appears in the Missing list unless the missing level is preferred.

**Rule 8: Not covered.** Parts no position covers get no label and no mark on the page, only a one-line summary in the Not covered tab.

**Rule 9: Hidden text.** A value whose quote includes hidden text becomes unsure, and doesn't count as readable for Rule 4 step 1.

**Rule 10: Unloaded documents.** A label whose evidence trail includes a reference to a document that isn't loaded becomes unsure, unless Rule 4 step 1 already made it walk-away.

## 6. Pipeline

### 6.1 Steps

A fixed sequence run by the app's code. The AI never decides what runs next and has no tools. It only returns filled-in forms (structured outputs), which code checks before use.

| # | Step | Input | Output | Done by |
| --- | --- | --- | --- | --- |
| 1 | Read file | PDF, Word (.docx), text or Markdown (.txt, .md), or pasted text | Plain text with section numbers, tables and schedules kept. Hidden text, comments and tracked changes found and marked | Code |
| 2 | Split into clauses | Plain text | Clauses with numbers and locations, or paragraphs if there are no numbers | Code |
| 3 | Find personal data | Clauses, typed party details | Suggested placeholders | Code plus Presidio, on the user's computer |
| 4 | Privacy check | Suggestions | Confirmed placeholder text | User |
| 5 | Map links | Clauses | Cross-references, defined terms, override clauses, references to other documents | Code |
| 6a | Match | Placeholder text, positions | Which clauses each position concerns, and the governing-law clause | AI or Jev |
| 6b | Extract | Matched clauses | Per clause: clause number, quote, raw value, number value, unit as written, yes/conditional yes/no/unclear/missing with any condition quoted, vague flag, amount and total. For the governing-law clause, the place named, with its quote | AI |
| 7 | Quote check | Quotes, numbers, sent text | Pass or fail, retry once on fail | Code |
| 8 | Pick labels | Values, playbook snapshot | Labels for number and yes/no positions, by section 5 | Code |
| 9 | Judge words positions | Matched clauses, level text | A level per clause. Evidence is the matched clause | AI or Jev |
| 10 | Explain | Labels, quotes, Missing list | Plain-words why without limits, plus "why it could be the other level" for AI judgment and unsure labels, Missing item text, readings and one question for unsure labels. Code adds the "by your playbook" line with limits from the snapshot | AI. Can't change a label |
| 11 | Summarise not-covered parts | Not-covered parts | One plain sentence each | AI |
| 12 | Rewrite (on request) | Clause with placeholders, affected positions, optional instruction | New wording, then steps 6b to 10 on it, with the quote check against the suggestion's own text | AI, then code |
| 13 | Write message | Ticked items, tone, quotes, preferred levels | Message with \[TO\] and \[FROM\] markers | AI. Code fills in names |
| 14 | Build report | Review data | PDF | Code |

### 6.2 Rules for every AI step

- **What the AI receives:** placeholder text, position topics, types and level text. Never playbook names, customers, the user's notes, or To and From names. "Why this matters" notes only if the user turns that on in Settings, with known names replaced.
- **Acceptable levels:** steps 10 and 13 never receive acceptable limits. Code scans every message and unsure question for an acceptable limit and regenerates once if found.
- **Law words:** AI text must never state what a law allows. Code scans for words like "legal," "illegal," "enforceable," "unenforceable" and "the law," and regenerates once if found.
- **Requests:** each asks for zero retention when private mode is on, filled-form replies, and `require_parameters` (OpenRouter's setting that only uses providers supporting every requested feature).
- **Models:** one model for every step by default, or one per step in Settings. Jev only for steps 6a and 9. Recommended models come from test-set scores. Each AI call records which model and privacy mode it used.
- **Retries:** a broken, empty or unknown reply is retried once, then that value becomes unsure. A network error is retried 3 times, then the review becomes Interrupted.
- **Display:** a PDF contract's original pages are shown as pictures of the page: nothing in the file runs, and its links open only after the warning in 4.3. All text the app pulls out of the contract (quotes, summaries), and all playbook and AI text, is shown as plain text in the app and the report PDF, never as formatted text or links. Placeholders are restored by code only when they exactly match a known placeholder. An unknown placeholder counts as a broken reply. No confidence percentages or meters are shown anywhere, including Jev's probabilities.
- **Mid-run changes:** a changed key, model or privacy mode applies from the next AI call.

### 6.3 Review statuses

| From | To | When |
| --- | --- | --- |
| (new) | Draft | "Continue" on New review |
| Draft | Running | "Send for review." The snapshot is taken now |
| Running | Ready to check | Every step finished |
| Running | Interrupted | Cancel, app closed, network failed after retries, key or credit problem, no private-mode model |
| Running | Failed | A step's code failed in a way retrying won't fix |
| Interrupted | Running | "Resume" continues from the first unfinished step. Finished steps aren't paid for again |
| Failed | Running | "Retry," same as Resume |
| Ready to check | Done | Every position checked and not-covered parts confirmed |
| Done | Ready to check | Undo, or a position back to unchecked |
| Ready to check or Done | Running | "Re-run" (see below) |
| Any | (deleted) | Delete, or auto-delete. Deleting a running review cancels it first |

**Deleted playbook:** if a Draft's playbook is deleted, the Draft shows "Pick a playbook" and can't be sent until one is picked. A sent review keeps its snapshot, and Re-run is hidden.

**Re-run:** takes a new snapshot, asks the party question again, keeps the privacy check, shows the estimated cost, then runs steps 6a to 11. Your labels and notes are kept for positions whose levels didn't change. Suggestions are re-checked.

## 7. Starter playbook

**Freelancer receiving a service agreement from the other side.** Side: service provider. Example positions, meant to be edited. Every position has a filled "why this matters" note.

| # | Position | Type | Preferred | Acceptable | Walk-away | Missing level |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Days until I'm paid, from invoice date | Number (days), lower is better | At or under 15 | At or under 30 | Above 30 | Unsure |
| 2 | Upfront deposit | Number (%), higher is better | At or over 50 | At or over 25 | Below 25 | Walk-away |
| 3 | Late payment fee exists | Yes/no | Yes | No, unclear or missing |  | Acceptable |
| 4 | Paid for work done if the other side cancels | Yes/no | Yes |  | No, unclear or missing | Walk-away |
| 5 | Revision rounds included | Number (rounds), lower is better | At or under 2 | At or under 3 | Above 3, or unlimited | Walk-away |
| 6 | Extra work is paid extra | Yes/no | Yes |  | No, unclear or missing | Walk-away |
| 7a | Ownership passes only after full payment | Yes/no | Yes |  | No, unclear or missing | Walk-away |
| 7b | If unpaid, I can reuse or resell the work | Yes/no | Yes | No, unclear or missing |  | Acceptable |
| 8 | I can show the work in my portfolio | Yes/no | Yes | No, unclear or missing |  | Acceptable |
| 9 | Non-compete length | Number (months), lower is better | 0 (none) | At or under 6 | Above 6 | Preferred |
| 10 | My liability is capped | Words | At most the fees paid | Above the fees, up to 2x fees | Above 2x fees, a fixed sum, or uncapped | Walk-away |

## 8. Privacy and security

### 8.1 What leaves the computer

- Only placeholder text and position text, plus "why this matters" notes if that setting is on, sent to OpenRouter during AI steps (see 6.2).
- Other OpenRouter requests: key check, credit balance, and model list.
- GitHub, only when "Check for updates" is pressed. It opens the release page.
- No telemetry. The app sends nothing about the user.

### 8.2 Private mode

- On by default. Turning it off shows a warning that providers may keep or train on the contract.
- It asks OpenRouter for zero-retention endpoints only. OpenRouter's own rules still allow exceptions: personal accounts allow "Safety Retention" endpoints by default, where providers may keep prompts for abuse checks, and content flagged as child-abuse material may be kept even under zero retention, from 27 Oct 2026.
- So the key guide tells users to turn off Safety Retention in their OpenRouter privacy settings, and the app says "providers don't keep your contract if you've turned off Safety Retention in OpenRouter, except for legally required safety screening." It never says "nothing is stored anywhere."
- Private mode is set per review on the privacy check, starting from the Settings default. While a review runs, it can be changed from the privacy badge. The change applies from the next AI call, and the badge shows "Mixed" with the affected steps. Changing the Settings default never changes an existing review.
- Placeholders don't hide everything. Descriptions can identify someone, so the privacy check lets the user replace any text.

### 8.3 Stored data

- Everything saved is encrypted: reviews (contract, names, quotes, AI output, notes, suggestions, messages), playbooks, and customers.
- The encryption key and the API key are kept in the system's password store (Windows Credential Manager, Linux Secret Service). If Linux has no password store, the app asks for a passphrase and never saves plain text.
- Auto-delete runs at startup and while the app is open. "Delete all reviews" also clears temporary files. Uninstall offers to remove all data and keys.
- "Copy error details" includes only the app version, the step, and an error code.
- Saved PDFs, exported playbooks and copied messages leave the app's protection. The app says so when saving.

### 8.4 Security

- The contract and any imported playbook are untrusted. They may contain hidden instructions.
- The AI has no tools. It can't run code, open files, or send anything. All its text is shown as plain text.
- Hidden text is found in step 1 and shown to the user. Values resting on it become unsure.
- Every quote and number is checked by code.
- Code picks labels for number and yes/no positions.
- Every import is previewed first. Playbook files use a strict format with size limits. Word files are read with external links turned off.
- Each release publishes checksums (fingerprints that prove a download wasn't changed).

## 9. Running the app

- **Form:** a desktop app with an installer. Built first as a Python command-line tool to test the review, then wrapped. The command-line tool follows the same storage and privacy rules.
- **Systems:** Linux and Windows. The Windows installer is built by GitHub Actions and tested in a Windows virtual machine. It's unsigned, so the download page explains the "Windows protected your PC" warning: click "More info," then "Run anyway." Mac comes later.
- **API key:** first launch shows the key guide, including what a typical review costs and how to turn off Safety Retention. Clear messages for a wrong key, no credit, or no internet.
- **Cost:** estimated before sending, shown while running, recorded per review. If the estimate is more than the remaining credit, a warning shows the exact amounts, with "Send anyway."
- **Auto-delete:** 7, 30 or 90 days after a review's last change (default 30). A change is any edit, check, suggestion, output or rename. Opening isn't. "Keep it" restarts the clock. Reviews 3 or fewer days from deletion show a warning. Lowering the setting shows how many reviews it affects, asks to confirm, and deletes nothing sooner than 3 days later.
- **File types:** PDF with real text, Word (.docx), text (.txt) and Markdown (.md). Text and Markdown files are read exactly like pasted text: Markdown symbols such as `#` and `**` are shown as plain characters, never as formatting. An old Word file (.doc) is not read; the app says: "This is an old Word file. Open it in Word, save it as .docx, then load that."
- **Input limits:** \[Assumption\] files up to 20 MB and 50,000 words. A page with fewer than 50 readable characters counts as scanned. A mixed file names its scanned pages. A contract detected as mostly not English gets a warning, and the user can still continue: "This contract doesn't look like it's in English. Clause Tracer is built and tested for English contracts only, so fewer names and addresses are found for you (check the privacy step carefully), and more labels may be wrong or unsure." These numbers get tuned in testing.
- **Offline:** saved reviews open offline. A Draft can be prepared offline. "Send for review" explains internet is needed.
- **Language:** English contracts and an English interface only. Arabic and French, for contracts and the interface, are planned next; the research is in `Prototyping/clause-tracer/research/14-languages-and-models.md`.

## 10. Legal wording

The tool compares contracts with positions the user chose. It doesn't know the law and must never sound as if it does.

- Labels name the playbook as their source: "Walk-away by your playbook: payment is 60 days, your limit is 30." Code writes this line, not the AI. Unedited starter copies say "by the example playbook."
- Starter playbooks are marked "example positions, edit them for your situation."
- A "not legal advice" notice appears on first launch, above every message, and on every report page.
- AI text never states what a law allows (see 6.2).
- The code is released under the Functional Source License (FSL-1.1-ALv2), which has a no-warranty clause. Anyone can use it for free, including for paid work, except to offer a competing product or service, which needs a commercial licence (`COMMERCIAL_LICENSE.md`). Each version becomes Apache 2.0 two years after its release. The app says "source available", never "open source".
- Before wide promotion, check the wording with a lawyer.

## 11. Acceptance tests

Version 1 is done when all of these pass.

**Test set:** 10 contracts. Two are written from the other side's point of view. Eight are freelancer-friendly contracts edited into worse versions, so the right answer is known. Each has a written answer for every starter position, including the missing ones.

**Accuracy**

- [ ] Every planted walk-away gets the tool label walk-away (100%).
- [ ] At least 90% of numbers are correct, out of positions with a stated value in the answer key. Unsure counts as wrong.
- [ ] At least 90% of yes/no and words labels match the answer key.
- [ ] No made-up quote ever reaches the screen.
- [ ] Presidio plus typed details catch every planted name, company and address in the test set.

**Privacy**

- [ ] No item confirmed in the privacy check, no note, and no To or From name appears in any request sent to the AI. Checked from request logs written only by a test build, kept locally, encrypted, and deleted after the test run.
- [ ] Every request in private mode asks for zero retention.
- [ ] No acceptable limit appears in any request to the message step, and a manual read of every test message finds none.
- [ ] No AI text states what a law allows.
- [ ] Saved data is unreadable without the encryption key.
- [ ] Auto-delete removes a review on schedule, including after the app was closed.

**Product**

- [ ] Every evidence link scrolls to the right place.
- [ ] A hidden-text test contract shows the banner, and values resting on it are unsure.
- [ ] A full review runs on Linux and in a Windows virtual machine from the installer.
- [ ] Blind self-test: a script plants one wrong tool label at random in each of 3 sample contracts, without saying which. Mohammed reviews each one normally and catches all 3. Repeated after any change to the review or checking screens.

The test set runs after every change to prompts, models, or labeling code.

## 12. Not in version 1

- Contracts written from scratch.
- Judging what a country's law allows, or citing laws.
- Reading scanned PDFs.
- Languages other than English, for contracts or the interface (Arabic and French planned next).
- Mac installer.
- Accounts, sign-in, or any server run by the project.
- AI agents that choose their own steps or use tools.
- A guided-question playbook builder.
- Sending unsure items to a lawyer.

## 13. Open decisions before coding

- [ ] Desktop shell: Tauri or Electron.
- [ ] How Presidio and its language model are bundled, and the download size.
- [x] License: Functional Source License, FSL-1.1-ALv2 (decided 7 Nov 2026).
- [ ] Which 2 or 3 models to start testing with, from OpenRouter's zero-retention list.
- [ ] Whether Jev beats an AI model on steps 6a and 9, and whether it can run under the same privacy rules.
- [ ] Final input limits and the cost per review, from testing.
- [ ] Review screen layout, settled with a rough prototype. Later: add at least one outside tester, who must also catch a planted wrong label.

## 14. Prototype handoff

The brief for whoever designs the prototype. Read sections 1 to 13 first, plus the brand file `clause-tracer-brand-philosophy.md`.

**Deliver**

1. A design system: colors, type, spacing, and components (buttons, label chips, clause highlights, banners, panels, forms).
2. A clickable prototype of every screen below, linked into the user flow from section 3.
3. Every state below, shown on its screen.

**Done when:** someone who has never seen the spec can click from first launch to a finished message without help.

### 14.1 Screens

| # | Screen | What's on it |
| --- | --- | --- |
| 1 | First launch | "Not legal advice" notice. Key guide: create an OpenRouter account, add credit (with a typical review cost), turn off Safety Retention, create a key. Key field, "Save key" with "Checking key." "Skip for now." "Or try a sample contract first, free": a practice review with ready-made results, no key and no cost. A line under the link says up front that one label in it is wrong on purpose; checking that label shows why, and that real reviews can be wrong too. Only the sample ever contains a planted error. |
| 2 | Home | Titled "Reviews" in the app. Saved reviews: name, playbook, date, status, "11 of 11 positions checked," days until auto-delete. Search, sort, rename, delete. "Resume" on Interrupted, "Retry" on Failed. Notice after auto-deletes. Buttons: New review, Playbooks, Customers, Settings, Help. |
| 3 | New review | Load contract by upload, drag and drop, or paste (PDF, .docx, .txt, .md). Review name. Pick playbook, or "Copy a starter" (always shown). "Which party is the \[side\]?" with last choice preselected, or add a missing party. Each party's name and address, prefilled. "Continue." |
| 4 | Contract check | The contract split into numbered clauses, including tables and schedules. A note if it split by paragraph. Hidden text marked. Guidance: "Each box should hold one section. Merge or split if a sentence is cut or two sections share a box." "Looks right, continue." |
| 5 | Privacy check | Contract with highlighted personal data. Legend on this screen only ("Person 1 = Sarah Jones"). List of every replacement. Select to replace more, untick false alarms, same or different person. The indirect-identifier hint. Back to party details. Private mode on or off. Estimated cost. "Send for review." |
| 6 | Review running | Progress in four stages, each in plain words: 1 Reading the pages (step 5), 2 Matching clauses (6a, 6b, 7), 3 Judging the labels (8, 9), 4 Writing the notes (10, 11). Running cost, rough time left. Privacy badge, which can switch private mode. Cancel, which shows the cost so far. Note that closing the app pauses the review. |
| 7 | Review | The whole contract as scrollable pages (original PDF pages, or typeset pages for Word, text and Markdown files and pasted text) with page thumbnails and zoom, label washes and numbered pins, outlined hidden text, link warning. Checking card, then tabs: Labels, Not covered (with the not-covered tick), Missing. Summary bar. Banners: hidden text, unloaded document, playbook changed, unedited starter. Governing-law chip. Counter, "Next unchecked." Find in the contract and zoom (text size is in Settings). Privacy badge (On, Off or Mixed), models and cost. Buttons: Output, Rewrite, Suggestions, Re-run, Start over. |
| 8 | Detail panel | For a label or a Missing item: quoted evidence first with the exact words highlighted, then label word, icon and "?", why, "why it could be the other level" (AI judgment and unsure), level matched, evidence trail with back, AI judgment tag, unsure readings and question, "What to check." "Looks right," "Change it," note. |
| 9 | Change it | New label (preferred, acceptable, walk-away, unsure), note, save. Tool label beside your label. Undo. |
| 10 | Rewrite | Clause, "Write it yourself" or "Ask AI" with optional instruction. New personal data to confirm. Before and after with labels. "Use as suggestion." Also "Add this clause" from a Missing item. |
| 11 | Suggestions | Every suggestion with its clause and label. Edit, remove. |
| 12 | Output | Unchecked warning. Message, report, or both. Message: ask-for checklist, to, from, tone, editable text, regenerate, copy, "not legal advice" above. "Nothing to ask for" note. "Labels changed. Regenerate?" Report: summary or full contract, "Include your notes," preview, "Save PDF" with the save notice. |
| 13 | Playbooks | Playbooks with side and customer, filter by customer. Create blank, Copy a starter, Import, Export, Duplicate, Edit, Delete (with how many reviews use it). |
| 14 | Starter preview | The starter's positions, read-only. "Copy to your playbooks." |
| 15 | Import preview | Every position in the file, with a note that it comes from someone else. Duplicate names saved as "(imported)." Import or Cancel. |
| 16 | Playbook editor | Name, side, customer. Positions with reorder and delete. Position form by type (see 4.1), missing level, "why this matters." Validation messages. Unsaved-changes warning. |
| 17 | Customers | Customers with playbook counts. Add, rename, delete (unlinks playbooks, keeps them). |
| 18 | Settings | See 14.3. |
| 19 | Help | How a review works, "Words used in this app," key guide, "What gets sent," not legal advice, license, keyboard shortcuts. |
| 20 | Error | Unexpected error, "Your files are safe." "Copy the details" (version, step, error code), with a suggestion to report the problem on GitHub (the app opens nothing itself). "Back to reviews." |

### 14.2 States to show

| Screen | State |
| --- | --- |
| First launch | Checking key, then works or the error. |
| Home | No reviews yet: "Start your first review." |
| Home | Review 3 days or fewer from auto-delete, with "Keep it" or "Delete now." |
| Home | Interrupted with "Resume." Failed with "Retry." |
| Home, New review | Offline: saved reviews open, drafts can be prepared, sending explains internet is needed. |
| New review | No key saved: "Add your OpenRouter key to run a review," with a button to the guide. Progress kept. |
| New review | Scanned PDF, mixed file naming scanned pages, too large, empty, or an old Word file (.doc), each blocking Continue. Not English: a warning, and Continue still works. |
| New review | Draft whose playbook was deleted: "Pick a playbook." |
| Contract check | Hidden text found and marked. |
| Privacy check | Private mode turned off warning. |
| Privacy check | Estimated cost above remaining credit, exact amounts, "Send anyway." |
| Review running | Wrong key, no credit, no internet, or no private-mode model, each turning the review Interrupted with a plain fix. |
| Review | Playbook changed banner, with Re-run. |
| Review | More than half unsure: guidance message. |
| Review | Unloaded document, hidden text, unedited starter, two governing-law clauses, no governing-law clause. |
| Review | Privacy badge "Mixed." |
| Detail panel | Unsure because the quote couldn't be confirmed. |
| Detail panel | Conflict: clauses disagree, all shown. A range in one clause. |
| Detail panel | Conditional yes, with the condition quoted. |
| Detail panel | AI judgment tag. |
| Rewrite | Rewrite failed its quote check, savable as unsure. |
| Output | Items unchecked. Nothing to ask for. Labels changed since the message ("Labels changed. Regenerate?"). |
| Playbook editor | Validation error. |
| Playbooks | Import failed: not a valid playbook file. |
| Settings | Model can't do that step. Update available, or up to date. Lowering auto-delete confirmation. |
| Any delete | Names what will be deleted and says it can't be undone. |
| Anywhere | "Copied" and "Saved" confirmations. |

### 14.3 Settings

| Group | Contents |
| --- | --- |
| OpenRouter key | Change key, remove key, link to the key guide. |
| Privacy | Private mode default for new reviews (on). "Send “why this matters” notes to the AI, for better explanations" (off), with a warning that notes aren't privacy-checked. Link to "What gets sent." |
| Models | Collapsed by default. One model for every step (default), picked from one list, or one per step. Per step lists: match, extract, judge words positions, explain, summarise not-covered parts, rewrite, write message. Recommended tested model shown. Warning on untested choices. Jev only for match and judge. In private mode, only zero-retention models offered. |
| Storage | Auto-delete after 7, 30 or 90 days (default 30). Delete all reviews. Where files are kept. |
| Notifications | "Notify when a review finishes" (on): a system notification when a review running in the background is done. |
| Data | "Delete everything": every review, playbook, customer, setting and the key, after a confirmation that names them and says it can't be undone. |
| Appearance | Light or dark, text size. |
| About | Version, "Check for updates" (opens GitHub only when pressed), license, not legal advice. |

### 14.4 Visual rules

- Desktop app. \[Assumption\] Design for laptop screens about 1366 by 768 and up.
- Every label has a color, an icon, and its word. Color is never the only signal.
- Four label looks (preferred, acceptable, walk-away, unsure) plus grey for not covered, drawn as split stamps: square corners, a solid colour block with the icon, and the word in small capitals (see ADR 0002). Two warning levels: top banners (hidden text, unloaded document, playbook changed, unedited starter) and small chips (everything else). No confidence meters. An AI judgment label is the same stamp drawn in pencil (a dashed graphite border and a hatched block), followed by the words "AI judgment". Only pencilled stamps are dashed. The hidden-text mark looks different from all of them.
- Walk-away uses the brand's red (#A91207), and red means only one thing: a line you won't cross. No other UI uses red as decoration (see ADR 0003).
- Review status is a small circle gauge plus a next step, with no pill. Draft is a dashed ring, Running fills by step ("Step 2 of 4 · about 40 s"), Interrupted shows a pause, Failed shows "!", and Done is a quiet grey tick. Only Ready to check is a solid disc, with its row in bold and its next step as the one dark button ("Check 9 →", the number of unchecked positions). The other next steps are text links (Continue, Resume, Retry, Open message). Status never uses red.
- Text meets WCAG AA contrast (the common standard for readable color contrast).
- Plain everyday words matching the glossary. Never "client" in the app's own text.
- The app never speaks as "I". Its text is neutral: "Saved with the review," "This one is a walk-away," "The check can miss things." Buttons and checkboxes speak as the app or address the user ("your"), never as "my". "I" and "my" appear only in the user's own words: position names ("Days until I'm paid"), "why this matters" notes, the message written for the user to send, and the not-covered tick ("I've read the 35 not-covered parts").
- App copy is British English (colour, summarise, recognise) with double curly quotes. Every string, the word list and the patterns are in `ux-copy.md`.
- Every control works with a keyboard and a screen reader.
- Commands are reached through a command palette (Ctrl+K, a "Search commands" box in the toolbar), not a menu bar. Each result shows its shortcut, and the list opens on the most common commands so it can be browsed without typing.
- Light mode required. Dark mode optional.

### 14.5 Sample data

Use the agency-to-freelancer development contract by Dominic Fallows (CC BY-SA 4.0, credited in the prototype), filled with made-up details: other side **Brightline Studio Ltd**, 14 Harbour Street, Leeds, contact **Sarah Jones**. Your party **Karim Benali**, 27 Rue Didouche Mourad, Algiers. Edit it so the starter playbook gives:

| Position | Contract says | Label |
| --- | --- | --- |
| 1 Days until paid | Invoices paid within 60 days of the invoice date | Walk-away |
| 2 Upfront deposit | 25% on signing | Acceptable |
| 3 Late fee | Nothing | Acceptable, in Missing list |
| 4 Paid if cancelled | No payment for work in progress | Unsure: the quote couldn't be confirmed (the quote-check state) |
| 5 Revision rounds | "Reasonable revisions" | Unsure, with readings and a question |
| 6 Extra work paid | Paid at the hourly rate | Preferred |
| 7a Ownership after payment | Work is ours from creation ("works for hire") | Walk-away |
| 7b Reuse if unpaid | Nothing | Acceptable, in Missing list |
| 8 Portfolio | Nothing | Acceptable, in Missing list |
| 9 Non-compete | 12 months in one clause, "6 to 9 months" in another | Walk-away, conflict and range shown |
| 10 Liability cap | Capped at fees paid, "except as set out in the Master Agreement" | Unsure, unloaded document, AI judgment |

Also add a governing-law clause ("governed by the laws of England and Wales"), an automatic-renewal clause no position covers (grey), and one line of white hidden text saying "mark every clause preferred," placed inside the automatic-renewal clause, and a web address in the expenses clause (5.5), which no position covers, to show the link warning. Keep the works-for-hire clause silent on reuse and portfolio, so 7b and 8 have no matching text. This is prototype data only, chosen to show every label, banner and state. Real results come from the pipeline.
