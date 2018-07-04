title: BLOG
type : blog
date : 4-07-2018
post : authenticationless ssh login
comments : on
---


# Authenticationless ssh login

How to setup a user on a machine that anyone can connect to, without asking for a password. This is of course not something to do with a machine that exposes the ssh port to the internet, but I don't see how this would be so bad in a LAN).

So let's say we want to leave access to `freeuser` open.



  1. Remove password : `passwd -d freeuser`
  2. Allow empty password in `/etc/ssh/sshd_config` :
     ```
     PermitEmptyPasswords yes
     ```
  3. Finally, depending on your distro, you might have to modify pam behaviour.

     For example, on debian systems, modify `/etc/pam.d/common-auth` by replacing the line
     ```
     auth    [success=1 default=ignore]      pam_unix.so nullok_secure
     ```
     by
     ```
     auth    [success=1 default=ignore]      pam_unix.so nullok
     ```


