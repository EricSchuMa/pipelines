import os
import requests
from typing import Literal, List, Optional

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        # Add your custom parameters here
        JUSTEMENT_API_KEY: str = ""
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline
            self.base_url = "https://justement.ch/api/v1/gpt"
            self.headers = {
                "Authorization": f"Bearer {self.pipeline.valves.JUSTEMENT_API_KEY}"
            }

        def search_decisions(self, query: str, page: int = 1) -> List[dict]:
            """
            Search for Swiss federal court decisions based on a query.

            :param query: Search hits have to include ALL keywords.
            :param page: Result page number, 10 results per page.
            :return: List of search results with highlighted text snippets.
            """
            params = {"query": query, "page": page}
            response = requests.get(f"{self.base_url}/search", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        def count_decisions(self, query: str) -> int:
            """
            Count the number of search results for a query.

            :param query: Search hits have to include ALL keywords.
            :return: Number of search results for the query.
            """
            params = {"query": query}
            response = requests.get(f"{self.base_url}/count", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

        def retrieve_document(self, docId: str) -> dict:
            """
            Retrieve the full text of a decision.

            :param docId: The docId of the document to retrieve.
            :return: The full text of the document.
            """
            params = {"docId": docId}
            response = requests.get(f"{self.base_url}/document", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    def __init__(self):
        super().__init__()
        self.name = "Justement Tools Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
                "JUSTEMENT_API_KEY": os.getenv("JUSTEMENT_API_KEY", ""),
            },
        )
        self.tools = self.Tools(self)

