---
title: "Silverline: Lightweight Virtualization and Orchestration of Distributed Systems"
order: 30
authors: [Arjun Ramesh, Tianshu Huang, Emily Ruppel, Dakshina Dasari, Behnaz Pourmohseni, Fedor Smirnov,
  Marco Giani, Paolo Pazzaglia, Charles Shelton, Nuno Pereira, Arne Hamann, Dirk Ziegenbein, Anthony Rowe]
figure: { src: /assets/pubs/Silverline.svg, alt: "Silverline architecture: application, host and platform manifests feed an orchestrator that deploys WebAssembly modules to edge platforms over a pub/sub bus" }
links:
  - { label: RTAS 2025, icon: ieee }
  - { label: Silverline Org, icon: github, url: "https://github.com/SilverLineFramework" }
---

Real-time cyber-physical systems naturally lend themselves to distributed compute, but are often programmed monolithically to curb complexity
and safety exploits.
Our framework, Silverline, explores programmability and orchestration of distributed applications transparently
across wide range of hardware using WebAssembly for lightweight virtualization.
