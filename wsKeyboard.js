(function (global) {
  var DEFAULT_PORT = 13579,
      ws = null,
      isonline = false,
      onconnected = null,
      onerror = null,
      ondisconnected = null,
      _wsKeyboard = null,
      wsKeyboard = {
        'online': online,
        'connected': connected,
        'error': error,
        'disconnected': disconnected,
        'connect': connect,
        'keyDown': keyDown,
        'keyUp': keyUp,
        'disconnect': disconnect
      };

  function online() {
    return isonline;
  }

  function connected(callback) {
    onconnected = callback;
    return wsKeyboard;
  }

  function error(callback) {
    onerror = callback;
    return wsKeyboard;
  }

  function disconnected(callback) {
    ondisconnected = callback;
    return wsKeyboard;
  }

  function connect(port, hostname) {
    if (typeof port === 'undefined') port = DEFAULT_PORT;
    if (typeof hostname === 'undefined') hostname = location.hostname;
    ws = new WebSocket('ws://' + hostname + ':' + port + '/');

    ws.onopen = function () {
      isonline = true;
      if (typeof onconnected === 'function')
        onconnected();
    };
    ws.onerror = function (event) {
      console.log(event);
      if (typeof onerror === 'function')
        onerror();
    };
    ws.onclose = function () {
      isonline = false;
      if (typeof ondisconnected === 'function')
        ondisconnected();
    };

    return wsKeyboard;
  }

  function keyDown(code) {
    ws.send('\x01' + String.fromCharCode(code));
    return wsKeyboard;
  }

  function keyUp(code) {
    ws.send('\x7E' + String.fromCharCode(code));
    return wsKeyboard;
  }

  function disconnect() {
    ws.close();
    return wsKeyboard;
  }

  if ('module' in global && module.export) {
    module.export = wsKeyboard;
  } else {
    if ('wsKeyboard' in global) {
      _wsKeyboard = global.wsKeyboard;
      wsKeyboard.noConflict = function () {
        global.wsKeyboard = _wsKeyboard;
        return wsKeyboard;
      };
    }
    global.wsKeyboard = wsKeyboard;
  }
})(this);