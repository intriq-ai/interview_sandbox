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
        """Save beginning of request"""
        self._client.set(str(key), datetime.now().timestamp())

    def get_timestamp(self, key: UUID) -> float | None:
        """Get beginning of request"""
        return self._client.get(str(key))

    def end_token(self, key: UUID):
        """Remove request and and it's duration into mean time"""
        if (start := self.get_timestamp(key)) is not None:
            duration: float = datetime.now().timestamp() - start

            # TODO make it a sliding window in time
            if (request_count := self._client.get("request_count")) is not None:
                request_count = int(request_count)
            else:
                request_count = 0

            mean_time = self._client.get("mean_time") or 0
            # add new duration time into weighted mean
            new_mean_time = (mean_time * request_count + duration) / (request_count + 1)

            self._client.set("mean_time", new_mean_time)
            self._client.set("request_count", request_count + 1)

        self._client.delete(str(key))

    def get_query_mean_time(self) -> float:
        if (mean_time := self._client.get("mean_time")) is None:
            mean_time = 10.0  # default value for the first call

        return mean_time
