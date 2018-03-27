const app = require('express')()
const http = require('http').Server(app)

app.get('/', function(req, res){

    if ('text' in req.query) {
        document.getElementById("text_div").style.visibility="Visible"
        document.getElementById("text").style.visibility="Visible"
        document.getElementById('text').innerHTML = req.query.text

        for (var i = 1; i <=7; i++) {
            document.getElementById("div"+i.toString()).style.visibility="hidden";
            document.getElementById(i.toString()).style.visibility="hidden";
            

        }
    }
   if('list' in req.query){
        var my_array = req.query.list.split('_')
        document.getElementById("text_div").style.visibility="hidden"
        document.getElementById("text").style.visibility="hidden"
        for (var i = 1; i <= my_array.length; i++) {
            document.getElementById("div"+i.toString()).style.visibility="Visible";
            document.getElementById(i.toString()).style.visibility="Visible";
            document.getElementById(i.toString()).innerHTML = my_array[i-1]

        }
    }

    if ('prompt' in req.query) {
        document.getElementById('prompt').innerHTML = req.query.prompt
    }


    res.end()
})

http.listen(8080)
