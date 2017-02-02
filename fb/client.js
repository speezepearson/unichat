#!/usr/bin/node
var login = require("facebook-chat-api");
var csv = require("csv");

if (process.env.SALAZAR_FB_EMAIL === undefined) throw new Error('SALAZAR_FB_EMAIL should be set');
if (process.env.SALAZAR_FB_PASSWORD === undefined) throw new Error('SALAZAR_FB_PASSWORD should be set');

var csvWriter = csv.stringify()
csvWriter.pipe(process.stdout)

login({email: process.env.SALAZAR_FB_EMAIL, password: process.env.SALAZAR_FB_PASSWORD}, function callback (err, api) {
    if (err) return console.error(err);

    api.listen(function callback(err, message) {
      if (message.type == 'message') {
        csvWriter.write([
          message.threadID,
          message.senderID,
          message.body]);
      }
    });

    var sendingStream = csv.parse().on('data', function(data) {
      api.sendMessage(data[3], data[1])
    });
    process.stdin.pipe(sendingStream);
});
