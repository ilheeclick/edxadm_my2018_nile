var file_name, file_ext, file_size;
$(document).ready(function(){
    var value_list;
    var id = {{id}};
    var use_yn = '{{use_yn}}';
    var html = "";
    $.ajax({
        url : '/manage/modi_knews/'+id+'/'+use_yn,
            data : {
                method : 'modi'
            }
    }).done(function(data){
        //console.log(data);
        if(data[4] != null){
            value_list = data[4].toString().split(',');
            for(var i=0;i<value_list.length;i++){
                html += "<a href='#' id='download' >"+value_list[i]+"</a>" +
                "<br>";
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
    //alert('d');
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
                //console.log(data);
                $("#summernote").summernote("insertImage", data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus+' '+errorThrown);
            }
        });
    }
});

//파일 다운로드
$(document).on('click', '#saved_file > a', function(){
    var file_name = $(this).text();
    var board_id = {{id}};
    var use_yn = '{{use_yn}}';

    $.ajax({
        url : '/manage/modi_knews/'+board_id+'/'+use_yn,
            data : {
                method : 'file_download',
                file_name : file_name
            }
    }).done(function(data){
        console.log(data);
        $("#download").prop("href", data);
        location.href=$("#download").attr('href');
    });
});


//수정 처리
$('#knews_mod').on('click', function(e){
    try{
        var action_mode;
        var knews_title, knews_content, knews_id, odby;
        var uploadfile = $('#uploadfile').val().substr(12);
        var head_title =  $('#head_title').find('option:selected').attr('id');

        knews_title = $('#knews_title').val();
        knews_content = $('.summernote').summernote('code');
        odby = $('#odby').val();
        action_mode = 'modi';
        knews_id = {{id}}
        //alert(uploadfile+'/'+file_name+'/'+file_ext+'/'+file_size)

        if(head_title == 'null'){
            head_title = ''
        }
        /* insert to database */
        $.post("/manage/new_knews/", {
            csrfmiddlewaretoken:$.cookie('csrftoken'),
            nt_title: knews_title,
            nt_cont: knews_content,
            noti_id : knews_id,
            head_title : head_title,
            uploadfile : uploadfile,
            file_name : file_name,
            file_ext : file_ext,
            file_size : file_size,
            notice: 'K',
            odby: odby,
            method: action_mode
        }).done(function(data){
            location.href='/manage/comm_k_news';

        }).fail(function(error) {
            alert('error = ' + error.responseJSON);
            alert('파일명이 잘못되었습니다.');
        });
    }catch(e){
        alert(e);
    }
});

//파일 업로드
$(document).on('click', '#fileupload', function(){
    $('#uploadform').ajaxForm({
        type: "POST",
        url:'/manage/new_knews/',
        beforeSubmit: function (data,form,option) {
            if( $("#uploadfile").val() != "" ){

                var ext = $('#uploadfile').val().split('.').pop().toLowerCase();

                //if($.inArray(ext, ['xls','xlsx', 'txt', 'hwp', 'pptx', 'jpg']) == -1) {
                //    //alert('xls,xlsx 파일만 업로드 할수 있습니다.');
                //    alert('정해진 파일 형식만 업로드 할수 있습니다.');
                //    return false;
                //}
            }else{
                alert('파일을 선택한 후 업로드 버튼을 눌러 주십시오.');
                return false;
            }
        },
        success: function(adata){
            //성공후 서버에서 받은 데이터 처리
            alert("업로드에 성공했습니다.");
            console.log(adata);
            file_name=adata[0];
            file_ext=adata[1];
            file_size=adata[2];
            console.log('file_name', file_name, 'file_ext', file_ext, 'file_size', file_size)

        },
        error: function() {
            alert("업로드에 실패했습니다.");
        }
    })
});

//숨김 처리
$('#knews_del').on('click', function(){
    var id = {{id}};
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
    var id = {{id}};
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