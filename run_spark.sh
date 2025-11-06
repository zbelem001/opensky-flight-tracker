#!/bin/bash
# Wrapper pour exécuter Spark Consumer avec Java 17

# Activer le venv
source venv/bin/activate

# Forcer Java 17
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Désactiver le Spark système pour utiliser PySpark du venv
unset SPARK_HOME

# Options JVM pour Java 17 (contourner les problèmes de réflexion)
export SPARK_SUBMIT_OPTS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED --add-opens=java.base/sun.util.calendar=ALL-UNNAMED --add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED"

# Vérifier
echo "Using Java: $(java -version 2>&1 | head -1)"
echo "JAVA_HOME: $JAVA_HOME"

./venv/bin/python spark_consumer.py
