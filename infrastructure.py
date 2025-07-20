from datetime import datetime
from uuid import UUID

from redis import Redis


class Storage:
    """
    Infrastructure class taking care of key-value storage.
    """

    def __init__(self, client: Redis):
        self._client = client
        self._client.set_response_callback("GET", float)

    def save_timestamp(self, key: UUID):
        self._client.set(str(key), datetime.now().timestamp())

    def get_timestamp(self, key: UUID) -> float | None:
        return self._client.get(str(key))

    def end_token(self, key: UUID):
        if (start := self.get_timestamp(key)) is not None:
            duration: float = datetime.now().timestamp() - start

            # TODO set weighted mean value of request duration and set it in redis

        self._client.delete(str(key))

    def get_query_mean_time(self) -> float:
        if (mean_time := self._client.get("mean_time")) is None:
            mean_time = 10.0  # default value for the first call

        return mean_time
