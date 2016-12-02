//var faq_page;
//$(document).ready(function(){
//    var value_list;
//    var action_mode="faq_list";
//    var html;
//    var total_page;
//    //total_page 로드
//    $.ajax({
//        url: '/comm_faq/',
//        data:{
//            method: 'total_page'
//        }
//    }).done(function(data){
//        total_page = data[0]
//        //alert(total_page);
//        //page 소스
//        var obj = $('#pagination').twbsPagination({
//            visiblePages: 5,
//            totalPages: total_page,
//            onPageClick: function (event, page) {
//                html = "";
//                console.info(page);
//                faq_page = page;
//                $.ajax({
//                    url:'/comm_faq/',
//                        data:{
//                            method: action_mode,
//                            page: page,
//                        }
//                }).done(function (data) {
//                    value_list = data[0].toString().split(',');
//                    for(var i=0; i<data.length; i++){
//                        html+='<tr id="faq_tr">';
//                        for(var j=0; j<value_list.length; j++){
//                            if(j==0){
//                                html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+(i+1)+'</td>'
//                            }
//                            else if(j==1){
//                                html+='<td id="title"><a href="/modi_faq/'+data[i][j-1]+'">'+data[i][j]+'</a></td>'
//                                //html+='<td id="title"><a onclick="modi('+data[i][j-1]+')">'+data[i][j]+'</a></td>'
//                            }
//                            else{
//                                html+='<td>'+data[i][j]+'</td>'
//                            }
//                        }
//                        html+='</tr>'
//                    }
//                    $('#faq_body').html(html);
//                })
//            },
//        });
//    });
//});

$(document).ready(function(){
    //var select =  $('#head_title').find('option:selected').val();
    $('.summernote').summernote({
        lang : 'ko-KR',
        height : 400,
    });

});



//신규 등록
$('#faq_save').on('click', function(e){
    var select =  $('#head_title').find('option:selected').val();
    //alert(select);
    try{
        var action_mode;
        var faq_question,faq_answer;
        var head_title =  $('#head_title').find('option:selected').attr('id');
        if(head_title == 'null'){
            head_title='';
        }

        //faq_question = $('.summernote1').summernote('code');
        faq_question = $('#noticecontent').val();
        faq_answer = $('.summernote').summernote('code');
        //alert(faq_question + ' / '  + faq_answer);
        action_mode = 'add';

        /* insert to database */
        $.post("/new_faq/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            faq_question: faq_question,
            faq_answer: faq_answer,
            head_title : head_title,
            section : 'F',
            method: action_mode
        }).done(function(data){
            //console.log(data);
            location.href='/comm_faq';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});

////삭제 처리
//$('#del_faq').on('click', function(){
//    var action_mode = 'faq_del';
//    if ($('#del_sel').val() == '전체 삭제'){
//        $("input[name^='ck']").prop('checked', true);
//    }else if($('#del_sel').val() == '선택하세요'){
//        $(this).prop('checked', true);
//    }
//    else{
//        $("input[name^='ck']").prop('checked', false);
//        $("input[name^='ck']").removeAttr('checked');
//    }
//
//    if($("input[name^='ck']:checked").length != 0) {
//        $("input[name^='ck']").each(function () {
//            if ($(this).is(':checked') == true) {
//                //alert($(this).attr('id'));
//                $.ajax({
//                    url:'/comm_faq/',
//                    data:{
//                        faq_id:$(this).attr('id'),
//                        method:action_mode
//                    }
//                }).done(function(data){
//                    location.href='/comm_faq'
//                });
//            }
//        });
//    }
//});






