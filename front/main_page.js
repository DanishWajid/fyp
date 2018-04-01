const app = require('express')()
const http = require('http').Server(app)

app.get('/', function(req, res) {

  if ('text' in req.query) {
    document.getElementById("text_div").style.visibility = "Visible"
    document.getElementById("text").style.visibility = "Visible"
    document.getElementById("tbl-header").style.visibility = "hidden"
    document.getElementById('text').innerHTML = req.query.text

    for (var i = 1; i <= 5; i++) {
      document.getElementById("div" + i.toString()).style.visibility = "hidden";
      document.getElementById(i.toString()).style.visibility = "hidden";

    }
  }

  if ('list' in req.query) {
    var my_array = req.query.list.split('_')
    document.getElementById("text_div").style.visibility = "hidden"
    document.getElementById("text").style.visibility = "hidden"
    document.getElementById("tbl-header").style.visibility = "hidden"
    for (var i = 1; i <= my_array.length; i++) {
      document.getElementById("div" + i.toString()).style.visibility = "Visible";
      document.getElementById(i.toString()).style.visibility = "Visible";
      document.getElementById(i.toString()).innerHTML = my_array[i - 1]

    }
  }

  if ('prompt' in req.query) {
    document.getElementById('prompt').innerHTML = req.query.prompt
  }
  if ('image' in req.query) {
    var img = document.createElement("img");
    img.src = req.query.image
    var src = document.getElementById("text");
    src.appendChild(img);

  }
  if ('currency' in req.query) {
    document.getElementById("text_div").style.visibility = "hidden"
    document.getElementById("text").style.visibility = "hidden"
    var my_array = req.query.currency.split(',')
    var myTable = document.getElementById('tbl');
    for (var i = 1; i <= my_array.length; i++) {
      myTable.rows[i].cells[2].innerHTML = my_array[i - 1];

    }
    document.getElementById("tbl-header").style.visibility = "Visible"
    for (var i = 1; i <= 5; i++) {
      document.getElementById("div" + i.toString()).style.visibility = "hidden";
      document.getElementById(i.toString()).style.visibility = "hidden";
    }
  }
  res.end()
})
http.listen(8080)
