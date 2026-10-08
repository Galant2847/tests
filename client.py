import logging
import time
from typing import Any, Optional

import requests

logger = logging.getLogger("met_api")

BASE_URL = "https://collectionapi.metmuseum.org/public/collection"
TIMEOUT = 30
MAX_BODY_IN_LOG = 500


class MetClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def _get(
        self, path: str, params: Optional[dict] = None
    ) -> requests.Response:
        url = f"{BASE_URL}/{path}"

        logger.info("REQUEST GET %s params=%s", url, params)
        started = time.perf_counter()
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
        except requests.RequestException as error:
            logger.error("ERROR %s: %s", type(error).__name__, error)
            raise

        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "RESPONSE %s (%.0f ms, %d bytes)",
            response.status_code, elapsed_ms, len(response.content),
        )
        logger.debug("BODY %s", response.text[:MAX_BODY_IN_LOG])
        if response.status_code >= 400:
            logger.warning(
                "HTTP %s: %s",
                response.status_code, response.text[:MAX_BODY_IN_LOG],
            )
        return response

    def get_object(self, object_id: Any) -> requests.Response:
        return self._get(f"v1/objects/{object_id}")

    def get_departments(self) -> requests.Response:
        return self._get("v1/departments")

    def search(
        self, q: Optional[str] = None, **filters: Any
    ) -> requests.Response:
        params: dict = {}
        if q is not None:
            params["q"] = q
        for key, value in filters.items():
            if isinstance(value, bool):
                value = str(value).lower()
            params[key] = value
        return self._get("v1.1/search", params)