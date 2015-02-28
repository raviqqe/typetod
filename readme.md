# typetod
##type anything forever
Here is [its tarball](https://github.com/raviqqe/typetod/raw/master/pkg/typetod-0.01.tar.gz).
And you can see [the videos on my website](http://www.raviqqe.com/typetod/).

![typetod screenshot](pic/screenshot.png)

## What is typetod?
typetod is a typing game that works on a terminal. It has four modes;

* fortune mode
* files mode
* RSS feeds mode
* stdin mode

When you choose stdin mode or others with -d option, typetod becomes endless
mode. It lets you type forever. And, typetod also evaluate your typing speed
and accurancy.

## Game modes
### fortune mode
  Like gtypist, it takes benefitial tips from fortune command as samples.
### files mode
  Text in files as samples.
### RSS feeds mode
  If you specify the url of a RSS feed, items of the feed will appear on your
  screen. Then, you can select one of them as a sample.
### stdin mode
  In this mode, typetod reads lines one by one from stdin adding it to the
  buffer of samples during the game. You can use a pipe to do that.

## FAQ
### How do you pronounce it?
type-to-D
### What is its license?
typetod is unlicensed. I mean all source codes of typetod are in public domain
and anyone can utilize them for theirselves.
See [the page of unlicense.org](http://unlicense.org/).
### I don't like this app! I'll scold you. First, it does not adhere the unix design prin...
Mail [me](mailto:raviqqe@gmail.com).

## Specification
* typing game with endless mode
* one input line and sample lines scrolling upwards
* fortune, text files, rss feeds, and stdin as samples
* fast as possible in python
