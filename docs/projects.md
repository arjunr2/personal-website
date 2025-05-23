# Projects

## Extending the RISC-V ISA

![riscv](assets/projects/RISCV_Logo.png){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Custom synthesizable Verilog implementation of RV32-IM core and memory hierarchy
* Added ISA + Microarchitectural extensions to accelerate:
    * Searching in Linear-Probed Hashsets (up to 10x speedup on high load-factors)
    * Breadth-First Search (average 2x speedup) 

[:octicons-video-16: Presentation](https://vimeopro.com/utece/capstone2021spring/video/543700201){ .custom-button }
[:material-file-document-outline: Design](https://docs.google.com/document/d/1Ygt9UbJ5kYmJLXBvFtrCkNEAzlkYbvzGRgO9i6_9oP4/edit?usp=sharing){ .custom-button }
[:material-github: Code](https://github.com/Patt-Senior-Design/core-design){ .custom-button }
&emsp; **Team of 2**
<br/>
<br/>

---

## Processing-In-Memory: Sorting Algorithms

![pim](assets/projects/PIM.jpg){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Surveyed the ability of PIM to accelerate sorting techniques
    * Two base algorithms -- *insertion/radix sort* + *merge* -- showed similar results
    * PIM performed slower than C/C++ quicksort
    * Effect of PIM parameters (DPU-CPU tradeoffs, cache size) are analyzed

[:octicons-video-16: Presentation](https://docs.google.com/presentation/d/1zqjP24BIFGV1ArI6x-K1hgJrn6dM-mcpVgXRz3by6Ms/edit#slide=id.p){ .custom-button }
[:material-github: Code](https://github.com/yashparakh111/upmem-dpu){ .custom-button }
&emsp; **Team of 5**
<br/>
<br/>

---

## XC2064 FPGA Design

![fpga](assets/projects/FPGA.jpg){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Fully-synthesizable Verilog design of the XC2064 from 1985
* Created tooling for demonstration
    * Unit tests for LUT and CLB
    * Web GUI for interconnect bitstream generation

[:material-file-document-outline: Reference Article](https://www.righto.com/2020/09/reverse-engineering-first-fpga-chip.html){ .custom-button }
&emsp; **Team of 3**
<br/>
<br/>

---

## 1D Cellular Automata Theory

![cell](assets/projects/multi_choice.png){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Brief survey of local pattern formation in 1D Cellular Automata Theory  

[:material-file-document-outline: Paper](https://drive.google.com/file/d/1P2Sxl4vDeoLRzdk5EeYzpcMRMJDdGRK9/view?usp=sharing){ .custom-button }
&emsp; **Solo**
<br/>
<br/>

---

## RTOS Design

![rtos](assets/projects/RTOS2.png){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Built a bare-metal RTOS on TM4C123 microcontroller with basic features:
    * Real-time priority scheduler with thread/process management 
    * FAT32 file system and memory management
    * Wireless remote-procedure calls and user interpreter 
* Demonstrated OS robustness with two-player remote battleship application

[:octicons-video-16: Demo](https://www.youtube.com/watch?v=N1q2bLxdYYM){ .custom-button }
&emsp; **Team of 2**
<br/>
<br/>

---

## JASP Cellular Phone

![jasp](assets/projects/JASP2.jpg){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Supports call+text functionality with total cost under $50
* Integrates a LCD, real-time clock, and numpad on a TM4C123 microcontroller
* Uses LittlevGL library for graphical rendering
* Voted best project during class (EE 445L) project showcase

[:material-github: Code](https://github.com/JASP-EE445L-Fall19/Phone_4C123){ .custom-button }
&emsp; **Team of 4**
<br/>
<br/>

---

## Enrich: PennApps 2019

![enrich](assets/projects/Enrich.png){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Prototype for an interactive course organization and lecturing platform. Includes a 
messaging service, speech-to-text translation, and anonymous real-time feedback.

[:fontawesome-brands-dev: Devpost](https://devpost.com/software/enrich-an-education-platform-to-increase-collaboration){ .custom-button }
[:material-github: Code](https://github.com/arjunramesh99/Enrich){ .custom-button }
&emsp;|&emsp; **Team of 4**
<br/>
<br/>

---

## RecycleMe: CreateAThon 2019

![recycle](assets/projects/TeamTrash.png){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Smart autonomous trash-sorter to sort Recyclable, Landfill, and Compostable materials 
    * Raspberry Pi controls movable compartment with camera to detect new objects
    * A trained CNN runs on offsite server to process data in real-time
* Built a mobile app to crowd-source the gathering and labelling of real-world dataset

[:material-file-document-outline: Presentation](https://docs.google.com/presentation/d/1hpvU2TW-b8DZ-9Plj63A9ec2fWhC68u3J7fawatYcz0/edit#slide=id.g6349289ee8_0_57){ .custom-button }
[:material-github: System Code](https://github.com/yashparakh111/createathon2019){ .custom-button }
[:material-github: Mobile App](https://github.com/yashparakh111/RecycleMe){ .custom-button }
&emsp; **Team of 5**
<br/>
<br/>

---

## Home-Unity: HackDFW 2019

![hu](assets/projects/HomeUnity.png){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em;margin-bottom:3em }

* Mobile app for homeless users to receive notifications about provisions from the City of 
 Dallas
* Data-visualization web platform for City of Dallas to better understand the 
 urban geography of homelessness
* Awarded first place from City of Dallas and OmniSci under social good category

[:fontawesome-brands-dev: Devpost](https://devpost.com/software/home-unity-fctb5s){ .custom-button }
[:material-github: Code](https://github.com/yashparakh111/Home-Unity){ .custom-button }
&emsp; **Team of 5**
<br/>
<br/>

---

## ChairIoT: CreateAThon 2018

![iot](assets/projects/Chair1_crop.jpg){ align=left width=20% style=margin:1em;margin-left:0;margin-top:0.3em;margin-bottom:0.3em }

* Prototype for a self-organizing chair platform
    * Raspberry Pi used for processing pipeline and motor control
    * Uses IMU to gather time-series acceleration data and gyroscope data
    * Implemented Kalman filter to compute net displacement
    * Power management components mounted below the platform

[:material-file-document-outline: Proposal](https://drive.google.com/file/d/1ro5dI3SfT6lGEWr6IyF8sTGZJdI4XTpq/view?usp=sharing){ .custom-button }
[:material-github: Code](https://github.com/yashparakh111/Self-Organizing-Chair){ .custom-button }
&emsp; **Team of 5**


<br/>
<br/>
