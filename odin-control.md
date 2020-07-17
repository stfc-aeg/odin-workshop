# AEG ODIN control workshop
## 14 November 18

## Table of Contents

* What is odin-control?
* What is tornado?
* Core concepts
  * `odin_server`
  * Adapters
  * Parameter tree
  * API vs static URLs
  * UI layer
* Getting started demo
* Using an external adapter

## What is odin-control?

* Python-based framework for the _**control plane**_ of detector systems 
* based on [tornado](http://www.tornadoweb.org/en/stable/) 
web application framework
* dynamically-loaded plugin _**adapters**_ provide system-specific functionality
* [this](https://accelconf.web.cern.ch/icalepcs2017/papers/tupha212.pdf) published conference paper gives an overview of odin-control
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

## What is tornado?

* [www.tornadoweb.org](http://www.tornadoweb.org/en/stable/)
* Written in Python 
* Web application framework and asynchronous networking library
* Originally developed at FriendFeed (aka Facebook)
* Makes use of non-blocking network I/O
* Supports large number of open client connections from single application thread

## Core Concepts

### `odin-server`

* the _installed_ application in `odin-control`
* a wrapper around a tornado HTTP server instance running on a defined IP address/port
* responsible for loading and configuring one or more _adapters_ to control elements of a system
* expose REST-like interface to adapters via a well-known API URL
* able to optionally serve static assets, e.g. HTML, CSS, JS to generate a control UI in a 
web browser

### Adapters

* do the heavy lifting in `odin-control`
* are python modules dynamically loaded into a running `odin_server` instance
* do _not_ need to be part of odin-control package
* transform incoming HTTP requests (GET and PUT) into actions
* expose a tree of parameter resources with read and/or write access via the REST API
* typically expose JSON access to parameter resources
* interface to hardware, other systems, compiled libraries, etc.
* can run background update tasks on a timer (e.g hardware update polling loop)
* are the bit you'll write!

**NB** : adapters should ensure GET requests are idempotent, i.e. do **not** affect state of system.
If you need to modify a parameter, trigger an command, launch a acquisition etc., 
**you MUST use a PUT request**

### Parameter tree

* a `dict`-like class used in adapters to define a tree of parameters
* allow recursive read/write access at arbitrary points in the tree
* bind set/get (i.e. read/write) methods to leaves on the tree
* can be nested (see later example)

### API vs static URLs 

* API access:
    * Adapters are bound into URL 'routes' in the HTTP server
    * Are accessed via a single, versioned top-level API URL, 
    e.g `http://127.0.0.1:8888/api/0.1/<adapter_name>/`
    * Can handle at least GET and PUT requests (+ optionally DELETE)

* Static URLs:
    * Server can also serve static assets from `static_path`: HTML, JS, CSS etc
    * Exposed at the upper-most URL of the server, e.g. `http://127.0.0.1/index.html`
    * Not required but used on e.g. LPD PSCU, QEM, PERCIVAL, ...

### UI layer

* not required if e.g another control system is accessing API
* typically has small number of HTML pages, with CSS and Javascript assets loaded
* interacts with API via AJAX requests
* **MUST** separate presentation from business logic (a la MVC pattern) - don't implement any control
logic on UI side, do it in the adapter
* Examples to date (LPD, QEM, PERCIVAL, ...) use JQuery / Bootstrap libraries

## Getting started demo

* For this demo you will need to have Python 3.5 or later installed on your machine as Tornado 6 does not work with earlier versions.

* Create a python >= 3.5 virtual environment in a directory of your choice (various methods):

Execute command:
```
$ virtualenv odin-workshop-3.8.3
```

Terminal output:
```
created virtual environment CPython3.8.3.final.0-64 in 2470ms
  creator CPython3Posix(dest=/u/user/odin-workshop/odin-workshop-3.8.3, clear=False, global=False)
  seeder FromAppData(download=False, pip=latest, setuptools=latest, wheel=latest, via=copy, app_data_dir=/u/user/.local/share/virtualenv/seed-app-data/v1.0.1)
  activators BashActivator,CShellActivator,FishActivator,PowerShellActivator,PythonActivator,XonshActivator
```

* Clone `odin-control` from GitHub:

Execute command:
```
$ git clone https://github.com/odin-detector/odin-control.git
```

Terminal output:

```
Cloning into 'odin-control'...
remote: Enumerating objects: 121, done.
remote: Counting objects: 100% (121/121), done.
remote: Compressing objects: 100% (59/59), done.
remote: Total 2057 (delta 53), reused 106 (delta 47), pack-reused 1936
Receiving objects: 100% (2057/2057), 704.91 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1255/1255), done.
```

* Install `odin-control` in develop mode (make sure that your virtual environment is activated):

Execute commands:
```
$ cd odin-control
```

```
$ python setup.py develop
```

Terminal output:
```
running develop
running egg_info
creating src/odin.egg-info
writing src/odin.egg-info/PKG-INFO
writing dependency_links to src/odin.egg-info/dependency_links.txt
writing entry points to src/odin.egg-info/entry_points.txt
writing requirements to src/odin.egg-info/requires.txt
writing top-level names to src/odin.egg-info/top_level.txt
writing manifest file 'src/odin.egg-info/SOURCES.txt'
reading manifest file 'src/odin.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
warning: no files found matching 'odin/_version.py'
writing manifest file 'src/odin.egg-info/SOURCES.txt'
running build_ext
Creating /u/user/odin-workshop/odin-workshop-3.8.3/lib/python3.8/site-packages/odin.egg-link (link to src)
Adding odin 1.0.0 to easy-install.pth file
Installing odin_server script to /u/user/odin-workshop/odin-workshop-3.8.3/bin

<< ... snip ... >>

Installed /u/user/odin-workshop/odin-workshop-3.8.3/lib/python3.8/site-packages/tornado-6.0.4-py3.8-linux-x86_64.egg
Finished processing dependencies for odin==1.0.0
```

* Behold the glory that is `odin_server`:

Execute command:
```
$ which odin_server
```

Terminal output:
```
/u/user/odin-workshop/odin-workshop-3.8.3/bin/odin_server
```

Execute command:
```
$ odin_server --help
```

Terminal output:
```
usage: odin_server [-h] [--version] [--config FILE] [--adapters ADAPTERS]
                   [--http_addr HTTP_ADDR] [--http_port HTTP_PORT]
                   [--debug_mode DEBUG_MODE]
                   [--access_logging debug|info|warning|error|none]
                   [--static_path STATIC_PATH]
                   [--log_file_max_size LOG_FILE_MAX_SIZE]
                   [--log_file_num_backups LOG_FILE_NUM_BACKUPS]
                   [--log_file_prefix PATH]
                   [--log_rotate_interval LOG_ROTATE_INTERVAL]
                   [--log_rotate_mode LOG_ROTATE_MODE]
                   [--log_rotate_when LOG_ROTATE_WHEN]
                   [--log_to_stderr LOG_TO_STDERR]
                   [--logging debug|info|warning|error|none]

optional arguments:
  -h, --help            show this help message and exit
  --version             Show the server version information and exit
  --config FILE         Specify a configuration file to parse
  --adapters ADAPTERS   Comma-separated list of API adapters to load
  --http_addr HTTP_ADDR
                        Set HTTP server address
  --http_port HTTP_PORT
                        Set HTTP server port
  --debug_mode DEBUG_MODE
                        Enable tornado debug mode
  --access_logging debug|info|warning|error|none
                        Set the tornado access log level
  --static_path STATIC_PATH
                        Set path for static file content
  --log_file_max_size LOG_FILE_MAX_SIZE
                        max size of log files before rollover
  --log_file_num_backups LOG_FILE_NUM_BACKUPS
                        number of log files to keep
  --log_file_prefix PATH
                        Path prefix for log files. Note that if you are
                        running multiple tornado processes, log_file_prefix
                        must be different for each of them (e.g. include the
                        port number)
  --log_rotate_interval LOG_ROTATE_INTERVAL
                        The interval value of timed rotating
  --log_rotate_mode LOG_ROTATE_MODE
                        The mode of rotating files(time or size)
  --log_rotate_when LOG_ROTATE_WHEN
                        specify the type of TimedRotatingFileHandler interval
                        other options:('S', 'M', 'H', 'D', 'W0'-'W6')
  --log_to_stderr LOG_TO_STDERR
                        Send log output to stderr (colorized if possible). By
                        default use stderr if --log_file_prefix is not set and
                        no other logging is configured.
  --logging debug|info|warning|error|none
                        Set the Python log level. If 'none', tornado won't
                        touch the logging configuration.
``` 

* Modify the `test.cfg` configuration file located in `odin-control/tests/config/` by changing the value of `http_addr` to `127.0.0.1`:

* Start `odin_server` with a demo adapter and UI:

Execute commands:
```
$ cd test
```

```
$ odin_server --config config/test.cfg --logging=debug --debug_mode=1
```

Terminal output:
```
[D 200715 15:57:39 dummy:47] Launching background task with interval 1.00 secs
[D 200715 15:57:39 selector_events:59] Using selector: EpollSelector
[D 200715 15:57:39 dummy:55] DummyAdapter loaded
[D 200715 15:57:39 api:230] Registered API adapter class DummyAdapter from module odin.adapters.dummy for path dummy
[D 200715 15:57:39 default:40] Static path for default handler is ./static
[I 200715 15:57:39 server:63] HTTP server listening on 127.0.0.1:8888
[D 200715 15:57:40 dummy:65] DummyAdapter: background task running, count = 0
[D 200715 15:57:41 dummy:65] DummyAdapter: background task running, count = 1
[D 200715 15:57:42 dummy:65] DummyAdapter: background task running, count = 2
```

* Browse to the default UI:

![Dummy UI](images/odin_dummy_ui.png)

* Interrogate the REST API:

Execute command:
```
$ curl -s http://127.0.0.1:8888/api | python -m json.tool
```

Terminal output:
```
{
    "api_version": 0.1
}
```

Execute command:
```
$ curl -s http://127.0.0.1:8888/api/0.1/adapters | python -m json.tool
```

Terminal output:
```
{
    "adapters": [
        "dummy"
    ]
}
```

Execute command:
```
$ curl -s http://127.0.0.1:8888/api/0.1/dummy/ | python -m json.tool
```

Terminal output:
```
{
    "response": "DummyAdapter: GET on path "
}
```

Execute command:
```
$ curl -s http://127.0.0.1:8888/api/0.1/dummy/random_path | python -m json.tool
```

Terminal output:
```
{
    "response": "DummyAdapter: GET on path random_path"
}
```

Execute command:
```
$ curl -s -H "Content-Type: application/json" -X PUT -d '' 'http://localhost:8888/api/0.1/dummy/test_put' | python -m json.tool
```

Terminal output:
```
{
    "response": "DummyAdapter: PUT on path test_put"
}
```


* Try a different adapter:

Execute command:
```
$ odin_server --config config/test_system_info.cfg
```

Terminal output:
```
[I 181113 15:46:00 server:65] Using the 0MQ IOLoop instance
[D 181113 15:46:00 system_info:36] SystemInfoAdapter loaded
[D 181113 15:46:00 api:229] Registered API adapter class SystemInfoAdapter from module odin.adapters.system_info for path system_info
[D 181113 15:46:00 default:40] Static path for default handler is static
[I 181113 15:46:00 server:72] HTTP server listening on 127.0.0.1:8888
[D 181113 15:46:22 server:87] 200 GET /api/0.1/adapters (127.0.0.1) 1.47ms
[D 181113 15:46:32 system_info:55] {'odin_version': '0.3.1+3.g8bcfc08.dirty', 'platform': {'node': 'te7bramley.te.rl.ac.uk', 'release': '18.2.0', 'version': 'Darwin Kernel Version 18.2.0: Fri Oct  5 19:41:49 PDT 2018; root:xnu-4903.221.2~2/RELEASE_X86_64', 'system': 'Darwin', 'processor': 'i386'}, 'server_uptime': 32.154356956481934, 'tornado_version': '4.5.3'}
[D 181113 15:46:32 server:87] 200 GET /api/0.1/system_info/ (127.0.0.1) 0.93ms
```

* `system_info` uses nested `ParameterTree` instances for API variables:

Execute command:
```
$ curl -s http://127.0.0.1:8888/api/0.1/system_info/ | python -m json.tool
```

Terminal output:
```
{
    "odin_version": "0.3.1+3.g8bcfc08.dirty",
    "platform": {
        "node": "te7bramley.te.rl.ac.uk",
        "processor": "i386",
        "release": "18.2.0",
        "system": "Darwin",
        "version": "Darwin Kernel Version 18.2.0: Fri Oct  5 19:41:49 PDT 2018; root:xnu-4903.221.2~2/RELEASE_X86_64"
    },
    "server_uptime": 32.154356956481934,
    "tornado_version": "4.5.3"
}
```

## Using an external adapter

* There is a demo external adapter included with in this repo
* First clone this repo somehwere (alongside `odin-control` above would be fine):

Execute command:
```
$ git clone https://github.com/stfc-aeg/odin-workshop.git
```

Terminal output:
```
Cloning into 'odin-workshop'...
remote: Enumerating objects: 77, done.
remote: Counting objects: 100% (77/77), done.
remote: Compressing objects: 100% (56/56), done.
remote: Total 120 (delta 24), reused 67 (delta 15), pack-reused 43
Receiving objects: 100% (120/120), 1.18 MiB | 1.89 MiB/s, done.
Resolving deltas: 100% (39/39), done.
```

Execute commands:
```
$ cd odin-workshop/python
```

```
$ tree -d
```

Terminal output:
```
.
├── test
│   ├── config
│   └── static
│       ├── css
│       └── js
│           └── bootstrap-3.3.6-dist
│               ├── css
│               ├── fonts
│               └── js
├── workshop
└── workshop.egg-info
```
* Contains an installable python module `workshop` containing an adapter, plus a config file and
static resources to demonstrate web interaction.

* Install it:

Execute command:
```
$ python setup.py develop
```

Terminal output:
```
running develop
running egg_info
creating workshop.egg-info
writing workshop.egg-info/PKG-INFO
writing dependency_links to workshop.egg-info/dependency_links.txt
writing top-level names to workshop.egg-info/top_level.txt
writing manifest file 'workshop.egg-info/SOURCES.txt'
reading manifest file 'workshop.egg-info/SOURCES.txt'
reading manifest template 'MANIFEST.in'
warning: no files found matching 'odin_workshop/_version.py'
writing manifest file 'workshop.egg-info/SOURCES.txt'
running build_ext
Creating /u/user/odin-workshop/odin-workshop-3.8.3/lib/python3.8/site-packages/workshop.egg-link (link to .)
Adding workshop 0+untagged.25.g4043dbc to easy-install.pth file

Installed /u/user/odin-workshop/odin-workshop/python
Processing dependencies for workshop==0+untagged.25.g4043dbc
Finished processing dependencies for workshop==0+untagged.25.g4043dbc
```

* Run `odin_server` with the appropriate config:

Execute command:
```
$ odin_server --config test/config/workshop.cfg
```

Terminal output: 
```
[D 200715 16:15:22 adapter:231] Launching background tasks with interval 1.00 secs
[D 200715 16:15:22 selector_events:59] Using selector: EpollSelector
[D 200715 16:15:22 adapter:45] WorkshopAdapter loaded
[D 200715 16:15:22 api:230] Registered API adapter class WorkshopAdapter from module workshop.adapter for path workshop
[D 200715 16:15:22 system_info:37] SystemInfoAdapter loaded
[D 200715 16:15:22 api:230] Registered API adapter class SystemInfoAdapter from module odin.adapters.system_info for path system_info
[D 200715 16:15:22 default:40] Static path for default handler is test/static
[I 200715 16:15:22 server:63] HTTP server listening on 127.0.0.1:8888
[D 200715 16:15:23 adapter:259] Background IOLoop task running, count = 0
[D 200715 16:15:23 adapter:278] Background thread task running, count = 0
[D 200715 16:15:24 adapter:259] Background IOLoop task running, count = 1
...
```

* Interact with the adapter at the command line:

Execute command:
```
$ curl -s http://127.0.0.1:8888/api/0.1/workshop/ | python -m json.tool
```

Terminal output
```
{
    "background_task": {
        "count": 2923,
        "enable": true,
        "interval": 1.0
    },
    "odin_version": "0.3.1+3.g8bcfc08.dirty",
    "server_uptime": 2935.4133479595184,
    "tornado_version": "4.5.3"
}
```

Execute command:
```
$ curl -s -H "Content-Type: application/json" -X PUT -d '{"enable": false}' 'http://localhost:8888/api/0.1/workshop/background_task' | python -m json.tool
```

Terminal output
```
{
    "background_task": {
        "count": 10,
        "enable": false,
        "interval": 1.0
    }
}
```

Execute command:
```
$ curl -s -H "Content-Type: application/json" -X PUT -d '{"interval": 0.1}' 'http://localhost:8888/api/0.1/workshop/background_task'
```

Terminal output
```
{
    "background_task": {
        "count": 214,
        "enable": true,
        "interval": 0.1
    }
}
```

* Try the demo UI in a browser:

![Workshop UI](images/odin_workshop_ui.png)

* Explore the code in `workshop\adapter.py`. 
* Demonstrates the following:
    * Initialization with parameters from config file
    * Handling GET/PUT
    * Passing off get/set to Workshop class
    * Use of nested parameter trees
    * Read-only and read/write methods on parameters
    * Background task in thread executor pool

* Explore the static resources `index.html` and `odin_server.js`:

    * UI interaction using HTML and JS
    * Background polling in JS to keep adapter state view refreshed
  
## Questions ??
