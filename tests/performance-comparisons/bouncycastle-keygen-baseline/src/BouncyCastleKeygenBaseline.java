import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

import org.bouncycastle.crypto.AsymmetricCipherKeyPair;
import org.bouncycastle.crypto.generators.RSAKeyPairGenerator;
import org.bouncycastle.crypto.params.RSAKeyGenerationParameters;
import org.bouncycastle.crypto.params.RSAKeyParameters;
import org.bouncycastle.crypto.params.RSAPrivateCrtKeyParameters;

public final class BouncyCastleKeygenBaseline {
    private static final String BENCHMARK_NAME = "bouncycastle-keygen-direct-core-baseline";
    private static final String ARTIFACT_ORIGIN = "source-build";
    private static final String BC_SOURCE_TAG = "r1rv83";
    private static final String BC_SOURCE_COMMIT = "d4cc9614fc849e840ffdc7941f4a2941131d0c9c";
    private static final String BCPROV_ARTIFACT = "bcprov-jdk18on";
    private static final String BCPROV_VERSION = "1.83";
    private static final int KEY_SIZE_BITS = 4096;
    private static final int ITERATIONS = 100;
    private static final int WARMUP_ITERATIONS = 0;
    private static final int CERTAINTY = 144;
    private static final String SECURE_RANDOM_ALGORITHM = "SHA1PRNG";
    private static final BigInteger PUBLIC_EXPONENT = BigInteger.valueOf(65537L);
    private static final byte[] SEED_BYTES = new byte[] {42};
    private static final String DEFAULT_OUTPUT_PATH =
        "results/bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json";

    private BouncyCastleKeygenBaseline() {
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

        SecureRandom random = SecureRandom.getInstance(SECURE_RANDOM_ALGORITHM);
        random.setSeed(SEED_BYTES);

        for (int i = 0; i < WARMUP_ITERATIONS; i++) {
            generateKeyPair(random);
        }

        Instant startedAt = Instant.now();
        List<Long> iterationTimesNs = new ArrayList<>(ITERATIONS);
        for (int i = 0; i < ITERATIONS; i++) {
            long startNs = System.nanoTime();
            AsymmetricCipherKeyPair keyPair = generateKeyPair(random);
            long elapsedNs = System.nanoTime() - startNs;
            validateKeyPair(keyPair);
            iterationTimesNs.add(elapsedNs);
        }
        Instant completedAt = Instant.now();

        Files.writeString(
            outputPath,
            buildJson(
                outputPath,
                startedAt,
                completedAt,
                iterationTimesNs,
                bcBuildJavaVersion,
                bcRuntimeJavaVersion,
                bcBuiltJarSha256
            )
        );
        System.out.println("wrote " + outputPath.toAbsolutePath());
    }

    private static AsymmetricCipherKeyPair generateKeyPair(SecureRandom random) {
        RSAKeyPairGenerator generator = new RSAKeyPairGenerator();
        RSAKeyGenerationParameters parameters =
            new RSAKeyGenerationParameters(PUBLIC_EXPONENT, random, KEY_SIZE_BITS, CERTAINTY);
        generator.init(parameters);
        return generator.generateKeyPair();
    }

    private static void validateKeyPair(AsymmetricCipherKeyPair keyPair) {
        RSAKeyParameters publicKey = (RSAKeyParameters) keyPair.getPublic();
        RSAPrivateCrtKeyParameters privateKey = (RSAPrivateCrtKeyParameters) keyPair.getPrivate();

        if (publicKey.getModulus().bitLength() != KEY_SIZE_BITS) {
            throw new IllegalStateException("unexpected modulus size");
        }
        if (!publicKey.getExponent().equals(PUBLIC_EXPONENT)) {
            throw new IllegalStateException("unexpected public exponent");
        }
        if (!privateKey.getModulus().equals(publicKey.getModulus())) {
            throw new IllegalStateException("public and private moduli differ");
        }
    }

    private static String buildJson(
        Path outputPath,
        Instant startedAt,
        Instant completedAt,
        List<Long> iterationTimesNs,
        String bcBuildJavaVersion,
        String bcRuntimeJavaVersion,
        String bcBuiltJarSha256
    ) {
        long totalTimeNs = 0L;
        long minTimeNs = Long.MAX_VALUE;
        long maxTimeNs = Long.MIN_VALUE;

        for (long value : iterationTimesNs) {
            totalTimeNs += value;
            if (value < minTimeNs) {
                minTimeNs = value;
            }
            if (value > maxTimeNs) {
                maxTimeNs = value;
            }
        }

        List<Long> sortedTimes = new ArrayList<>(iterationTimesNs);
        Collections.sort(sortedTimes);
        double meanTimeMs = nanosToMillis(totalTimeNs) / ITERATIONS;
        double medianTimeMs = nanosToMillis(median(sortedTimes));
        double minTimeMs = nanosToMillis(minTimeNs);
        double maxTimeMs = nanosToMillis(maxTimeNs);
        double totalTimeMs = nanosToMillis(totalTimeNs);

        StringBuilder builder = new StringBuilder();
        builder.append("{\n");
        builder.append("  \"benchmark\": \"").append(BENCHMARK_NAME).append("\",\n");
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
        builder.append("    \"bits\": ").append(KEY_SIZE_BITS).append(",\n");
        builder.append("    \"iterations\": ").append(ITERATIONS).append(",\n");
        builder.append("    \"warmup_iterations\": ").append(WARMUP_ITERATIONS).append(",\n");
        builder.append("    \"public_exponent\": ").append(PUBLIC_EXPONENT).append(",\n");
        builder.append("    \"certainty\": ").append(CERTAINTY).append(",\n");
        builder.append("    \"secure_random_algorithm\": \"").append(SECURE_RANDOM_ALGORITHM).append("\",\n");
        builder.append("    \"seed_bytes_decimal\": [42],\n");
        builder.append("    \"java_version\": \"")
            .append(escapeJson(System.getProperty("java.version"))).append("\",\n");
        builder.append("    \"java_vendor\": \"")
            .append(escapeJson(System.getProperty("java.vendor"))).append("\",\n");
        builder.append("    \"os_name\": \"")
            .append(escapeJson(System.getProperty("os.name"))).append("\",\n");
        builder.append("    \"os_arch\": \"")
            .append(escapeJson(System.getProperty("os.arch"))).append("\"\n");
        builder.append("  },\n");
        builder.append("  \"summary\": {\n");
        builder.append("    \"total_time_ns\": ").append(totalTimeNs).append(",\n");
        builder.append("    \"total_time_ms\": ").append(formatMillis(totalTimeMs)).append(",\n");
        builder.append("    \"mean_time_ms\": ").append(formatMillis(meanTimeMs)).append(",\n");
        builder.append("    \"median_time_ms\": ").append(formatMillis(medianTimeMs)).append(",\n");
        builder.append("    \"min_time_ms\": ").append(formatMillis(minTimeMs)).append(",\n");
        builder.append("    \"max_time_ms\": ").append(formatMillis(maxTimeMs)).append("\n");
        builder.append("  },\n");
        builder.append("  \"iteration_times_ms\": [\n");
        for (int i = 0; i < iterationTimesNs.size(); i++) {
            builder.append("    ").append(formatMillis(nanosToMillis(iterationTimesNs.get(i))));
            if (i + 1 < iterationTimesNs.size()) {
                builder.append(",");
            }
            builder.append("\n");
        }
        builder.append("  ]\n");
        builder.append("}\n");
        return builder.toString();
    }

    private static String requiredProperty(String name) {
        String value = System.getProperty(name);
        if (value == null || value.isEmpty()) {
            throw new IllegalStateException("missing required system property: " + name);
        }
        return value;
    }

    private static long median(List<Long> sortedTimes) {
        int middle = sortedTimes.size() / 2;
        if (sortedTimes.size() % 2 == 1) {
            return sortedTimes.get(middle);
        }
        long left = sortedTimes.get(middle - 1);
        long right = sortedTimes.get(middle);
        return (left + right) / 2L;
    }

    private static double nanosToMillis(long nanos) {
        return nanos / 1_000_000.0;
    }

    private static String formatMillis(double milliseconds) {
        return String.format(Locale.US, "%.6f", milliseconds);
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
