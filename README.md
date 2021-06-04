# dnf-dbus
A DBus backend for interfacing with the dnf package manager

**This is very early in development, so everything can change**

## Goals
 * Written using the latest python (3.9)
 * Use dasbus for DBUS handling
 * All core code should be coved by unit tests
 * Use only DNF public API
 * clean code and easy to use API

## What about dnfdaemon ?
dnfdaemon was designed as a replacement for yumdaemon, to be a package backend for Yum Extender.
Dnf public API was not very mature at that time, so there is a lot of code copied for dnf and private internal API used.
This give problems with dnfdaemon breaking when internals change inside DNF.
dnfdaemon is used by other applications, so it is very hard to clean it up, because API must be kept stable.