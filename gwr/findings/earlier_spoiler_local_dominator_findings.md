# Earlier-Spolier Local Dominator Findings

This note records the executed prime-gap admissibility result from
[`earlier_spoiler_local_dominator_scan.py`](../experiments/proof/earlier_spoiler_local_dominator_scan.py).

The question is direct:

for each actual earlier competing integer inside a prime gap, how far to the
right does one have to go before finding a later interior composite that beats
 it exactly on the score?

## Executed Artifacts

- [`earlier_spoiler_local_dominator_scan_1e6.json`](../../output/gwr_proof/earlier_spoiler_local_dominator_scan_1e6.json)
- [`earlier_spoiler_local_dominator_scan_2e7.json`](../../output/gwr_proof/earlier_spoiler_local_dominator_scan_2e7.json)

## Exact Results

On the full exact surface through $10^6$:

- `70327` prime gaps with composite interior,
- `169021` earlier competing integers,
- `0` unresolved earlier candidates.

On the full exact surface through $2 \cdot 10^7$:

- `1163198` prime gaps with composite interior,
- `3349874` earlier competing integers,
- `0` unresolved earlier candidates.

So on both exact surfaces, every actual earlier competing integer has a later
interior dominator.

## Offset Law

At the exact $2 \cdot 10^7$ surface, the first later dominator arrives very
quickly:

- offset `1`: about `61.72%`,
- offset `2`: about `80.07%` cumulative,
- offset `3`: about `88.30%` cumulative,
- offset `4`: about `93.14%` cumulative,
- offset `6`: about `97.36%` cumulative,
- offset `12`: about `99.85%` cumulative.

So the earlier-competing-integer mechanism is not surviving deep into the gap on the
tested exact surface. It is being killed locally.

## Divisor-Class Extremal Case

The strongest structural result in the current run is this:

the required dominator offset shrinks sharply as the earlier divisor count
rises.

At the exact $2 \cdot 10^7$ surface:

- earlier class `d = 64`: max first-dominator offset `2`,
- earlier class `d = 72`: max first-dominator offset `2`,
- earlier class `d = 96`: max first-dominator offset `2`,
- earlier class `d = 120`: max first-dominator offset `1`,
- earlier class `d = 144`: max first-dominator offset `1`,
- earlier class `d = 192`: max first-dominator offset `1`,
- earlier class `d = 240`: max first-dominator offset `1`,
- highest observed classes through `d = 512` also have max first-dominator
  offset `1`.

The larger offsets are concentrated in the low divisor classes:

- `d = 4`: max offset `90`,
- `d = 6`: max offset `27`,
- `d = 8`: max offset `30`,
- `d = 12`: max offset `10`,
- `d = 16`: max offset `9`,
- `d = 24`: max offset `5`,
- `d = 32`: max offset `4`,
- `d = 48`: max offset `3`.

So the hard part of the earlier-competing-integer problem is no longer the high-divisor
tail. On the tested exact surface, the high-divisor candidates are killed
almost immediately.

## Current Reading

This is the first exact artifact in the repo that directly measures the
prime-gap admissibility of earlier competing integers rather than only their divisor
classes.

The strongest supported claim is:

actual earlier competing integers are locally unstable inside prime gaps, and that
instability becomes stronger, not weaker, as the earlier divisor count rises.
