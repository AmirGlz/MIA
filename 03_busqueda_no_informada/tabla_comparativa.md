| Algoritmo | Status | Path | Depth (roads) | Cost (km) | Expanded (nodes) | Generated (nodes) |
|---|---|---|---|---|---|---|
| **Breadth First** | Success | Zerind -> Arad -> Sibiu -> Rinmicu Vilcea -> Craiova | 4 | 441 | 7 | 17|
| **Uniform Cost** | Success | Zerind -> Arad -> Sibiu -> Rinmicu Vilcea -> Craiova | 4 | 441 | 10 | 26 |
| **Depth First** | Success | Zerind -> Arad -> Sibiu -> Fagaras -> Bucharest -> Pitesti -> Craiova  | 6 | 764 | 7 | 20 |
| **Depth Limited 2** | Cutoff | limit 2 | N/A | N/A | 3 | 8 |
| **Depth Limited 4** | Success | Zerind -> Arad -> Sibiu -> Rinmicu Vilcea -> Craiova | 4 | 441 | 6 | 12 |
| **Iterative Deeping** | Success | Zerind -> Arad -> Sibiu -> Rinmicu Vilcea -> Craiova | 4 | 441 | 16 | 42 |