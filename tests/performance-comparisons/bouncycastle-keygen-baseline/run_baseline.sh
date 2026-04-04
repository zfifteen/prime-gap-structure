#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$ROOT_DIR/build"
CLASSES_DIR="$BUILD_DIR/classes"
BC_SOURCE_DIR="$ROOT_DIR/vendor/bc-java-r1rv83"
JAR_PATH="$BC_SOURCE_DIR/prov/build/libs/bcprov-jdk18on-1.83.jar"
SOURCE_PATH="$ROOT_DIR/src/BouncyCastleKeygenBaseline.java"
OUTPUT_PATH="$ROOT_DIR/results/bcprov-jdk18on-1.83-source-r1rv83-rsa4096-direct-core-seed-byte-42-runs-100.json"
BC_BUILD_JAVA_HOME="/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home"
BC_RUNTIME_JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"

mkdir -p "$CLASSES_DIR" "$(dirname "$OUTPUT_PATH")"

if [ ! -d "$BC_SOURCE_DIR" ]; then
  echo "Missing vendored Bouncy Castle source tree: $BC_SOURCE_DIR" >&2
  exit 1
fi

JAVA_HOME="$BC_BUILD_JAVA_HOME" PATH="$BC_BUILD_JAVA_HOME/bin:$PATH" \
  "$BC_SOURCE_DIR/gradlew" -p "$BC_SOURCE_DIR" :prov:jar --console=plain

if [ ! -f "$JAR_PATH" ]; then
  echo "Expected built jar not found: $JAR_PATH" >&2
  exit 1
fi

jar tf "$JAR_PATH" | grep -q '^org/bouncycastle/crypto/generators/RSAKeyPairGenerator.class$'
jar tf "$JAR_PATH" | grep -q '^org/bouncycastle/jcajce/provider/asymmetric/util/PrimeCertaintyCalculator.class$'

BC_BUILD_JAVA_VERSION="$("$BC_BUILD_JAVA_HOME/bin/java" -version 2>&1 | head -n 1)"
BC_RUNTIME_JAVA_VERSION="$("$BC_RUNTIME_JAVA_HOME/bin/java" -version 2>&1 | head -n 1)"
BC_BUILT_JAR_SHA256="$(shasum -a 256 "$JAR_PATH" | awk '{print $1}')"

JAVA_HOME="$BC_RUNTIME_JAVA_HOME" PATH="$BC_RUNTIME_JAVA_HOME/bin:$PATH" \
  javac -cp "$JAR_PATH" -d "$CLASSES_DIR" "$SOURCE_PATH"

JAVA_HOME="$BC_RUNTIME_JAVA_HOME" PATH="$BC_RUNTIME_JAVA_HOME/bin:$PATH" \
  java \
    -Dbc.build.java.version="$BC_BUILD_JAVA_VERSION" \
    -Dbc.runtime.java.version="$BC_RUNTIME_JAVA_VERSION" \
    -Dbc.built.jar.sha256="$BC_BUILT_JAR_SHA256" \
    -cp "$JAR_PATH:$CLASSES_DIR" \
    BouncyCastleKeygenBaseline \
    "$OUTPUT_PATH"
