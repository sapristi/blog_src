title: YAAC
menu-position: 4
type: page
category: achem
---

Presenting YAAC, yet another artificial chemistry based on petri nets.

A running simulation can be found [here](http://artlife.ml:51461/).
Sources can be found [here](https://github.com/sapristi/alife/tree/dev)

## Context

Multiple attempts have been made to create artificial chemistries that can support « life »; or, to be
more precise, where evolution can take place (the Game of Life, Tierra, Avida, Hutton's chemistry to cite some of them).

YAAC is another attempt to tackle this challenge.

## Presentation

YAAC takes it's inspiration from a (very simplified) vision of the operation of a biological cell, and especially of proteins :

 * A proteine is a string of aminate acids; this means it is easy to create one using a recipe (the DNA) :
   it is basically a linear read/write operation.
 * In its folded form, a proteine can perform functions on regular molecules or other proteines.
 
An artificial chemistry is a system that contains *molecules*, that live in a *world*, and that interact following *chemical reaction*. In this context, YAAC can be described as follow : 

 * An **atom** is a letter in the range [A-F].
 * A **molecule** is a  string of **atoms**.
 * Certain patterns in molecules are decoded as **acids**.
 * A **proteine** (a string of **acids**) can be folded to constuct a **petri net**, the functional form of a **protein**.
 * **Chemical reactions** are of two types :
     * some reactions are performed by the **petri nets**.
     * some reactions are statically defined.
 * Finally, the **world** is a dimensionless space.


We will talk more about YAAC's particular petri nets in the next section; let us say for now that they are extended versions of regular [Petri Nets](https://en.wikipedia.org/wiki/Petri_net), in such a way that they provide the possibility to create a petri net that can duplicate an arbitrary molecule. In other words, the extensions are designed so that basic duplication can take place in YAAC's world.    


## More details

### YAAC's petri nets

A petri net is a bipartite graph, where

 * a node is either a **place** or a **transition**
 * an **arc** links either a **place** to a **transition**, or a **transition** to a **place**
 * **tokens** can be present in **places**; when a **transition** is **launched**, tokens present in the **places** leading to this **transition** will be moved to the **places** following the **transition**.




The extensions to petri nets provided by YAAC are

* A **token** can hold a molecule, and then keeps a cursor to a position in the molecule.
* A **place** can hold at most one token. It can be extended with properties that allow it to interact with the world. For example,
   
     * catch another molecule from the world and create a token that contains it
     * when it receives a token, it will release the molecule inside of it back to the world

* An **arc** can be extended with properties that allow it to modify the molecules present in the **tokens** that go through this arc. More precisely, the possible actions are :
     * move the cursor forward or backward.
     * cut the holded molecule at the position defined by the cursor. This will create a new token that will hold the dangling part of the molecule. This action is only available to arcs that lead to a transition
     * bind 




