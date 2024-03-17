import asyncio
import functools
import json
import logging
import time
import traceback
from asyncio import Event, Queue

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.core import config
logger = logging.getLogger(__name__)


def print_traceback(_, error):
    error_type = type(error)
    logger.error(
        {
            "error_type": error_type.__name__,
            "error": error,
        }
    )
    tb_str = traceback.format_exc()
    logger.error(f"{error}, \n{tb_str}")


def retry(max_retries=3, retry_delay=5, on_retry=None, on_failure=None):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            retry_count = 0

            while retry_count < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if on_retry:
                        on_retry(retry_count, e)

                    retry_count += 1
                    logger.error(f"Error: {e}")
                    logger.info(f"Retrying ({retry_count}/{max_retries})...")
                    await asyncio.sleep(retry_delay)  # Add a delay before retrying

            if on_failure:
                on_failure(retry_count)

            raise RuntimeError(f"Failed after {max_retries} retries")

        return wrapped

    return wrapper


def log_speed(
    counter: int, start_time: float, _queue: Queue, topic: str, interval: int = 15
) -> tuple[float, int]:
    # Calculate the time elapsed since the function started
    delta_time = time.time() - start_time

    # Check if the specified interval has not elapsed yet
    if delta_time < interval:
        # Return the original start time and the current counter value
        return start_time, counter

    # Calculate the processing speed (messages per second)
    speed = counter / delta_time

    # Log the processing speed and relevant information
    log_message = (
        f"{topic=}, qsize={_queue.qsize()}, "
        f"processed {counter} in {delta_time:.2f} seconds, {speed:.2f} msg/sec"
    )
    logger.info(log_message)

    # Return the current time and reset the counter to zero
    return time.time(), 0


# async def kafka_consumer_safe(topic: str, group: str, max_retries=3, retry_delay=30):
#     retry_count = 0

#     while retry_count < max_retries:
#         try:
#             return await kafka_consumer(topic, group)
#         except Exception as e:
#             retry_count += 1
#             logger.error(f"Error connecting to Kafka: {e}")
#             logger.info(f"Retrying Kafka connection ({retry_count}/{max_retries})...")
#             await asyncio.sleep(retry_delay)  # Add a delay before retrying

#     raise RuntimeError("Failed to connect to Kafka after multiple retries")


@retry(max_retries=3, retry_delay=5, on_failure=print_traceback)
async def kafka_consumer(topic: str, group: str):
    logger.info(f"Starting consumer, {topic=}, {group=}, {config.KAFKA_HOST=}")

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=[config.KAFKA_HOST],
        group_id=group,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="earliest",
    )
    await consumer.start()
    logger.info("Started")
    return consumer


# async def kafka_producer_safe(max_retries=3, retry_delay=30):
#     retry_count = 0

#     while retry_count < max_retries:
#         try:
#             return await kafka_producer()
#         except Exception as e:
#             retry_count += 1
#             logger.error(f"Error connecting to Kafka: {e}")
#             logger.info(f"Retrying Kafka connection ({retry_count}/{max_retries})...")
#             await asyncio.sleep(retry_delay)  # Add a delay before retrying

#     raise RuntimeError("Failed to connect to Kafka after multiple retries")


@retry(max_retries=3, retry_delay=5, on_failure=print_traceback)
async def kafka_producer():
    logger.info("Starting producer")

    producer = AIOKafkaProducer(
        bootstrap_servers=[config.KAFKA_HOST],
        value_serializer=lambda v: json.dumps(v).encode(),
        acks="all",
    )
    await producer.start()
    logger.info("Started")
    return producer


@retry(max_retries=3, retry_delay=5, on_failure=print_traceback)
async def receive_messages(
    consumer: AIOKafkaConsumer,
    receive_queue: Queue,
    shutdown_event: Event,
    batch_size: int = 200,
):
    while not shutdown_event.is_set():
        batch = await consumer.getmany(timeout_ms=1000, max_records=batch_size)
        for tp, messages in batch.items():
            logger.info(f"Partition {tp}: {len(messages)} messages")
            await asyncio.gather(*[receive_queue.put(m.value) for m in messages])
            logger.info("done")
            await consumer.commit()

    logger.info("shutdown")


@retry(max_retries=3, retry_delay=5, on_failure=print_traceback)
async def send_messages(
    topic: str,
    producer: AIOKafkaProducer,
    send_queue: Queue,
    shutdown_event: Event,
):
    start_time = time.time()
    messages_sent = 0

    while not shutdown_event.is_set():
        start_time, messages_sent = log_speed(
            counter=messages_sent,
            start_time=start_time,
            _queue=send_queue,
            topic=topic,
        )
        if send_queue.empty():
            await asyncio.sleep(1)
            continue

        message = await send_queue.get()
        await producer.send(topic, value=message)
        send_queue.task_done()

        messages_sent += 1

    logger.info("shutdown")