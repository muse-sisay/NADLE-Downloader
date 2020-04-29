![NADLE logo](http://ndl.ethernet.edu.et/image/NADLE-jspui2.png)

# NADLE Downloader

> The National Academic Digital Library of Ethiopia (NADLE) is a project under Ministry of Science and Higher Education, Ethiopia. The objective is to collect and collate metadata and provide full text index from several national and international digital libraries, as well as other relevant sources. It is a academic digital repository containing textbooks, articles, audio books, lectures, simulations, fiction and all other kinds of learning media. The NADLE provides free of cost access to many academic books in English and the Other languages. [NADLE](http://ndl.ethernet.edu.et/) 

A small python tool for downloading from NADLE.

```
Usage: nadle-dl.py [OPTIONS] COMMAND [ARGS]...

  A small python script to facilitate downloading books from NADLE.

Options:
  -o, --output PATH  Output path for downloaded files
  --help             Show this message and exit.

Commands:
  download  Download a single book or a collection
  scrape    Download all the books from NADLE.

```


## Example / Usage

#### Download a Single book or a Collection
Take the **ID** of a book/collection and pass it to the subcommand *download*.

``` shell
BOOK = Python For Everyone
URL  = http://ndl.ethernet.edu.et/handle/123456789/32346
ID   = 32346

$ python3 nadle-dl.py download 32346
```

```shell
COLLECTION = Information and Computer Science
URL 		 = http://ndl.ethernet.edu.et/handle/123456789/43
ID 			 = 43

$ python3 nadle-dl.py download 43

```

##### Download the entire site

```shell
$ python3 nadle-dl.py scrape

```


-
Note

- This project is **NOT** affiliated with, funded, or in any way associated with the organnization NADLE (National Academic Digital Library of Ethiopia). Use it at your own risk!

