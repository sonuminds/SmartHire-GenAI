import pickle

import faiss
import numpy as np

from src.config import JOBS_INDEX_PATH, JOBS_METADATA_PATH, client
from src.search.embed import get_embedding


faiss_index = faiss.read_index(str(JOBS_INDEX_PATH))

with open(JOBS_METADATA_PATH, "rb") as file:
    jobs_df = pickle.load(file)


def search_jobs(resume_text, top_k=5):
    """
    Return the top matching jobs for the given resume text.
    """

    resume_vector = get_embedding(
        client,
        resume_text
    )

    resume_vector = np.array(
        [resume_vector],
        dtype="float32"
    )

    distances, indices = faiss_index.search(
        resume_vector,
        top_k
    )

    matched_jobs = jobs_df.iloc[indices[0]].copy()
    matched_jobs["distance"] = distances[0]

    return matched_jobs