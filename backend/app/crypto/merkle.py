import hashlib
from typing import List, Optional

class MerkleTree:
    def __init__(self, leaves: List[str]):
        self.leaves = leaves
        self.tree = self._build_tree(leaves)
        self.root = self.tree[0][0] if self.tree else None

    def _hash_pair(self, a: str, b: str) -> str:
        combined = sorted([a, b])
        return hashlib.sha256((combined[0] + combined[1]).encode()).hexdigest()

    def _build_tree(self, leaves: List[str]) -> List[List[str]]:
        if not leaves:
            return []
        current = leaves[:]
        tree = [current]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_level.append(self._hash_pair(left, right))
            tree.insert(0, next_level)
            current = next_level
        return tree

    def get_proof(self, index: int) -> List[dict]:
        """Get Merkle proof for a leaf at given index."""
        proof = []
        for level in reversed(self.tree[1:]):
            sibling_idx = index + 1 if index % 2 == 0 else index - 1
            if sibling_idx < len(level):
                proof.append({"index": sibling_idx, "hash": level[sibling_idx], "direction": "right" if index % 2 == 0 else "left"})
            index //= 2
        return proof

    def verify_proof(self, leaf_hash: str, index: int, proof: List[dict]) -> bool:
        current = leaf_hash
        for step in proof:
            if step["direction"] == "right":
                current = self._hash_pair(current, step["hash"])
            else:
                current = self._hash_pair(step["hash"], current)
            index //= 2
        return current == self.root
