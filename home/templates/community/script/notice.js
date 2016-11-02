//페이지 로드
//var noti_page;
//$(document).ready(function(){
//    //var search_con = $('#search option:selected').attr('id');
//    //var search_search = $('#textarea').val();
//    var value_list;
//    var action_mode="notice_list";
//    var html;
//    var total_page;
//
//    //total_page 로드
//    $.ajax({
//        url: '/comm_notice/',
//        data:{
//            method : 'total_page',
//        }
//    }).done(function(data){
//        total_page = data[0];
//        //page 소스
//        var obj = $('#pagination').twbsPagination({
//            visiblePages: 5,
//            totalPages: total_page,
//            onPageClick: function (event, page) {
//                html = "";
//                console.info(page);
//                noti_page = page;
//                $.ajax({
//                    url:'/comm_notice/',
//                        data:{
//                            method: 'notice_list',
//                            page: page
//                        }
//                }).done(function (data) {
//                    value_list = data[0].toString().split(',');
//                    for(var i=0; i<data.length; i++){
//                        html+='<tr id="notice_tr">'
//                        for(var j=0; j<value_list.length; j++){
//                            if(j==0){
//                                //html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+data[i][j]+'</td>'
//                                html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+(i+1)+'</td>'
//                            }
//                            else if(j==1){
//                                html+='<td id="title"><a href="/modi_notice/'+data[i][j-1]+'">'+data[i][j]+'</a></td>'
//                            }
//                            else{
//                                html+='<td>'+data[i][j]+'</td>'
//                            }
//                        }
//                        html+='</tr>'
//                    }
//                    $('#notice_body').html(html);
//                });
//            }
//        });
//    });
//});


//검색
//$('#search_notice').on('click', function(){
//    var search_con = $('#search option:selected').attr('id');
//    var search_search = $('#textarea').val();
//    var value_list;
//    var action_mode="notice_list";
//    var html;
//
//    html = "";
//    //alert(search_con + " / " + search_search);
//    $.ajax({
//        url:'/comm_notice/',
//            data:{
//                method: action_mode,
//                search_con : search_con,
//                search_search : search_search,
//                page : noti_page
//            }
//    }).done(function (data) {
//        value_list = data[0].toString().split(',');
//        for(var i=0; i<data.length; i++){
//            html+='<tr id="notice_tr">'
//            for(var j=0; j<value_list.length; j++){
//                if(j==0){
//                    html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+data[i][j]+'</td>'
//                }
//                else if(j==1){
//                    html+='<td id="title"><a href="/modi_notice/'+data[i][j-1]+'">'+data[i][j]+'</a></td>'
//                }
//                else{
//                    html+='<td>'+data[i][j]+'</td>'
//                }
//            }
//            html+='</tr>'
//        }
//        $('#notice_body').html(html);
//    });
//});

//신규 등록
$('#notice_save').on('click', function(e){
    try{
        var action_mode;
        var noticetitle, noticecontent, notice;

        noticetitle = $('#noticetitle').val();
        //noticecontent = $('#noticecontent').val();
        noticecontent = $('.summernote').summernote('code');
        //alert(noticetitle + ' / '  + noticecontent);
        action_mode = 'add';

        /* insert to database */
        $.post("/new_notice/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: noticetitle,
            nt_cont: noticecontent,
            notice: 'N',
            method: action_mode
        }).done(function(data){
            location.href='/comm_notice';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});


//$('#del_notice').on('click', function(){
//    var action_mode = 'notice_del';
//    if ($('#del_sel').val() == '전체 삭제'){
//        $("input[name^='ck']").prop('checked', true);
//    }else if($('#del_sel').val() == '선택하세요'){
//        $(this).prop('checked', true);
//    }
//    else{
//        $("input[name^='ck']").prop('checked', false);
//        $("input[name^='ck']").removeAttr('checked');
//    }
//    if($("input[name^='ck']:checked").length != 0) {
//        $("input[name^='ck']").each(function () {
//            if ($(this).is(':checked') == true) {
//                //alert($(this).attr('id'));
//                $.ajax({
//                    url:'/comm_notice/',
//                    data:{
//                        noti_id:$(this).attr('id'),
//                        method:action_mode
//                    }
//                }).done(function(){
//                    location.href='/comm_notice'
//                });
//            }
//        });
//    }else{
//        alert('삭제할 항목을 선택하세요.')
//    }
//});





