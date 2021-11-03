const WebSocket = require('ws');

const PORT = 5000;

const wsServer = new WebSocket.Server({
    port: PORT
});

var id = 0;
var id_den = 0;
var lookup = {};
var all = {};
var clients_tag = [];
var is_active = [];

Object.size = function(obj) {
  var size = 0,
    key;
  for (key in obj) {
    if (obj.hasOwnProperty(key)) size++;
  }
  return size;
};

wsServer.on('connection', function (socket) {

    socket.on('message', function (msg) {
      if (msg.slice(0, 3) == "TAG"){
          console.log(msg)
          var ib = socket.id
          var index = search(clients_tag, msg.slice(3));
          if(index != -1){
            console.log(msg.slice(3) + " - just reconnected, id: "+ index);
            lookup[index] = socket;
            socket.id = index;
          }
          else{
            socket.id = id;
            lookup[socket.id ] = socket;
            clients_tag[socket.id] = msg.slice(3);
            console.log(msg.slice(3) + " - just connected, with id: "+ id);
            id++;
          }
        }
      else if(msg.slice(0, 4) == "pong"){
         var index = search(clients_tag, msg.slice(5));
         if(index != -1){
           console.log("active -> id: ", lookup[index].id, "|| TAG: ", clients_tag[index]);
           is_active[index] = true;
         }
        }
        else if(msg.slice(0, 8) == "isactive"){
         var index = search(clients_tag, msg.slice(9));
         let load = {"tag":msg.slice(9), "isActive":false};
         if(index != -1){
           load.isActive = is_active[index];
           }
          var msg_pog = "pong "+JSON.stringify(load);;
          socket.send(msg_pog)
        }

       else{
         const msg_obj = JSON.parse(msg);
         console.log(msg)
         var type;
         if(msg_obj.color != undefined)
           {
             console.log("from "+  msg_obj.user + " to " + msg_obj.device_tag + " || color value: " +  msg_obj.color);
             type = 1;
           }
         if(msg_obj.NEW_TAG != undefined)
           {
             console.log("old tag: " +  msg_obj.device_tag + " device name: " + msg_obj.NAME + " || new tag: " +  msg_obj.NEW_TAG);
             type = 2;
           }

         var online = false;
         var index = search(clients_tag, msg_obj.device_tag);
         if (index != -1){
           console.log("sending to client with id: ", lookup[index].id, "|| TAG: ", clients_tag[index]);
           lookup[index].send(msg);
           online = true;
         }
         if (!online){
           console.log("client is offline");
         }
       }
    });
});




/// functions
const ping = () => {
    for (var i = 0; i < Object.size(lookup); i++){
      lookup[i].send("ping");
      is_active[i]=false;
      console.log('ping', clients_tag[i]);
   }
}

function timeout() {
  setTimeout(function () {
    ping();
    timeout();
  }, 5000);}

function search(arr, what) {
  for (var i = 0; i < Object.size(arr); i++){
   if(arr[i] == what){
     return i;
    }
  }
  return -1;
}

timeout();
console.log( (new Date()) + " Server is listening on port " + PORT);