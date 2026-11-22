---
title: Empowering WebAssembly with Thin Kernel Interfaces
order: 10
authors: [Arjun Ramesh, Tianshu Huang, Ben L. Titzer, Anthony Rowe]
figure: { src: /assets/pubs/WALI.svg, alt: Diagram comparing the Native, WALI, and WASI software stacks }
links:
  - { label: EuroSys 2025, icon: acm, url: "https://dl.acm.org/doi/epdf/10.1145/3689031.3717470" }
  - { label: Pre-Print, icon: arxiv, url: "https://arxiv.org/abs/2312.03858" }
  - { label: WALI, icon: github, url: "https://github.com/arjunr2/WALI" }
  - { label: Rust Target, icon: rust, url: "https://doc.rust-lang.org/nightly/rustc/platform-support/wasm32-wali-linux.html" }
---

Webassembly (Wasm) adoption for new domains is often hindered by the lack of standard system interfaces.
Kernel interface support in Wasm engines allow numerous languages and applications to target Wasm, including
arbitrary high-level Wasm APIs (WASI), driving ISA portability and software safety down to even deeply embedded
OS ecosystems
