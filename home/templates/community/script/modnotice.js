$(document).ready(function(){
    var value_list;
    var id = {{id}}
    var use_yn = '{{use_yn}}';
    $.ajax({
        url : '/modi_notice/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        value_list = data[0].toString().split(',');
        $('#noticetitle').val(value_list[0]);
        $('.summernote').summernote('code', value_list[1].replace(/\&\^\&/g, ','));
        $('#odby').val(value_list[2]);
    })
});


//수정 처리
$('#notice_mod').on('click', function(e){
    try{
        var action_mode;
        var noticetitle, noticecontent, notice, noti_id, odby;


        noticetitle = $('#noticetitle').val();
        noticecontent = $('.summernote').summernote('code');
        odby = $('#odby').val();
        action_mode = 'modi';
        noti_id = {{ id }}


        /* insert to database */
        $.post("/new_notice/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: noticetitle,
            nt_cont: noticecontent,
            noti_id : noti_id,
            notice: 'N',
            odby: odby,
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
//삭제 처리
$('#notice_del').on('click', function(){
    var id = {{id}}
    var use_yn = '{{use_yn}}';

    $.ajax({
        url:'/comm_notice/',
        data:{
            noti_id:id,
            use_yn:use_yn,
            method:'notice_del'
        }
    }).done(function(data){
        console.log(data);
        location.href='/comm_notice'
    });
});