# Nokia contacts converter
Convert Gmail (or any vcard3.0) contacts to Nokia vcard2.1 format with ability to merge 

## Why?

I did not find any other way to put my Gmail contacts into new **"Series 30+ powered Microsoft/Nokia" mobile phone**. There is no way to install any Java app, but you can backup you phone contacts, copy backup.dat file via USB cable and merge with data exported from google using this tool.

## Installation

You will need python2.7 and pip installed on your system. Script require only vobject package.
#### Ubuntu/Debian
```
sudo apt-get install python-pip
sudo pip install virtualenv
```
#### Other linuxes/OSX/Windows
TODO

#### Setup virtual env:
```
virtualenv . --no-site-packages
source bin/activate
pip install -r requirements
```
## Usage

```
./covert3to2.py data/gbackup.dat --file21 data/currentbackup.dat --outfile data/backup.dat
```
Copy backup.dat to mobile phone and use restore menu item.

## TODO
For now only N nd TEL phone is supported but other fields can be easily added
