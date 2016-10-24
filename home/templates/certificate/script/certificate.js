/**
 * Created by dev on 2016. 10. 20..
 */
//대학명 처리
$(document).ready(function(){
    var html="";
    var value_list=[];
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

    $.ajax({
        url : '/certificate/',
        data : {
            method : 'uni_certificate'
        }
    }).done(function(data){
        value_list = data.split(5);
        console.log(value_list)
    })
});

//강좌명 처리
$(document).on('change', '#org', function(){
    var org = $(this).find('option:selected').attr('id');
    var html = "";

    if(org == '' || org == null){
        alert('학교를 선택하세요.');
    }else{
        html="";
        $.ajax({
            url : '/certificate/',
            data : {
                method : 'course',
                org : org
            }
        }).done(function(data){
            html+="<option>선택하세요</option>";
            if(data != ''){
                for(var key in data){
                    html+="<option id="+key+">"+data[key]+"</option>"
                }
            }
            $('#course').html(html);
            $('#run').html(html)
;        });

    }
});

//기관별 강좌번호 처리
$(document).on('change', '#course', function(){
    var course = $(this).find('option:selected').attr('id');
    var html = "";
    //if(course == '' || course == null){
    //    alert('error');
    //}else{
    //    html="";
    //    $.ajax({
    //        url : '/certificate/',
    //        data : {
    //            method : 'run',
    //            course : course
    //        }
    //    }).done(function(data){
    //        html+="<option>선택하세요</option>";
    //        html+="<option id="+data+">"+data+"</option>";
    //        $('#run').html(html);
    //    })
    //}
});

//이수증 생성 처리
$('#create_certi').on('click', function(){
    var ready_certi = $('#uni').val();
    var org_id = $('#org').find('option:selected').attr('id');
    var course_pb= $('#course').find('option:selected').attr('id');
    var run= $('#run').find('option:selected').val();
    //alert('org_id == '+org_id+' course_id == '+course_id+' run == '+run);

    if(ready_certi == ''){
        $('#loading').show();
        $.ajax({
            url : '/certificate',
            data : {
                method : 'create_certi',
                org_id : org_id,
                course_pb : course_pb,
                run : run
            }
        }).done(function(data){
            if(data == 'success'){
                $('#loading').hide();
                alert('이수증 생성이 완료되었습니다.');
            }else {
                $('#loading').hide();
                alert('오류가 발생하였습니다.');
            }
        });
    }else{
        alert('강좌를 선택하세요 !!');
    }
});

//이수증 생성 검색 처리
$('#search').on('click', function(){
    var org = $('#org').find('option:selected').val();
    var course= $('#course').find('option:selected').val();
    var run= $('#run').find('option:selected').val();
    //var org_id = $('#org').find('option:selected').attr('id');
    var course_id= $('#course').find('option:selected').attr('id');
    var html="";

    //alert(org+' / '+course+' / '+run);
    if($('#run').find('option:selected').attr('id') == null || $('#run').find('option:selected').attr('id') == ''){
        alert('강좌를 선택하세요');
    }else{
        var html="";
        $.ajax({
            url : '/certificate/',
            data : {
                method : 'certificate',
                course_id : course_id,
                run : run
            }
        }).done(function(data){
            //console.log(data);
            html+="<tr>";
            html+="<td id='uni'>"+org+"</td>";
            html+="<td>"+course+"</td>";
            html+="<td>"+run+"</td>";
            if(data == 'O') {
                html += "<td>생성됨</td>";
            }else{
                html += "<td>미생성</td>";
            }
            html+="</tr>";
            $('#certi_tbody').html(html);
        });
    }
});

//대학별 이수증 검색 처리
$('#uni_search').on('click', function(){
    var org = $('#org').find('option:selected').val();
    var org_id = $('#org').find('option:selected').attr('id');
    var course= $('#course').find('option:selected').val();
    var run= $('#run').find('option:selected').val();
    var course_id= $('#course').find('option:selected').attr('id');
    var html="";
    alert(org_id+' / '+course_id+' / '+run);
    if($('#run').find('option:selected').attr('id') == null || $('#run').find('option:selected').attr('id') == ''){
        alert('강좌를 선택하세요');
    }else{
        var html="";
        $.ajax({
            url : '/certificate/',
            data : {
                method : 'uni_certificate',
                course_id : course_id,
                run : run
            }
        }).done(function(data){
            //console.log(data);
            html+="<tr>";
            html+="<td id='uni'>"+org+"</td>";
            html+="<td>"+course+"</td>";
            html+="<td>"+run+"</td>";
            if(data == 'O') {
                html += "<td>생성됨</td>";
            }else{
                html += "<td>미생성</td>";
            }
            html+="</tr>";
            $('#certi_tbody').html(html);
        });
    }
});




