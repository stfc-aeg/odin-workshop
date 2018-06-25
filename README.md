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
* Default output file location from FP is /tmp/test.hdf5
* Can configure to varying degree from command line, config file and client control connection (not shown here)

![EXCALIBUR image](images/excalibur.png)