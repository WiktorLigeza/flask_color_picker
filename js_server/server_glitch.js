const WebSocket = require('ws');

const PORT = 5000;

const wsServer = new WebSocket.Server({
    port: PORT
});

var id = 0;
var id_den = 0;
var clients = [];
const went_silent_th = 3; //interval after which not responding client is_active flag is set to false
const drop_th = 10; //interval after which not responding client is dropped from clients list

Object.size = function(obj) {
  var size = 0,
    key;
  for (key in obj) {
    if (obj.hasOwnProperty(key)) size++;
  }
  return size;
};

wsServer.on('connection', function (socket) {
    socket.on('close', function (socket){
      console.log("Connection closed")
    });

    socket.on('message', function (msg) {
      const msg_obj = JSON.parse(msg);

      // TAG HANDLER
      if (msg_obj.head == "first_connection"){
          var ib = socket.id
          var client = search(clients, msg_obj.TAG);
          if(client != null){
            console.log(client.clients_tag + " - just reconnected, id: "+ client.id);
            client.is_active = true;
            client.socket = socket;
            client.timeout_terator = 0;
          }
          else{
            var client = new Object();
            socket.id = id;
            client.id = id;
            client.socket = socket;
            client.timeout_terator = 0;
            client.clients_tag = msg_obj.TAG;
            console.log(client.clients_tag + " - just connected, with id: "+ client.id);
            client.is_active = true;
            id++;
            clients.push(client)
          }
        }

      // PONG HANDLER
      else if(msg_obj.head == "pong"){
         var client = search(clients, msg_obj.TAG);
         if(client != null){
           console.log("active -> id: ", client.id, "|| TAG: ", client.clients_tag);
           client.is_active = true;
           client.timeout_terator = 0;
         }
        }

      // IS ACTIVE HANDLER
      else if(msg_obj.head == "isactive"){
         var client = search(clients, msg_obj.TAG);
         let load = {"tag":msg_obj.TAG, "isActive":false};
         if(client != null){
           load.isActive = client.is_active;
           }
          var msg_pog = "pong "+JSON.stringify(load);
          socket.send(msg_pog)
        }

      // SET HANDLER
      else if(msg_obj.head == "set"){
         var client = search(clients, msg_obj.TAG);
         if (client != null){
           console.log("sending to client with id: ", client.id, "|| TAG: ", client.clients_tag);
           client.socket.send(msg);
         }
         else{
           console.log("client is offline");
         }
       }
    });
});

//https://stackoverflow.com/questions/50876766/how-to-implement-ping-pong-request-for-websocket-connection-alive-in-javascript


/// functions
const ping = () => {
  clients.forEach(function_ping);
}


function function_ping(client, index, arr){
  if(client.timeout_terator >= drop_th){
    console.log("dropping client: ", client.clients_tag);
    console.log(index)
    clients.splice(index, 1);

  }
  else{
    try{
      if(client.timeout_terator == went_silent_th){
          console.log("went silent:", index, client.clients_tag);
          client.is_active = false;
        }
      client.timeout_terator+=1;
      client.socket.send('{"type": "ping"}');
      console.log('ping', client.clients_tag, client.timeout_terator);
    }
    catch{}
  }
}


function timeout() {
  setTimeout(function () {
    ping();
    timeout();
  }, 5000);}

function search(arr, what) {
  var output = null;
  arr.forEach((client, index, arr)=>{
              if(client.clients_tag== what){
                output = client;
              }
            });
  return output
}

function get_index(arr, what) {
  var index = 0;
  arr.forEach((client, index, arr)=>{
              if(client.clients_tag== what){
                return index;
              }
              index += 1;
            });
  return null;
}

timeout();
console.log( (new Date()) + " Server is listening on port " + PORT);