var file_name= [];
var file_ext= [];
var file_size= [];
jQuery.ajaxSettings.traditional = true;
$(document).ready(function(){
    var value_list;
    var id = '{{id}}';
    var use_yn = '{{use_yn}}';
    var html = "";
    $.ajax({
        url : '/manage/modi_knews/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        if(data[4] != null) {
            value_list = data[4];
            for (var i = 0; i < value_list.length; i++) {
                html += "<li><a href='/manage/file_download/" + value_list[i][1] + "' class='file_download' target='hidden_target' id='" + value_list[i][0] + "'>" + value_list[i][1] + "</a> <button type='button' onclick='file_delete(" + value_list[i][0] + ");' class='btn btn-default' class='file_delete'>X</button></li>";
            }
            $('#saved_file').html(html);
        }
        $('#knews_title').val(data[0]);
        $('.summernote').summernote('code', data[1].replace(/\&\^\&/g));
        $('#odby').val(data[2]);
        if(data[3] == ''){
            $('#head_title').val('선택하세요.');
        }else{
            $('#head_title').val(data[3]);
        }
    });
    $('.summernote').summernote({
        lang : 'ko-KR',
        height : 400,
        callbacks : {
            onImageUpload: function (files, modules, editable){
            sendFile(files[0], modules, editable);
           }
        }
    });
    function sendFile(file, modules, editable) {
        data = new FormData();
        data.append("file", file);
        $.ajax({
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            type: 'POST',
            url: '/manage/summer_upload/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            success: function(data){
                $("#summernote").summernote("insertImage", data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus+' '+errorThrown);
            }
        });
    }
});

// modify board
$('#knews_mod').on('click', function(e){
    try{
        var action_mode;
        var knews_title, knews_content, knews_id, odby;
        var head_title =  $('#head_title').find('option:selected').attr('id');
        knews_title = $('#knews_title').val();
        knews_content = $('.summernote').summernote('code');
        action_mode = 'modi';
        odby = $('#odby').val();
        knews_id = '{{id}}';
        if(head_title == 'null'){
            head_title = ''
        }

        // get file
        var file_list = "";
        file_cnt = $('#file_cnt').text();
        for(i=0; i<file_cnt; i++){
            item = '#file_'+i;
            file_list += ($(item).text());
            file_list += '+';
        }

        // ajax
        $.post("/manage/new_notice/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            title: knews_title,
            content: knews_content,
            board_id : knews_id, // between
            head_title : head_title,
            uploadfile : file_list,
            section: 'K',
            method: action_mode,
            odby: odby
        }).done(function(data){
            location.href='/manage/comm_k_news';
        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
        });
    }catch(e){
        alert(e);
    }
});

// file upload
$(document).on('click', '#fileupload', function(){
    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/manage/new_notice/',
        beforeSubmit: function (data,form,option) {
            if( $("#uploadfile").val() != "" ){
                var ext = $('#uploadfile').val().split('.').pop().toLowerCase();
            }else{
                swal("업로드 경고", "파일을 선택한 후 업로드 버튼을 눌러 주십시오", "warning");
                return false;
            }
        },
        success: function(data){
            for(i=0; i<data.len; i++){
                $( "#file_array" ).append("<div id = 'file_" + i + "'>"+ data.name[i] + "&nbsp; &nbsp;" + data.size[i] +"</div>");
            }
            $( "#file_array" ).append("<div id = 'file_cnt' style = 'display:none'>"+ data.len +"</h5>");
            swal("업로드 완료", "OK 버튼을 눌러주세요", "success");
        },
        error: function() {
            swal("업로드 실패", "다시 시도해주세요", "error");
        }
    })
});

//숨김 처리
$('#knews_del').on('click', function(){
    var id = '{{id}}';
    var use_yn = '{{use_yn}}';
    $.ajax({
        url:'/manage/comm_k_news/',
        data:{
            noti_id:id,
            use_yn:use_yn,
            method:'knews_del'
        }
    }).done(function(data){
        console.log(data);
        location.href='/manage/comm_k_news'
    });
});

//삭제 처리
$('#knews_delete').on('click', function(){
    var id = '{{id}}';
    var use_yn = '{{use_yn}}';
    $.ajax({
        url:'/manage/comm_k_news/',
        data:{
            noti_id:id,
            use_yn:use_yn,
            method:'knews_delete'
        }
    }).done(function(data){
        console.log(data);
        location.href='/manage/comm_k_news'
    });
});
