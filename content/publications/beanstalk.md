---
title: Unveiling Heisenbugs with Diversified Execution
order: 20
authors: [Arjun Ramesh, Tianshu Huang, Jaspreet Riar, Ben L. Titzer, Anthony Rowe]
figure: { src: /assets/pubs/Beanstalk.svg, alt: "Heatmaps of bug detection probability across different devices and amounts of debugging instrumentation, for ordinary bugs versus Heisenbugs" }
links:
  - { label: OOPSLA 2025, icon: acm, url: "https://dl.acm.org/doi/epdf/10.1145/3720428" }
  - { label: Data Artifact, icon: github, url: "https://doi.org/10.5281/zenodo.14933663" }
---

The detection of quirky Heisenbugs are influenced by numerous factors including (but not limited to) hardware platforms
and, strangely, the extent of instrumentation used by debuggers themselves.
We propose a debugging methodology that harnesses diversity across platforms
and the debugger's instrumentation to enable low-overhead debugging at scale.
Skim our paper for a characterization of over 100 numerous funky bug behaviors!
