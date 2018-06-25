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
* dynamically-loaded plugin _**adapters**_ provide system-specific functionality
* presents REST-like control API and/or web content using HTTP and JSON:
```
$ curl http://127.0.0.1:8888/api/0.1/excalibur/

[D 180622 16:23:08 server:75] 200 GET /api/0.1/excalibur/ (127.0.0.1) 0.87ms
{u'command': {u'api_trace': False,
              u'connect': None,
              u'fe_init': None,
              u'fe_param_read': {u'chip': 0,
                                 u'fem': 0,
                                 u'param': [u'frames_acquired',
                                            u'control_state'],
                                 u'value': {u'control_state': [1073741855],
                                            u'efuseid': [[2788134078,
                                                          3979316414,
                                                          3962539198,
                                                          321883326,
                                                          3601829054,
                                                          2393870014,
                                                          347049662,
                                                          1588563646]],
                                            u'frames_acquired': [100]}},
              u'fem_reboot': None,
              u'load_dacconfig': None,
              u'load_pixelconfig': None,
              u'reset_udp_counter': None,
              u'start_acquisition': None,
              u'stop_acquisition': None},
 u'status': {u'command_pending': False,
             u'command_succeeded': True,
             u'connected': True,
             u'fem': [{u'address': u'192.168.0.106',
                       u'chip_enable_mask': 255,
                       u'chips_enabled': [1, 2, 3, 4, 5, 6, 7, 8],
                       u'data_address': u'10.0.2.1',
                       u'error_code': 0,
                       u'error_msg': u'',
                       u'id': 1,
                       u'port': 6969,
                       u'state': 1}],
             u'num_pending': 0,
             u'powercard_fem_idx': 0}}
```

![Tornado Logo](http://www.tornadoweb.org/en/stable/_images/tornado.png)

![ODIN control](images/odin_control.png)

![LPD PCSU](images/lpd_pcsu.png)

* not going to cover this any further today :wink:

## odin-data

* `odin-data` is the _**data plane**_ component of ODIN-based systems
* provides a high-performance, scalable data capture and processing chain
* designed (primarily) for systems sending data as _frames_ over 10GigE+ network links
* consists of two communicating processes:
  * **frame receiver**
  * **frame processor**
* generic applications written in C++ with dynamically-loaded plugins for specific detectors
* both have integrated IPC ZeroMQ channels to allow control/monitoring
* can be integrated with `odin-control`

![ODIN data](images/odin_data.png)

### Frame Receiver

* does what is says on the tin! :+1:
* captures incoming data (UDP, TCP, ZeroMQ channels, +...)
* stores frames in shared memory buffers
* hands off completed frames to frame processor for further processing
* designed to be as lightweight as possible
* tolerant of packet loss and out-of-order data

### Frame Processor

* also does what it says on the tin!
* listens from frame ready notifications from FR via ZeroMQ channel
* passes frames through dynamically-configurable chain of plugins for e.g.:
  * decoding/reordering pixel data
  * applying calibration algorithms (e.g. flat field, b/g subtraction)
  * writes data out to file system in e.g. HDF5 format
  * side-channel plugins for handling e.g. metadata
* future components planned:
  * live image preview endpoint
  * remote streaming endpoint
  * opportunities here for contributions!

### Shared Buffers

* shared buffers are *stateless* - message driven sharing
* each buffer contains header followed by payload
* Header contains metadata describing *state* of received frame, e.g. frame counter, 
number of received packets, missing packets, timestamp etc
* Headers are detector-specific, defined in common include files, e.g:
```
    /*
     * ExcaliburDefinitions.h
     */

    typedef struct
    {
      uint32_t packets_received;
      uint8_t  sof_marker_count;
      uint8_t  eof_marker_count;
      uint8_t  packet_state[max_num_subframes][max_primary_packets + num_tail_packets];
    } FemReceiveState;

    typedef struct
    {
        uint32_t frame_number;
        uint32_t frame_state;
        struct timespec frame_start_time;
        uint32_t total_packets_received;
        uint8_t total_sof_marker_count;
        uint8_t total_eof_marker_count;
        uint8_t num_active_fems;
        uint8_t active_fem_idx[max_num_fems];
        FemReceiveState fem_rx_state[max_num_fems];
    } FrameHeader;
```

### External Software Dependencies

The following libraries and packages are required:

* [CMake](http://www.cmake.org) : build management system (version >= 2.8)
* [Boost](http://www.boost.org) : portable C++ utility libraries. The following components are used - program_options, unit_test_framework, date_time, interprocess, bimap (version >= 1.41)
* [ZeroMQ](http://zeromq.org) : high-performance asynchronous messaging library (version >= 3.2.4)
* [Log4CXX](http://logging.apache.org/log4cxx/): Configurable message logger (version >= 0.10.0)
* [HDF5](https://www.hdfgroup.org/HDF5): __Optional:__ if found, the filewriter application will be built (version >= 1.8.14)

## Demo using EXCALIBUR as example

* Show how FR and FP apps are run together with simulated source of data
* Using *install* tree:
```
<<project_install_dir>> $ tree -d
.
|-- bin                     <- installed executables
|-- config                  <- configuration files
|   |-- client
|   |-- control
|   `-- data
|       `-- client_msgs
|-- include                 <- shared include files for building
|   |-- frameProcessor
|   |-- frameReceiver
|   |-- rapidjson
|   `-- zmq
|-- lib                     <- loadable shared libraries
|-- pcap
`-- test
```

1. Start FR instance:
```
$ cd <<project_install_dir>>
$ ./bin/frameReceiver --debug=2 --config=config/data/fr_test_excalibur_1.config
```

2. Start FP instance (in second terminal):
```
$cd <<project_installed_dir>>
$./bin/frameProcessor --config=config/data/fp_test_excalibur_1.config
```

3. Send data - in this case captured packet playback:
```
$ python ../excalibur-detector/data/tools/python/excalibur_frame_producer.py -a 127.0.0.1 -p 61649 -n 1 pcap/excalibur_10_frames_tpcount_2000.pcap 
I Extracting EXCALIBUR frame packets from PCAP file pcap/excalibur_10_frames_tpcount_2000.pcap
I Found 10 frames in file with a total of 1320 packets and 10496480 bytes
I Launching threads to send frames to 1 destination ports
I Sending 1 frames to destination 127.0.0.1:61649 ...
I Sent 1 frames with a total of 132 packets and 1049648 bytes, dropping 0 packets (0.0%)
```

* Can experiment with e.g. varying debug levels to see more/less output (from FR in particular)
* Logging configurable, goes to stdout and to log files (see config)
* Can configure to varying degree from command line, config file and client control connection (not shown here)
* Default output file location from FP is /tmp/test.hdf5

![EXCALIBUR image](images/excalibur.png)

## Building odin-data and plugins

### Create development environment

* Need to ensure the `aeg_sw` profile is loaded:
```
$ source /aeg_sw/etc/profile.sh
```
for `bash`-like shells, or
```
$ source /aeg_sw/etc/profile.csh
```
for `csh`-like shells. 
* Allows you to use `environment-modules` to load various libraries, packages
etc into your environment. To see what's available:

```
$ module avail

-------------------------------------------- /aeg_sw/etc/modulefiles -------------------------------

---------------------------------------- /usr/share/Modules/modulefiles ----------------------------
dot         module-git  module-info modules     null        use.own

----------------------------------------------- /etc/modulefiles -----------------------------------
openmpi-1.4-psm-x86_64 openmpi-1.4-x86_64

------------------------------------------- <home_dir>/.privatemodules -------------------------------
odin-data

--------------------------------------- /aeg_sw/apps/Modules/modulefiles ---------------------------
arduino/1-8-3        dawn/2-7-0           eclipse/472_20171218
dawn/2-5-0           eclipse/472(default) pycharm/2017-1-4

------------------------------- /aeg_sw/tools/CentOS6-x86_64/Modules/modulefiles -------------------
boost/1-48-0        hdf5/1-10-0         python/2-7-13       ruby/2              zeromq/4-2-1
boost/1-66-0        log4cxx/0-10-0      python/3            ruby/2-4
git/2-13-2          python/2            python/3-6          ruby/2-4-1
git/2-17-1(default) python/2-7          python/3-6-2        subversion/1-8-19
```

* Load the correct modules for odin-development:
```
$ module load boost/1-48-0 hdf5/1-10-0 zeromq/4-2-1 log4cxx/0-10-0
```
* Sets up your shell environment with various paths etc:
```
$ echo $BOOST_ROOT
/aeg_sw/tools/CentOS6-x86_64/boost/1-48-0/prefix
$ echo $HDF5_ROOT
/aeg_sw/tools/CentOS6-x86_64/hdf5/1-10-0/prefix
$ echo $ZEROMQ_ROOT
/aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix
$ echo $LOG4CXX_ROOT
/aeg_sw/tools/CentOS6-x86_64/log4cxx/0-10-0/prefix
```

* Create a project development dir (using AEG path convention if appropriate)

```
$ mkdir -p ~/develop/projects/<project-name>
$ cd ~/develop/projects/<project-name>
```

### Clone, build and install odin-data

* Clone `odin-data` repo from Github:
```
$ git clone https://github.com/odin-detector/odin-data.git
Initialized empty Git repository in <home_dir>/develop/projects/odin-demo/odin-data/.git/
remote: Counting objects: 5189, done.
remote: Compressing objects: 100% (69/69), done.
remote: Total 5189 (delta 57), reused 81 (delta 47), pack-reused 5073
Receiving objects: 100% (5189/5189), 1.50 MiB | 1.23 MiB/s, done.
Resolving deltas: 100% (3440/3440), done.
```

* Create an `install` directory to install `odin-data` and plugins into:
```
mkdir install
```

* Create a build directory for CMake to use N.B. ODIN uses CMake ***out-of-source*** build semantics:
```
$ cd odin-data
$ mkdir build && cd build
```

* Configure CMake to define use of correct packages and set up install directory:
```
$ cmake -DBoost_NO_BOOST_CMAKE=ON -DBOOST_ROOT=$BOOST_ROOT \
  -DZEROMQ_ROOTDIR=$ZEROMQ_ROOT -DLOG4CXX_ROOT_DIR=$LOG4CXX_ROOT \
  -DHDF5_ROOT=$HDF5_ROOT \ 
  -DCMAKE_INSTALL_PREFIX=~/develop/projects/<project-name>/install ..
```
(This is verbose and error-prone but you only have to do it once per setup). 

* Check output from CMake for errors and correct paths:
```
-- The C compiler identification is GNU 4.4.7
-- The CXX compiler identification is GNU 4.4.7
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Boost version: 1.48.0
-- Found the following Boost libraries:
--   program_options
--   system
--   filesystem
--   unit_test_framework
--   date_time
--   thread

Looking for log4cxx headers and libraries
-- Root dir: /aeg_sw/tools/CentOS6-x86_64/log4cxx/0-10-0/prefix
-- Found PkgConfig: /usr/bin/pkg-config (found version "0.23")
-- Found LOG4CXX: /usr/lib64/liblog4cxx.so
-- Include directories: /usr/include/log4cxx
-- Libraries: /usr/lib64/liblog4cxx.so

Looking for ZeroMQ headers and libraries
-- Root dir: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix
-- checking for one of the modules 'libzmq'
-- Found ZEROMQ: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix/lib/libzmq.so
-- Include directories: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix/include
-- Libraries: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix/lib/libzmq.so

Searching for HDF5
-- HDF5_ROOT set: /aeg_sw/tools/CentOS6-x86_64/hdf5/1-10-0/prefix
-- HDF5 include files:  /aeg_sw/tools/CentOS6-x86_64/hdf5/1-10-0/prefix/include
-- HDF5 libs:           /aeg_sw/tools/CentOS6-x86_64/hdf5/1-10-0/prefix/lib/libhdf5.so/aeg_sw/tools/CentOS6-x86_64/hdf5/1-10-0/prefix/lib/libhdf5_hl.so
-- HDF5 defs:
-- Found Doxygen: /usr/bin/doxygen (found version "1.6.1")
-- Configuring done
-- Generating done
-- Build files have been written to: <home_dir>/develop/projects/odin-demo/odin-data/build
```
* This creates all the directories, makefiles etc needed to compile:
```
$ tree -d -L 1
.
├── bin
├── CMakeFiles
├── common
├── config
├── doc
├── frameProcessor
├── frameReceiver
├── lib
└── tools
```
* Compile odin-data:
```
$ make -j4
```
* Produces a lot of output first time through:
```
Scanning dependencies of target CopyPythonToolModules
Scanning dependencies of target CopyTestConfigs
Scanning dependencies of target CopyClientMsgFiles
Scanning dependencies of target OdinData
[  3%] [  3%] Generating ../test_config/fp_log4cxx.xml
Generating ../../test_config/client_msgs/reconfig_endpoints.json
[  4%] [  6%] Generating ../test_config/fr_log4cxx.xml
Generating ../../test_config/client_msgs/reconfig_buffer_manager.json
[  8%] [  9%] Generating ../test_config/fr_test.config
Generating ../../test_config/client_msgs/config_ctrl_chan_port_5010.json
[ 11%] [ 13%] Generating ../test_config/fp_test.config
Generating ../../test_config/client_msgs/config_ctrl_chan_port_5000.json
[ 14%] [ 14%] Generating ../test_config/fr_test_osx.config
Built target CopyPythonToolModules
[ 16%] Generating ../../test_config/client_msgs/reconfig_rx_thread.json
[ 18%] Generating ../../test_config/client_msgs/reconfig_decoder.json
[ 19%] Generating ../test_config/fp_py_test.config
[ 21%] Generating ../test_config/fp_py_test_osx.config
[ 21%] Built target CopyClientMsgFiles
[ 22%] [ 24%] [ 26%] Generating ../test_config/fp_py_test_excalibur.config
Generating ../test_config/fr_excalibur1.config
Generating ../test_config/fr_excalibur2.config
[ 27%] [ 29%] Generating ../test_config/fp_excalibur1.config
Generating ../test_config/fp_excalibur2.config
[ 29%] Built target CopyTestConfigs
[ 31%] Building CXX object common/src/CMakeFiles/OdinData.dir/logging.cpp.o
[ 32%] [ 34%] Building CXX object common/src/CMakeFiles/OdinData.dir/SharedBufferManager.cpp.o
[ 36%] Building CXX object common/src/CMakeFiles/OdinData.dir/IpcReactor.cpp.o
Building CXX object common/src/CMakeFiles/OdinData.dir/IpcMessage.cpp.o
[ 37%] Building CXX object common/src/CMakeFiles/OdinData.dir/IpcChannel.cpp.o
Linking CXX shared library ../../lib/libOdinData.so
[ 37%] Built target OdinData

<< snip >>

Linking CXX executable ../../bin/frameReceiver
Linking CXX executable ../../bin/frameProcessor
[ 88%] Built target frameReceiver
[ 90%] Building CXX object frameReceiver/test/CMakeFiles/frameReceiverTest.dir/__/src/FrameReceiverController.cpp.o
[ 91%] Building CXX object frameReceiver/test/CMakeFiles/frameReceiverTest.dir/__/src/DummyUDPFrameDecoderLib.cpp.o
[ 91%] Built target frameProcessor
[ 93%] Building CXX object frameReceiver/test/CMakeFiles/frameReceiverTest.dir/__/src/FrameReceiverZMQRxThread.cpp.o
Linking CXX shared library ../../lib/libHdf5Plugin.so
[ 93%] Built target Hdf5Plugin
[ 95%] Building CXX object frameReceiver/test/CMakeFiles/frameReceiverTest.dir/__/src/DummyUDPFrameDecoder.cpp.o
[ 96%] Building CXX object frameReceiver/test/CMakeFiles/frameReceiverTest.dir/__/src/FrameReceiverRxThread.cpp.o
[ 98%] Building CXX object frameReceiver/test/CMakeFiles/frameReceiverTest.dir/__/src/FrameDecoder.cpp.o
Scanning dependencies of target frameProcessorTest
[100%] Building CXX object frameProcessor/test/CMakeFiles/frameProcessorTest.dir/FrameProcessorTest.cpp.o
Linking CXX executable ../../bin/frameReceiverTest
[100%] Built target frameReceiverTest
Linking CXX executable ../../bin/frameProcessorTest
[100%] Built target frameProcessorTest
```

* This compiles ***four*** applications into `build/bin`:
```
$ tree bin
bin
├── frameProcessor
├── frameProcessorTest
├── frameReceiver
└── frameReceiverTest

0 directories, 4 files
```

* Run the unit test applications (optional):
```
$ bin/frameReceiverTest
Running 32 test cases...

*** No errors detected
$ bin/frameProcessorTest
bin/frameProcessorTest
Running 16 test cases...
TRACE - Frame constructed
TRACE - copy_data called with size: 24 bytes

<< snip >>

*** No errors detected
```

* Install `odin-data` into `<project-name>/install` directory:
```
$ make install
$ make install
[  8%] Built target OdinData
[  9%] Built target FrameReceiver
[ 13%] Built target DummyUDPFrameDecoder
[ 21%] Built target frameReceiver
[ 44%] Built target frameReceiverTest
[ 55%] Built target FrameProcessor
[ 57%] Built target DummyPlugin
[ 63%] Built target Hdf5Plugin
[ 68%] Built target frameProcessor
[ 70%] Built target frameProcessorTest
[ 70%] Built target CopyPythonToolModules
[ 90%] Built target CopyTestConfigs
[100%] Built target CopyClientMsgFiles
Install the project...
-- Install configuration: ""
-- Installing: <home_dir>/develop/projects/odin-demo/install/include/ClassLoader.h

<< snip >> 

"<home_dir>/develop/projects/odin-demo/install/lib:/aeg_sw/tools/CentOS6-x86_64/boost/1-48-0/prefix/lib:/aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix/lib:/aeg_sw/tools/CentOS6-x86_64/hdf5/1-10-0/prefix/lib"
```

### Clone, build and install project-specific plugins

* Using EXCALIBUR as example - can be used as template and renamed
* Builds alongside installed `odin-data`
* Change to the project directory, e.g.:
```
$ cd ~/develop/projects/<project-name>
```

* Clone the appropriate repo from Github:
```
$ git clone https://github.com/dls-controls/excalibur-detector.git
```
* ***NB project-specific repo may contain both `control` and `data` directories***

* Create the CMake build directory for `data`:
```
$ cd excalibur-detector/data
$ mkdir build && cd build
```

* Setup CMake ***NB reference to installed*** `odin-data`:
```
cmake -DBoost_NO_BOOST_CMAKE=ON -DBOOST_ROOT=$BOOST_ROOT \
  -DZEROMQ_ROOTDIR=$ZEROMQ_ROOT \
  -DLOG4CXX_ROOT_DIR=$LOG4CXX_ROOT 
  -DODINDATA_ROOT_DIR=~/develop/projects/<project-name>/install 
  -DCMAKE_INSTALL_PREFIX=~/develop/projects/<project-name>/install ..
```

* Checkout output for errors and correct paths:
```
-- The C compiler identification is GNU 4.4.7
-- The CXX compiler identification is GNU 4.4.7
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Boost version: 1.48.0
-- Found the following Boost libraries:
--   program_options
--   system
--   filesystem
--   unit_test_framework
--   date_time
--   thread

Looking for log4cxx headers and libraries
-- Root dir: /aeg_sw/tools/CentOS6-x86_64/log4cxx/0-10-0/prefix
-- Found PkgConfig: /usr/bin/pkg-config (found version "0.23")
-- Found LOG4CXX: /usr/lib64/liblog4cxx.so
-- Include directories: /usr/include/log4cxx
-- Libraries: /usr/lib64/liblog4cxx.so

Looking for ZeroMQ headers and libraries
-- Root dir: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix
-- checking for one of the modules 'libzmq'
-- Found ZEROMQ: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix/lib/libzmq.so
-- Include directories: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix/include
-- Libraries: /aeg_sw/tools/CentOS6-x86_64/zeromq/4-2-1/prefix/lib/libzmq.so

Looking for odinData headers and libraries
-- Root dir: ~/develop/projects/excalibur/install
-- Found ODINDATA: <home_dir>/develop/projects/odin-demo/install/lib/libOdinData.so
-- Include directories: <home_dir>/develop/projects/odin-demo/install/include;<home_dir>/develop/projects/excalibur/install/include/frameReceiver;<home_dir>/develop/projects/excalibur/install/include/frameProcessor
-- Libraries: <home_dir>/develop/projects/odin-demo/install/lib/libOdinData.so;<home_dir>/develop/projects/odin-demo/install/lib/libFrameReceiver.so;<home_dir>/develop/projects/odin-demo/install/lib/libFrameProcessor.so
-- Configuring done
-- Generating done
-- Build files have been written to: <home_dir>/develop/projects/odin-demo/excalibur-detector/data/build
```

* Build it:
```
make -j4
```
* Should produce output similar to this:
```
Scanning dependencies of target ExcaliburFrameDecoder
Scanning dependencies of target ExcaliburProcessPlugin
[ 25%] Building CXX object frameProcessor/src/CMakeFiles/ExcaliburProcessPlugin.dir/ExcaliburProcessPlugin.cpp.o
[ 50%] [ 75%] Building CXX object frameReceiver/src/CMakeFiles/ExcaliburFrameDecoder.dir/ExcaliburFrameDecoder.cpp.o
Building CXX object frameReceiver/src/CMakeFiles/ExcaliburFrameDecoder.dir/ExcaliburFrameDecoderLib.cpp.o
Linking CXX shared library ../../lib/libExcaliburProcessPlugin.so
[ 75%] Built target ExcaliburProcessPlugin
Scanning dependencies of target excaliburFrameProcessorTest
Linking CXX shared library ../../lib/libExcaliburFrameDecoder.so
[ 75%] Built target ExcaliburFrameDecoder
[100%] Building CXX object frameProcessor/test/CMakeFiles/excaliburFrameProcessorTest.dir/ExcaliburFrameProcessorTest.cpp.o
Linking CXX executable ../../bin/excaliburFrameProcessorTest
[100%] Built target excaliburFrameProcessorTest
```
* Install it:
```
$ make install
```
* Copies the plugins into the `install/lib` directory:
```
[ 50%] Built target ExcaliburFrameDecoder
[ 75%] Built target ExcaliburProcessPlugin
[100%] Built target excaliburFrameProcessorTest
Install the project...
-- Install configuration: ""
-- Installing: <home_dir>/develop/projects/odin-demo/install/lib/libExcaliburFrameDecoder.so
-- Installing: <home_dir>/develop/projects/odin-demo/install/lib/libExcaliburProcessPlugin.so
```
* And you're ready to try to reproduce the demo!

## Further discussion topics

* Code structure walkthrough for `odin-data` and `excalibur-detector`
* IDE integration with e.g. Eclipse, VS Code
* Forking/cloning repos, branching model
* CI jobs for unit & integration testing on Travis (+ Jenkins...?)
