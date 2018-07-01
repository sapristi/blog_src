title: BLOG
type : blog
date : 29-06-2018
post : chroot for a custom environment
---


# chroot for a custom environment

Using a single computer, I found myself wanting multiple times to be able to switch environment based on what I was doing.

For example, when developping, I would like a git-aware prompt in my fish shell. When playing games, I don't want all the 32-bit libraries accumulating in my os. And I don't want to load too much packages in emacs when I am not developping.

In order to achieve this, I will present here a method based on chroot, that enables :

   + to have multiple environments integrated into one : no need to launch a VM, no need to swap sessions
   + to have the environments perform under the same X session
   + to have the users of the main OS enabled on the other environments, simplying system administration
   + to easily setup shared folders across environments


## 1. Installation

 1. Install a bare linux system in a folder
 2. Setup schroot
 3. Setup the new environment

#### 1.1 Install a bare linux system in a folder

This step is highly dependant on the distribution you want to install.
I advise you to look for ways to install a bootstrap of the distribution of your choice. For example

 + debian provides the debootstrap utility
 + archlinux provides bootstrap images that you can decompress in a directory
 + and so on...

I will assume in the rest of this post that an distribution has been installed in the `/envs/myenv` directory of your main OS.

#### 1.2 Setup schroot

schroot is a tool that simplifies the use of chroot. Install the package in your main OS

##### 1.2.1 schroot.conf

The first thing to do is to write a configuration file for schroot. Examples of configuration can be found in the file `/etc/schroot/schroot.conf`. You can either add a configuration to this file, or write a configuration in a new file, which we will do.

I will here assume that we want a chroot to an os with the same architecture, with a shared X session.

Create the file  `/etc/schroot/chroot.d/myenv.conf` and add these lines :

```
[my-environment]
description=custom environment
aliases=myenv
type=directory
directory=/envs/myenv
users=me
root-groups=root
preserve-environment=true
profile=desktop-custom
```

See `man schroot.conf` to describe the provided options.

 + The line `profile=desktop-custom` points schroot to look for specific configuration files in the folder `/etc/schroot/desktop-custom` that we will discuss in the next session.
 + The line `preserve-environment=true` is here to easily enable applications run in the chroot to access the X server, although it could be enabled by other means.

##### 1.2.2 desktop-custom directory

We can copy the `desktop` directory in `/etc/schroot/` to `desktop-custom` and modify it according to our needs. This folder contains three files :

 + `nssdatabases`  that we will not modify.
 + `copyfiles` :
     - add a line with `/home/me/.Xauthority` to enable shared X session.
     - add a line with `/etc/localtime` to setup time.
     - add a line with `/etc/locale.gen` (or `/etc/locale.conf` ?) to setup locale.
   ```
   ZERZER
   ```
 + `fstab` : a custom fstab file. I did some changes to this file :
     - comment out `/home` to have separate user configuration
     - add `/home/Documents  /home/Documents none   rw,bind         0       0` where `/home/Documents` is a folder containing configuration and is meant to be shared between envs.
     - add `/usr/share/fonts /usr/share/fonts none rw,bind          0       0` to share fonts between envs.
     - add `/usr/share/themes /usr/share/themes none rw,bind          0       0` to share themes between envs.


#### 1.3 Setup the new environment

     
Once the previous session is set, you can enter the chroot with the command `schroot -c myenv`

For easier access, you can put a script in your path that launches the terminal emulator of your choice (terminator here). 

```
:::bash
#!/bin/bash

schroot -c dev -- sh -c "terminator"
```

