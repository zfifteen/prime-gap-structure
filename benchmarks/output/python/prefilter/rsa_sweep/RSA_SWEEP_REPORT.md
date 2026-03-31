# RSA Sweep Benchmark Report

This report benchmarks the deterministic RSA key-generation pipeline across
the fixed sweep schedule up to the requested RSA ceiling. Its invariant target is
the **Divisor Curvature Identity** (DCI) \(Z(n) = n^{1 - d(n)/2}\).

## Configuration

- `public_exponent`: 65537
- `rsa_sizes`: [512, 1024, 2048, 3072, 4096]
- `keypair_counts`: [100, 100, 50, 20, 10]

## Sweep Summary

| RSA bits | Keypairs | Baseline total (ms) | Accelerated total (ms) | Speedup | Proxy rejection rate | Saved MR call rate |
|---|---:|---:|---:|---:|---:|---:|
| 512 | 100 | 946.245083 | 1566.871875 | 0.603907x | 91.237058% | 91.237058% |
| 1024 | 100 | 10014.005208 | 7936.873958 | 1.261706x | 91.142364% | 91.142364% |
| 2048 | 50 | 54162.186416 | 25518.274625 | 2.122486x | 90.968361% | 90.968361% |
| 3072 | 20 | 81871.287041 | 32310.299291 | 2.533907x | 91.278689% | 91.278689% |
| 4096 | 10 | 125005.477625 | 45168.493917 | 2.767537x | 91.151371% | 91.151371% |

## RSA 512

- Baseline generated `100` deterministic keypairs in `946.245083` ms total.
- The accelerated path generated the same keypairs in `1566.871875` ms for a measured `0.60x` speedup.
- The proxy removed `17096` Miller-Rabin calls (`91.24%` of baseline MR work).
- Proxy rejection rate was `91.24%` across the full candidate stream.
- All `200` confirmed primes remained on the DCI band `Z = 1.0` after final `sympy.isprime` confirmation.

## RSA 1024

- Baseline generated `100` deterministic keypairs in `10014.005208` ms total.
- The accelerated path generated the same keypairs in `7936.873958` ms for a measured `1.26x` speedup.
- The proxy removed `33246` Miller-Rabin calls (`91.14%` of baseline MR work).
- Proxy rejection rate was `91.14%` across the full candidate stream.
- All `200` confirmed primes remained on the DCI band `Z = 1.0` after final `sympy.isprime` confirmation.

## RSA 2048

- Baseline generated `50` deterministic keypairs in `54162.186416` ms total.
- The accelerated path generated the same keypairs in `25518.274625` ms for a measured `2.12x` speedup.
- The proxy removed `36975` Miller-Rabin calls (`90.97%` of baseline MR work).
- Proxy rejection rate was `90.97%` across the full candidate stream.
- All `100` confirmed primes remained on the DCI band `Z = 1.0` after final `sympy.isprime` confirmation.

## RSA 3072

- Baseline generated `20` deterministic keypairs in `81871.287041` ms total.
- The accelerated path generated the same keypairs in `32310.299291` ms for a measured `2.53x` speedup.
- The proxy removed `19488` Miller-Rabin calls (`91.28%` of baseline MR work).
- Proxy rejection rate was `91.28%` across the full candidate stream.
- All `40` confirmed primes remained on the DCI band `Z = 1.0` after final `sympy.isprime` confirmation.

## RSA 4096

- Baseline generated `10` deterministic keypairs in `125005.477625` ms total.
- The accelerated path generated the same keypairs in `45168.493917` ms for a measured `2.77x` speedup.
- The proxy removed `13031` Miller-Rabin calls (`91.15%` of baseline MR work).
- Proxy rejection rate was `91.15%` across the full candidate stream.
- All `20` confirmed primes remained on the DCI band `Z = 1.0` after final `sympy.isprime` confirmation.
