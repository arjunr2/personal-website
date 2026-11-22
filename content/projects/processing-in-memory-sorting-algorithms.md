---
title: "Processing-In-Memory: Sorting Algorithms"
order: 100
team: Team of 5
image: { src: /assets/projects/PIM.jpg, alt: UPMEM logo }
size: [12, 6]
image_beside: true
links:
  - { label: Presentation, icon: video, url: "https://docs.google.com/presentation/d/1zqjP24BIFGV1ArI6x-K1hgJrn6dM-mcpVgXRz3by6Ms/edit#slide=id.p" }
  - { label: Code, icon: github, url: "https://github.com/yashparakh111/upmem-dpu" }
---

* Surveyed the ability of PIM to accelerate sorting techniques
    * Two base algorithms – *insertion/radix sort* + *merge* – showed similar results
    * PIM performed slower than C/C++ quicksort
    * Effect of PIM parameters (DPU-CPU tradeoffs, cache size) are analyzed
