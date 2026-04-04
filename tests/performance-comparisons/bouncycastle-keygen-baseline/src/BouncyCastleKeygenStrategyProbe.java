import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

import org.bouncycastle.math.Primes;
import org.bouncycastle.util.BigIntegers;

public final class BouncyCastleKeygenStrategyProbe {
    private static final String PROBE_NAME = "bouncycastle-keygen-direct-core-strategy-probe";
    private static final String ARTIFACT_ORIGIN = "source-build";
    private static final String BC_SOURCE_TAG = "r1rv83";
    private static final String BC_SOURCE_COMMIT = "d4cc9614fc849e840ffdc7941f4a2941131d0c9c";
    private static final String BCPROV_ARTIFACT = "bcprov-jdk18on";
    private static final String BCPROV_VERSION = "1.83";
    private static final String SECURE_RANDOM_ALGORITHM = "SHA1PRNG";
    private static final String DEFAULT_OUTPUT_PATH =
        "results/bcprov-jdk18on-1.83-source-r1rv83-rsa4096-strategy-probe-seed-byte-42.json";
    private static final String CURRENT_BC_VARIANT = "current_bc";
    private static final String TABLE_300007_VARIANT = "bc_plus_chunked_gcd_300007";
    private static final String TABLE_1000003_VARIANT = "bc_plus_chunked_gcd_1000003";
    private static final int RSA_BITS = 4096;
    private static final int CANDIDATE_BITS = RSA_BITS / 2;
    private static final int CORPUS_SIZE = 4096;
    private static final int CREATE_RANDOM_PRIME_CERTAINTY = 1;
    private static final int BC_CERTAINTY = 144;
    private static final int BC_MR_ITERATIONS = 12;
    private static final int BC_CREATE_RANDOM_PRIME_LIMIT = 743;
    private static final int CHUNK_SIZE = 256;
    private static final int TABLE_LIMIT_300007 = 300007;
    private static final int TABLE_LIMIT_1000003 = 1000003;
    private static final byte[] SEED_BYTES = new byte[] {42};
    private static final BigInteger ONE = BigInteger.ONE;
    private static final BigInteger PUBLIC_EXPONENT = BigInteger.valueOf(65537L);
    private static final BigInteger SQUARED_BOUND = ONE.shiftLeft(RSA_BITS - 1);

    private BouncyCastleKeygenStrategyProbe() {
    }

    public static void main(String[] args) throws Exception {
        if (args.length > 1) {
            throw new IllegalArgumentException("expected zero or one output path argument");
        }

        Path outputPath = args.length == 1 ? Path.of(args[0]) : Path.of(DEFAULT_OUTPUT_PATH);
        Files.createDirectories(outputPath.toAbsolutePath().getParent());

        String bcBuildJavaVersion = requiredProperty("bc.build.java.version");
        String bcRuntimeJavaVersion = requiredProperty("bc.runtime.java.version");
        String bcBuiltJarSha256 = requiredProperty("bc.built.jar.sha256");

        Instant startedAt = Instant.now();

        List<BigInteger> corpus = buildCorpus();
        ChunkedPrimeTable table300007 = new ChunkedPrimeTable(TABLE_LIMIT_300007, CHUNK_SIZE, BC_CREATE_RANDOM_PRIME_LIMIT);
        ChunkedPrimeTable table1000003 = new ChunkedPrimeTable(TABLE_LIMIT_1000003, CHUNK_SIZE, BC_CREATE_RANDOM_PRIME_LIMIT);

        VariantResult currentBc = evaluateVariant(CURRENT_BC_VARIANT, BC_CREATE_RANDOM_PRIME_LIMIT, null, corpus);
        VariantResult plus300007 = evaluateVariant(TABLE_300007_VARIANT, TABLE_LIMIT_300007, table300007, corpus);
        VariantResult plus1000003 = evaluateVariant(TABLE_1000003_VARIANT, TABLE_LIMIT_1000003, table1000003, corpus);

        double ceiling300007 = incrementalRejectCeilingVsBcCreateRandomPrime(TABLE_LIMIT_300007);
        double ceiling1000003 = incrementalRejectCeilingVsBcCreateRandomPrime(TABLE_LIMIT_1000003);

        Instant completedAt = Instant.now();

        Files.writeString(
            outputPath,
            buildJson(
                outputPath,
                startedAt,
                completedAt,
                bcBuildJavaVersion,
                bcRuntimeJavaVersion,
                bcBuiltJarSha256,
                currentBc,
                plus300007,
                plus1000003,
                ceiling300007,
                ceiling1000003
            )
        );
        System.out.println("wrote " + outputPath.toAbsolutePath());
    }

    private static List<BigInteger> buildCorpus() throws Exception {
        SecureRandom random = seededRandom();
        List<BigInteger> corpus = new ArrayList<>(CORPUS_SIZE);

        for (int i = 0; i < CORPUS_SIZE; i++) {
            BigInteger candidate = BigIntegers.createRandomPrime(CANDIDATE_BITS, CREATE_RANDOM_PRIME_CERTAINTY, random);
            if (candidate.bitLength() != CANDIDATE_BITS) {
                throw new IllegalStateException("unexpected candidate bit length");
            }
            if (!candidate.testBit(0)) {
                throw new IllegalStateException("createRandomPrime returned an even candidate");
            }
            corpus.add(candidate);
        }

        return Collections.unmodifiableList(corpus);
    }

    private static VariantResult evaluateVariant(
        String name,
        int tableLimit,
        ChunkedPrimeTable table,
        List<BigInteger> corpus
    ) throws Exception {
        SecureRandom mrRandom = seededRandom();

        long addedTableScreenTimeNs = 0L;
        long bcMrTimeNs = 0L;
        long totalTimeNs = 0L;
        int rejectedModE = 0;
        int rejectedSquaredBound = 0;
        int rejectedAddedTable = 0;
        int rejectedBcSmallFactors = 0;
        int rejectedBcMr = 0;
        int rejectedGcd = 0;
        int eligibleAfterBasicBcScreens = 0;
        int bcMrCalls = 0;
        int finalSurvivors = 0;

        for (BigInteger candidate : corpus) {
            long candidateStartNs = System.nanoTime();

            if (candidate.mod(PUBLIC_EXPONENT).equals(ONE)) {
                rejectedModE++;
                totalTimeNs += System.nanoTime() - candidateStartNs;
                continue;
            }

            if (candidate.multiply(candidate).compareTo(SQUARED_BOUND) < 0) {
                rejectedSquaredBound++;
                totalTimeNs += System.nanoTime() - candidateStartNs;
                continue;
            }

            eligibleAfterBasicBcScreens++;

            if (table != null) {
                long tableStartNs = System.nanoTime();
                BigInteger factor = table.findFactor(candidate);
                addedTableScreenTimeNs += System.nanoTime() - tableStartNs;
                if (factor != null) {
                    rejectedAddedTable++;
                    totalTimeNs += System.nanoTime() - candidateStartNs;
                    continue;
                }
            }

            if (Primes.hasAnySmallFactors(candidate)) {
                rejectedBcSmallFactors++;
                totalTimeNs += System.nanoTime() - candidateStartNs;
                continue;
            }

            bcMrCalls++;
            long mrStartNs = System.nanoTime();
            boolean passedMr = Primes.isMRProbablePrime(candidate, mrRandom, BC_MR_ITERATIONS);
            bcMrTimeNs += System.nanoTime() - mrStartNs;

            if (!passedMr) {
                rejectedBcMr++;
                totalTimeNs += System.nanoTime() - candidateStartNs;
                continue;
            }

            if (!PUBLIC_EXPONENT.gcd(candidate.subtract(ONE)).equals(ONE)) {
                rejectedGcd++;
                totalTimeNs += System.nanoTime() - candidateStartNs;
                continue;
            }

            finalSurvivors++;
            totalTimeNs += System.nanoTime() - candidateStartNs;
        }

        int totalRejected = rejectedModE
            + rejectedSquaredBound
            + rejectedAddedTable
            + rejectedBcSmallFactors
            + rejectedBcMr
            + rejectedGcd;

        if (totalRejected + finalSurvivors != corpus.size()) {
            throw new IllegalStateException("stage accounting mismatch for variant " + name);
        }

        return new VariantResult(
            name,
            tableLimit,
            addedTableScreenTimeNs,
            bcMrTimeNs,
            totalTimeNs,
            rejectedModE,
            rejectedSquaredBound,
            rejectedAddedTable,
            rejectedBcSmallFactors,
            rejectedBcMr,
            rejectedGcd,
            eligibleAfterBasicBcScreens,
            bcMrCalls,
            finalSurvivors,
            totalRejected
        );
    }

    private static double incrementalRejectCeilingVsBcCreateRandomPrime(int limit) {
        double logBaseSurvival = logSurvivalProbability(BC_CREATE_RANDOM_PRIME_LIMIT);
        double logExtendedSurvival = logSurvivalProbability(limit);
        double relativeSurvival = Math.exp(logExtendedSurvival - logBaseSurvival);
        return 1.0 - relativeSurvival;
    }

    private static double logSurvivalProbability(int limit) {
        List<Integer> primes = sievePrimes(limit);
        double logSurvival = 0.0;
        for (int prime : primes) {
            if (prime == 2) {
                continue;
            }
            logSurvival += Math.log1p(-1.0 / prime);
        }
        return logSurvival;
    }

    private static List<Integer> sievePrimes(int limit) {
        if (limit < 2) {
            return List.of();
        }

        byte[] flags = new byte[limit + 1];
        for (int i = 2; i <= limit; i++) {
            flags[i] = 1;
        }

        for (int value = 2; (long) value * value <= limit; value++) {
            if (flags[value] == 0) {
                continue;
            }
            for (int composite = value * value; composite <= limit; composite += value) {
                flags[composite] = 0;
            }
        }

        List<Integer> primes = new ArrayList<>();
        for (int value = 2; value <= limit; value++) {
            if (flags[value] != 0) {
                primes.add(value);
            }
        }
        return primes;
    }

    private static SecureRandom seededRandom() throws Exception {
        SecureRandom random = SecureRandom.getInstance(SECURE_RANDOM_ALGORITHM);
        random.setSeed(SEED_BYTES);
        return random;
    }

    private static String buildJson(
        Path outputPath,
        Instant startedAt,
        Instant completedAt,
        String bcBuildJavaVersion,
        String bcRuntimeJavaVersion,
        String bcBuiltJarSha256,
        VariantResult currentBc,
        VariantResult plus300007,
        VariantResult plus1000003,
        double ceiling300007,
        double ceiling1000003
    ) {
        long currentTotalNs = currentBc.modeledTotalPostCreateRandomPrimeTimeNs;
        int currentBcMrCalls = currentBc.bcMrCalls;
        VariantResult best = currentBc;
        if (plus300007.modeledTotalPostCreateRandomPrimeTimeNs < best.modeledTotalPostCreateRandomPrimeTimeNs) {
            best = plus300007;
        }
        if (plus1000003.modeledTotalPostCreateRandomPrimeTimeNs < best.modeledTotalPostCreateRandomPrimeTimeNs) {
            best = plus1000003;
        }

        StringBuilder builder = new StringBuilder();
        builder.append("{\n");
        builder.append("  \"probe\": \"").append(PROBE_NAME).append("\",\n");
        builder.append("  \"output_path\": \"").append(escapeJson(outputPath.toString())).append("\",\n");
        builder.append("  \"started_at_utc\": \"").append(startedAt).append("\",\n");
        builder.append("  \"completed_at_utc\": \"").append(completedAt).append("\",\n");
        builder.append("  \"provenance\": {\n");
        builder.append("    \"artifact_origin\": \"").append(ARTIFACT_ORIGIN).append("\",\n");
        builder.append("    \"bc_source_tag\": \"").append(BC_SOURCE_TAG).append("\",\n");
        builder.append("    \"bc_source_commit\": \"").append(BC_SOURCE_COMMIT).append("\",\n");
        builder.append("    \"bc_build_java_version\": \"")
            .append(escapeJson(bcBuildJavaVersion)).append("\",\n");
        builder.append("    \"bc_runtime_java_version\": \"")
            .append(escapeJson(bcRuntimeJavaVersion)).append("\",\n");
        builder.append("    \"bc_built_jar_sha256\": \"")
            .append(escapeJson(bcBuiltJarSha256)).append("\"\n");
        builder.append("  },\n");
        builder.append("  \"configuration\": {\n");
        builder.append("    \"bcprov_artifact\": \"").append(BCPROV_ARTIFACT).append("\",\n");
        builder.append("    \"bcprov_version\": \"").append(BCPROV_VERSION).append("\",\n");
        builder.append("    \"generator_path\": \"org.bouncycastle.crypto.generators.RSAKeyPairGenerator\",\n");
        builder.append("    \"candidate_source\": \"org.bouncycastle.util.BigIntegers.createRandomPrime\",\n");
        builder.append("    \"rsa_bits\": ").append(RSA_BITS).append(",\n");
        builder.append("    \"candidate_bits\": ").append(CANDIDATE_BITS).append(",\n");
        builder.append("    \"corpus_size\": ").append(CORPUS_SIZE).append(",\n");
        builder.append("    \"create_random_prime_certainty\": ").append(CREATE_RANDOM_PRIME_CERTAINTY).append(",\n");
        builder.append("    \"bc_certainty\": ").append(BC_CERTAINTY).append(",\n");
        builder.append("    \"bc_mr_iterations\": ").append(BC_MR_ITERATIONS).append(",\n");
        builder.append("    \"public_exponent\": ").append(PUBLIC_EXPONENT).append(",\n");
        builder.append("    \"secure_random_algorithm\": \"").append(SECURE_RANDOM_ALGORITHM).append("\",\n");
        builder.append("    \"corpus_seed_bytes_decimal\": [42],\n");
        builder.append("    \"mr_seed_bytes_decimal\": [42],\n");
        builder.append("    \"chunk_size\": ").append(CHUNK_SIZE).append(",\n");
        builder.append("    \"table_start_exclusive\": ").append(BC_CREATE_RANDOM_PRIME_LIMIT).append(",\n");
        builder.append("    \"java_version\": \"")
            .append(escapeJson(System.getProperty("java.version"))).append("\",\n");
        builder.append("    \"java_vendor\": \"")
            .append(escapeJson(System.getProperty("java.vendor"))).append("\",\n");
        builder.append("    \"os_name\": \"")
            .append(escapeJson(System.getProperty("os.name"))).append("\",\n");
        builder.append("    \"os_arch\": \"")
            .append(escapeJson(System.getProperty("os.arch"))).append("\"\n");
        builder.append("  },\n");
        builder.append("  \"theoretical_incremental_ceiling\": {\n");
        builder.append("    \"bc_create_random_prime_limit\": ").append(BC_CREATE_RANDOM_PRIME_LIMIT).append(",\n");
        builder.append("    \"rows\": [\n");
        builder.append("      {\n");
        builder.append("        \"table_limit\": ").append(TABLE_LIMIT_300007).append(",\n");
        builder.append("        \"incremental_reject_rate_vs_bc_create_random_prime_survivors\": ")
            .append(formatRate(ceiling300007)).append("\n");
        builder.append("      },\n");
        builder.append("      {\n");
        builder.append("        \"table_limit\": ").append(TABLE_LIMIT_1000003).append(",\n");
        builder.append("        \"incremental_reject_rate_vs_bc_create_random_prime_survivors\": ")
            .append(formatRate(ceiling1000003)).append("\n");
        builder.append("      }\n");
        builder.append("    ]\n");
        builder.append("  },\n");
        builder.append("  \"summary\": {\n");
        builder.append("    \"best_variant_by_modeled_total\": \"").append(best.name).append("\",\n");
        builder.append("    \"best_variant_modeled_total_ms\": ")
            .append(formatMillis(nanosToMillis(best.modeledTotalPostCreateRandomPrimeTimeNs))).append(",\n");
        builder.append("    \"current_bc_modeled_total_ms\": ")
            .append(formatMillis(nanosToMillis(currentTotalNs))).append("\n");
        builder.append("  },\n");
        builder.append("  \"variants\": [\n");
        appendVariantJson(builder, currentBc, currentTotalNs, currentBcMrCalls, true);
        appendVariantJson(builder, plus300007, currentTotalNs, currentBcMrCalls, true);
        appendVariantJson(builder, plus1000003, currentTotalNs, currentBcMrCalls, false);
        builder.append("  ]\n");
        builder.append("}\n");
        return builder.toString();
    }

    private static void appendVariantJson(
        StringBuilder builder,
        VariantResult result,
        long currentTotalNs,
        int currentBcMrCalls,
        boolean trailingComma
    ) {
        builder.append("    {\n");
        builder.append("      \"name\": \"").append(result.name).append("\",\n");
        builder.append("      \"table_limit\": ").append(result.tableLimit).append(",\n");
        builder.append("      \"added_table_screen_time_ns\": ").append(result.addedTableScreenTimeNs).append(",\n");
        builder.append("      \"added_table_screen_time_ms\": ")
            .append(formatMillis(nanosToMillis(result.addedTableScreenTimeNs))).append(",\n");
        builder.append("      \"bc_mr_time_ns\": ").append(result.bcMrTimeNs).append(",\n");
        builder.append("      \"bc_mr_time_ms\": ")
            .append(formatMillis(nanosToMillis(result.bcMrTimeNs))).append(",\n");
        builder.append("      \"modeled_total_post_create_random_prime_time_ns\": ")
            .append(result.modeledTotalPostCreateRandomPrimeTimeNs).append(",\n");
        builder.append("      \"modeled_total_post_create_random_prime_time_ms\": ")
            .append(formatMillis(nanosToMillis(result.modeledTotalPostCreateRandomPrimeTimeNs))).append(",\n");
        builder.append("      \"modeled_speedup_vs_current_bc\": ")
            .append(formatRate((double) currentTotalNs / result.modeledTotalPostCreateRandomPrimeTimeNs)).append(",\n");
        builder.append("      \"added_table_reject_rate_vs_basic_bc_eligible\": ")
            .append(formatRate(rate(result.rejectedAddedTable, result.eligibleAfterBasicBcScreens))).append(",\n");
        builder.append("      \"mr_call_reduction_vs_current_bc\": ")
            .append(formatRate(1.0 - rate(result.bcMrCalls, currentBcMrCalls))).append(",\n");
        builder.append("      \"counts\": {\n");
        builder.append("        \"total_candidates\": ").append(CORPUS_SIZE).append(",\n");
        builder.append("        \"eligible_after_mod_e_and_squared_bound\": ")
            .append(result.eligibleAfterBasicBcScreens).append(",\n");
        builder.append("        \"bc_mr_calls\": ").append(result.bcMrCalls).append(",\n");
        builder.append("        \"final_survivors\": ").append(result.finalSurvivors).append(",\n");
        builder.append("        \"total_rejected\": ").append(result.totalRejected).append("\n");
        builder.append("      },\n");
        builder.append("      \"rejections\": {\n");
        builder.append("        \"mod_e\": ").append(result.rejectedModE).append(",\n");
        builder.append("        \"squared_bound\": ").append(result.rejectedSquaredBound).append(",\n");
        builder.append("        \"added_table\": ").append(result.rejectedAddedTable).append(",\n");
        builder.append("        \"bc_small_factors\": ").append(result.rejectedBcSmallFactors).append(",\n");
        builder.append("        \"bc_mr\": ").append(result.rejectedBcMr).append(",\n");
        builder.append("        \"gcd_e_p_minus_1\": ").append(result.rejectedGcd).append("\n");
        builder.append("      }\n");
        builder.append("    }");
        if (trailingComma) {
            builder.append(",");
        }
        builder.append("\n");
    }

    private static String requiredProperty(String name) {
        String value = System.getProperty(name);
        if (value == null || value.isEmpty()) {
            throw new IllegalStateException("missing required system property: " + name);
        }
        return value;
    }

    private static double nanosToMillis(long nanos) {
        return nanos / 1_000_000.0;
    }

    private static String formatMillis(double milliseconds) {
        return String.format(Locale.US, "%.6f", milliseconds);
    }

    private static String formatRate(double value) {
        return String.format(Locale.US, "%.12f", value);
    }

    private static double rate(int numerator, int denominator) {
        if (denominator == 0) {
            return 0.0;
        }
        return (double) numerator / denominator;
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static final class ChunkedPrimeTable {
        private final List<List<Integer>> chunks;
        private final List<BigInteger> chunkProducts;

        private ChunkedPrimeTable(int limit, int chunkSize, int startExclusive) {
            if (limit <= startExclusive) {
                throw new IllegalArgumentException("limit must be larger than startExclusive");
            }
            if (chunkSize < 1) {
                throw new IllegalArgumentException("chunkSize must be positive");
            }

            List<Integer> primes = sievePrimes(limit);
            List<Integer> filteredPrimes = new ArrayList<>();
            for (int prime : primes) {
                if (prime != 2 && prime > startExclusive) {
                    filteredPrimes.add(prime);
                }
            }

            this.chunks = new ArrayList<>();
            this.chunkProducts = new ArrayList<>();
            for (int start = 0; start < filteredPrimes.size(); start += chunkSize) {
                List<Integer> chunk = new ArrayList<>(
                    filteredPrimes.subList(start, Math.min(start + chunkSize, filteredPrimes.size()))
                );
                BigInteger product = ONE;
                for (int prime : chunk) {
                    product = product.multiply(BigInteger.valueOf(prime));
                }
                this.chunks.add(Collections.unmodifiableList(chunk));
                this.chunkProducts.add(product);
            }
        }

        private BigInteger findFactor(BigInteger candidate) {
            for (int i = 0; i < chunks.size(); i++) {
                if (candidate.gcd(chunkProducts.get(i)).equals(ONE)) {
                    continue;
                }
                for (int prime : chunks.get(i)) {
                    BigInteger divisor = BigInteger.valueOf(prime);
                    if (candidate.mod(divisor).equals(BigInteger.ZERO)) {
                        return divisor;
                    }
                }
            }
            return null;
        }
    }

    private static final class VariantResult {
        private final String name;
        private final int tableLimit;
        private final long addedTableScreenTimeNs;
        private final long bcMrTimeNs;
        private final long modeledTotalPostCreateRandomPrimeTimeNs;
        private final int rejectedModE;
        private final int rejectedSquaredBound;
        private final int rejectedAddedTable;
        private final int rejectedBcSmallFactors;
        private final int rejectedBcMr;
        private final int rejectedGcd;
        private final int eligibleAfterBasicBcScreens;
        private final int bcMrCalls;
        private final int finalSurvivors;
        private final int totalRejected;

        private VariantResult(
            String name,
            int tableLimit,
            long addedTableScreenTimeNs,
            long bcMrTimeNs,
            long modeledTotalPostCreateRandomPrimeTimeNs,
            int rejectedModE,
            int rejectedSquaredBound,
            int rejectedAddedTable,
            int rejectedBcSmallFactors,
            int rejectedBcMr,
            int rejectedGcd,
            int eligibleAfterBasicBcScreens,
            int bcMrCalls,
            int finalSurvivors,
            int totalRejected
        ) {
            this.name = name;
            this.tableLimit = tableLimit;
            this.addedTableScreenTimeNs = addedTableScreenTimeNs;
            this.bcMrTimeNs = bcMrTimeNs;
            this.modeledTotalPostCreateRandomPrimeTimeNs = modeledTotalPostCreateRandomPrimeTimeNs;
            this.rejectedModE = rejectedModE;
            this.rejectedSquaredBound = rejectedSquaredBound;
            this.rejectedAddedTable = rejectedAddedTable;
            this.rejectedBcSmallFactors = rejectedBcSmallFactors;
            this.rejectedBcMr = rejectedBcMr;
            this.rejectedGcd = rejectedGcd;
            this.eligibleAfterBasicBcScreens = eligibleAfterBasicBcScreens;
            this.bcMrCalls = bcMrCalls;
            this.finalSurvivors = finalSurvivors;
            this.totalRejected = totalRejected;
        }
    }
}
