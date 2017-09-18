/**
 * Created by dev on 2016. 10. 20..
 */
//대학명 처리
$(document).ready(function(){
    var html="";
    var html2="";
    var value_list=[];
    var value_list2=[];
    $('#loading').hide();
    $.ajax({
        url : '/manage/certificate/',
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
    });


    //초기 이수현황 출력
    //$.ajax({
    //    url : '/certificate/',
    //    data : {
    //        method : 'uni_certi'
    //    }
    //}).done(function(data){
    //    for(var i=0; i<data.length; i++){
    //        value_list = data[i].toString().split(',');
    //        html2+="<tr>";
    //        for(var j=0; j<value_list.length; j++){
    //            //console.log(i+"/"+value_list[j])
    //            html2+="<td>"+value_list[j]+"</td>"
    //        }
    //        html2+="</tr>"
    //    }
    //    $('#uni_body').html(html2)
    //});

    //대학별 이수증 검색 처리
    //$('#uni_search').on('click', function(){
    //    var org = $('#org').find('option:selected').val();
    //    var course= $('#course').find('option:selected').val();
    //    var org_id = $('#org').find('option:selected').attr('id');
    //    var run= $('#course').find('option:selected').attr('name');
    //    var course_id= $('#course').find('option:selected').attr('id');
    //    var html="";
    //    //alert(org_id+' / '+course_id+' / '+run);
    //    if($('#org').find('option:selected').attr('id') == null || $('#org').find('option:selected').attr('id') == ''){
    //        alert('대학명을 선택하세요.');
    //    }
    //    else if($('#org').find('option:selected').attr('id') != null && $('#course').find('option:selected').attr('id') != null ){
    //        var html2="";
    //        $.ajax({
    //            url : '/certificate/',
    //            data : {
    //                method : 'uni_certi',
    //                org_id : org_id,
    //                run : run
    //            }
    //        }).done(function(data){
    //            console.log(data);
    //            if(data.length == null || data == ''){
    //                alert('정보가 없습니다.')
    //            }else{
    //                for(var i=0; i<data.length; i++){
    //                    value_list = data[i].toString().split(',');
    //                    html2+="<tr>"
    //                    for(var j=0; j<value_list.length; j++){
    //                        html2+="<td>"+value_list[j]+"</td>"
    //                    }
    //                    html2+="</tr>"
    //                }
    //                $('#uni_body').html(html2)
    //            }
    //        });
    //    }
    //    else{
    //        var html2="";
    //        $.ajax({
    //            url : '/certificate/',
    //            data : {
    //                method : 'uni_certi',
    //                org_id : org_id
    //                //course_id : course_id,
    //            }
    //        }).done(function(data){
    //            console.log(data);
    //            if(data.length == null || data == ''){
    //                alert('정보가 없습니다.')
    //            }else{
    //                for(var i=0; i<data.length; i++){
    //                    value_list = data[i].toString().split(',');
    //                    html2+="<tr>"
    //                    for(var j=0; j<value_list.length; j++){
    //                        html2+="<td>"+value_list[j]+"</td>"
    //                    }
    //                    html2+="</tr>"
    //                }
    //                $('#uni_body').html(html2)
    //            }
    //        });
    //    }
    //});
});

//강좌명 기관번호 처리
$(document).on('change', '#org', function(){
    var org = $(this).find('option:selected').attr('id');
    var html = "";
    var course = "";
    if(org == '' || org == null){
        alert('학교를 선택하세요.');
    }else{
        html="";
        $.ajax({
            url : '/manage/certificate/',
            data : {
                method : 'course',
                org : org
            }
        }).done(function(data){
            html+="<option>선택하세요</option>";
            for(var i=0; i<data.length;i++){
                html+="<option id="+data[i][0]+" name="+data[i][2]+">"+data[i][1]+"   ("+data[i][2]+")</option>";
                $('#course').html(html);
            }
        });
    }
});
