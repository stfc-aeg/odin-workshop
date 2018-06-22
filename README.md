# AEG ODIN data workshop
## 25 June 18

# Table of Contents

* What is odin?
  * odin-control
  * odin-data


# What is ODIN?

* set of frameworks designed to facilitate control and readout of detector systems
* joint initiative by STFC and DLS  
* currently in development/use for a range of detector systems:
  * EXCALIBUR
  * PERCIVAL
  * TRISTAN
  * EIGER
  * LPD
  * QEM
* consists of two main parts: `odin-control` and `odin-data`.

## odin-control

* Python-based framework for control
* based on [tornado](http://www.tornadoweb.org/en/stable/) 
web application framework
* presents REST-like control API and/or web content using HTTP and JSON
* dynamically-loaded plugin *adapters* provide system-specific functionality

![ODIN control](images/odin_control.png)

![Tornado Logo](http://www.tornadoweb.org/en/stable/_images/tornado.png) EXCALIBUR ODIN Architecture