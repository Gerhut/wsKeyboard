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
        'press': press,
        'disconnect': disconnect,
      };

  function online() {
    return isonline;
  }

  function connected(callback) {
    return wsKeyboard;
  }

  function error(callback) {
    return wsKeyboard;
  }
  
  function disconnected(callback) {
    return wsKeyboard;
  }

  function connect(port, hostname) {
    if (typeof port === 'undefined') port = DEFAULT_PORT;
    if (typeof hostname === 'undefined') hostname = location.hostname
    ws = new WebSocket('ws://' + hostname + ':' + port + '/');
    
    ws.onopen = function () {
      isonline = true;
      if (typeof onconnected === 'Function')
        onconnected();
    };
    ws.onerror = function () {
      if (typeof onerror === 'Function')
        onerror();
    };
    ws.onclose = function () {
      isonline = false;
      if (typeof ondisconnected === 'Function')
        ondisconnected();
    };

    return wsKeyboard;
  }

  function press(code) {
    ws.send(code.toString());
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