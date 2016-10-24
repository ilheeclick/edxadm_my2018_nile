/**
 * Created by dev on 2016. 10. 24..
 */
$(document).ready(function(){
    var html="";
    $('#loading').hide();
    $.ajax({
        url : '/certificate/',
        data :{
            method : 'org'
        }
    }).done(function(data){
        //console.log(data)
        html+="<option>선택하세요.</option>";
        for(var key in data){
            //alert(data[key]);
            html+="<option id="+key+">"+data[key]+"</option>"
        }
        $('#org').html(html);
    })
});