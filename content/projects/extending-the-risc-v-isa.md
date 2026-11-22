---
title: Extending the RISC-V ISA
order: 10
team: Team of 2
image: { src: /assets/projects/RISCV_Logo.png, alt: RISC-V logo }
# Optional layout: size = [columns of 12 on desktop, columns of 6 on tablet];
# image_style = plate (logo on white, default) or photo (fills its box); image_beside = image left of the text.
size: [7, 6]
image_beside: true
links:
  - { label: Presentation, icon: video, url: "https://vimeopro.com/utece/capstone2021spring/video/543700201" }
  - { label: Design, icon: document, url: "https://docs.google.com/document/d/1Ygt9UbJ5kYmJLXBvFtrCkNEAzlkYbvzGRgO9i6_9oP4/edit?usp=sharing" }
  - { label: Code, icon: github, url: "https://github.com/Patt-Senior-Design/core-design" }
---

* Custom synthesizable Verilog implementation of RV32-IM core and memory hierarchy
* Added ISA + Microarchitectural extensions to accelerate:
    * Searching in Linear-Probed Hashsets (up to 10x speedup on high load-factors)
    * Breadth-First Search (average 2x speedup)
