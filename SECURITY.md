# Security policy

Clause Tracer handles contracts, which are often confidential. If you find a way to break its privacy or security, please tell us privately first, so we can fix it before anyone else can use it.

## Report a vulnerability privately

**Don't open a public issue for a security problem.** Report it in one of these ways:

1. **GitHub (preferred):** go to the repo's [Security tab](https://github.com/mohamed-benoughidene/clause-tracer/security) and choose **Report a vulnerability**. Only the maintainer can see your report.
2. **Email:** mohamedbenoughidene@gmail.com, with `[SECURITY] Clause Tracer` in the subject line.

Please include:

- what the problem is, and what someone could do with it;
- the steps to reproduce it, with a sample file if one is needed;
- the version or commit you tested.

Don't send real contracts, real personal data or a live API key. Make a sample that shows the problem instead.

## What happens next

| Step | When |
| --- | --- |
| We confirm we got your report | Within 48 hours |
| We tell you how serious we think it is | Within 1 week |
| We fix it, or tell you how to work around it | As soon as we can. Serious problems come first. |

We'll keep you updated, and we'll agree a date with you before anything is made public. We'll thank you by name in the release notes, unless you'd rather stay anonymous.

## Supported versions

Clause Tracer is still in design, so no version has been released yet. Until then, only the latest commit on `main` is supported. Once releases start, the latest release will get security fixes.

## What counts

These are the promises the app makes in the [spec](docs/spec.md#8-privacy-and-security). Breaking any of them is a security problem.

**In scope:**

- **Personal data reaching the AI.** A name, address or other personal data is sent to OpenRouter after the privacy check should have replaced it.
- **Data leaving the computer.** Anything is sent anywhere other than the places listed in Spec section 8.1.
- **A contract taking control.** Text in a contract or an imported playbook makes the app run code, open files or links without a warning, change a label, or hide text from the user. This includes prompt injection.
- **Hidden text missed.** Hidden text in a contract isn't found and shown to the user.
- **Wrong evidence.** A quote or number shown as checked isn't actually in the contract.
- **Stored data exposed.** Saved reviews, playbooks or keys can be read without the system password store or passphrase, or survive auto-delete or "Delete all reviews".
- **Tampered downloads.** A release or its checksums can be changed without anyone noticing.
- **Our dependencies.** A known vulnerability in a library we ship that affects Clause Tracer.

**Out of scope:**

- A bug in a library that doesn't affect Clause Tracer. Please report it to that project.
- What OpenRouter or an AI provider does with data once it's sent. See their privacy policies, and Spec section 8.2.
- Someone who already has full access to your unlocked computer.
- Social engineering and denial-of-service attacks.
- Wrong or unsure labels that aren't caused by an attack. Those are ordinary bugs, so please [open an issue](https://github.com/mohamed-benoughidene/clause-tracer/issues).

## Safe harbour

If you act in good faith, follow this policy and only test on your own computer and your own data, we won't take legal action against you for your research.
