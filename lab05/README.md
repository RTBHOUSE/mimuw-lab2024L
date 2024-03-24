# Stream processing part 2 - Kafka Streams

In this laboratory you will learn how to process streams using Kafka Streams. If you are stuck, ask the instructor for help.

## 1. Start Kafka

Follow the instructions from *[the previous lab](https://github.com/RTBHOUSE/mimuw-lab2024L/tree/main/lab04)* to start a single-node Kafka cluster.

## 2. Run the demo app

Kafka Streams library is shipped with several example applications, including
the classic of all classics: word count. Follow the instructions below to run it.

1. Go to Kafka installation directory:
```bash
$ cd /opt/kafka
```

2. Create the input topic and the output topic:
```bash
$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic streams-plaintext-input
Created topic streams-plaintext-input.
$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --config cleanup.policy=compact --topic streams-wordcount-output
Created topic streams-wordcount-output.
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe
Topic: streams-wordcount-output	TopicId: 7seQkML0Sv2Auo8YdgJm5w	PartitionCount: 1	ReplicationFactor: 1	Configs: cleanup.policy=compact,segment.bytes=1073741824
	Topic: streams-wordcount-output	Partition: 0	Leader: 101	Replicas: 101	Isr: 101
Topic: streams-plaintext-input	TopicId: HqBemQ-GTDKBc4lHiwmuEg	PartitionCount: 1	ReplicationFactor: 1	Configs: segment.bytes=1073741824
	Topic: streams-plaintext-input	Partition: 0	Leader: 101	Replicas: 101	Isr: 101
```

3. Write some data into the input topic:
```bash
$ bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic streams-plaintext-input
>elitarny mimuw jest elitarny
```

4. Open another terminal and run the demo app:
```bash
$ bin/kafka-run-class.sh org.apache.kafka.streams.examples.wordcount.WordCountDemo
```

5. Open a third terminal and read from the output topic:
```bash
$ bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
    --topic streams-wordcount-output \
    --from-beginning \
    --formatter kafka.tools.DefaultMessageFormatter \
    --property print.key=true \
    --property print.value=true \
    --property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
    --property value.deserializer=org.apache.kafka.common.serialization.LongDeserializer
elitarny	1
mimuw	1
jest	1
elitarny	2
```

6. Write some more data into the input topic and examine the output topic.

## 3. Create a Maven project and build the example app from the sources

1. Create a new directory for the project:
```bash
$ cd && mkdir lab05 && cd lab05
```

2. Install Maven and tree:
```bash
$ sudo apt -y install maven tree
```

3. Run Maven command to create the project:

```bash
$ mvn archetype:generate \
    -DarchetypeGroupId=org.apache.kafka \
    -DarchetypeArtifactId=streams-quickstart-java \
    -DarchetypeVersion=3.1.1 \
    -DgroupId=streams.examples \
    -DartifactId=streams.examples \
    -Dversion=0.1 \
    -Dpackage=myapps
```

4. You will see a prompt waiting for you to confirm the project configuration (press Enter to confirm):

```bash
...
[INFO] Using property: artifactId = streams.examples
[INFO] Using property: version = 0.1
[INFO] Using property: package = myapps
Confirm properties configuration:
groupId: streams.examples
artifactId: streams.examples
version: 0.1
package: myapps
 Y: :
```

5. Examine the project tree. It should look like this:
```bash
$ tree streams.examples/
streams.examples/
├── pom.xml
└── src
    └── main
        ├── java
        │   └── myapps
        │       ├── LineSplit.java
        │       ├── Pipe.java
        │       └── WordCount.java
        └── resources
            └── log4j.properties
```

6. Read and analyze class WordCount.java:
```bash
$ cat streams.examples/src/main/java/myapps/WordCount.java
/*
 * ...
 */
package myapps;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.utils.Bytes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.KeyValueMapper;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.kstream.ValueMapper;
import org.apache.kafka.streams.state.KeyValueStore;

import java.util.Arrays;
import java.util.Locale;
import java.util.Properties;
import java.util.concurrent.CountDownLatch;

/**
 * In this example, we implement a simple WordCount program using the high-level Streams DSL
 * that reads from a source topic "streams-plaintext-input", where the values of messages represent lines of text,
 * split each text line into words and then compute the word occurrence histogram, write the continuous updated histogram
 * into a topic "streams-wordcount-output" where each record is an updated count of a single word.
 */
public class WordCount {

    public static void main(String[] args) throws Exception {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "streams-wordcount");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        final StreamsBuilder builder = new StreamsBuilder();

        builder.<String, String>stream("streams-plaintext-input")
               .flatMapValues(value -> Arrays.asList(value.toLowerCase(Locale.getDefault()).split("\\W+")))
               .groupBy((key, value) -> value)
               .count(Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("counts-store"))
               .toStream()
               .to("streams-wordcount-output", Produced.with(Serdes.String(), Serdes.Long()));

        final Topology topology = builder.build();
        final KafkaStreams streams = new KafkaStreams(topology, props);
        final CountDownLatch latch = new CountDownLatch(1);

        // attach shutdown handler to catch control-c
        Runtime.getRuntime().addShutdownHook(new Thread("streams-shutdown-hook") {
            @Override
            public void run() {
                streams.close();
                latch.countDown();
            }
        });

        try {
            streams.start();
            latch.await();
        } catch (Throwable e) {
            System.exit(1);
        }
        System.exit(0);
    }
}

```

The most important part is setting up the topology:
```bash
        final StreamsBuilder builder = new StreamsBuilder();

        // this line creates a stream from input topic named streams-plaintext-input
        builder.<String, String>stream("streams-plaintext-input")
                // this line performs stream transformation: each line from the stream is converted
                // to lower case and split into single words; then flat map is applied in order to
                // get a stream of strings (and not a stream of lists)
               .flatMapValues(value -> Arrays.asList(value.toLowerCase(Locale.getDefault()).split("\\W+")))
               // this line re-partitions the input data, with the new record key being the words
               .groupBy((key, value) -> value)
               // this line performs the actual counting; the count will be saved on the disk
               // and will be available even after the application terminates
               .count(Materialized.<String, Long, KeyValueStore<Bytes, byte[]>>as("counts-store"))
               // this line converts the output table to the output stream
               .toStream()
               // this line redirects the output stream to streams-wordcount-output topic
               .to("streams-wordcount-output", Produced.with(Serdes.String(), Serdes.Long()));

        final Topology topology = builder.build();
```

7. Change the default compiler from jdt to javac:
```bash
$ sed -i 's/<compilerId>jdt/<compilerId>javac/g' streams.examples/pom.xml
```

8. Compile and run the application:
```bash
$ cd streams.examples/ && mvn clean package
...
$ mvn exec:java -Dexec.mainClass=myapps.WordCount
```

9. Open the producer and the consumer in new terminals as in the previous example. Process some data and observe the results (it might take about one minute before the results are flushed to the output topic):
```bash
$ bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic streams-plaintext-input
>elitarny mimuw jest elitarny
```
```bash
$ bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
    --topic streams-wordcount-output \
    --from-beginning \
    --formatter kafka.tools.DefaultMessageFormatter \
    --property print.key=true \
    --property print.value=true \
    --property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
    --property value.deserializer=org.apache.kafka.common.serialization.LongDeserializer
...
mimuw	1
jest	1
elitarny	2
```

10. Restart the application and repeat some of the previously sent words. Observe that the count for the repeated words does not start from 1. This proves that the state has been preserved during the restart:
```bash
# in the producer terminal
>jeszcze bardziej elitarny
```
```bash
# in the consumer terminal
jeszcze	1
bardziej	1
elitarny	3
```

11. List all topics in your Kafka cluster:
```bash
$ /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
__consumer_offsets
streams-plaintext-input
streams-wordcount-counts-store-changelog
streams-wordcount-counts-store-repartition
streams-wordcount-output
```
Note that your application (streams-wordcount) created two auxiliary topics: streams-wordcount-counts-store-changelog and streams-wordcount-counts-store-repartition - this is where the state is stored. You can delete the state by calling `streams.cleanUp()` in your Java code.

## 4. Write your own app from scratch

Use the created project to write your own Kafka Streams application from scratch. The application will read a stream of purchases from an online shop. Each line will have exactly two fields: user id and product price. For example:  
user12314265 120  
user234672 40  
Your task is to calculate the total number of purchases per user and the total amount of money spent by each user. The result should be stored in an external database.

1. Create file MyApp.java in streams.examples/src/main/java/myapps:
```java
package myapps;

import java.util.Properties;
import java.util.concurrent.CountDownLatch;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.state.KeyValueStore;
import org.apache.kafka.streams.state.StoreBuilder;
import org.apache.kafka.streams.state.Stores;

public class MyApp {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "purchases-aggregator");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        StoreBuilder<KeyValueStore<String, Long>> countStoreBuilder = Stores.keyValueStoreBuilder(
                Stores.persistentKeyValueStore("purchases-count"),
                Serdes.String(),
                Serdes.Long()
        );

        StoreBuilder<KeyValueStore<String, Long>> sumStoreBuilder = Stores.keyValueStoreBuilder(
                Stores.persistentKeyValueStore("purchases-sum"),
                Serdes.String(),
                Serdes.Long()
        );

        Topology builder = new Topology();
        builder.addSource("source", "purchases")
                .addProcessor("processor", PurchaseProcessor::new, "source")
                .addStateStore(countStoreBuilder, "processor")
                .addStateStore(sumStoreBuilder, "processor");

        final KafkaStreams streams = new KafkaStreams(builder, props);
        final CountDownLatch latch = new CountDownLatch(1);

        // attach shutdown handler to catch control-c
        Runtime.getRuntime().addShutdownHook(new Thread("streams-shutdown-hook") {
            @Override
            public void run() {
                streams.close();
                latch.countDown();
            }
        });

        try {
            streams.start();
            latch.await();
        } catch (Throwable e) {
            System.exit(1);
        }
        System.exit(0);
    }
}
```
2. Create file PurchaseProcessor.java in streams.examples/src/main/java/myapps:
```java
package myapps;


import org.apache.kafka.streams.processor.api.Processor;
import org.apache.kafka.streams.processor.api.ProcessorContext;
import org.apache.kafka.streams.processor.api.Record;
import org.apache.kafka.streams.state.KeyValueStore;


public class PurchaseProcessor implements Processor<String, String, String, String> {
    private KeyValueStore<String, Long> countStore;
    private KeyValueStore<String, Long> sumStore;
    private DatabaseMock database;

    @Override
    public void init(ProcessorContext<String, String> context) {
        countStore = context.getStateStore("purchases-count");
        sumStore = context.getStateStore("purchases-sum");
        database = new DatabaseMock();
    }

    @Override
    public void process(Record<String, String> record) {
        String[] splitMessage = record.value().split("\\W+");
        String userId = splitMessage[0];
        int purchaseValue = Integer.parseInt(splitMessage[1]);

        Long oldCount = countStore.get(userId);
        long newCount = oldCount == null ? 1 : oldCount + 1;
        countStore.put(userId, newCount);

        Long oldSum = sumStore.get(userId);
        long newSum = oldSum == null ? purchaseValue : oldSum + purchaseValue;
        sumStore.put(userId, newSum);

        database.updateUserProfile(userId, newCount, newSum);
    }
}
```
3. Create file DatabaseMock.java in streams.examples/src/main/java/myapps:
```java
package myapps;

public class DatabaseMock {
    public void updateUserProfile(String userId, long count, long sum) {
        System.out.println("Updated profile " + userId + ", current count = " + count + ", current sum = " + sum);
    }
}
```
4. Create the input topic:
```bash
$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --topic purchases
Created topic purchases.
$ bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic purchases
>user1 100
>user2 30
>user3 1000
>user2 500
>user3 1
>user3 2
>user3 3
>user3 4
```
5. Run the application:
```bash
$ mvn clean package
...
$ mvn exec:java -Dexec.mainClass=myapps.MyApp
...
Updated profile user1, current count = 1, current sum = 100
Updated profile user2, current count = 1, current sum = 30
Updated profile user3, current count = 1, current sum = 1000
Updated profile user2, current count = 2, current sum = 530
Updated profile user3, current count = 2, current sum = 1001
Updated profile user3, current count = 3, current sum = 1003
Updated profile user3, current count = 4, current sum = 1006
Updated profile user3, current count = 5, current sum = 1010
```

6. Restart the application and send some more messages to verify that the stores are persistent.

7. Assume that the database can perform efficient batch updates. Update DatabaseMock.java:
```java
package myapps;

import java.util.List;

public class DatabaseMock {
    public void updateUserProfile(String userId, long count, long sum) {
        System.out.println("Updated profile " + userId + ", current count = " + count + ", current sum = " + sum);
    }

    public void batchUpdate(List<UserProfile> profiles) {
        for (UserProfile userProfile : profiles) {
            System.out.println("Fast update of " + userProfile.userId + " count = "
                    + userProfile.count + " sum = " + userProfile.sum);
        }
        System.out.println("updated " + profiles.size() + " profiles");
    }

    public static class UserProfile {
        private final String userId;
        private final long count;
        private final long sum;

        public UserProfile(String userId, long count, long sum) {
            this.userId = userId;
            this.count = count;
            this.sum = sum;
        }
    }
}
```
8. Modify PurchaseProcessor.java to periodically flush profiles to the database:
```java
package myapps;


import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.processor.PunctuationType;
import org.apache.kafka.streams.processor.api.Processor;
import org.apache.kafka.streams.processor.api.ProcessorContext;
import org.apache.kafka.streams.processor.api.Record;
import org.apache.kafka.streams.state.KeyValueIterator;
import org.apache.kafka.streams.state.KeyValueStore;


public class PurchaseProcessor implements Processor<String, String, String, String> {
    private KeyValueStore<String, Long> countStore;
    private KeyValueStore<String, Long> sumStore;
    private DatabaseMock database;

    @Override
    public void init(ProcessorContext<String, String> context) {
        countStore = context.getStateStore("purchases-count");
        sumStore = context.getStateStore("purchases-sum");
        database = new DatabaseMock();
        context.schedule(Duration.ofSeconds(10), PunctuationType.WALL_CLOCK_TIME, timestamp -> {
            List<DatabaseMock.UserProfile> profiles = new ArrayList<>();
            try (final KeyValueIterator<String, Long> iter = countStore.all()) {
                while (iter.hasNext()) {
                    final KeyValue<String, Long> entry = iter.next();
                    String userId = entry.key;
                    Long count = entry.value;
                    Long sum = sumStore.get(userId);
                    profiles.add(new DatabaseMock.UserProfile(userId, count, sum));
                }
            }
            database.batchUpdate(profiles);
        });
    }

    @Override
    public void process(Record<String, String> record) {
        String[] splitMessage = record.value().split("\\W+");
        String userId = splitMessage[0];
        int purchaseValue = Integer.parseInt(splitMessage[1]);

        Long oldCount = countStore.get(userId);
        long newCount = oldCount == null ? 1 : oldCount + 1;
        countStore.put(userId, newCount);

        Long oldSum = sumStore.get(userId);
        long newSum = oldSum == null ? purchaseValue : oldSum + purchaseValue;
        sumStore.put(userId, newSum);
    }
}
```

9. Compile and run the application again.

## 5. Read more about Kafka Streams
1. *[Kafka Streams core concepts](https://kafka.apache.org/33/documentation/streams/core-concepts)*
2. *[Kafka Streams developer guide](https://kafka.apache.org/33/documentation/streams/developer-guide/)*
3. *[More Kafka Streams examples](https://docs.confluent.io/platform/current/streams/code-examples.html#java)*
