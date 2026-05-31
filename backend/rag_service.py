def retrieve_cases(query: str, top_k: int = 5, filters: dict | None = None):
    return [
        {
            "title": "Example Case v. State",
            "court": "Example Court",
            "date": "2020-01-01",
            "snippet": "This retrieved case is a placeholder showing where legal case text will appear.",
            "score": 0.91,
            "source_url": "https://case.law/"
        }
    ]


def generate_answer(query: str, retrieved_chunks: list):
    answer = (
        f"You asked: '{query}'. Based on the retrieved legal references, "
        "this prototype would explain whether the cases support or contradict the claim."
    )

    reasoning_path = [
        "User submits a legal question or claim.",
        "The API sends the query to the retriever.",
        "The retriever returns the top-k most relevant legal case chunks.",
        "The system generates a user-friendly answer with references."
    ]

    return answer, reasoning_path