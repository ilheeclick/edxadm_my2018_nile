$(document).ready(function(){
    var value_list;
    var id = {{id}};
    var use_yn = '{{use_yn}}';
    var html = "";
    $.ajax({
        url : '/modi_knews/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        value_list = data.toString().split(',');
        $('#knews_title').val(value_list[0]);
        $('.summernote').summernote('code', value_list[1].replace(/\&\^\&/g, ','));
        $('#odby').val(value_list[2]);
        for(var i=3;i<value_list.length;i++){
            html += "<a href='#' id='download' >"+value_list[i]+"</a>" +
            "<br>";
        }
        $('#saved_file').html(html);
    })
});

//파일 다운로드
$(document).on('click', '#saved_file > a', function(){
    var file_name = $(this).text();
    var board_id = {{id}};
    var use_yn = '{{use_yn}}';

    $.ajax({
        url : '/modi_knews/'+board_id+'/'+use_yn,
            data : {
                method : 'file_download',
                file_name : file_name
            }
    }).done(function(data){
        $("#download").prop("href", data);
        location.href=$("#download").attr('href');
    });
});


//수정 처리
$('#knews_mod').on('click', function(e){
    try{
        var action_mode;
        var knews_title, knews_content, knews_id, odby;


        knews_title = $('#knews_title').val();
        knews_content = $('.summernote').summernote('code');
        odby = $('#odby').val();
        action_mode = 'modi';
        knews_id = {{id}}


        /* insert to database */
        $.post("/new_knews/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: knews_title,
            nt_cont: knews_content,
            noti_id : knews_id,
            notice: 'K',
            odby: odby,
            method: action_mode
        }).done(function(data){
            location.href='/comm_k_news';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});
//삭제 처리
$('#knews_del').on('click', function(){
    var id = {{id}}
    var use_yn = '{{use_yn}}';

    $.ajax({
        url:'/comm_k_news/',
        data:{
            noti_id:id,
            use_yn:use_yn,
            method:'knews_del'
        }
    }).done(function(data){
        console.log(data);
        location.href='/comm_k_news'
    });
});