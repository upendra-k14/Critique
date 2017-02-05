$(document).ready(function () {
  var data = {{tree_object | safe}};
  var source ={datatype: "json",datafields: [{ name: 'id' },{ name: 'parentid' },{ name: 'text' }],
      id: 'id',localdata: data};
  var dataAdapter = new $.jqx.dataAdapter(source);
  dataAdapter.dataBind();
  var records = dataAdapter.getRecordsHierarchy('id', 'parentid', 'items', [{ name: 'text', map: 'label'}]);
  $('#jqxWidget').jqxTree({ source: records, width: '300px',checkboxes:true, hasThreeStates:true});
  $('#jqxWidget').css('visibility', 'visible');
  $("#jqxbutton").jqxButton({theme: 'energyblue',width: 200,height: 30  });
  $('#jqxbutton').click(function () {
      var str = "";
      var items = $('#jqxWidget').jqxTree('getCheckedItems');
      for (var i = 0; i < items.length; i++) {
          var item = items[i];
          str += item.label + "<br>";
        }
        console.log(str);
        alert(str);
        document.getElementById("content").innerHTML = 'You selected the following classes:<br><div id = "string">'+str+'</div>Would you like to confirm?<br><input type="button" id ="confirm" onClick="divFunction()" value="Confirm"/>';
  });
});
