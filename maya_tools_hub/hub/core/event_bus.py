"""EventBus - publish/subscribe event system."""
from hub.core.logging import get_logger

logger = get_logger(__name__)


class EventBus:
    """Publish/subscribe event bus for component communication.
    
    Components can subscribe to topics and receive notifications when events are published.
    """
    
    def __init__(self):
        """Initialize empty event registry."""
        self._subscribers = {}  # topic -> list of callbacks
    
    def subscribe(self, topic, callback):
        """Subscribe to a topic.
        
        Args:
            topic: Event topic (string)
            callback: Callable that accepts payload as argument
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)
        logger.debug(f"Subscribed to topic: {topic}")
    
    def publish(self, topic, payload):
        """Publish an event to a topic.
        
        Args:
            topic: Event topic
            payload: Event data (any type, typically dict)
        """
        logger.debug(f"Publishing event: {topic}")
        if topic in self._subscribers:
            subscriber_count = len(self._subscribers[topic])
            logger.debug(f"Event '{topic}' has {subscriber_count} subscriber(s)")
            for callback in self._subscribers[topic]:
                try:
                    callback(payload)
                except Exception as e:
                    # Log error but don't break other subscribers
                    logger.error(f"Error in callback for topic '{topic}': {e}", exc_info=True)

