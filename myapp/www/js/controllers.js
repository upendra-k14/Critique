angular.module('starter.controllers', ['ionic-toast'])

.controller('HomeCtrl', function($scope, $http,$httpParamSerializerJQLike,$location,ionicToast) {
    if(localStorage.getItem("auth_token") !== null && localStorage.getItem("auth_token") !== ""){
        var username = localStorage.getItem("username");
        var token = localStorage.getItem("auth_token");
        var send = {
            'username':username,
            'auth_token':token
        };
        var url =' http://10.0.3.191:8000/api/check_session/'
    	$http({
    		url:url,
    		method:'POST',
    		data:$httpParamSerializerJQLike(send),
    		headers : {"Content-Type" : "application/x-www-form-urlencoded"}})
    		.then(function(response){
    			status = response.data.message;
    			if (status === 'activesession'){
                     $location.path("/tab/dash");
    			}
    			else {
    				alert(status);
    			}
    		},
    		function(response){
    			alert("error")
    		});
    }
    $scope.login=function(){
        var uname = document.getElementById('uname').value;
        var pass = document.getElementById('pass').value
        if (uname === '')
		alert("Username Required")
	    else if (pass === '')
		alert('Password Required')
        var send = {
		'username' : uname,
		'password' : pass
	};
    var url =' http://10.0.3.191:8000/api/mobile_login/'
	var status = 'failed'
	$http({
		url:url,
		method:'POST',
		data:$httpParamSerializerJQLike(send),
		headers : {"Content-Type" : "application/x-www-form-urlencoded"}})
		.then(function(response){
			status = response.data.login_status
			if (status === 'success'){
                localStorage.setItem("username", response.data.username);
                localStorage.setItem("rollno", response.data.rollno);
                localStorage.setItem("auth_token", response.data.auth_token);
                 $location.path("/tab/dash");
			}
			else {
				alert(status);
			}
		},
		function(response){
			alert("error")
		});
    /*    if(true){
             $location.path("/tab/dash");
        }
        else {

         ionicToast.show('Login Failed', 'top', true, 500);
     }*/
    };
})

.controller('DashCtrl', function($scope) {})

.controller('ChatsCtrl', function($scope, $http,$httpParamSerializerJQLike,$location,Chats) {
  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //
  //$scope.$on('$ionicView.enter', function(e) {
  //});
  var username = localStorage.getItem("username");
  var auth_token = localStorage.getItem("auth_token");
  var send = {
      'username':username,
      'auth_token':auth_token
  };
  var url ='http://10.0.3.191:8000/api/get_requested_feedbacks/'
  $http({
      url:url,
      method:'POST',
      data:$httpParamSerializerJQLike(send),
      headers : {"Content-Type" : "application/x-www-form-urlencoded"}})
      .then(function(response){
          status = response.data.message;
          if (status === 'activesession'){
               localStorage.setItem("requested_feedbacks",response.data.requested_feedbacks);
               $scope.chats = response.data.requested_feedbacks;
          }
          else {
              alert(status);
              $location.path("/home");
          }
      },
      function(response){
          alert("error")
      });
})

.controller('ChatDetailCtrl', function($scope,$http,$httpParamSerializerJQLike, $location,$stateParams, Chats) {

$scope.submit = function(){
 var reqid = $stateParams.chatId;
 var  cname = $stateParams.cname;
 var rq_fed = localStorage.getItem("requested_feedbacks");
 var rq_item = {}
 for(var i =0 ;i<rq_fed.length ; i++){
     console.log(rq_fed[i].rqst_id,reqid);
     if(rq_fed[i].rqst_id == reqid){
         rq_item = rq_fed[i];
         break;
     }
 }
 rq_item['username']=localStorage.getItem("username");
 rq_item['auth_token']=localStorage.getItem("auth_token");
 var send = {};
 send["How would you rate the course on the whole ?"]=document.getElementById("1").value;
 send["Level of effort you put into the course:"]=document.getElementById("2").value;
 send["You level of knowledge at the start and end of the course:"]=document.getElementById("3").value;
 send["Would you recommend this course to your friends ? "]=document.getElementById("4").value;
 send["Were the course contents interesting and challenging ?"]=document.getElementById("5").value;
 send["Would you like to learn more about the concepts presented in the course ?"]=document.getElementById("6").value;
 send["The instructor’s knowledgeability on the subject."]=document.getElementById("7").value;
 send["The instructor demonstrated enthusiasm in teaching the topics."]=document.getElementById("8").value;
 send["Did the instructor respond to the questions properly ?"]=document.getElementById("9").value;
 send["The tutorial time used efficiently. "]=document.getElementById("10").value;
 send["TA’s are effective in helping you learn."]=document.getElementById("11").value;
 send["The number of lab exercises were sufficient."]=document.getElementById("12").value;
 send["Anything else you care to share or get off your chest?"]=document.getElementById("13").value;
 rq_item['json_feedback'] = JSON.stringify(send);
 rq_item['course_name'] = cname;
 rq_item['rqst_id'] = reqid;

 alert(JSON.stringify(rq_item))
 var url ='http://10.0.3.191:8000/api/receive_feedback/'
 $http({
     url:url,
     method:'POST',
     data:$httpParamSerializerJQLike(rq_item),
     headers : {"Content-Type" : "application/x-www-form-urlencoded"}})
     .then(function(response){
         status = response.data.message;
         if (status === 'submitted feedback'){
             alert("success")
             $location.path("/tab/chats");
         }
         else {
             alert(status);
             $location.path("/tab/chats");
         }
     },
     function(response){
         alert("error")
     });

 }
})

.controller('AccountCtrl', function($scope,$location) {
  $scope.logout = function(){
      localStorage.setItem("auth_token","");
      localStorage.setItem("username","");
      localStorage.setItem("rollno","");
       $location.path("/home");
  }
});
