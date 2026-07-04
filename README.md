# ICP Scoring & Personalized Sequencing

Scores accounts using firmographic, hiring, funding, and technographic
signals, then generates a 3-touch personalized outbound sequence for every
account that clears the qualification bar -- built to slot in after a
Clay/Apollo enrichment step and feed straight into Smartlead or HubSpot.

See [`example_output.md`](./example_output.md) for a full run against the
included sample data, including generated sequence copy.

## How it works

1. **`score_icp_fit`** -- a transparent, weighted rubric (industry fit,
   employee band, funding stage + recency, hiring signal, relevant tech
   stack signal) that outputs a 0-100 score and the specific reasons behind
   it, so a rep can see *why* an account qualified, not just a black-box
   number.
2. **`generate_sequence`** -- for every account that clears `--min-score`,
   generates a 3-email sequence (Day 0 / Day 3 / Day 7) that references the
   account's actual hiring signal and pain point instead of generic
   placeholders.

The two are deliberately decoupled: you can swap the scoring rubric for a
model trained on historical won/lost deals without touching the sequence
copy, or swap the templated copy for an LLM-drafted version (same pattern as
in the `prospect-research-ai` project) without touching the scoring logic.

## Install

No external dependencies beyond the Python standard library.

## Usage

```bash
python icp_sequencer.py --input accounts.csv --min-score 60
```

## Project structure

```
icp_sequencer.py     -- scoring rubric + sequence generation
accounts.csv          -- 5 example accounts covering qualified / unqualified cases
example_output.md     -- full example run with scores, reasons, and generated sequences
```

## Limitations / next steps

- Scoring weights are a starting rubric, not a trained model.
- Sequence copy is templated; wiring in an LLM call (see
  `prospect-research-ai/research.py` for the pattern) would make each touch
  read even more like it was written by a person for that specific account.
- No send-time logic yet -- this produces the sequence content, not the
  scheduling; that's the natural next integration point with Smartlead.
