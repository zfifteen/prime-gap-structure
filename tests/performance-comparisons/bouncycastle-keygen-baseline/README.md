# Bouncy Castle RSA Keygen Baseline

This testbed captures the current unmodified performance of the direct
Bouncy Castle core RSA key generator from a vendored source snapshot.

## Fixed Baseline Contract

- Bouncy Castle source tag: `r1rv83`
- Bouncy Castle source commit: `d4cc9614fc849e840ffdc7941f4a2941131d0c9c`
- Bouncy Castle built artifact: `bcprov-jdk18on-1.83.jar`
- Generator path: `org.bouncycastle.crypto.generators.RSAKeyPairGenerator`
- RSA size: `4096` bits
- Timed iterations: `100`
- Warmup iterations: `0`
- Public exponent: `65537`
- Certainty: `144`
- SecureRandom algorithm: `SHA1PRNG`
- Seed bytes: `[42]`

The certainty value mirrors Bouncy Castle's provider-side default for
`4096`-bit RSA in release `1.83`.

The benchmark builds Bouncy Castle from the vendored `r1rv83` source tree under
JDK `25`, then runs the benchmark itself under JDK `21`.

## Run

```bash
./run_baseline.sh
```

The script first builds the vendored Bouncy Castle source tree, then compiles
the Java benchmark harness against the generated jar, and finally writes the
measured baseline JSON to:

`./results/bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json`

This source-built JSON is the canonical baseline for future Bouncy Castle
modification comparisons. The older Maven-jar result is retained only as a
historical artifact.
