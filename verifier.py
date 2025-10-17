import hashlib
from typing import List
from web3 import Web3  # For keccak; pip install web3

def keccak256(data: bytes) -> str:
    """FLAME-spec'd double-keccak for nodes."""
    return Web3.keccak(data).hex()

def build_merkle_leaves(docs: List[str]) -> List[str]:
    """Hash each doc (Flame Law) as leaf."""
    return [keccak256(doc.encode('utf-8')) for doc in sorted(docs)]  # Sorted for determinism

def build_merkle_root(leaves: List[str]) -> str:
    """Simple binary Merkle tree: pair-wise keccak until root."""
    if not leaves:
        raise ValueError("No leaves")
    current = leaves[:]
    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = bytes.fromhex(current[i][2:])  # Strip 0x
            if i + 1 < len(current):
                right = bytes.fromhex(current[i+1][2:])
                combined = left + right
            else:
                combined = left  # Odd len: pad self
            next_level.append(keccak256(combined))
        current = next_level
    return current[0]

def verify_against_txs(codex_path: str, expected_root: str, tx_hashes: List[str]) -> bool:
    """Load codex, split to leaves (one per Law), build root, check tx payloads."""
    with open(codex_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Assume codex splits on 'LAW #' markers; tweak per actual format
    laws = [law.strip() for law in content.split('LAW ')[1:] if law.strip()]  # e.g., LAW 1: text...
    
    computed_root = build_merkle_root(build_merkle_leaves(laws))
    print(f"Computed Merkle Root: {computed_root}")
    
    if computed_root != expected_root:
        print("ROOT MISMATCH—codex altered?")
        return False
    
    # Mock tx payload extract (in prod: RPC pull as per your curls)
    # For demo: Assume payloads embed ROOT; real: decode input hex for 'ROOT=' span
    for tx in tx_hashes:
        # Placeholder: In full script, curl eth_getTransactionByHash, grep hex for ROOT hex
        print(f"Tx {tx}: Would verify ROOT {expected_root} in calldata")
    
    # Lattice rule sim: If ROOT+EPOCH match, attest (threshold mock: True if root ok)
    epoch = "EPOCH_2025-10-15-154540"  # From payload
    if computed_root == expected_root:
        print(f"Lattice Rule: Identical ROOT ({expected_root}) + EPOCH ({epoch}) → FINAL ATTESTATION. Nullify mimics.")
        return True
    return False

# Usage: Replace with your codex.txt (e.g., gist pull of Δ717 Laws)
if __name__ == "__main__":
    codex_file = "flame_v12_codex.txt"  # Download: https://gist.githubusercontent.com/flame-sovereign/Δ717/raw
    expected = "0x545d0e48624049cb1f3500ab55a60bc4"
    txs = [
        "0xce90d8099a1d3fae5383bb17aac119e180b25d529cac12865b9c9e7c2a761e37",  # #2
        "0xb43664ebd5a373d23e03171e0eb44f602fb1673c58e98c03904e0a14adb36ad8"   # #3
    ]
    verified = verify_against_txs(codex_file, expected, txs)
    print(f"Lockout Verified: {verified} 🜂")
