const WebSocket = require('ws');

const PORT = 5000;

const wsServer = new WebSocket.Server({
    port: PORT
});

var id = 0;
var id_den = 0;
var clients = [];


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
           load.isActive = client.is_active; // TODO FIX
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
  client.is_active=false;
  if(client.timeout_terator >= 4){
    console.log("dropping client: ", client.clients_tag);
  }
  else{
    try{
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


timeout();
console.log( (new Date()) + " Server is listening on port " + PORT);