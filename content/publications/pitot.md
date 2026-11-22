---
title: Interference-aware Edge Runtime Prediction with Conformal Matrix Completion
order: 40
authors: [Tianshu Huang, Arjun Ramesh, Emily Ruppel, Nuno Pereira, Anthony Rowe, Carlee Joe-Wong]
figure: { src: /assets/pubs/Pitot.svg, alt: "Model overview: workload and platform features feed MLPs that complete a runtime matrix, with extra terms for interfering workloads" }
links:
  - { label: MLSys 2025, icon: acm, url: "https://proceedings.mlsys.org/paper_files/paper/2025/hash/40b8fb4f90004405e14b1ede6ab42373-Abstract-Conference.html" }
  - { label: Data Artifact, icon: github, url: "https://zenodo.org/records/14977004" }
---

Performance prediction in heterogeneous edge computing systems is critical for effective resource allocation and cost optimization.
We formulate this problem as matrix completion, which can be extended to handle complex, edge-specific concerns
such as interference and uncertainty quantification accurately.
