wsKeyboard
==========

Remote Keyboard Controller based on WebSocket

Requirements
------------

- Built on Python 2.7

WebSocket Transform Protocol
----------------------------

Each message contains 2 bytes:

1. 01 -> Key down, 7F-> Key up
2. Key code (01 - 7F)
