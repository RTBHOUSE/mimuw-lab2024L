# Stream processing part 1 - Apache Kafka

In this laboratory you will learn how to run Kafka and perform basic operations. If you are stuck, read the solution.

## 1. Kafka installation

1. Log into one of your machines, preferably the first available one:

```bash
ssh <username>@<username>vm101.rtb-lab.pl
```

2. Install Ansible and sshpass:

```bash
sudo apt -y install ansible sshpass
```

3. Clone the laboratory repository if not present:

```bash
git clone https://github.com/RTBHOUSE/mimuw-lab2024L.git
```

or update the repository if already present:
```bash
git pull https://github.com/RTBHOUSE/mimuw-lab2024L.git
```

4. Edit the `mimuw-lab2024L/lab04/kafka/hosts` file to specify your selected Kafka broker nodes.

5. Run the Kafka installation playbook:

```bash
cd mimuw-lab2024L/lab04/kafka
ansible-playbook --extra-vars "ansible_user=<user> ansible_password=<password> ansible_ssh_extra_args='-o StrictHostKeyChecking=no'" -i hosts kafka.yaml
```

In case of problems with the playbook, upgrade to the latest version of Ansible:
```bash
sudo add-apt-repository ppa:ansible/ansible
sudo apt update
sudo apt upgrade ansible
```

6. Verify that all nodes are available on the cluster:

```bash
/opt/kafka/bin/zookeeper-shell.sh localhost:2181 ls /brokers/ids
```

## 2. Creating topics

Log in to the one of the Kafka machines.

Run `/opt/kafka/bin/kafka-topics.sh` and read the output. Focus on the following options:
`--bootstrap-server, --config, --create, --delete, --describe, --list, --partitions,
--topic`. Use this program to create topic `my_first_topic` with 10 partitions. Hint:
bootstrap-server expected format is `kafka_address:kafka_port`, and default Kafka port
is 9092.

<details>
<summary>Solution</summary>
<br>

```bash
$ /opt/kafka/bin/kafka-topics.sh --create --topic my_first_topic --partitions 10 --bootstrap-server localhost:9092
```
</details>

Use the same program to list all topics. Make sure your attempt to create a topic
was successful. Then use `--describe` option to get more details about the topic.

<details>
<summary>Solution</summary>
<br>

```bash
$ /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
my_first_topic
$ /opt/kafka/bin/kafka-topics.sh --describe --topic my_first_topic --bootstrap-server localhost:9092
Topic: my_first_topic	TopicId: VCMVMJJtTviWJo2nQDeBPQ	PartitionCount: 10	ReplicationFactor: 1	Configs: segment.bytes=1073741824
	Topic: my_first_topic	Partition: 0	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 1	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 2	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 3	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 4	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 5	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 6	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 7	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 8	Leader: 0	Replicas: 0	Isr: 0
	Topic: my_first_topic	Partition: 9	Leader: 0	Replicas: 0	Isr: 0
```
</details>

## 3. Sending and receiving messages

Run `/opt/kafka/bin/kafka-console-producer.sh` and read the output. For now focus on two options:
`--bootstrap-server, --topic`. Use this program to send several messages to `my_first_topic`
(each line you enter will be treated as a separate message).

<details>
<summary>Solution</summary>
<br>

```bash
$ /opt/kafka/bin/kafka-console-producer.sh --topic my_first_topic --bootstrap-server localhost:9092
>This is my first message
>This is my second message
```
</details>

You can stop the producer with Ctrl-C, but keep it running, as it will be needed for next tasks.

Open two more terminals and use `/opt/kafka/bin/kafka-console-consumer.sh` in each to read messages
from `my_first_topic`.

<details>
<summary>Solution</summary>
<br>

```bash
# in second terminal:
$ /opt/kafka/bin/kafka-console-consumer.sh --topic my_first_topic --bootstrap-server localhost:9092
# in third terminal
$ /opt/kafka/bin/kafka-console-consumer.sh --topic my_first_topic --bootstrap-server localhost:9092
```

Note that consumers didn't write the first two messages. By default, they will consume only
new messages, so messages produced while a consumer is down will be skipped. To read all the
messages, start consumers with `--from-beginning` option added.

```bash
# in fourth terminal:
$ /opt/kafka/bin/kafka-console-consumer.sh --topic my_first_topic --bootstrap-server localhost:9092 --from-beginning
This is my first message
This is my second message
```

New messages should be received by both consumers.
```bash
# send more messages in first terminal (producer):
>This is my third message
>This is my fourth message
# receive in second terminal (consumer 1):
This is my third message
This is my fourth message
# receive in third terminal (consumer 2):
This is my third message
This is my fourth message
```
</details>

## 4. Assigning consumer groups

Stop the consumers with Ctrl-C, then start them again, but this time with a consumer group
assigned. Send ten different messages and observe output from the consumers.

<details>
<summary>Solution</summary>
<br>

To start the consumers run:
```bash
# in second terminal:
$ /opt/kafka/bin/kafka-console-consumer.sh --topic my_first_topic --bootstrap-server localhost:9092 --group my_group
# in third terminal:
$ /opt/kafka/bin/kafka-console-consumer.sh --topic my_first_topic --bootstrap-server localhost:9092 --group my_group
```

Now run the producer 20 times:
```bash
for i in $(seq 1 20); do echo $RANDOM | md5sum | head -c 20 | /opt/kafka/bin/kafka-console-producer.sh --topic my_first_topic --bootstrap-server localhost:9092; done
```

Each message should be read by just one consumer, and messages should be distributed
equally between the consumers.

```bash
# second terminal (consumer 1):
cc2a408385e4289bca6f
44194499adc4d2b753ee
d2df74f418ff67255769
2ce7b6fbc1467ea49880
a5c5422437556c7d5139
0ebd30ec7ae6573785db
10bd45485b105d5ce014
22dfdd4c783accf87f4c
b481526567842be26abe
5a3cef669c85353cdc72
# third terminal (consumer 2):
ac0098a40d8291c80e3a
5434cadd4a0ded769b18
26054fa1adb51b3dc60b
51d1e4ec2826de71289b
796bd28a1a50d8e93466
43d7143c04803f8a0f1e
62fbfd9d0693028d6274
92be124931817a166322
5bac1ea46467fd42b9c7
d2a8ac172cefbe49cbd2
```
</details>

## 5. Checking offsets and lag
Stop all consumers with Ctrl-C. Use `/opt/kafka/bin/kafka-consumer-groups.sh` script to get the details
of your consumer group.

<details>
<summary>Solution</summary>
<br>

```bash
$ /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my_group --describe

Consumer group 'my_group' has no active members.

GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID     HOST            CLIENT-ID
my_group        my_first_topic  1          0               0               0               -               -               -
my_group        my_first_topic  9          3               3               0               -               -               -
my_group        my_first_topic  2          0               0               0               -               -               -
my_group        my_first_topic  3          0               0               0               -               -               -
my_group        my_first_topic  0          2               2               0               -               -               -
my_group        my_first_topic  8          0               0               0               -               -               -
my_group        my_first_topic  5          0               0               0               -               -               -
my_group        my_first_topic  7          4               4               0               -               -               -
my_group        my_first_topic  6          4               4               0               -               -               -
my_group        my_first_topic  4          1               1               0               -               -               -

```
</details>

Now start two consumers within group `my_group`, and run the script again.

<details>
<summary>Solution</summary>
<br>

```bash
$ /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my_group --describe
GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                           HOST            CLIENT-ID
my_group        my_first_topic  9          3               3               0               console-consumer-70f5666e-4146-4e0c-97d4-67777dc7eebb /127.0.0.1      console-consumer
my_group        my_first_topic  6          4               4               0               console-consumer-70f5666e-4146-4e0c-97d4-67777dc7eebb /127.0.0.1      console-consumer
my_group        my_first_topic  8          0               0               0               console-consumer-70f5666e-4146-4e0c-97d4-67777dc7eebb /127.0.0.1      console-consumer
my_group        my_first_topic  5          0               0               0               console-consumer-70f5666e-4146-4e0c-97d4-67777dc7eebb /127.0.0.1      console-consumer
my_group        my_first_topic  7          4               4               0               console-consumer-70f5666e-4146-4e0c-97d4-67777dc7eebb /127.0.0.1      console-consumer
my_group        my_first_topic  1          0               0               0               console-consumer-67bab267-9f45-412f-ba32-0085d9076214 /127.0.0.1      console-consumer
my_group        my_first_topic  2          0               0               0               console-consumer-67bab267-9f45-412f-ba32-0085d9076214 /127.0.0.1      console-consumer
my_group        my_first_topic  3          0               0               0               console-consumer-67bab267-9f45-412f-ba32-0085d9076214 /127.0.0.1      console-consumer
my_group        my_first_topic  0          2               2               0               console-consumer-67bab267-9f45-412f-ba32-0085d9076214 /127.0.0.1      console-consumer
my_group        my_first_topic  4          1               1               0               console-consumer-67bab267-9f45-412f-ba32-0085d9076214 /127.0.0.1      console-consumer

```
Note that now every partition belongs to a consumer. There are two consumers, each has 5
partitions assigned.
</details>

Stop both consumers, then send several messages to the topic, and run the script once more.

<details>
<summary>Solution</summary>
<br>

```bash
$ /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my_group --describe

Consumer group 'my_group' has no active members.

GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID     HOST            CLIENT-ID
my_group        my_first_topic  1          0               4               4               -               -               -
my_group        my_first_topic  9          3               3               0               -               -               -
my_group        my_first_topic  2          0               0               0               -               -               -
my_group        my_first_topic  3          0               0               0               -               -               -
my_group        my_first_topic  0          2               2               0               -               -               -
my_group        my_first_topic  8          0               0               0               -               -               -
my_group        my_first_topic  5          0               2               2               -               -               -
my_group        my_first_topic  7          4               4               0               -               -               -
my_group        my_first_topic  6          4               4               0               -               -               -
my_group        my_first_topic  4          1               2               1               -               -               -

```

The group has no active members, so new messages remain unconsumed. Number of unconsumed messages
is shown in the column LAG.
</details>

Now restart one fo the consumers. It should consume instantly the lagged messages.

## 6. Data retention

Run the console consumer (without specifying consumer group) and with the `--from-beginning` flag.
The consumer should print all the messages that have been produced so far:

```bash
$ /opt/kafka/bin/kafka-console-consumer.sh --topic my_first_topic --bootstrap-server localhost:9092 --from-beginning
```

Now let's configure the data retention period for the messages in `my_first_topic`. Data retention period forces the broker to purge the messages
that are older than the specified threshold.

To configure the period for 1 minute, execute the following command:
```bash
$ /opt/kafka/bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_first_topic --alter --add-config retention.ms=60000
```

Now rerun the above console consumer command several times. After a while no messages should be available for immediate consumption.


## 7. Data compaction

Compaction strives to achieve finer-grained per record retention by gradually removing messages
that have been "updated" by a later message with the same key.

Create `my_second_topic`, and then add with data compaction related configuration parameters:

```bash
$ /opt/kafka/bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_second_topic --alter --add-config cleanup.policy=compact
$ /opt/kafka/bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_second_topic --alter --add-config delete.retention.ms=1000
$ /opt/kafka/bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_second_topic --alter --add-config segment.ms=1000
$ /opt/kafka/bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_second_topic --alter --add-config min.cleanable.dirty.ratio=0.01
$ /opt/kafka/bin/kafka-configs.sh --bootstrap-server localhost:9092 --entity-type topics --entity-name my_second_topic --alter --add-config min.compaction.lag.ms=500
```

Now produce several messages with the same key:
```bash
$ for i in $(seq 1 20); do echo "key1:value$i" | /opt/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic my_second_topic --property "parse.key=true" --property "key.separator=:"; done
```

Consume the messages with corresponding keys:
```bash
$ /opt/kafka/bin/kafka-console-consumer.sh --topic my_second_topic --bootstrap-server localhost:9092 --property print.key=true --from-beginning
```

Observe the number of messages available for consumption.

<details>
<summary>Warning!</summary>
Keep in mind that the above compaction configuration is only appropriate for the demonstration purposes, because it is a bit too IO aggresive.
For normal production scenarios the `cleanup.policy=compact` is sufficient for majority of cases.
</details>

## 8. Creating simple data pipelines

Create two topics: `transactions` and `balance`, each with 10 partitions. Read the introduction
to kafka-python *[here](https://kafka-python.readthedocs.io/en/master/)*. Write two simple
programs in Python. The first program should send to each partition of `transactions` a random
integer between -10 and 10 once every second. We will assume that positive numbers represent
cash deposits and negative numbers represent cash withdrawals. We will also assume that each
partition represents a separate bank account. The other program should read `transactions` and
send the current balance of each account to `balance`.

<details>
<summary>Solution</summary>
<br>

transaction_generator.py:
```python
import random
import time

from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')
while True:
    for account_number in range(0, 10):
        transaction_value = random.randrange(-10, 11)
        producer.send('transactions', value=b'%d' % transaction_value, partition=account_number)
        print(f'new transaction: value={transaction_value} account_number={account_number}')
    time.sleep(1)
```

balance_calculator.py:
```python
from kafka import KafkaConsumer, KafkaProducer

balance = {}
consumer = KafkaConsumer('transactions', bootstrap_servers='localhost:9092')
producer = KafkaProducer(bootstrap_servers='localhost:9092')
for msg in consumer:
    account_number = msg.partition
    if account_number in balance:
        balance[account_number] += int(msg.value)
    else:
        balance[account_number] = int(msg.value)
    producer.send('balance', b'%d' % balance[account_number], partition=account_number)
    print(f'current balance for account {account_number} is {balance[account_number]}')
```
</details>


## 9. Ensuring exactly-once delivery semantics (optional)

What will happen when you restart your app? How can you improve it to guarantee
that balance has the same number of messages as transactions and the n-th message in balance
represents the exact balance after n transactions, even with processing app occasionally
failing? Hint: you may need to use *[Producer API](https://kafka.apache.org/31/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html)*
and *[Consumer API](https://kafka.apache.org/31/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)* for this task.


## 10. Data compression (optional)

Sometimes structured messages can consume lot of storage space within a Kafka cluster. To mitigate this problem we can use either producer or broker side compression.

Let's test how producer-side compression works in Kafka with the custom `kafka-producer` application, which produces random JSON messages to `my_third_topic` topic.

1. Install maven:
```bash
$ sudo apt install maven
```

2. Build the `kafka-producer` application:
```bash
$ cd mimuw-lab2024L/lab04/kafka-producer
$ mvn clean install
```

3. Create a topic:
```bash
$ /opt/kafka/bin/kafka-topics.sh --create --topic my_third_topic --partitions 10 --bootstrap-server localhost:9092
```

4. Run the application:
```bash
$ java -jar mimuw-lab2024L/lab04/kafka-producer/target/kafka-producer-1.0-SNAPSHOT.jar
```

5. Check how many messages have been produced:
```bash
$ /opt/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic my_third_topic
```

6. Check the size of the kafka-logs directories for `my_third_topic` partitions:
```bash
$ du -hc /opt/kafka/kafka-logs/my_third_topic-*
```

7. Delete the topic:
```bash
$ /opt/kafka/bin/kafka-topics.sh --delete --topic my_third_topic --bootstrap-server localhost:9092
```

Now introduce producer-side compression in the `kafka-producer` application and check how it reduces the `kafka-logs` size. Also measure how it affects the application performance.

<details>
<summary>Hints</summary>
<br>

1. Edit the parameters in `com/rtbhouse/producer/ProducerApp.java`, add `ProducerConfig.COMPRESSION_TYPE_CONFIG` and `ProducerConfig.LINGER_MS_CONFIG` (with value equal to '5')
2. Valid compression types are `gzip`, `lz4`, `snappy`, and `zstd`. Focus on `snappy` and `zstd`.
3. Remember to rebuild the `kafka-producer` application after each change.
4. Recreate the `my_third_topic` before every new run of the application (delete & create).
</details>

## 11. Ensuring high availability (optional)
Create a cluster of 3 brokers. Add a topic with replication factor 2.

```bash
$ /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic my_third_topic --replication-factor 2 --partitions 2
```

Check what happens when you send a message with one of the brokers down. What if two brokers are down?
To bring down a node execute the following command on one of the Kafka hosts:
```bash
$ sudo systemctl stop kafka
```

Read about availability and durability guarantees *[here](https://kafka.apache.org/documentation/#design_ha)*.
Test different values of `acks`.
