---
status: accepted
date: 2026-11-05
---

# Show the contract as its original PDF pages

The Review screen shows a PDF contract as its own pages, the way a PDF reader shows them, so reviewing feels like reading the real document. The spec first said contract text is always shown as plain text, because the contract is untrusted and plain text can't hide anything or run anything. We keep that protection by showing the pages as pictures: nothing in the file runs, links open only after a warning, and every piece of text the app pulls out (quotes, summaries, AI text) stays plain text. Hidden text, which is invisible on the real page, gets an outline where it sits.

## Considered options

- **Typeset pages for every file:** the app lays the extracted text out on its own pages. This kept the plain-text rule unchanged and looks the same for every file type, but a PDF no longer looked like the document the user was sent. It's still used for Word files and pasted text, which have no pages of their own, and those reviews look and work exactly like a PDF review.
- **Links that never open:** this was the safest option, but rejected as less handy. A link now opens only after the user confirms where it goes.

## Consequences

- Labels are drawn on top of the page: a wash in the label's colour plus a numbered pin in the margin. The app has to place them using where each clause sits on the page.
- Clauses no rule covers are not drawn on the page; they're listed in the Not covered tab. Drawing them too made the page hard to read, because most clauses in a typical contract are not covered.
- A cheaper "show extracted text" view would need its own decision record to undo this one.
