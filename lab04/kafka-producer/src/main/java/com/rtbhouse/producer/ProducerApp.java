package com.rtbhouse.producer;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

import org.apache.commons.lang3.RandomStringUtils;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.apache.kafka.common.serialization.StringSerializer;
import org.jeasy.random.EasyRandom;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.FieldNamingPolicy;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class ProducerApp {

    private static final Logger logger = LoggerFactory.getLogger(ProducerApp.class);

    private static final String TOPIC = "my_third_topic";
    public static final int NUM_THREADS = 20;
    public static final long MSGS_PER_THREAD = 20000;

    public static final int TERMINATION_TIMEOUT_SEC = 300;

    private static final Map<String, Object> kafkaProperties = new HashMap<>();

    static {
        kafkaProperties.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        kafkaProperties.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        kafkaProperties.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
    }

    private static final Gson GSON = new GsonBuilder().setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES).create();

    public static void main(String[] args) throws InterruptedException {
        try (Producer<String, String> producer = new KafkaProducer<>(kafkaProperties)) {
            ExecutorService fixedThreadPool = Executors.newFixedThreadPool(NUM_THREADS);

            IntStream.range(0, NUM_THREADS).forEach(i -> fixedThreadPool.submit(() -> {
                EasyRandom generator = new EasyRandom();
                List<Future<RecordMetadata>> sendFutures = new LinkedList<>();
                for (long j = 0; j < MSGS_PER_THREAD; j++) {
                    sendFutures.add(producer.send(new ProducerRecord<>(TOPIC, RandomStringUtils.randomAlphabetic(20), GSON.toJson(generator.nextObject(Data.class))),
                            (RecordMetadata metadata, Exception exception) -> {
                                if (exception != null) {
                                    logger.warn("send() failed with exception:", exception);
                                }
                            }));

                    sendFutures.removeIf(Future::isDone);
                }

                while (!sendFutures.isEmpty()) {
                    sendFutures.removeIf(Future::isDone);
                }
            }));

            fixedThreadPool.shutdown();
            if (!fixedThreadPool.awaitTermination(TERMINATION_TIMEOUT_SEC, TimeUnit.SECONDS)) {
                logger.warn("Threads didn't terminate before timeout!");
            }
        }
    }
}
