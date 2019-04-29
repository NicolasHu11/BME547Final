# BME547Final
- Authors: Yijia Hu, Chris Zhou, Yuhan Liu 
- Class: BME547 Medical Software Design, Duke University
- Date: Apr, 2019
- [![Build Status](https://travis-ci.org/NicolasHu11/BME547Final.svg?branch=master)](https://travis-ci.org/NicolasHu11/BME547Final)

## How to run the code 
- clone this github repo and use pip to install the virtual environment 

`git clone https://github.com/briandzt/bme590final.git`

`pip3 install -r requirements.txt`

- Use pycharm, run  `server.py` and `gui.py`, below is the walk through video 

## Walkthough video
[Walkthrough Video](https://youtu.be/XkqojiIgSjs)

## Description 
- The goal of this project is to implement a software system to upload an image or an archive of images to a web-server, perform image-processing tasks on the web-server, and then display / download your processed image(s). 
- The program is constructed by three main parts: the GUI, the Processing Server and online database. User can use our GUI to choose the give commands, and then the GUI will communicate with our processing server by POST/GET requests, the server will communicate with database to store all the uploaded/processed images and user actions, etc. 

- To register, user needs to provide a unique username to start to use the program. 
- User needs to input username when he/she wants to  upload one image or a set of images in a zip file using the GUI. Then user chooses an image processing method for the uploaded image(s) and makes a request. This request will be sent to the server, where image proceesing is held. Aftet the processing, all useful data will store in database and server sends back provessed images to GUI.
- User can view the image(s) on the GUI, compare them with the original, and finally download the images. 
- The program also allows the user to view the metadata of the each request (time_uploaded, processing time, and image size) and user metrics(number of each procedure, the creation time of user.)

- Re-inputting the same username is not allowed, returns message " User already exists"
- Re-upload the same image/s is seen as a new request

## Environment 
- all the dependencies are listed in `requirements.txt`     
`pytest`
`pytest-pep8`
`requests`
`flask`
`pymodm`
`matplotlib`
`scikit-image`
`scipy`
`dnspython`


## Server

- Server can be run on your local machine or remote virtual machine. 
- To execute server, run `python server.py` from a python environment. 
- The current setting allows the server to operate locally. To operate via internet, the last line in the `server.py`
need to be updated with the proper host url.

## GUI
1. Username 
2. Choose image file(s)
3. Choose procedures
4. Result, display Histogram
5. Download option, multiple files are downloaded as zip file by default
6. Other functions:
    - user info/metrics
    - view previous requests
    - display and compare images

## Database
- Database is held on MongoDB. the username and password is written in `mongodb.py`
- The main class is `User`, which stores all the user info
- The second class is `Requests`, which is an embedded document in `User`



## Image Processing
There are several different image processes performed by the web server. Each is described in the table below. Essentially, images are uploaded from the GUI to the webserver as Base64 strings. The webserver stores the image data with the database as base64. However, in order to process the image, the webserver decodes the Base64 into an Array-like object. This array object is manipulated using functions in the skimage, scipy, and matplotlib libraries to produce modified images. All of the processes described below manipulate the array data of the image to produce images that are slightly different. 

| Name          | Function      |
| ------------- | ------------- |
| Histogram Equalization         | Takes the pixel intensities and evenly distributes the intensity data throughout the entire histogram to produce a higher contrast image |
| Contrast Stretching      | Similar to histogram equalization. Takes the pixel intensities and stretches it. Different than histogram equailzation in that the intensities are not stretched for the full range of pixel intensities. |
| Log Compression | Applies a log filter to the pixel intensities. Low intensity pixels will be "log reduced" less than high intesnity pixels. |
| Reverse Video | Turns black pixels white, and white pixels black. |



