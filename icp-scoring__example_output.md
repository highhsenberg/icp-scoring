# Example run

```
$ python icp_sequencer.py --input accounts.csv --min-score 60

Scored 5 accounts against ICP rubric (min-score=60)

[QUALIFIED] Northwind Data        score=100/100
             - Industry match: Data Infrastructure
             - Employee count 85 within target band 10-250
             - Raised Series A 21d ago
             - Hiring signal: GTM Engineer
             - Tech signal: Added Clay
[QUALIFIED] Fieldworks AI         score=100/100
             - Industry match: Vertical SaaS
             - Employee count 40 within target band 10-250
             - Raised Seed 45d ago
             - Hiring signal: SDR Manager
             - Tech signal: Added Smartlead
[QUALIFIED] Colby Robotics        score=100/100
             - Industry match: Industrial Tech
             - Employee count 120 within target band 10-250
             - Raised Series B 60d ago
             - Hiring signal: Head of RevOps
             - Tech signal: Added HubSpot
[skip     ] Ledgerline            score= 25/100
             - Industry match: Fintech
[skip     ] Barrow & Finch        score= 20/100
             - Employee count 22 within target band 10-250

=== Sequence for Northwind Data ===

[Day 0] Subject: Saw Northwind Data is hiring a GTM Engineer
Hi there,

Noticed Northwind Data is hiring a GTM Engineer -- usually a sign you're
scaling GTM execution right now. I help teams in that exact spot automate
the manual parts of outbound so the new hire starts from a running system
instead of a blank slate.

Worth a quick chat?

[Day 3] Subject: Re: the GTM Engineer hire at Northwind Data
Following up -- most teams at Northwind Data's stage tell me manual lead
routing is slowing down SDR follow-up. That's usually the first thing worth
fixing before the new hire ramps up, since it compounds every week it stays
manual.

Happy to show you how that's solved in practice.

[Day 7] Subject: Closing the loop, Northwind Data
I'll leave this here -- if fixing how Northwind Data handles 'manual lead
routing is slowing down SDR follow-up' becomes a priority later this
quarter, happy to pick this back up. Good luck with the GTM Engineer search
either way.

=== Sequence for Fieldworks AI ===

[Day 0] Subject: Saw Fieldworks AI is hiring a SDR Manager
...

=== Sequence for Colby Robotics ===

[Day 0] Subject: Saw Colby Robotics is hiring a Head of RevOps
...
```

(Full sequences for Fieldworks AI and Colby Robotics follow the same
structure -- truncated here for brevity. Run the script yourself against
`accounts.csv` to see all three in full.)

## Why this is two steps, not one

Scoring answers "is this worth our time." Sequencing answers "what do we
actually say." Keeping them as separate functions (`score_icp_fit` and
`generate_sequence`) means you can swap in a smarter scoring model later
(e.g. trained on historical won/lost deals) without touching the copy, or
swap the copy for an LLM-drafted version (same pattern as in
`prospect-research-ai`) without touching the scoring logic.
