// api initialize

var ROOT = 'https://project-gabriel.appspot.com/_ah/api';
var userId = 5684453372329984;

function init() {
    gapi.client.load('gabriel', 'v1', function() {
        setInterval(getUser, 3000);
    }, ROOT);
}

function getUser() {
    gapi.client.gabriel.users.get({
        id: userId
    }).execute(function(res) {
        showStatus(res);
    });
}

var counter = 1;

function showStatus(user) {
    $('#name').text(user.name)
    $('#eda').text(Math.round(user.eda * 100) / 100);
    $('#hr').text(Math.round(user.hr * 100) / 100);
    $('#acc').text(Math.round(user.acc * 100) / 100);
    $('#stress').text(Math.round(user.stress * 100) / 100);
    
    $('#counter').text(counter);
    counter++;
}















