# Repository Split Diagram

```mermaid
flowchart TB
    A["Current repository<br/>z-band-prime-prefilter"] --> B["Repo 1<br/>z-band-prime-prefilter<br/><br/>Normative production artifact"]
    A --> C["Repo 2<br/>z-band-prime-gap-ridge<br/><br/>Gap-ridge research and findings"]
    A --> D["Optional Repo 3<br/>z-band-prime-composite-field<br/><br/>Shared exact divisor-count and field helpers"]

    B --> B1["Keep<br/>src/python/geodesic_prime_prefilter/<br/>spec/contract.md<br/>spec/vectors/<br/>tests/python/prefilter/<br/>docs/prefilter/<br/>docs/architecture.md"]
    C --> C1["Move<br/>benchmarks/python/gap_ridge/<br/>benchmarks/output/python/gap_ridge/<br/>docs/gap_ridge/<br/>docs/findings/<br/>tests/python/gap_ridge/"]
    D --> D1["Move only if needed<br/>src/python/geodesic_prime_composite_field/<br/>src/python/geodesic_prime_gap_ridge/<br/>shared field utilities"]

    B -. "GitHub links" .-> C
    B -. "submodule or subtree only if parity tracking is needed" .-> D
    C -. "can vendor or depend on shared package" .-> D

    E["GitHub migration options"] --> E1["Clean split<br/>new repos with preserved history via git filter-repo"]
    E --> E2["Independent repos<br/>cross-link with README docs"]
    E --> E3["Optional integration<br/>submodule or subtree"]
```

## Plain Reading

- `Repo 1` stays narrow and remains the normative production implementation.
- `Repo 2` becomes the research surface for the gap-ridge program and findings.
- `Repo 3` is optional and only worth creating if the exact composite-field code
  becomes a genuinely shared dependency rather than just internal research code.

## Recommended First Split

Start with two repos, not three:

1. `z-band-prime-prefilter`
2. `z-band-prime-gap-ridge`

Only split out a shared field/core repo later if both repos actually need to
version that code independently.
