title: ACHEM
menu-position: 4
type: page
category: achem
---

Presenting an artificial chemistry based on petri nets.

A running simulation can be found [here](http://artlife.ml:51461/).
Sources can be found [here](https://github.com/sapristi/alife/tree/dev)

## Context

Multiple attempts have been made to create artificial chemistries that can support « life »; or, to be
more precise, where evolution can take place (the Game of Life, Tierra, Avida, Hutton's chemistry to cite some of them).

YAACS is another attempt to tackle this challenge.

## Overview

In the real (very simplified) world, the operation of a biological cell is based on proteines :

* a proteine is a string of aminate acids; this means it is easy to create for a recipe (the DNA) :
   it is basically a linear read/write operation.
 * in its folded form, a proteine can perform functions on regular molecules or other proteines.


YAACS takes it's inspiration on those facts in the following way :

 * *molecules* are strings of *atoms*
 * certain patterns in molecules are decoded as *acids*
 * *proteines* (strings of *acids*) can be folded to constuct a *petri net*, the functional form of a *protein*

The [Petri Nets](https://en.wikipedia.org/wiki/Petri_net) are extended with custom properties, in order to provide the possibility to duplicate an arbitrary molecule. In other words, the set of rules is designed so that basic duplication can take place in YAACS world.




