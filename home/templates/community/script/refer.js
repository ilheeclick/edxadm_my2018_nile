$(document).ready(function(){
    var value_list;
    var action_mode="notice_list";
    var html;
    var total_page;
    //total_page 로드
    $.ajax({
        url: '/comm_reference_room/',
        data:{
            method: 'total_page'
        }
    }).done(function(data){
        //total_page = data[0];
        //alert(total_page);
        //page 소스
        //var obj = $('#pagination').twbsPagination({
        //    visiblePages: 5,
        //    totalPages: total_page,
        //    onPageClick: function (event, page) {
        //        html = "";
        //        console.info(page);
        //        $.ajax({
        //            url:'/comm_notice/',
        //                data:{
        //                    method: action_mode,
        //                    page: page,
        //                }
        //        }).done(function (data) {
        //            value_list = data[0].toString().split(',');
        //            for(var i=0; i<data.length; i++){
        //                html+='<tr id="notice_tr">'
        //                for(var j=0; j<value_list.length; j++){
        //                    if(j==0){
        //                        html+='<td><input type="checkbox" id="'+data[i][j]+'" name="ck">  '+data[i][j]+'</td>'
        //                    }
        //                    else{
        //                        html+='<td>'+data[i][j]+'</td>'
        //                    }
        //                }
        //                html+='</tr>'
        //            }
        //            $('#notice_body').html(html);
        //        })
        //    },
        //});
    });
});



$('#refer_save').on('click', function(e){
    try{
        var action_mode;
        var refertitle, refercontent;
        var file;

        refertitle = $('#refertitle').val();
        refercontent = $('.summernote').summernote('code');
        file = $('#uploadfile').files;
        //referfile = $('#referfile').val();
        alert(refertitle + ' / '  + refercontent);
        action_mode = 'add';

        /* insert to database */
        $.post("/new_refer/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            refer_title: refertitle,
            refer_cont: refercontent,
            method: action_mode
        }).done(function(data){
            location.href='/comm_reference_room';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});

$('#fileupload').on('click', function(){

    var img_form = new FormData();
    var file = $('#uploadfile').files;
    alert(file);
    img_form.append('Upload File', file);
    $.ajax({
        url: '/new_refer/',
        data:{
            file: img_form,
            cache: false,
            processData: false,
            contentType: false
        }
    }).done(function(data){
       alert(data);
    });
});

$('#del_refer').on('click', function(){
    var action_mode = 'notice_del';
    if ($('#del_sel').val() == '전체 삭제'){
        $("input[name^='ck']").prop('checked', true);
    }else{
        $("input[name^='ck']").prop('checked', false);
        $("input[name^='ck']").removeAttr('checked');
    }

    if($("input[name^='ck']:checked").length != 0) {
        $("input[name^='ck']").each(function () {
            if ($(this).is(':checked') == true) {
                //alert($(this).attr('id'));
                $.ajax({
                    url:'/comm_notice/',
                    data:{
                        noti_id:$(this).attr('id'),
                        method:action_mode
                    }
                }).done(function(){
                    location.href='/comm_reference_room'
                });
                new PNotify({
                    title: '시스템 알림',
                    text: '선택된 학생들을 삭제하였습니다',
                    type: 'success',
                    addclass: 'notification-warning',
                    //addclass: 'stack-bar-top',
                    //width: "100%",
                    icon: 'fa fa-check'
                });
            }
        });
    }
});

$('#search_notice').on('click', function(){
    var search_con = $('#search').val();
    var search_title = $('#textarea').val();
    alert(search_con + "/" + search_title);


});
