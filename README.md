# Take Home Instructions

## Requirements

- [x] Must be done in Python.  
- [x] Accept webcam feed as input.  
- [x] Retrieve video stream from the webcam, this should include fps, video source, frame
dimensions.  
- [x] Add a multithreaded process to show simultaneously -[BGR image, gray scale , Blue
image channel] on the same UI side by side in real time.  
- [x] Provide an option to modify the frame dimensions prior to display, enabling the
application of a scale factor to resize the original frame width.  
- [x] Display the requested video feeds to the user by a webUI, adding a gray scale slider to
change the grayscale intensity of the image, and an option to change the channel between
Red, Green, and default Blue.  
- [x] Cache the video stream for 30 secs for both BGR and grayscale, display indicator in the
UI if result is pulled from cache.  

## Assumptions

- [x] This project is open to interpretation.  
- [x] Functionality is a priority over form.  
- [x] If you get stuck, complete as much as you can.  


## Submission

- [x]  Use a public source code repository (GitHub, etc) to store your code.  
- [x]  Send us the link to your completed code.  
- [x]  Preferred implementing using Object Oriented Programming.  

***

# Video Jawn

Note: First commit made using the hatch build system, see [here](https://hatch.pypa.io/1.13/intro/) for details.  


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

Required packages will be installed when you pip install this package.  
You may install it in-place (editable) or into site-packages.  

Editable
```console
pip install -e .
```

Into site-packages
```console
pip install .
```

## Usage

```console
python -m video_jawn serve
```
Then just open [http://localhost:10578/](http://localhost:10578/) in your browser or click [here](http://127.0.0.1:10578/)  

One may also specify the port with -p PORT  
```console
python -m video_jawn serve -p 8080
```

## License

`video-jawn` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.  
