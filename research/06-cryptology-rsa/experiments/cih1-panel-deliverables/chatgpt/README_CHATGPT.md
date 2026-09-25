Saddle’s up. The CIH-1 analysis engine is built, tested, and packaged.

The sandbox smoke run passes all unit tests and the end-to-end smoke. The smoke corpus correctly has **0 near-square exclusions**, but the experiment still aborts because the fallback freeze requires **≥30 included cases**; that is exactly the intended fail-closed behavior. The smoke therefore demonstrates the engine without pretending a four-case toy corpus can support the scientific decision rule.

Key smoke result: `median_R = 1.13039`, `f_beat = 0.25`, `p = 0.9375`, decision `aborted_insufficient_n`.

[Download the complete CIH-1 ChatGPT analysis package](sandbox:/mnt/data/pgs_cih1_analysis_chatgpt_v1.zip)

[Open the package directory](sandbox:/mnt/data/pgs_cih1_analysis_chatgpt_v1)

The package contains the requested source tree, fallback freeze, schemas, tests, examples, smoke script, README, self-check report, and SHA-256 manifest. It follows the supplied CIH-1 contract: carrier distance is the primary signal, reciprocal-floor behavior is not a success criterion, there is no historical false-class blacklist, and the reporting language stays in the measured/hypothesis-support lane.
