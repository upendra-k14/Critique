angular.module('starter.controllers', [])

.controller('DashCtrl', function($scope) {})

.controller('LoginCtrl', function($scope,$http,$httpParamSerializerJQLike) {
	$scope.login=function (){
	var uname = document.getElementById('uname').value
	var pass = document.getElementById('pass').value
	if (uname === '')
		alert("Username Required")
	else if (pass === '')
		alert('Password Required')
	var send = {
		'username' : uname,
		'password' : pass
	};
	var url =' http://127.0.0.1:8000/api/mobile_login/'
	var status = 'failed'
	$http({
		url:url,
		method:'POST',
		data:$httpParamSerializerJQLike(send),
		headers : {"Content-Type" : "application/x-www-form-urlencoded"}})
		.then(function(response){
			status = response.data.login_status
			if (status === 'success'){
				alert('success' + response.data.id)
			}
			else if(status === 'failed'){
				alert('failed')
			}
		},
		function(response){
			alert("error")
		});
	
	document.getElementById('uname').value=''
	document.getElementById('pass').value=''
	}	
})

	
	