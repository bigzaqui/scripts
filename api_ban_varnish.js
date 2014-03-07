//Nodejs varnish API ban url or hosts. usage:
//http://localhost:4321/clean/host?v=machine1.mydomain.com
//http://localhost:4321/clean/url?v=aHR0cHM6Ly93d3cuZ29vZ2xlLnNlLz9nZmVfcmQ9Y3ImZWk9ZWNVWlU2cmVNWUhLOGdmbXBJR1lCUQ==
//the basecode64 is the full URL -> "https://www.google.se/?gfe_rd=cr&ei=ecUZU6reMYHK8gfmpIGYBQ"

//Bugs: This is an internal tool so I was not really careful with the escape characters when pasing the URL... if you are going to use this in a production environment focus more on that!

var express = require('express');
var URI = require('URIjs');
var app = express();
var sys = require('sys')
var exec = require('child_process').exec;
var child;
var run = "";


app.get('/clean/:type', function(req, res) {
p = req.query.v;
if (req.params.type == "host")
{
        run = "req.http.host";
} else if (req.params.type == "url")
{
        run = "req.url";
        url = new Buffer(p, 'base64').toString('ascii');
        url = url.replace(/\\/g,'');
        p = URI(url).pathname() + URI(url).search();
}
command = "varnishadm ban "+ run + " == \"" + p+"\"";
sys.print(command);
child = exec(command, function (error, stdout, stderr) {
sys.print('stdout: ' + stdout+ p);
sys.print('stderr: ' + stderr);
  if (error !== null) {
    res.send(500,{"error": error, "output":stderr});
  } else{
    res.send("ok");
}
});
});

app.listen(4321);
console.log('Listening on port 4321...');


