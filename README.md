# About LExTeS
LExTeS: Link Extraction and Testing Suite is a series of scripts written for the paper Schroedinger's Code: A Preliminary Study on Research Source Code Availability and Link Persistence in Astrophysics (ApJS, in press). 

# Requirements
Python 2.7 and the pyPdf and sqlite3 libraries.

# Instructions
`process_pdfs.py foo/*.pdf` scrapes all links from the PDFs in `foo/`, filters out domains and protocols irrelevant to our paper, and stores the remaining links in `links.sqlite`, along with information about which paper each link is from.

`check_links.py` tests each link in the `links.sqlite` database and stores each result to the `checks` column of the database.

`link_data.py` displays information about the results of the `check_links.py` runs: how many links worked consistently, how many only worked in some checks, how many didn't work in any checks, etc.
