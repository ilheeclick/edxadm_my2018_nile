$(document).ready(function(){
    var value_list;
    var id = {{id}}
    $.ajax({
        url : '/modi_notice/'+id,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        value_list = data[0].toString().split(',');
        $('#noticetitle').val(value_list[0]);
        $('.summernote').summernote('code', value_list[1].replace(/\&\^\&/g, ','));

    })
});


//수정 처리
$('#notice_mod').on('click', function(e){
    try{
        var action_mode;
        var noticetitle, noticecontent, notice, noti_id;


        noticetitle = $('#noticetitle').val();
        noticecontent = $('.summernote').summernote('code');
        action_mode = 'modi';
        noti_id = {{ id }}


        /* insert to database */
        $.post("/new_notice/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: noticetitle,
            nt_cont: noticecontent,
            noti_id : noti_id,
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