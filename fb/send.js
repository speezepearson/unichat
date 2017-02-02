#!/usr/bin/node
var login = require("facebook-chat-api");
var fastCsv = require("fast-csv");
var csv = require("csv");

if (process.env.SALAZAR_FB_EMAIL === undefined) throw new Error('SALAZAR_FB_EMAIL should be set');
if (process.env.SALAZAR_FB_PASSWORD === undefined) throw new Error('SALAZAR_FB_PASSWORD should be set');

login({email: process.env.SALAZAR_FB_EMAIL, password: process.env.SALAZAR_FB_PASSWORD}, function callback (err, api) {
    if (err) return console.error(err);

    // stream = fastCsv({headers: true})
    //   .on('data', function(data) {
    //     console.log('sending:', data);
    //     api.sendMessage(data.content, data.thread)
    //   });
    stream = csv.parse().on('data', function(data) {
      console.log('sending:', data);
      api.sendMessage(data[3], data[1])
    });
    process.stdin.pipe(stream);
});
