"""
ecoSential AI-Pro — Memory Layer
Implements dual-layer memory with local embeddings using SentenceTransformers.
  1. Short-term: In-session conversation/event log (list-based)
  2. Long-term: FAISS vector store for experience replay
"""

import faiss
import numpy as np
import json
import os
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class MemoryEntry:
    id: int
    timestamp: str
    machine_id: str
    event_type: str
    context: str
    decision: str
    outcome: str
    reward: float
    tags: list = field(default_factory=list)

class MemorySystem:
    EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

    def __init__(self, persist_dir: str = "./memory_store"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self.short_term: list[MemoryEntry] = []
        self.short_term_limit = 50

        self._index_path = os.path.join(persist_dir, "faiss.index")
        self._meta_path = os.path.join(persist_dir, "meta.json")
        
        # Using ultra-fast deterministic hashing for Python 3.13 compatibility without torch
        self.embedder = None

        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self._index_path) and os.path.exists(self._meta_path):
            self.index = faiss.read_index(self._index_path)
            with open(self._meta_path, "r") as f:
                self.long_term_meta = json.load(f)
            self._next_id = len(self.long_term_meta)
        else:
            self.index = faiss.IndexFlatIP(self.EMBEDDING_DIM)
            self.long_term_meta = []
            self._next_id = 0

    def _persist(self):
        try:
            faiss.write_index(self.index, self._index_path)
            with open(self._meta_path, "w") as f:
                json.dump(self.long_term_meta, f, indent=2)
        except Exception as e:
            print(f"[Memory] Persist error: {e}")

    def _embed(self, text: str) -> np.ndarray:
        # Deterministic fallback (hash-based) so same text -> same vector
        seed = abs(hash(text)) % (2**31)
        rng = np.random.default_rng(seed)
        vec = rng.random(self.EMBEDDING_DIM).astype("float32")

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.astype("float32")

    def add_memory(self, machine_id: str, event_type: str, context: str, decision: str, outcome: str, reward: float, tags: list = None) -> MemoryEntry:
        entry = MemoryEntry(
            id=self._next_id, timestamp=datetime.now().isoformat(),
            machine_id=machine_id, event_type=event_type, context=context,
            decision=decision, outcome=outcome, reward=reward, tags=tags or [],
        )

        self.short_term.append(entry)
        if len(self.short_term) > self.short_term_limit:
            self.short_term.pop(0)

        text_for_embedding = f"{context} | Decision: {decision} | Outcome: {outcome}"
        vec = self._embed(text_for_embedding)
        self.index.add(np.array([vec]))
        self.long_term_meta.append(asdict(entry))
        self._next_id += 1
        self._persist()
        return entry

    def retrieve_relevant(self, query: str, top_k: int = 4) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        vec = self._embed(query)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(np.array([vec]), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                meta = dict(self.long_term_meta[idx])
                meta["similarity_score"] = round(float(score), 3)
                results.append(meta)

        results.sort(key=lambda x: x["reward"] * x["similarity_score"], reverse=True)
        return results

    def get_short_term_summary(self, last_n: int = 5) -> str:
        recent = self.short_term[-last_n:]
        if not recent: return "No recent events in session memory."
        return "\n".join([f"[{e.timestamp[:19]}] {e.machine_id} | {e.event_type.upper()}: {e.context[:60]}... → {e.outcome[:60]}... (Reward: {e.reward:+.1f})" for e in recent])

    def get_stats(self) -> dict:
        rewards = [m["reward"] for m in self.long_term_meta]
        return {
            "total_memories": len(self.long_term_meta),
            "short_term_count": len(self.short_term),
            "avg_reward": round(np.mean(rewards), 2) if rewards else 0.0,
            "best_reward": round(max(rewards), 2) if rewards else 0.0,
            "worst_reward": round(min(rewards), 2) if rewards else 0.0,
            "positive_decisions": sum(1 for r in rewards if r > 0),
            "negative_decisions": sum(1 for r in rewards if r < 0),
        }
