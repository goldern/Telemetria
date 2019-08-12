var
	app = require('express')(),
	hbs = require('express-handlebars'),
	handlebars = require('handlebars'),
	http = require('http').createServer(app),
    io = require('socket.io')(http),
    server = io.listen(5555);

let
    sequenceNumberByClient = new Map();
	
app.set('view engine', 'hbs');
app.set('views', 'views');

app.listen(5556, function () {
  console.log('Example app listening on port 5556');
});


// Our template
const source = `
{{message}}
`;



var pou = 1;


	
// event fired every time a new client connects:
server.on("connection", (socket) => {
	console.info('Server started on port 5555');
    console.info(`Client connected [id=${socket.id}]`);
    // initialize this client's sequence number
    sequenceNumberByClient.set(socket, 1);

    // when socket disconnects, remove it from the list:
    socket.on("disconnect", () => {
        sequenceNumberByClient.delete(socket);
        console.info(`Client gone [id=${socket.id}]`);
    });
	// What happens when a message is received:
	socket.on("message", (data) => {
		console.info('Received message');
		
		testBuff = new Buffer.from(data, 'iso-8859-1').toString('base64');
		result = "data:image/jpg;base64," + testBuff;
		// Our data source
		var params = {
		  message: result
		};
		
		// Use strict mode so that Handlebars will throw exceptions if we
		// attempt to use fields in our template that are not in our data set.
		var template = handlebars.compile(source, { strict: false });
		var resultado = template(params);
		//console.log(resultado);
		
		app.get('/', function (req, res) {
			//testBuff = new Buffer.from(data, 'iso-8859-1').toString('base64');
			//var result = "data:image/jpg;base64," + testBuff;
			//res.render('index', {message: result} );
			res.render('index', {message: resultado} );
			//console.log(data);
		});
	});
});