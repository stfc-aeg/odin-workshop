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
* dynamically-loaded plugin _**adapters**_ provide system-specific functionality
* not going to cover this any further today :wink:

![Tornado Logo](http://www.tornadoweb.org/en/stable/_images/tornado.png)

![ODIN control](images/odin_control.png)

## odin-data

* `odin-data` is the _**data plane**_ component of ODIN-based systems
* provides a high-performance data capture and processing chain
* designed (primarily) for systems sending data as _frames_ over 10GigE+ network links
* consists of two communicating processes:
  * frameReceiver
  * frameProcessor
* written in C++ with dynamically-loaded plugins for specific detectors

![ODIN data](images/odin_data.png)

