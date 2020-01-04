# pySurvey

A small python library to read/write data to and from .xlsx templates defined by named 
ranges in the .xlsx file. 

## Installation

Clone this reposistory, all functions and objects can be found in `pySurvey.py`

## Usage

* Create an .xlsx file which will serve at the template for your survey. 
* The points at which a user can enter data need to be selected as a named range
* **A named ranged must also exist, at the same size as the data range, somewhere in the workbook called `<namedRange>Tags` which contains a short string with which each data item will be tagged.**
* Upon recieveing a completed survey `load_survey_data` can extract the data in the named ranges, based on the original template. If the user has altered the file in anyway this will error by design. 

## Contributors 
Ben Corcoran - *2019*
