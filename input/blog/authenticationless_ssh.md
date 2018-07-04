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
  2. Allow empty password in sshconfig :

  ```
  /etc/ssh/sshd_config
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  ...
  PermitEmptyPasswords yes
  ...
  ```
  3. Modify pam authentication parameters :
  ```
  /etc/pam.d/common-auth
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  
  auth    [success=1 default=ignore]      pam_unix.so nullok
  ```


