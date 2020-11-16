const crypto = require('crypto ');
const downloadMD5 = crypto.createHash('md5 ');
var net = require('net ');
var fs = require('fs ');
var buffer = require('buffer ');
var HOST = '0.0.0.0 ';
var params = process.argv;
var fileName = String(params.slice(2, 3));
var dir = "C:\\ Snort \\ log"; // \\" + fileName . split ('. pcap ') [0];
var file_size = params.slice(3, 4);
var md5 = params.slice(4, 5);
var PORT = parseInt(params.slice(5, 6));
var downloadedBytes = 0;
// test that args were being received correctly
// process . send (" arguments : " + params . slice (2, 3) + "\n" + params . slice (3, 4) + "\n" + params . slice (4, 5));
// process . send (" filename : " + params . slice (2, 3));
var fileStream = fs.createWriteStream(dir + '\\ ' + fileName);
var server = net.createServer(function (sock) {
    process.send('Downloading PCAP : \n');
    downloadedBytes = sock.on('data ', function (data) {
        // fs. access (file , fs. constants .W_OK , (err ) => {
        // process . send (`${ file } ${err ? 'is not writable ' : 'is writable '}`);
        // });
        downloadedBytes += data.length;
        fileStream.write(data);
    });
    sock.on('close ', function (data) {
        process.send('Download Complete ');
        // process . send (" Downloaded : "+ downloadedBytes + " bytes ");
        server.close();
        // md5Verification ();
        process.exit()
    });
});
server.once('error ', function (err) {
    if (err.code === 'EADDRINUSE ') {
        process.send('Port Already in Use !: \n');
        process.exit()
    }
});
server.listen(PORT, HOST);
process.send('Transfer Server bound on ' + HOST + ':' + PORT);
